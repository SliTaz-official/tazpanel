#!/bin/sh
#
# Use imagemagick to convert icon images for TazPanel
#

STYLE=$1
IMAGES=../styles/$STYLE/images
SIZE=16x16

[ -z "$1" ] && exit 0
cd $IMAGES

echo ""
for i in *.png
do
	echo "convert $i -resize $SIZE $i"
	convert $i -resize $SIZE $i
done
echo ""

exit 0
