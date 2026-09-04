# 🌸 SecondBloom™ — The Second Bloom Method™ for Perimenopause

**Niche:** Perimenopause / "Second Puberty" — the viral women's-health trend cresting
right now (#perimenopause = 4.17 BILLION TikTok views; "Second Puberty" is the 2026
shorthand; hospitals are airing specials like St. Luke's "The Second Puberty Nobody
Warned You About" starting Sept 7, 2026).

**The gap:** Awareness is exploding, but women still have no roadmap — comments
sections are full of women who now know *what* it is and not *what to do*. SecondBloom
sells the execution layer.

**Product:** The Second Bloom Method™ — a 5-stage system (**B.L.O.O.M.**: Baseline →
Lights Out → Optimize → Open Up → Master) delivered as **8 done-for-you PDF tools**
for **$19** (launch price, $79 value).

## The 8 deliverables (real product, in private repo `secondbloom-data`)

1. `core-guide.pdf` — The Second Bloom Core Guide (B.L.O.O.M. roadmap + 34-symptom dictionary)
2. `symptom-census.pdf` — The 7-Day Second Puberty Census (tracker + hormone-timeline locator)
3. `cool-sleep-system.pdf` — The Cool Sleep System (end the 2 AM furnace)
4. `hot-flash-rescue-kit.pdf` — The Hot Flash Rescue Kit (34 triggers + 60-sec cool-down scripts)
5. `hormone-food-map.pdf` — The Hormone Food Map (+ supplement cheat-sheet)
6. `strength-bone-builder.pdf` — The Strength & Bone Builder (10 min, 3×/week)
7. `mood-brain-fog-toolkit.pdf` — The Mood & Brain-Fog Toolkit
8. `doctor-talk-scripts.pdf` — The Doctor Visit Scripts (+ HRT guide + 90-Day Thrive Plan)

## Order stack (proven GutMap architecture, adapted)

- **Buy:** Stripe payment link (test mode) → thank-you.html
- **Webhook:** `/api/webhook` (Stripe HMAC) → stores buyer in `buyers.json`, registers
  user + generates `SB-XXXXX-XXXXX` access code in `users.json`, emails code via
  AgentMail (from: gentledesk632@agentmail.to)
- **Delivery:** `/api/download` serves PDFs from the PRIVATE repo only after
  email+code verification; `/api/verify` checks codes; `/api/admin` manages users
  (add/revoke/list/orders)
- **Files:** users.json + buyers.json + product PDFs live ONLY in
  `github.com/getclients4u-lab/secondbloom-data` (private). The public repo has no
  PDFs and no buyer data.

## Repos

- Public site: `github.com/getclients4u-lab/secondbloom` → deployed on Vercel
- Private data: `github.com/getclients4u-lab/secondbloom-data` (private)

## Live URL

**https://secondbloom-glow.vercel.app** (final URL confirmed after deploy)

## Content assets

- Landing page: `index.html` (long-form, B.L.O.O.M. mechanism, 60-day guarantee)
- Emails: `emails/launch-emails.md` (teaser → launch → follow-up)
- VSL: `vsl/vsl-script.md` + `vsl/vsl-slideshow.mp4` (~5:00 silent UPPERCASE slideshow
  targeting the #SecondPuberty trend videos; voice track renders when ElevenLabs key
  is available)
- Admin: `/admin.html` · Member downloads: `/download.html` · Post-purchase: `/thank-you.html`

---
*Educational wellness content — not medical advice. © 2026 SecondBloom. Built nightly
by Archie for Castle. 🌸*
