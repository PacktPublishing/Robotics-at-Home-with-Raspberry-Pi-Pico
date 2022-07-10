#!/bin/bash
set -eiu -o pipefail

DEST=/volumes/CIRCUITPY
LIBRARY_SRC=/Users/danielstaple/git_work/projects_in_cloud/book_authoring/book-research/pico-book-research/circuitpython/3rdparty/built/adafruit-circuitpython-bundle-7.x-mpy-20220228

FILES=(adafruit_pioasm.mpy adafruit_requests.mpy adafruit_vl53l1x.mpy)
#bno_055, adafruit_register
FOLDERS=(adafruit_wsgi adafruit_esp32spi)

for file in "${FILES[@]}"; do
  cp -v "${LIBRARY_SRC}/lib/${file}" "${DEST}/lib/${file}"
done

for folder in "${FOLDERS[@]}"; do
 rsync -rv "${LIBRARY_SRC}/lib/${folder}/" "${DEST}/lib/${folder}/"
done
