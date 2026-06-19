# Wellcum — Men's Spa & Lifestyle Club + 4U Hotel

Static website rebuild of the **Wellcum** club ([wellcum.at](https://wellcum.at)) and its partner **4U Hotel** ([4uhotel.at](https://4uhotel.at)), with a luxury dark aesthetic, opening videos, and full **IT / EN / DE** versions.

## Structure
- `index.html` — Wellcum club (fuchsia theme)
- `hotel.html` — 4U Hotel (sand theme)
- `en/`, `de/` — English and German versions
- `css/`, `js/`, `assets/` — shared styles, script, and media

Dependency-free HTML/CSS/JS. Hero sections use the brands' opening videos; the design features an animated palette, scroll reveals, parallax, a custom cursor, an 18+ age gate (club pages), a discreet gallery, and a fully responsive layout. The two sites are cross-linked, with hotel booking pointing to the live reservation page.

## Local preview
```bash
python -m http.server 5050
# then open http://localhost:5050/
```
