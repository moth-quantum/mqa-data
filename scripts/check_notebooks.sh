#!/usr/bin/env bash
# Lint every marimo notebook, then run each one headlessly via `marimo export html`.
# Export exits non-zero if any cell raises, so a passing run proves the notebook
# opens and executes offline (gated cells stop cleanly via mo.stop).
#
# Usage: scripts/check_notebooks.sh [OUT_DIR] [notebooks...]
#   NB_TIMEOUT  seconds per notebook (default 900)
#   SMOKE=1     also start `marimo edit --headless` and probe it over HTTP
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-${TMPDIR:-/tmp}/marimo-html}"
shift || true
if [ "$#" -gt 0 ]; then
  NOTEBOOKS=("$@")
else
  NOTEBOOKS=("$ROOT"/notebooks/*.py)
fi
NB_TIMEOUT="${NB_TIMEOUT:-900}"
export MPLBACKEND=Agg MARIMO_SKIP_UPDATE_CHECK=1

mkdir -p "$OUT"
cd "$ROOT"

echo "== marimo check"
marimo check --strict "${NOTEBOOKS[@]}"

echo "== marimo export html"
failed=()
for nb in "${NOTEBOOKS[@]}"; do
  name="$(basename "$nb" .py)"
  start=$(date +%s)
  if timeout "$NB_TIMEOUT" marimo export html "$nb" -o "$OUT/$name.html" -f >"$OUT/$name.log" 2>&1; then
    echo "PASS $name ($(( $(date +%s) - start ))s)"
  else
    echo "FAIL $name ($(( $(date +%s) - start ))s) -- see $OUT/$name.log"
    tail -n 30 "$OUT/$name.log"
    failed+=("$name")
  fi
done

if [ "${SMOKE:-0}" = "1" ]; then
  echo "== marimo edit --headless smoke"
  port="${PORT:-2718}"
  marimo edit --headless --no-token --host 127.0.0.1 -p "$port" "$ROOT/notebooks/" >"$OUT/edit.log" 2>&1 &
  pid=$!
  ok=0
  for _ in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$port/" >/dev/null 2>&1; then ok=1; break; fi
    sleep 1
  done
  kill "$pid" 2>/dev/null || true
  if [ "$ok" = "1" ]; then echo "PASS edit server responded"; else echo "FAIL edit server"; failed+=("edit-server"); fi
fi

if [ "${#failed[@]}" -gt 0 ]; then
  echo "FAILED: ${failed[*]}"
  exit 1
fi
echo "All notebooks OK -> $OUT"
