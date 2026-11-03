#!/bin/sh
# Run a memory-heavy command (headless Chrome, draw.io export) under a
# machine-wide lock, so parallel workers never start two at once.
#
#   tools/lock.sh node tools/render_check.js ...
#   tools/lock.sh drawio -x -f svg -o out.svg in.drawio
LOCK="${TMPDIR:-/tmp}/andrewrosemberg-heavy.lock"
while ! mkdir "$LOCK" 2>/dev/null; do
  pid=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then rm -rf "$LOCK"; continue; fi
  sleep 2
done
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT INT TERM
"$@"
