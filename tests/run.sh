#!/bin/zsh
# Renderiza los casos en REAPER (pestaña temporal) y verifica contra la teoría. Uso: tests/run.sh [patron de casos]
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}   # necesita numpy, scipy y soundfile
python3 tools/check_names.py || exit 1
[ -f tests/signals/vowel430.wav ] || $PY tests/make_signals.py
mkdir -p tests/out; echo "${1:-$NUBE_CASE}" > tests/out/only.txt   # REAPER no hereda las variables de entorno
rm -f tests/out/log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/render_cases.lua" >/dev/null 2>&1 &
for i in $(seq 1 300); do grep -q done tests/out/log.txt 2>/dev/null && break; sleep 1; done
grep -q done tests/out/log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
grep -i error tests/out/log.txt
[ -n "${1:-$NUBE_CASE}" ] && exit 0
$PY tests/check.py
