#!/bin/zsh
# Renderiza los casos en REAPER (pestaña temporal) y verifica la respuesta. NUBE_CASE=texto corre solo esos casos.
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}   # necesita numpy, scipy y soundfile
[ -f tests/signals/vowel430.wav ] || $PY tests/make_signals.py
mkdir -p tests/out; echo "${NUBE_CASE:-}" > tests/out/only.txt   # REAPER no hereda las variables de entorno
rm -f tests/out/log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/render_cases.lua" >/dev/null 2>&1 &
for i in $(seq 1 300); do grep -q done tests/out/log.txt 2>/dev/null && break; sleep 1; done
grep -q done tests/out/log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
grep -i error tests/out/log.txt
[ -z "$NUBE_CASE" ] && $PY tests/check.py || echo "(solo $NUBE_CASE: sin check.py)"
