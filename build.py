"""Build the static portfolio site(s).

Two sites share one content/ folder and one output tree (docs/):
  classic/   -> the original clean portfolio (templates + its css/js)
  atlas/     -> The Traveler's Atlas storybook site (templates + its css/js)
  content/   -> shared data: YAML lists, about.md, projects/*.md, realms.yaml
  static/    -> shared assets: images/, resume.pdf

Run locally:   python build.py
Preview:       python -m http.server -d docs 8000

Content layout under content/:
  *.yaml             -> merged at top level (yaml top-level keys become template vars)
  about.md           -> data["about"] (rendered HTML)
  projects/*.md      -> data["projects"] (list; frontmatter fields + body_html, sorted by order)
  realms.yaml        -> data["atlas"] + data["realms"] (storybook layer)

Output layout under docs/:
  index.html                       -> the classic main page
  projects/<slug>/index.html       -> one classic subpage per project
  realms/<slug>/index.html         -> one atlas realm page per active realm
  static/...                       -> shared assets + both sites' css/js, merged
"""
from pathlib import Path
import hashlib
import html
import re
import shutil

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


# Callout patterns: blockquote whose first <strong> matches one of these labels
# becomes a styled callout. Class drives the visual treatment in styles.css.
_CALLOUT_LABELS = {
    "TODO": "todo",
    "What didn't work": "postmortem",
    "What didn’t work": "postmortem",   # curly apostrophe
    "Note": "note",
    "Why": "note",
}
_CALLOUT_RE = re.compile(
    r"<blockquote>\s*<p><strong>("
    + "|".join(re.escape(k) for k in _CALLOUT_LABELS)
    + r"):</strong>"
)


def _apply_callouts(html_str: str) -> str:
    def repl(m):
        label = m.group(1)
        cls = _CALLOUT_LABELS.get(label, "note")
        # Trim ":" off the strong, but keep the label text for the badge.
        return (
            f'<blockquote class="callout callout--{cls}">'
            f'<span class="callout__label">{label}</span>'
            f"<p>"
        )
    return _CALLOUT_RE.sub(repl, html_str)


_COVER_PALETTES = [
    ("#2A2D5E", "#7C7FD8"),
    ("#3B3D8F", "#8E92E8"),
    ("#5B5DC3", "#C9CAFB"),
    ("#3F4474", "#A4ACEC"),
    ("#1F2452", "#8E92E8"),
    ("#262A6F", "#B4B8F0"),
]


def _slug_hash(slug: str) -> int:
    return int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16)


def _initials(name: str) -> str:
    parts = [w for w in re.split(r"\s+", name) if w and w[0].isalpha()]
    return "".join(p[0] for p in parts[:2]).upper() or "··"


def generate_cover_svg(slug: str, name: str) -> str:
    """Build a deterministic 16:9 cover SVG for a project.

    Pure function of slug. Same slug -> same cover across rebuilds.
    Inlined into the page (no extra HTTP requests).
    """
    h = _slug_hash(slug)
    a, b = _COVER_PALETTES[h % len(_COVER_PALETTES)]
    pattern = h % 3
    grad_id = f"cov-{slug}"
    safe_label = html.escape(f"{name} cover")
    initials = _initials(name)

    if pattern == 0:
        # dot lattice
        dots = "".join(
            f'<circle cx="{x}" cy="{y}" r="1.6" />'
            for x in range(20, 320, 24)
            for y in range(20, 180, 24)
        )
        overlay = f'<g fill="#fff" opacity="0.18">{dots}</g>'
    elif pattern == 1:
        # diagonal hatch
        lines = "".join(
            f'<line x1="{i-120}" y1="180" x2="{i+120}" y2="0" />'
            for i in range(-80, 460, 32)
        )
        overlay = f'<g stroke="#fff" stroke-width="1" opacity="0.14">{lines}</g>'
    else:
        # concentric arcs from top-right corner
        rings = "".join(
            f'<circle cx="320" cy="0" r="{r}" />'
            for r in (60, 110, 160, 210, 260, 310, 360)
        )
        overlay = f'<g stroke="#fff" stroke-width="1.4" fill="none" opacity="0.18">{rings}</g>'

    return (
        f'<svg class="card-cover-svg" viewBox="0 0 320 180" '
        f'preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{safe_label}">'
        f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/>'
        f'</linearGradient></defs>'
        f'<rect width="320" height="180" fill="url(#{grad_id})"/>'
        f'{overlay}'
        f'<text x="20" y="162" font-family="JetBrains Mono, ui-monospace, monospace" '
        f'font-size="14" font-weight="500" fill="#fff" fill-opacity="0.9" '
        f'letter-spacing="2">{html.escape(initials)}</text>'
        f'</svg>'
    )

