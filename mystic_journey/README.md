# The Traveler's Atlas — `mystic_journey/`

An immersive portfolio homepage: project realms floating in the Pillars of
Creation, a wandering guide, and a "sucked into the realm" transition that
never leaves space. Fully self-contained — **nothing outside this folder is
ever modified**; `images/`, `content/`, and `static/` are read-only sources.

## Folder structure

```
mystic_journey/
├── build.py              # the ONLY build script for this site
├── data/
│   └── realms.yaml       # single source of truth: names, teasers, palettes,
│                         #   positions, guide anchors — edit this, not templates
├── templates/            # Jinja2: base.html, index.html, realm.html, ledger.html
├── static/
│   ├── css/atlas.css
│   └── js/  home.js, realm.js
├── assets/               # GENERATED — copied/derived imagery, resume (safe to delete; rebuilt)
├── index.html            # GENERATED homepage
├── realms/<slug>/        # GENERATED realm pages
├── ledger/               # GENERATED Traveler's Ledger stub
└── sitemap.xml           # GENERATED
```

Generated output is committed alongside sources (same convention as the
repo's `docs/` tree). Rebuild after any data/template/CSS-source change.

## Build & preview

```bash
# from the repo root
python mystic_journey/build.py
python -m http.server 8000
# open http://localhost:8000/mystic_journey/
```

Requires the repo's existing deps (`pip install -r requirements.txt`) plus
Pillow (used to precompute the blurred nebula + resized keyart variants).

Notes for local preview:
- The header's **Classic view** link points at `/index.html` (the deployed
  classic site, from `site.classic_url` in the data file). When the page is
  served from `localhost`/`127.*`, a small script in `base.html` rewrites it
  to `/docs/index.html` so it works from a repo-root preview server too.
- The arrival choreography runs **once per session**; to replay it, clear
  sessionStorage (DevTools → Application) or open a private window.
- GSAP loads from a CDN, so choreography and the suck-in need network;
  without it the site quietly falls back to plain fades.

## Adding the Lunar content later

1. Write `content/projects/lunar.md` in the same frontmatter style as the
   other projects (`name`, `blurb`, `tags`, `links`, then body sections).
2. In `data/realms.yaml`, on the `lunar` realm set:
   ```yaml
   content: "content/projects/lunar.md"
   status: live          # was: in-progress
   ```
3. `python mystic_journey/build.py` — the island brightens and the realm
   page fills itself in. Nothing else to touch.

## Adding a brand-new realm

1. Drop keyart into `images/` (any wide-aspect webp/avif pair, or omit for a
   silhouette island).
2. Append an entry to `realms:` in `data/realms.yaml` — copy an existing one;
   the fields are documented at the top of the file. Positions are viewport
   percentages; pick a gap in the sky.
3. Rebuild. The island, its page, teaser, transition, and sitemap entry are
   all generated from the data.

Renaming anything (mythic or professional) is also just a data edit.

## Editing a realm page's content

Everything a realm page shows comes from two places:

- **Facts** (blurb, tags, links) — the frontmatter of the file named in the
  realm's `content:` field under `content/projects/`. Edit there; the classic
  site and the atlas both pick it up.
- **Atlas layer** (in `data/realms.yaml`, per realm):
  - `narration:` — list of 2–3 storybook passages (scroll-revealed)
  - `record.role:` — one paragraph, recruiter-facing (`null` renders a
    TODO placeholder — currently the case for `prithvi-eo`)
  - `record.results:` — list of 1–2 concrete result bullets
  - `artifacts:` — list of `{src, caption}`; `src` points at an original
    under `static/images/projects/...` — the build converts it to a sized
    webp in `assets/artifacts/` automatically (originals never touched)

## Activating the Traveler's Ledger

The header already links to `ledger/` (a "coming soon" shell rendered from
`templates/ledger.html`). To activate it, replace that template's narration
block with real content and rebuild. To hide it instead, delete the
`Traveler’s Ledger` line from the header block in `templates/base.html`.

## Tuning the transition

The homepage suck-in crossfades to a **precomputed** blurred+darkened nebula
(`assets/bg/nebula_blur.*`), which is byte-identical to every realm page's
backdrop — that's what makes the page swap invisible. Blur radius / darkening
/ width live at the top of `build.py` (`BLUR_RADIUS`, `BLUR_DARKEN`,
`BLUR_WIDTH`). Change them and rebuild; homepage and realm pages stay in
sync automatically.

## Deploying

This folder previews standalone. To publish it, copy `mystic_journey/`
into whatever tree GitHub Pages serves (currently `docs/`) — decision
deliberately left open; also update `site.base_url` in `data/realms.yaml`
(used for sitemap + OG tags) before going live.
