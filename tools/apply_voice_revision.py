"""Embed the speech revision in existing standalone pages, preserving prior edits."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- PM2_CLEAR_READING_START -->"
END = "<!-- PM2_CLEAR_READING_END -->"


def apply(path):
    text = path.read_text()
    scripts = [(ROOT / "tools" / name).read_text() for name in ("speech_reading.js", "voice_controls.js")]
    if any("</script" in script.lower() for script in scripts):
        raise ValueError("Unexpected script closing tag in speech source")
    block = START + "\n<script>\n" + "\n".join(scripts) + "\n</script>\n" + END
    if text.count("</body>") != 1:
        raise ValueError(f"Expected one body closing tag in {path}")
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ValueError(f"Invalid speech enhancement markers in {path}")
    if START in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.replace("</body>", block + "\n</body>")
    path.write_text(text)
    print("updated", path)


if __name__ == "__main__":
    for folder in (ROOT / "play", ROOT.parent):
        for name in ("06_Project_CASTOR_EN.html", "09_Project_POLLUX_EN.html"):
            path = folder / name
            if path.exists():
                apply(path)