ROOT = Path(__file__).parent
CLASSIC_TEMPLATES_DIR = ROOT / "classic" / "templates"
ATLAS_TEMPLATES_DIR = ROOT / "atlas" / "templates"
# Static sources are merged into docs/static in this order (no name overlaps).
STATIC_DIRS = [
    ROOT / "static",             # shared assets: images/, resume.pdf
    ROOT / "classic" / "static", # styles.css, js/site.js
    ROOT / "atlas" / "static",   # atlas.css, js/atlas.js
]
CONTENT_DIR = ROOT / "content"
OUT_DIR = ROOT / "docs"


def load_content():
    data = {}

    for path in sorted(CONTENT_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            chunk = yaml.safe_load(f) or {}
        data.update(chunk)

    about_path = CONTENT_DIR / "about.md"
    if about_path.exists():
        data["about"] = markdown.markdown(about_path.read_text(encoding="utf-8"))

    projects_dir = CONTENT_DIR / "projects"
    if projects_dir.exists():
        projects = []
        for path in sorted(projects_dir.glob("*.md")):
            post = frontmatter.load(path)
            entry = dict(post.metadata)
            if post.content.strip():
                md = markdown.Markdown(
                    extensions=["fenced_code", "toc"],
                    extension_configs={"toc": {"permalink": False, "toc_depth": "2-2"}},
                )
                body_html = md.convert(post.content)
                entry["body_html"] = _apply_callouts(body_html)
                # toc_tokens is the structured outline. Keep only h2 entries.
                tokens = getattr(md, "toc_tokens", []) or []
                # toc_tokens names come HTML-escaped; un-escape once so
                # Jinja autoescape doesn't double them.
                entry["toc"] = [
                    {"id": t["id"], "name": html.unescape(t["name"])}
                    for t in tokens if t.get("level") == 2
                ]
            else:
                entry["body_html"] = ""
                entry["toc"] = []
            if entry.get("slug") and not entry.get("thumbnail"):
                entry["cover_svg"] = generate_cover_svg(entry["slug"], entry.get("name", entry["slug"]))
            projects.append(entry)
        projects.sort(key=lambda p: p.get("order", 999))
        data["projects"] = projects

    return data


def generate_favicon_svg(name: str) -> str:
    initials = _initials(name)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="6" fill="#3B3D8F"/>'
        f'<text x="16" y="22" text-anchor="middle" '
        'font-family="JetBrains Mono, ui-monospace, monospace" '
        'font-size="14" font-weight="600" fill="#FFFFFF" '
        f'letter-spacing="0.5">{html.escape(initials)}</text>'
        "</svg>"
    )


def generate_og_svg(name: str, title: str, tagline: str) -> str:
    """1200x630 OG image. Indigo bg with a dot-grid corner and large name."""
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="3" />'
        for x in range(820, 1200, 28)
        for y in range(60, 280, 28)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" '
        'width="1200" height="630">'
        '<rect width="1200" height="630" fill="#0F1115"/>'
        '<rect x="0" y="0" width="1200" height="630" fill="url(#og-grad)" opacity="0.6"/>'
        '<defs>'
        '<linearGradient id="og-grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#1F2452"/>'
        '<stop offset="1" stop-color="#3B3D8F"/>'
        '</linearGradient>'
        '</defs>'
        f'<g fill="#8E92E8" opacity="0.35">{dots}</g>'
        '<text x="80" y="270" font-family="JetBrains Mono, ui-monospace, monospace" '
        'font-size="22" font-weight="500" fill="#8E92E8" letter-spacing="6">'
        f'{html.escape(title.upper())}'
        '</text>'
        '<text x="80" y="380" font-family="Georgia, serif" '
        'font-size="92" font-weight="700" fill="#FAFAF7" letter-spacing="-2">'
        f'{html.escape(name)}'
        '</text>'
        '<text x="80" y="450" font-family="-apple-system, system-ui, sans-serif" '
        'font-size="28" fill="#9B9DA6">'
        f'{html.escape(tagline)}'
        '</text>'
        '<line x1="80" y1="540" x2="200" y2="540" stroke="#3B3D8F" stroke-width="3"/>'
        '</svg>'
    )


