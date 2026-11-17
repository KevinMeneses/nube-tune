#!/bin/zsh
# Cierra la demo de la interfaz (si hay) y la vuelve a abrir con el código nuevo. NUBE_SHOT=archivo.png toma captura.
# NUBE_PRESET (2), NUBE_KEY (0 = C), NUBE_SCALE (0 = cromática), NUBE_AUDIO (signals/voz.wav)
cd "$(dirname "$0")"
python3 ../tools/check_names.py ../nube_tune.jsfx || exit 1
R=/Applications/REAPER.app/Contents/MacOS/REAPER
mkdir -p out   # antes de cerrar: ui_close.lua guarda ahí (sin la carpeta REAPER muestra un error modal)
osascript -e 'tell application "System Events" to tell process "REAPER" to get name of every window' 2>/dev/null | grep -q "Nube Tune demo" && { $R -nonewinst "$PWD/ui_close.lua" >/dev/null 2>&1 & sleep 3; }
echo "${NUBE_PRESET:-2} ${NUBE_KEY:-0} ${NUBE_SCALE:-0} ${NUBE_AUDIO:-}" > out/demo_opts.txt   # REAPER no hereda las variables de entorno
rm -f out/ui.txt; $R -nonewinst "$PWD/ui_demo.lua" >/dev/null 2>&1 &
for i in $(seq 1 20); do grep -q done out/ui.txt 2>/dev/null && break; sleep 0.5; done; sleep 3.5
[ -n "$NUBE_SHOT" ] && python3 -c "import sys; sys.path.insert(0, '.'); from ui import shot; shot('$NUBE_SHOT')"
echo listo
