#!/bin/sh
# Export every page of every tools/diagrams/*.drawio to src/assets/img/diagrams/.
#
#   tools/diagrams/export.sh            # all diagrams
#   tools/diagrams/export.sh dc2ac ...  # only these (file names without .drawio)
#
# Page 1 of NAME.drawio -> NAME.svg; a page named "compact" -> NAME-compact.svg; any
# other page P -> NAME-P.svg. Skipped: *-original.drawio (gate files) and kit.drawio.
#
# Method: draw.io CLI -> PDF (MathJax typeset by draw.io itself), then
# pdftocairo -svg + pdf2svg.py: every glyph becomes a path, so the SVG needs no fonts,
# no MathJax and no foreignObject, and renders identically as an <img> in any browser.
# Every draw.io run goes through tools/lock.sh (one heavy process at a time).
set -eu
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC="$ROOT/tools/diagrams"
OUT="$ROOT/src/assets/img/diagrams"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/diagrams.XXXXXX")
trap 'rm -rf "$TMP"' EXIT INT TERM
mkdir -p "$OUT"

if [ $# -gt 0 ]; then
  files=""; for n in "$@"; do files="$files $SRC/${n%.drawio}.drawio"; done
else
  files=$(ls "$SRC"/*.drawio)
fi

for f in $files; do
  name=$(basename "$f" .drawio)
  case "$name" in *-original|kit) continue ;; esac
  python3 "$SRC/check_style.py" "$f"
  python3 "$SRC/padframe.py" "$f" "$TMP/padded.drawio"   # keeps the PDF page edge off the outer strokes
  i=0
  python3 -c '
import re, sys, html
for n in re.findall(r"<diagram\b[^>]*\bname=\"([^\"]*)\"", open(sys.argv[1]).read()):
    print(html.unescape(n))' "$f" > "$TMP/pages"
  while IFS= read -r page; do
    i=$((i + 1))
    if [ $i -eq 1 ]; then out="$name.svg"
    elif [ "$page" = compact ]; then out="$name-compact.svg"
    else out="$name-$(printf %s "$page" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-').svg"
    fi
    "$ROOT/tools/lock.sh" drawio -x -f pdf --crop -p "$i" -o "$TMP/p.pdf" "$TMP/padded.drawio" >/dev/null 2>&1
    python3 "$SRC/pdf2svg.py" "$TMP/p.pdf" "$OUT/$out"
  done < "$TMP/pages"
done