def make_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_index(env, data):
    return env.get_template("index.html").render(asset_prefix="", **data)


# Matches src="static/..." or href="static/..." (but NOT "../static/" or "/static/")
# so markdown bodies can use natural `static/...` paths and we rewrite at render
# time to the correct relative depth for the subpage.
_STATIC_PATH_RE = re.compile(r'((?:src|href)=")(static/)')


def render_project_page(env, data, project):
    asset_prefix = "../../"
    page_title = f"{project['name']} — {data['profile']['name']}"
    meta_description = project.get("blurb", data.get("seo", {}).get("meta_description", ""))
    html = env.get_template("project.html").render(
        asset_prefix=asset_prefix,
        page_title=page_title,
        meta_description=meta_description,
        project=project,
        **data,
    )
    return _STATIC_PATH_RE.sub(r'\1' + asset_prefix + r'\2', html)


def render_realm_page(env, data, realm, project):
    """Render one Traveler's Atlas realm page (docs/realms/<slug>/).

    Realm narrative comes from content/realms.yaml; factual project details
    (links, tags, thumbnail) come from the matching content/projects/*.md
    entry so nothing is duplicated.
    """
    asset_prefix = "../../"
    page_title = f"{realm['realm_name']} — {realm['realm_subtitle']} | {data['profile']['name']}"
    meta_description = (project or {}).get("blurb") or realm.get("tagline", "")
    classic_url = f"{asset_prefix}projects/{project['slug']}/" if project else f"{asset_prefix}index.html"
    return env.get_template("realm.html").render(
        asset_prefix=asset_prefix,
        page_title=page_title,
        meta_description=meta_description,
        realm=realm,
        project=project,
        classic_url=classic_url,
        **data,
    )


def realm_pages_to_build(data):
    """Realms that get a page: 'active' (and 'forming', once built)."""
    return [r for r in data.get("realms", []) if r.get("status") == "active"]


def write_output(classic_env, atlas_env, data):
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()

    # Classic site: main page + project subpages
    (OUT_DIR / "index.html").write_text(render_index(classic_env, data), encoding="utf-8")

    for project in data.get("projects", []):
        slug = project.get("slug")
        if not slug:
            continue
        out_dir = OUT_DIR / "projects" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_project_page(classic_env, data, project), encoding="utf-8")

    # Atlas site: realm pages
    projects_by_slug = {p["slug"]: p for p in data.get("projects", []) if p.get("slug")}
    for realm in realm_pages_to_build(data):
        out_dir = OUT_DIR / "realms" / realm["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        project = projects_by_slug.get(realm.get("project"))
        (out_dir / "index.html").write_text(
            render_realm_page(atlas_env, data, realm, project), encoding="utf-8"
        )

    # Static assets (shared + per-site, merged) + Jekyll opt-out
    for static_dir in STATIC_DIRS:
        if static_dir.exists():
            shutil.copytree(static_dir, OUT_DIR / "static", dirs_exist_ok=True)
    (OUT_DIR / ".nojekyll").touch()

    # Generated assets — favicon and OG image. Written into the output static
    # dir so they ship alongside other static files. Derived from profile data,
    # so renaming the profile auto-updates them on next build.
    out_static = OUT_DIR / "static"
    out_static.mkdir(exist_ok=True)
    profile = data.get("profile", {})
    pname = profile.get("name", "Site")
    ptitle = profile.get("title", "")
    ptag = profile.get("tagline", "") or ""
    # Short tagline: first sentence or first 80 chars
    short_tag = ptag.split(".")[0].strip()
    if len(short_tag) > 80:
        short_tag = short_tag[:77].rstrip() + "..."
    (out_static / "favicon.svg").write_text(generate_favicon_svg(pname), encoding="utf-8")
    (out_static / "og-image.svg").write_text(
        generate_og_svg(pname, ptitle, short_tag), encoding="utf-8"
    )


def main():
    data = load_content()
    classic_env = make_env(CLASSIC_TEMPLATES_DIR)
    atlas_env = make_env(ATLAS_TEMPLATES_DIR)
    write_output(classic_env, atlas_env, data)
    pages = (
        ["index.html"]
        + [f"projects/{p['slug']}/index.html" for p in data.get("projects", []) if p.get("slug")]
        + [f"realms/{r['slug']}/index.html" for r in realm_pages_to_build(data)]
    )
    print(f"Built {len(pages)} pages:")
    for p in pages:
        print(f"  docs/{p}")


if __name__ == "__main__":
    main()
