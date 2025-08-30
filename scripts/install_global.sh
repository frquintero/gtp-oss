#!/usr/bin/env bash
# Instala el ejecutable `gptv2` globalmente en /usr/local/bin
set -euo pipefail

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
TARGET="/usr/local/bin/gptv2"
SRC="${SRC_DIR}/gptv2"

if [ ! -f "${SRC}" ]; then
    echo "Error: ${SRC} no existe." >&2
    exit 2
fi

if [ ! -x "${SRC}" ]; then
    echo "Añadiendo permiso ejecutable a ${SRC}"
    chmod +x "${SRC}"
fi

echo "Creando symlink ${TARGET} -> ${SRC} (requiere sudo si no eres root)"
sudo ln -sf "${SRC}" "${TARGET}"
echo "Instalado. Ejecuta 'gptv2 --help' o 'gptv2' para probar."
