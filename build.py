"""Build the static portfolio site.

Reads content/ + templates/ + static/ and writes docs/.
Run locally:   python build.py
Preview:       python -m http.server -d docs 8000

Content layout under content/:
  *.yaml             -> merged at top level (yaml top-level keys become template vars)
  about.md           -> data["about"] (rendered HTML)
  projects/*.md      -> data["projects"] (list; frontmatter fields + body_html, sorted by order)
"""
from pathlib import Path
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


def render(env, data):
    return env.get_template("index.html").render(**data)


def write_output(html):
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUT_DIR / "static")
    # Tell GitHub Pages not to run Jekyll on the artifact.
    (OUT_DIR / ".nojekyll").touch()


def main():
    data = load_content()
    env = make_env()
    html = render(env, data)
    write_output(html)
    print(f"Built {OUT_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
