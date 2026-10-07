#!/usr/bin/env python3
"""Add context support to existing story pages without rebuilding their content.

Usage: python3 tools/install_context.py path/to/story.html [...]
The bounded enhancement blocks are replaceable; embedded story/audio data is untouched.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/context.json"


def payload(html):
    match = re.search(r"const P\s*=\s*", html)
    if not match:
        raise ValueError("Story payload not found")
    return json.JSONDecoder().raw_decode(html[match.end():])[0]


def install(html):
    data = json.loads(DATA.read_text())
    tag = re.search(r'const VTAG\s*=\s*[\"\'](castor|pollux)[\"\']', html)
    if not tag:
        raise ValueError("Expected CASTOR or POLLUX story page")
    story = payload(html)
    scenes = data["projects"][tag[1]]["scenes"]
    missing = [s["id"] for s in story["S"] if s["id"] not in scenes]
    if missing:
        raise ValueError("Missing scene context: " + ", ".join(missing))
    for scene_id, briefing in scenes.items():
        if len(briefing) != 3 or not all(isinstance(x, str) and x.strip() for x in briefing):
            raise ValueError("Invalid scene context: " + scene_id)
    css = (ROOT / "tools/context.css").read_text().strip()
    js = (ROOT / "tools/context.js").read_text().strip()
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    style = '<!-- PM2_CONTEXT_STYLE_START -->\n<style id="pm2-context-style">\n' + css + '\n</style>\n<!-- PM2_CONTEXT_STYLE_END -->'
    script = '<!-- PM2_CONTEXT_SCRIPT_START -->\n<script type="application/json" id="pm2-context-data">' + encoded + '</script>\n<script>\n' + js + '\n</script>\n<!-- PM2_CONTEXT_SCRIPT_END -->'
    if html.count("</head>") != 1 or html.count("</body>") != 1:
        raise ValueError("Expected one head and one body")
    for marker, block, anchor in (("STYLE", style, "</head>"), ("SCRIPT", script, "</body>")):
        start = f"<!-- PM2_CONTEXT_{marker}_START -->"
        end = f"<!-- PM2_CONTEXT_{marker}_END -->"
        if not html.count(start) and not html.count(end):
            html = html.replace(anchor, block + "\n" + anchor)
            continue
        if html.count(start) != 1 or html.count(end) != 1:
            raise ValueError(f"Expected one complete context {marker.lower()} block")
        match = re.search(re.escape(start) + r".*?" + re.escape(end), html, re.S)
        if not match:
            raise ValueError(f"Malformed context {marker.lower()} block")
        # Keep the block's position and surrounding whitespace. Other installers
        # may add scripts after ours; moving either block would make them oscillate.
        html = html[:match.start()] + block + html[match.end():]
    if payload(html) != story:
        raise AssertionError("Installation changed the story payload")
    return html


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate only; do not edit pages")
    args = parser.parse_args()
    # Validate every target before writing any target.
    changes = [(page, install(page.read_text())) for page in args.pages]
    for page, updated in changes:
        if not args.check:
            page.write_text(updated)
        print(("Validated " if args.check else "Installed context: ") + str(page))


if __name__ == "__main__":
    main()
