#!/bin/zsh
# Instala Nube Tune en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
# También instala el ayudante (mueve la reproducción con un clic en el editor de notas) y lo arranca;
# el ayudante se agrega solo a Scripts/__startup.lua para arrancar con REAPER.
set -e
RES="$HOME/Library/Application Support/REAPER"
cd "$(dirname "$0")"
mkdir -p "$RES/Effects/Nube Tune" "$RES/Scripts/Nube Tune"
ln -sf "$PWD/nube_tune.jsfx" "$RES/Effects/Nube Tune/nube_tune.jsfx"
ln -sf "$PWD/Nube Tune - ayudante.lua" "$RES/Scripts/Nube Tune/Nube Tune - ayudante.lua"
if pgrep -xq REAPER; then
  /Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$RES/Scripts/Nube Tune/Nube Tune - ayudante.lua" >/dev/null 2>&1 &
  echo "Ayudante corriendo (y agregado al arranque de REAPER)."
else
  grep -qs "Nube Tune - ayudante" "$RES/Scripts/__startup.lua" || printf '\n-- Nube Tune - ayudante (mover la reproducción desde el plugin)\ndofile([[%s]])\n' "$RES/Scripts/Nube Tune/Nube Tune - ayudante.lua" >> "$RES/Scripts/__startup.lua"
  echo "El ayudante arrancará la próxima vez que abras REAPER."
fi
echo "Listo: en REAPER busca \"Nube Tune\" en el navegador de FX (JS: Nube Tune)."
