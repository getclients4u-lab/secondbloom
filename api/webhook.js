// Vercel serverless webhook for Stripe payment events (secondbloom)
// ESM only. bodyParser:false REQUIRED (Vercel's JSON parsing breaks Stripe HMAC).
// Pattern proven on dopamine-reset + habitbloom.
import crypto from 'crypto';

export const config = { api: { bodyParser: false } };

const WH_SECRET = process.env.STRIPE_WEBHOOK_SECRET || '';
const GH_TOKEN = process.env.GH_TOKEN || '';
const GH_OWNER = process.env.GH_OWNER || 'getclients4u-lab';
const GH_REPO = process.env.GH_DATA_REPO || 'secondbloom-data';
const MAIL_FROM = process.env.SECONDBLOOM_MAIL_FROM || 'gentledesk632@agentmail.to';
const AGENTMAIL_KEY = process.env.AGENTMAIL_API_KEY || '';
const BUYERS_FILE = 'buyers.json';
const USERS_FILE = 'users.json';
const ACCESS_PEPPER = process.env.ACCESS_PEPPER || 'secondbloom-pepper-0lz502u9';

function genCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let s = '';
  for (let i = 0; i < 10; i++) s += chars[crypto.randomInt(chars.length)];
  return `SB-${s.slice(0, 5)}-${s.slice(5)}`;
}

function hashCode(code) {
  return crypto.createHash('sha256').update(`${code}::${ACCESS_PEPPER}`).digest('hex');
}

// Read raw request body as a Buffer (so HMAC over raw bytes works)
function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function verifyStripe(payloadBuf, sigHeader) {
  if (!WH_SECRET || !sigHeader) return false;
  try {
    const parts = {};
    sigHeader.split(',').forEach(p => { const [k, ...v] = p.split('='); parts[k] = v.join('='); });
    const ts = parts['t'], sig = parts['v1'];
    if (!ts || !sig) return false;
    const expected = crypto.createHmac('sha256', WH_SECRET).update(`${ts}.${payloadBuf}`).digest('hex');
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sig));
  } catch (e) { return false; }
}

async function ghGet(path) {
  const res = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${path}`,
    { headers: { Authorization: `token ${GH_TOKEN}`, Accept: 'application/vnd.github.v3+json' } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error('GH GET ' + res.status);
  return res.json();
}

async function ghPut(path, content, sha, message) {
  const res = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${path}`, {
    method: 'PUT',
    headers: { Authorization: `token ${GH_TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/vnd.github.v3+json' },
    body: JSON.stringify({ message, content: Buffer.from(content).toString('base64'), sha }),
  });
  return res.ok;
}

async function addToAllowList(email) {
  try {
    await fetch('https://api.agentmail.to/v0/lists/send/allow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${AGENTMAIL_KEY}` },
      body: JSON.stringify({ entry: email }),
    });
  } catch (e) { /* best effort */ }
}

