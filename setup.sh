#!/usr/bin/env bash
# One-time setup: bring in the audio, set your username in the links, publish.
set -euo pipefail
cd "$(dirname "$0")"

echo "── PM² by playing it — setup ──────────────────────────────────"
echo

# ---- 1. the recorded voice ---------------------------------------------------
if compgen -G "play/voice/*.mp3" > /dev/null; then
  echo "✓ voice files already in place ($(ls play/voice/*.mp3 | wc -l | tr -d ' ') files)"
else
  DEFAULT="$HOME/Documents/projects/PM Certificate/voice"
  echo "The 16 recorded-voice MP3s are not in this folder yet."
  read -rp "Path to your voice folder [$DEFAULT]: " VDIR
  VDIR="${VDIR:-$DEFAULT}"
  if compgen -G "$VDIR/*.mp3" > /dev/null; then
    mkdir -p play/voice
    cp "$VDIR"/*.mp3 "$VDIR"/index.json play/voice/ 2>/dev/null || cp "$VDIR"/*.mp3 play/voice/
    echo "✓ copied $(ls play/voice/*.mp3 | wc -l | tr -d ' ') files into play/voice/"
  else
    echo "! nothing found there. Skipping — the pages will fall back to browser voices."
    echo "  You can rebuild the audio later with: python3 tools/make_voices.py"
  fi
fi
echo

# ---- 2. your name in the links ----------------------------------------------
read -rp "Your GitHub username: " USER
read -rp "Repository name [pm2-by-playing-it]: " REPO
REPO="${REPO:-pm2-by-playing-it}"
for f in README.md index.html; do
  perl -pi -e "s/YOUR-GITHUB-USERNAME/\Q$USER\E/g; s{pm2-by-playing-it}{$REPO}g" "$f"
done
echo "✓ links point at https://github.com/$USER/$REPO"
echo

# ---- 3. first commit ---------------------------------------------------------
git init -q 2>/dev/null || true
git add -A
git -c user.name="$USER" -c user.email="$USER@users.noreply.github.com" \
    commit -qm "PM² by playing it — two playable case studies, 33 artefacts, 550 questions, 8h of voice" \
    2>/dev/null || echo "  (nothing new to commit)"
git branch -M main
echo "✓ committed $(git ls-files | wc -l | tr -d ' ') files"

cat <<EOF

── to publish ─────────────────────────────────────────────────

  With the GitHub CLI:
      gh repo create $REPO --public --source=. --push

  By hand:
      1. make an empty PUBLIC repo called "$REPO" at https://github.com/new
         (no README, no .gitignore, no licence — this folder has them)
      2. git remote add origin https://github.com/$USER/$REPO.git
         git push -u origin main

── then the live demo ─────────────────────────────────────────

  Settings → Pages → Source: "Deploy from a branch"
                     Branch: main   Folder: / (root)     → Save

  Live in a minute or two at
      https://$USER.github.io/$REPO/

EOF
