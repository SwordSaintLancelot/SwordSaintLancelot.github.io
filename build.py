"""Build the static portfolio site.

Reads content/ + templates/ + static/ and writes docs/.
Run locally:   python build.py
Preview:       python -m http.server -d docs 8000

Content layout under content/:
  *.yaml             -> merged at top level (yaml top-level keys become template vars)
  about.md           -> data["about"] (rendered HTML)
  projects/*.md      -> data["projects"] (list; frontmatter fields + body_html, sorted by order)

Output layout under docs/:
  index.html                       -> the main page
  projects/<slug>/index.html       -> one subpage per project
  static/...                       -> copied verbatim
"""
from pathlib import Path
import re
import shutil

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
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
            entry["body_html"] = markdown.markdown(post.content) if post.content.strip() else ""
            projects.append(entry)
        projects.sort(key=lambda p: p.get("order", 999))
        data["projects"] = projects

    return data


def make_env():
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
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


def write_output(env, data):
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()

    # Main page
    (OUT_DIR / "index.html").write_text(render_index(env, data), encoding="utf-8")

    # Project subpages
    for project in data.get("projects", []):
        slug = project.get("slug")
        if not slug:
            continue
        out_dir = OUT_DIR / "projects" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_project_page(env, data, project), encoding="utf-8")

    # Static assets + Jekyll opt-out
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUT_DIR / "static")
    (OUT_DIR / ".nojekyll").touch()


def main():
    data = load_content()
    env = make_env()
    write_output(env, data)
    pages = ["index.html"] + [f"projects/{p['slug']}/index.html" for p in data.get("projects", []) if p.get("slug")]
    print(f"Built {len(pages)} pages:")
    for p in pages:
        print(f"  docs/{p}")


if __name__ == "__main__":
    main()