async function sendEmail(buyer, code) {
  if (!AGENTMAIL_KEY || !MAIL_FROM) return false;
  await addToAllowList(buyer.email);
  const body =
`Welcome to SecondBloom™ — The Second Bloom Method™ 🌸

Hi ${buyer.name || 'there'},

Thank you! Your order is confirmed.

YOUR PERSONAL ACCESS CODE: ${code || 'SB-XXXXX-XXXXX'}

OPEN YOUR DOWNLOADS:
→ https://secondbloom.vercel.app/download.html
(enter your email + access code above)

WHAT'S INSIDE (8 deliverables):
• 1. The Second Bloom Core Guide (B.L.O.O.M. roadmap + 34-symptom dictionary)
• 2. The 7-Day Second Puberty Census (symptom tracker + hormone timeline)
• 3. The Cool Sleep System (end the 2 AM furnace)
• 4. The Hot Flash Rescue Kit (34 triggers + 60-second cool-down scripts)
• 5. The Hormone Food Map (+ supplement cheat-sheet)
• 6. The Strength & Bone Builder (10 min, 3x/week)
• 7. The Mood & Brain-Fog Toolkit
• 8. The Doctor Visit Scripts (+ HRT guide + 90-Day Thrive Plan)

START TONIGHT:
1. Read the Core Guide (20 minutes)
2. Start the 7-Day Symptom Census tomorrow morning
3. Book your doctor visit for 3 weeks out (Tool 8 scripts it)

60-day, no-questions-asked "Peace of Mind" guarantee — keep everything either way.

You're not falling apart. You're starting over — and now you have the manual.
— The SecondBloom Team`;
const res = await fetch(`https://api.agentmail.to/v0/inboxes/${MAIL_FROM}/messages/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${AGENTMAIL_KEY}` },
    body: JSON.stringify({ to: [buyer.email], subject: "Your SecondBloom™ Method access 🌸", text: body }),
  });
  return res.ok;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  const raw = await readRawBody(req);
  const sig = req.headers['stripe-signature'] || '';
  if (!verifyStripe(raw, sig)) return res.status(400).json({ error: 'invalid signature' });

  let event;
  try { event = JSON.parse(raw.toString('utf8')); } catch (e) { return res.status(400).json({ error: 'bad json' }); }

  if (event.type === 'checkout.session.completed') {
    const s = event.data.object;
    const buyer = {
      id: s.id,
      email: (s.customer_details && s.customer_details.email) || s.customer_email || '',
      name: (s.customer_details && s.customer_details.name) || '',
      amount: (s.amount_total || 0) / 100,
      currency: s.currency || 'usd',
      product: 'secondbloom',
      ts: new Date().toISOString(),
    };
    if (!buyer.email) return res.status(200).json({ received: true, error: 'no email' });

    let buyers = [];
    let users = [];
    let stored = false, emailed = false, registered = false;
    let accessCode = null;
    try {
      const existing = await ghGet(BUYERS_FILE);
      if (existing) {
        try { buyers = JSON.parse(Buffer.from(existing.content, 'base64').toString('utf8')); } catch (e) { buyers = []; }
        if (!Array.isArray(buyers)) buyers = [];
      }
      buyers.push(buyer);
      stored = await ghPut(BUYERS_FILE, JSON.stringify(buyers, null, 2), existing ? existing.sha : undefined,
        `buyer: ${buyer.email}`);
    } catch (e) { stored = false; }

    // Register buyer as product user (personal access code)
    try {
      const uExisting = await ghGet(USERS_FILE);
      if (uExisting) {
        try { users = JSON.parse(Buffer.from(uExisting.content, 'base64').toString('utf8')); } catch (e) { users = []; }
        if (!Array.isArray(users)) users = [];
      }
      const norm = String(buyer.email).trim().toLowerCase();
      const existingUser = users.find(u => String(u.email || '').trim().toLowerCase() === norm);
      if (existingUser && existingUser.status === 'active') {
        registered = true; // already has access
      } else {
        accessCode = genCode();
        const user = {
          email: norm,
          name: buyer.name || norm.split('@')[0],
          codeHash: hashCode(accessCode),
          status: 'active',
          added: new Date().toISOString(),
          source: 'stripe',
        };
        if (existingUser) {
          const i = users.findIndex(u => String(u.email || '').trim().toLowerCase() === norm);
          users[i] = user;
        } else {
          users.push(user);
        }
        registered = await ghPut(USERS_FILE, JSON.stringify(users, null, 2), uExisting ? uExisting.sha : undefined,
          `user: ${norm}`);
      }
    } catch (e) { registered = false; }

    emailed = await sendEmail(buyer, accessCode);
    return res.status(200).json({ received: true, stored: stored ? 1 : 0, registered: registered ? 1 : 0, emailed });
  }
  return res.status(200).json({ received: true, ignored: event.type });
}
