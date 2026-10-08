#!/bin/sh
set -eu
ROOT="${HSI_3SYS_HOME:-$HOME/.hsi-three}"
mkdir -p "$ROOT"
get(){
  u="$1"; f="$2"; t="$f.tmp.$$"
  if command -v wget >/dev/null 2>&1; then wget -qO "$t" "$u"
  elif command -v curl >/dev/null 2>&1; then curl -fsSL "$u" -o "$t"
  else echo "wget or curl required" >&2; exit 127
  fi
  test -s "$t"; mv "$t" "$f"
}
command -v python3 >/dev/null 2>&1 || {
  if command -v apk >/dev/null 2>&1; then apk add --no-cache python3 >/dev/null
  else echo "python3 required" >&2; exit 127
  fi
}
get "https://raw.githubusercontent.com/letsgo0226/UTM.sh/hsi-three-system-v1/hsi_common/core.py" "$ROOT/core.py"
get "https://raw.githubusercontent.com/letsgo0226/UTM.sh/hsi-three-system-v1/hsi_blue_native.py" "$ROOT/hsi_blue_native.py"
cd "$ROOT"
if [ "$#" -eq 0 ] && [ -r /dev/tty ]; then exec python3 hsi_blue_native.py </dev/tty; fi
exec python3 hsi_blue_native.py "$@"
