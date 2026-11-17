#!/bin/zsh
# Instala Nube Tune en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Tune"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_tune.jsfx" "$DST/nube_tune.jsfx"
echo "Listo: en REAPER busca \"Nube Tune\" en el navegador de FX (JS: Nube Tune)."
