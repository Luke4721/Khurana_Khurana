# Khurana & Khurana — Site (rebuilt on the cloned base)

The Momento Legal clone has been fully rebranded into a **Khurana & Khurana (K&K)**
site: their identity, content, team, articles, offices, and color language — on the
cloned site's structure and design system.

## What's inside

- **63 pages**, all verified serving 200 locally:
  - Home, About, Culture/Pro-Bono, Team, Expertise (10 practice areas), Insights (15 real K&K articles), Contact, Policies (6)
  - 24 team profile pages (real K&K practitioners with their photos and bios)
- **K&K brand palette** (replaces the indigo): warm charcoal `#14100e` base,
  maroon `#7C0303`/`#9A0000` accents, slate `#2b5672`, bronze highlights.
- **Identity**: typographic "KHURANA & KHURANA" wordmark with
  "Advocates & IP Attorneys · An ISO 9001:2022 Certified Firm" tagline,
  K&K monogram favicon, `info@khuranaandkhurana.com`, `+91-(120) 3132513`,
  K&K socials (Instagram/LinkedIn/Facebook/YouTube/WhatsApp).
- **Contact**: all 10 India offices (Noida HQ, New Delhi, Bangalore, Pune, Mumbai,
  Hyderabad, Punjab, Chennai, Ahmedabad, Indore) with addresses and phone numbers.
- **Team**: 24 practitioners — 3 Founding (incl. Tarun Khurana, Managing Partner),
  Partners, Directors, Associate Partners, Principal Associates — each with a
  profile page (photo, role, office, practice, full bio).
- **Insights**: 15 real K&K articles (IBC, competition, data protection, trademarks,
  UDRP, GST, …) with cover images and full body text.
- **Turkish mirror removed**: `/tr/*` 308-redirects to `/` (K&K has no Turkish content).
- Legacy `/cookie-policy` → `/policies/cookie-policy` kept.

## Static-rendering note

Most pages are **fully static documents** (React hydration scripts stripped).
Reason: the original ships precomputed React flight data per page; once page
content was rewritten, that data no longer matched the markup, and React's
hydration fails fatally on mismatch. Static rendering keeps every page working
pixel-perfect (Tailwind CSS, fonts, videos, and images all load normally).
Trade-offs: no client-side page transitions and no JS-driven widgets on those
pages (e.g. the 3D clock on the old contact page); normal `<a>` navigation is used.

## Run

```bash
npm start        # http://127.0.0.1:3000 (PORT to override)
```

`server.mjs` provides clean URLs, the `/_next/image` passthrough shim, and redirects.

## Layout

```
server.mjs            static server + image shim + redirects
public/
  index.html          home            team/*.html       24 profiles
  about|culture|contact|policies|404 .html
  expertise/*.html    10 K&K practice areas
  insights/*.html     15 K&K articles
  policies/*.html     privacy / terms / Bar Council / notices
  images/teams        K&K member photos   images/insights   article covers
  _next/static/chunks patched CSS/JS bundles
```

Content © Khurana & Khurana, Advocates and IP Attorneys (khuranaandkhurana.com).
This is a development base; verify content and branding before any public use.
