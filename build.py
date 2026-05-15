"""Build the static portfolio site.

Reads data.yaml + templates/ + static/ and writes docs/.
Run locally:   python build.py
Preview:       python -m http.server -d docs 8000
"""
from pathlib import Path
import shutil

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
DATA_FILE = ROOT / "data.yaml"
OUT_DIR = ROOT / "docs"


def load_data():
    with DATA_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


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
    data = load_data()
    env = make_env()
    html = render(env, data)
    write_output(html)
    print(f"Built {OUT_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
