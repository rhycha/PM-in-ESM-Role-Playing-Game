"""Validate the actual standalone deliverables and preserve their embedded content."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_context import install, payload
from repair_study_facts import repair
from vnorm import norm

briefs = json.loads((ROOT / "src/context.json").read_text())
all_text = []
for folder in (ROOT / "play", ROOT.parent):
    for project, name in (("castor", "06_Project_CASTOR_EN.html"), ("pollux", "09_Project_POLLUX_EN.html")):
        page = folder / name
        if not page.exists():
            continue
        html = page.read_text()
        data = payload(html)
        assert len(data["S"]) == (52 if project == "castor" else 25)
        assert all(scene["id"] in briefs["projects"][project]["scenes"] for scene in data["S"])
        assert html.count("<!-- PM2_CLEAR_READING_START -->") == 1
        for script_name in ("speech_reading.js", "voice_controls.js"):
            assert (ROOT / "tools" / script_name).read_text().strip() in html, f"Stale speech source: {page}"
        assert html.count("<!-- PM2_CONTEXT_SCRIPT_START -->") == 1
        assert install(html) == html, f"Context installer is not idempotent: {page}"
        repair_check = copy.deepcopy(data["FACTS"])
        assert repair(repair_check, project) == data["FACTS"]
        for attrs, source in re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S):
            if 'application/json' in attrs:
                json.loads(source)
            else:
                with tempfile.NamedTemporaryFile(suffix=".js", mode="w") as temp:
                    temp.write(source); temp.flush()
                    subprocess.run(["node", "--check", temp.name], check=True, capture_output=True)
        # The backups exist only on the working Mac; portable checks do not need them.
        prefix = "play-" if folder == ROOT / "play" else "root-"
        backup = ROOT.parent / ".revision-backups/2026-10-06" / (prefix + name)
        if backup.exists():
            before = payload(backup.read_text())
            after = copy.deepcopy(data)
            before.pop("FACTS"); after.pop("FACTS")
            assert before == after, f"Story content changed: {page}"
            def index(text):
                return json.JSONDecoder().raw_decode(text.split("const VIDX=", 1)[1])[0]
            assert index(backup.read_text()) == index(html), f"Audio timing changed: {page}"
        for scene in data["S"]:
            lines = list(scene["lines"])
            lines += [option["reply"] for option in (scene.get("choice") or {}).get("options", []) if isinstance(option.get("reply"), dict)]
            for line in lines:
                all_text.extend(line[key] for key in ("text", "plain") if line.get(key))
        print("PASS", page, len(data["S"]), "scene briefs; script syntax, payload and audio preservation")

js = "const fs=require('fs'),s=require(process.argv[1]);const t=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(t.map(s.normalize)));"
browser = json.loads(subprocess.check_output(["node", "-e", js, str(ROOT / "tools/speech_reading.js")], input=json.dumps(all_text), text=True))
assert [norm(text) for text in all_text] == browser, "Browser and recording pronunciation differ"
assert not any(re.search(r"\d", text) for text in browser), "A spoken number was not expanded"
assert (ROOT / "docs/study/PM2_VOICE_STUDY_PACK.md").read_text() == (ROOT / "docs/study/PM2_VOICE_STUDY_PACK.txt").read_text()
print("PASS", len(all_text), "live-page spoken texts; browser/Python parity, number expansion, attachment parity")
