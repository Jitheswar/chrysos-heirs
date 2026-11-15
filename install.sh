#!/bin/bash
# Chrysos Heirs for Omarchy — one theme whose palette follows the wallpaper.
#   ./install.sh              build + install the theme and the wallpaper watcher
#   ./install.sh --lock       also add the HSR lock-screen overlay (clones omarchy.lock)
#   ./install.sh --uninstall  remove the theme, watcher and lock clone
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
themes="$HOME/.config/omarchy/themes"
unit="$HOME/.config/systemd/user/chrysos-heirs-sync.service"
lock_id="${USER:-$(id -un)}.lock"
lock_dir="$HOME/.config/omarchy/plugins/$lock_id"

if [[ ${1:-} == --uninstall ]]; then
  [[ $(cat ~/.local/state/omarchy/current/theme.name 2>/dev/null) == chrysos-heirs* ]] && omarchy theme set jade-horse
  systemctl --user disable --now chrysos-heirs-sync.service 2>/dev/null || true
  rm -f "$unit"; systemctl --user daemon-reload
  rm -rf "$themes"/chrysos-heirs "$themes"/chrysos-heirs-*
  if [[ -f $lock_dir/ChrysosOverlay.qml ]]; then
    omarchy plugin enable omarchy.lock >/dev/null
    omarchy plugin remove "$lock_id" --yes
    omarchy restart shell
  fi
  echo "Chrysos Heirs removed."
  exit 0
fi

command -v inotifywait >/dev/null || { echo "needs inotify-tools: omarchy pkg add inotify-tools" >&2; exit 1; }

python3 -I "$here/build.py"

mkdir -p "$(dirname "$unit")"
cp "$here/chrysos-heirs-sync.service" "$unit"
systemctl --user daemon-reload
systemctl --user enable chrysos-heirs-sync.service >/dev/null 2>&1
systemctl --user restart chrysos-heirs-sync.service

if [[ ${1:-} == --lock ]]; then
  [[ -d $lock_dir ]] || omarchy plugin clone omarchy.lock
  cp "$here/lock/ChrysosOverlay.qml" "$lock_dir/"
  if ! grep -q ChrysosOverlay "$lock_dir/LockView.qml"; then
    python3 -I - "$lock_dir/LockView.qml" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
anchor = "      contrast: -0.08\n    }\n"
hook = ("\n    // Chrysos Heirs: draws only when the theme ships chrysos-lock.json.\n"
        "    ChrysosOverlay { anchors.fill: parent; backgroundPath: root.video ? root.videoPosterPath : root.backgroundPath; loadBackground: root.loadBackground }\n")
assert anchor in s, "LockView.qml changed upstream; add the ChrysosOverlay line by hand"
open(p, "w").write(s.replace(anchor, anchor + hook, 1))
PY
  fi
  omarchy restart shell
fi
echo 'Done. Apply with: omarchy theme set "Chrysos Heirs"'
