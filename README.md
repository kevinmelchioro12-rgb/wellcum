# Wellcum — Men's Spa & Lifestyle Club + 4U Hotel

Static website rebuild of the **Wellcum** club ([wellcum.at](https://wellcum.at)) and its partner **4U Hotel** ([4uhotel.at](https://4uhotel.at)), with a luxury dark aesthetic, opening videos, and full **IT / EN / DE** versions.

## Structure
- `index.html` — Wellcum club (fuchsia theme)
- `hotel.html` — 4U Hotel (sand theme)
- `profilo.html` — Big Five / OCEAN psychometric profile (IT; `en/profile.html`, `de/profil.html`)
- `en/`, `de/` — English and German versions
- `css/`, `js/`, `assets/` — shared styles, scripts, and media
- `js/profile.js` — self-contained assessment engine (item bank, scoring, radar, i18n)

Dependency-free HTML/CSS/JS. Hero sections use the brands' opening videos; the design features an animated palette, scroll reveals, parallax, a custom cursor, an 18+ age gate (club pages), a discreet gallery, and a fully responsive layout. The two sites are cross-linked, with hotel booking pointing to the live reservation page.

### Big Five / OCEAN profile
An interactive personality self-assessment built on the **public-domain IPIP Big-Five Factor Markers** (50 items, Goldberg 1992) — the same framework family as the **IPIP-NEO** and **BFI-2**. It scores the five OCEAN traits (with proper reverse-keying), renders an inline-SVG radar chart and per-trait narratives, and is fully localised in IT / EN / DE. Everything runs client-side: answers and results are kept in `localStorage` and never leave the browser. The page is for self-knowledge only and is not a clinical instrument.

## Local preview
```bash
python -m http.server 5050
# then open http://localhost:5050/
```
