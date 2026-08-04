"""Build The Traveler's Atlas (mystic_journey) — fully self-contained.

Reads (read-only, never modifies):
  mystic_journey/data/realms.yaml   -> the single source of truth for the atlas
  content/projects/*.md             -> factual project content (frontmatter + body)
  images/, static/                  -> source imagery + resume

Writes ONLY inside mystic_journey/:
  index.html                        -> the homepage scene
  realms/<slug>/index.html          -> one page per realm
  ledger/index.html                 -> Traveler's Ledger stub
  sitemap.xml
  assets/                           -> copied + generated imagery (originals untouched)

Run:      python mystic_journey/build.py        (from the repo root)
Preview:  python -m http.server 8000            (repo root) -> http://localhost:8000/mystic_journey/
"""
from pathlib import Path
import json
import shutil
import sys

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent          # mystic_journey/
REPO = HERE.parent                              # repo root (read-only)
ASSETS = HERE / "assets"

# Blur treatment for the persistent-nebula transition. The homepage suck-in
# crossfades to THIS exact image, and realm pages use it as their backdrop,
# so the page swap is invisible. Change these and rebuild to retune both.
BLUR_WIDTH = 1920
BLUR_RADIUS = 10
BLUR_DARKEN = 0.70


# ---------------------------------------------------------------- utilities

def newer(src: Path, dst: Path) -> bool:
    """True if dst is missing or older than src (idempotent asset builds)."""
    return not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime


