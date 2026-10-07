"""Correct misleading reference cards without changing dialogue or audio indexes."""
import json
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"castor": "06_Project_CASTOR_EN.html", "pollux": "09_Project_POLLUX_EN.html"}


def repair(facts, project):
    if project == "castor":
        for row in facts["money"]:
            if row[0] == "Effort":
                row[2] = "One person-day = one person working one day. Effort is total work, not elapsed calendar time."
            elif row[0] == "Duration":
                row[1] = "Jan 2026 to Jul 2028"
                row[2] = ("The dated timeline runs from 12 Jan 2026 to 28 Jul 2028: about 30.5 calendar months. "
                          "Dialogue also quotes a 26-month baseline without defining its endpoints; do not treat it as the full dated span.")
        for row in facts["conv"]:
            if row[0] == "Risk score":
                row[2] = ("3 × 4 = 12. Scene 15 uses these colour bands: 1–2 green, 3–16 yellow, 20–25 red. "
                          "The separate project escalation ladder is: up to 6, Project Manager; 8–15, Project Owner; "
                          "16 or above, Steering Committee. Scores 7 and 17–19 cannot result from multiplying two integers from 1 to 5. "
                          "Colour and escalation authority are different checks.")
    else:
        for row in facts["conv"]:
            if row[0] == "Definition of Done":
                row[2] = ("A shared quality standard for the team, revised through the agreed process and recorded in the Development Handbook. "
                          "Apply the agreed version consistently. Acceptance criteria describe the needs of an individual work item.")
    return facts


def update_page(path, project):
    html = path.read_text()
    start = html.index("const P=") + len("const P=")
    payload, length = json.JSONDecoder().raw_decode(html[start:])
    before = json.dumps(payload["FACTS"], ensure_ascii=False)
    repair(payload["FACTS"], project)
    after = json.dumps(payload["FACTS"], ensure_ascii=False)
    if before == after:
        return False
    # Only replace the exact FACTS value; leave scene data byte-for-byte intact.
    segment = html[start:start + length]
    if segment.count(before) != 1:
        raise ValueError(f"Cannot identify the unique FACTS value in {path}")
    path.write_text(html[:start] + segment.replace(before, after, 1) + html[start + length:])
    return True


def patch_source(text, before, after):
    for key in ("money", "conv"):
        for old_row, new_row in zip(before[key], after[key]):
            for old, new in zip(old_row, new_row):
                if old != new:
                    old_json, new_json = (json.dumps(value, ensure_ascii=False) for value in (old, new))
                    if text.count(old_json) != 1:
                        raise ValueError(f"Cannot identify unique source value: {old}")
                    text = text.replace(old_json, new_json, 1)
    return text


if __name__ == "__main__":
    for project, name in NAMES.items():
        source = ROOT / "src" / f"facts_{project}.json"
        source_text = source.read_text()
        facts = json.loads(source_text)
        before = copy.deepcopy(facts)
        repair(facts, project)
        source.write_text(patch_source(source_text, before, facts))
        for folder in (ROOT / "play", ROOT.parent):
            page = folder / name
            if page.exists():
                print("updated" if update_page(page, project) else "unchanged", page)
