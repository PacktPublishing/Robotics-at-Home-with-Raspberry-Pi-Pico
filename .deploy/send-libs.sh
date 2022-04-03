#!/bin/bash
set -eiu -o pipefail

DEST=/volumes/CIRCUITPY
# DEST=dummy
LIBRARY_SRC=libs/circuitpython-bundle-7/lib
mkdir -p "${DEST}/lib"

for ITEM in "$@"; do
  rsync -rv "${LIBRARY_SRC}/${ITEM}" "${DEST}/lib/"
done