def copy_asset(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if newer(src, dst):
        shutil.copy2(src, dst)


def save_variants(img: Image.Image, stem: Path, webp_q=72, avif_q=55, jpg_q=None):
    """Save webp (+avif if the encoder is available, + optional jpg fallback).

    Returns dict of format -> relative-to-mystic_journey path string.
    """
    out = {}
    stem.parent.mkdir(parents=True, exist_ok=True)
    webp = stem.with_suffix(".webp")
    img.save(webp, "WEBP", quality=webp_q, method=4)
    out["webp"] = str(webp.relative_to(HERE))
    try:
        avif = stem.with_suffix(".avif")
        img.save(avif, "AVIF", quality=avif_q)
        out["avif"] = str(avif.relative_to(HERE))
    except Exception:
        pass  # no AVIF encoder — webp (+jpg) is fine
    if jpg_q:
        jpg = stem.with_suffix(".jpg")
        img.convert("RGB").save(jpg, "JPEG", quality=jpg_q, optimize=True)
        out["jpg"] = str(jpg.relative_to(HERE))
    return out


# ------------------------------------------------------------------- assets

def build_assets(data: dict) -> dict:
    """Copy source imagery into assets/ and generate derived variants."""
    gen = {}

    # Background: copy originals.
    bg = data["site"]["background"]
    for fmt in ("webp", "avif"):
        src = REPO / bg[fmt]
        dst = ASSETS / "bg" / f"nebula.{fmt}"
        copy_asset(src, dst)
        gen[f"bg_{fmt}"] = str(dst.relative_to(HERE))

    # Blurred + darkened variant (precomputed — never live-blurred in CSS).
    src = REPO / bg["webp"]
    blur_stem = ASSETS / "bg" / "nebula_blur"
    if newer(src, blur_stem.with_suffix(".webp")):
        img = Image.open(src)
        w = BLUR_WIDTH
        img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
        img = ImageEnhance.Brightness(img).enhance(BLUR_DARKEN)
        variants = save_variants(img, blur_stem, webp_q=62, avif_q=50, jpg_q=70)
    else:
        variants = {
            fmt: str(blur_stem.with_suffix("." + fmt).relative_to(HERE))
            for fmt in ("webp", "avif", "jpg")
            if blur_stem.with_suffix("." + fmt).exists()
        }
    for fmt, path in variants.items():
        gen[f"blur_{fmt}"] = path

    # Character.
    guide = data["guide"]
    for key, fmt in (("image_webp", "webp"), ("image_avif", "avif")):
        src = REPO / guide[key]
        dst = ASSETS / "character" / f"wayfinder.{fmt}"
        copy_asset(src, dst)
        gen[f"guide_{fmt}"] = str(dst.relative_to(HERE))

    # Resume.
    src = REPO / data["site"]["resume_src"]
    dst = ASSETS / "resume.pdf"
    copy_asset(src, dst)
    gen["resume"] = str(dst.relative_to(HERE))

    # Realm keyart: copy full-size originals + generate 800w island variants.
    for realm in data["realms"]:
        ka = realm.get("keyart")
        if not ka:
            continue
        paths = {}
        for fmt in ("webp", "avif"):
            src = REPO / ka[fmt]
            dst = ASSETS / "realms" / f"{realm['slug']}.{fmt}"
            copy_asset(src, dst)
            paths[f"full_{fmt}"] = str(dst.relative_to(HERE))
        # 800w variants for homepage islands (from the webp original).
        src = REPO / ka["webp"]
        stem = ASSETS / "realms" / f"{realm['slug']}_800"
        if newer(src, stem.with_suffix(".webp")):
            img = Image.open(src)
            img = img.resize((800, round(img.height * 800 / img.width)), Image.LANCZOS)
            small = save_variants(img, stem, webp_q=74, avif_q=56)
        else:
            small = {
                fmt: str(stem.with_suffix("." + fmt).relative_to(HERE))
                for fmt in ("webp", "avif")
                if stem.with_suffix("." + fmt).exists()
            }
        for fmt, path in small.items():
            paths[f"small_{fmt}"] = path
        realm["assets"] = paths

    # Artifacts: convert source figures to lazy-loadable webp (max 1400w),
    # recording dimensions so pages reserve space (no layout shift).
    for realm in data["realms"]:
        processed = []
        for art in realm.get("artifacts") or []:
            src = REPO / art["src"]
            if not src.exists():
                print(f"  !! artifact missing for {realm['slug']}: {art['src']}")
                continue
            stem = ASSETS / "artifacts" / realm["slug"] / src.stem
            dst = stem.with_suffix(".webp")
            if newer(src, dst):
                img = Image.open(src)
                if img.width > 1400:
                    img = img.resize(
                        (1400, round(img.height * 1400 / img.width)), Image.LANCZOS)
                dst.parent.mkdir(parents=True, exist_ok=True)
                img.save(dst, "WEBP", quality=84, method=4)
            with Image.open(dst) as im:
                w, h = im.size
            processed.append({
                "src": str(dst.relative_to(HERE)),
                "w": w, "h": h,
                "caption": art["caption"].strip(),
            })
        realm["artifacts_out"] = processed
    return gen


# ------------------------------------------------------------------ content

def load_project(realm: dict) -> None:
    """Attach frontmatter facts (and body html) from the realm's content file."""
    src = realm.get("content")
    if not src:
        realm["project"] = None
        return
    path = REPO / src
    if not path.exists():
        print(f"  !! content file missing for {realm['slug']}: {src}")
        realm["project"] = None
        return
    post = frontmatter.load(path)
    md = markdown.Markdown(extensions=["extra", "attr_list"])
    realm["project"] = {
        "name": post.get("name"),
        "blurb": (post.get("blurb") or "").strip(),
        "tags": post.get("tags") or [],
        "links": post.get("links") or [],
        "body_html": md.convert(post.content),
    }


# ------------------------------------------------------------------- render

def render(data: dict, gen: dict) -> None:
    env = Environment(
        loader=FileSystemLoader(HERE / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    site = data["site"]
    base = dict(site=site, guide=data["guide"], clusters=data["clusters"],
                realms=data["realms"], gen=gen)

    # Compact JSON consumed by home.js (positions, teasers, anchors, preloads).
    atlas_json = {
        "guide": {
            "greeting": data["guide"]["greeting"],
            "hint": data["guide"]["hint"],
            "anchors": data["guide"]["anchors"],
        },
        "clusters": data["clusters"],
        "blur": {k.split("_")[1]: v for k, v in gen.items() if k.startswith("blur_")},
        "realms": [
            {
                "slug": r["slug"],
                "cluster": r["cluster"],
                "status": r["status"],
                "teaser": r["teaser"],
                "x": r["position"]["x"],
                "y": r["position"]["y"],
                "size": r["size"],
                "depth": r["depth"],
                "keyart": r.get("assets") or None,
            }
            for r in data["realms"]
        ],
    }

    def write(rel_path: str, template: str, **ctx):
        out = HERE / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        html = env.get_template(template).render(**base, **ctx)
        out.write_text(html, encoding="utf-8")
        print(f"  -> mystic_journey/{rel_path}")

    write("index.html", "index.html", rel="", page="home",
          atlas_json=json.dumps(atlas_json, separators=(",", ":")))

    for realm in data["realms"]:
        write(f"realms/{realm['slug']}/index.html", "realm.html",
              rel="../../", page="realm", realm=realm)

    write("ledger/index.html", "ledger.html", rel="../", page="ledger")

    # Sitemap for mystic_journey pages only (never touches the old site's).
    base_url = site["base_url"].rstrip("/")
    urls = [f"{base_url}/"] + [
        f"{base_url}/realms/{r['slug']}/" for r in data["realms"]
    ]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (HERE / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    print("  -> mystic_journey/sitemap.xml")


def main() -> int:
    data = yaml.safe_load((HERE / "data" / "realms.yaml").read_text(encoding="utf-8"))
    print("assets:")
    gen = build_assets(data)
    print("content:")
    for realm in data["realms"]:
        load_project(realm)
    print("pages:")
    render(data, gen)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
