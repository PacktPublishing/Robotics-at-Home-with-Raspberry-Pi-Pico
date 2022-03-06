#!/bin/bash
set -eiu -o pipefail

DEST=/volumes/CIRCUITPY

# take the param, strip the filename.
source="$1"
support_files=( "${@:2}" )
sourcebase="$(basename "$source")"
# get the filename without the extension.
module="${sourcebase%.py}"

# empty code.py
echo "" >${DEST}/code.py

# send the file
cp "${source}" "${DEST}/${sourcebase}"

# make a code.py
echo "import ${module}" >"${DEST}/code.py"

if [ -n "${support_files[*]}" ]; then
  for file in "${support_files[@]}"; do
    cp "$file" "${DEST}/$(basename "${file}")"
  done
fi
