"""Render README.md to README.pdf as one continuous page.

The markdown is rendered with GitHub's own renderer (so it matches the profile page),
styled with github-markdown-css, then printed by headless Edge. Needs network access and Edge.
"""
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
WIDTH = 930
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-light.css"

# Sets the page height to the full document height once every image has loaded.
FIT_PAGE = """
<script>
window.addEventListener('load', function () {
  var h = Math.ceil(document.documentElement.scrollHeight) + 1;
  var s = document.createElement('style');
  s.textContent = '@page { size: %dpx ' + h + 'px; margin: 0 }';
  document.head.appendChild(s);
});
</script>
""" % WIDTH


def render_html():
    md = (ROOT / "README.md").read_text(encoding="utf-8")
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": md, "mode": "gfm"}).encode(),
        headers={"User-Agent": "readme-pdf", "Content-Type": "application/json"},
    )
    body = urllib.request.urlopen(req).read().decode("utf-8")
    assets = (ROOT / "assets").as_uri() + "/"
    body = body.replace('src="./assets/', f'src="{assets}').replace('href="./assets/', f'href="{assets}')
    return (
        f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{CSS}">'
        "<style>html,body{margin:0;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}"
        ".markdown-body{box-sizing:border-box;max-width:880px;margin:0 auto;padding:24px}</style>"
        f'{FIT_PAGE}</head><body><article class="markdown-body">{body}</article></body></html>'
    )


def main():
    out = ROOT / "README.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "readme.html"
        page.write_text(render_html(), encoding="utf-8")
        subprocess.run([
            EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
            f"--window-size={WIDTH},1000", "--virtual-time-budget=10000", "--no-pdf-header-footer",
            f"--print-to-pdf={out}", page.as_uri(),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    sys.exit(main())
