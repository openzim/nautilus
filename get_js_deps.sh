#!/bin/bash
set -e  # fail script on error

###
# download JS dependencies and place them in our templates/assets folder
# then launch our ogv.js script to fix dynamic loading links
###

function die {
    echo "$1"
    exit 1
}

if ! command -v wget > /dev/null; then
    die "you need wget."
fi

if ! command -v unzip > /dev/null; then
    die "you need unzip."
fi

# Absolute path this script is in.
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
VENDORS_PATH="${SCRIPT_PATH}/nautiluszim/templates/vendors"

echo "About to download JS assets to ${VENDORS_PATH}"

echo "getting video.js"
wget -c https://github.com/videojs/video.js/releases/download/v7.6.4/video-js-7.6.4.zip
rm -rf $VENDORS_PATH/videojs
mkdir -p $VENDORS_PATH/videojs
unzip -o -d $VENDORS_PATH/videojs video-js-7.6.4.zip
rm -rf $VENDORS_PATH/videojs/alt $VENDORS_PATH/videojs/examples
rm -f video-js-7.6.4.zip

echo "getting ogv.js"
wget -c https://github.com/brion/ogv.js/releases/download/1.6.1/ogvjs-1.6.1.zip
rm -rf $VENDORS_PATH/ogvjs
unzip -o ogvjs-1.6.1.zip
mv ogvjs-1.6.1 $VENDORS_PATH/ogvjs
rm -f ogvjs-1.6.1.zip

echo "getting videojs-ogvjs.js"
wget -c https://github.com/hartman/videojs-ogvjs/archive/v1.3.1.zip
rm -f $VENDORS_PATH/videojs-ogvjs.js
unzip -o v1.3.1.zip
mv videojs-ogvjs-1.3.1/dist/videojs-ogvjs.js $VENDORS_PATH/videojs-ogvjs.js
rm -rf videojs-ogvjs-1.3.1
rm -f v1.3.1.zip

echo "fixing JS files"
python3 $SCRIPT_PATH/nautiluszim/fix_ogvjs_dist.py

echo "getting jquery.js"
wget -c -O $VENDORS_PATH/jquery.min.js https://code.jquery.com/jquery-3.4.1.min.js

echo "getting bootstrap"
wget -c https://github.com/twbs/bootstrap/archive/v4.4.1.zip
rm -rf $VENDORS_PATH/bootstrap
unzip -o v4.4.1.zip
mv bootstrap-4.4.1/dist/ $VENDORS_PATH/bootstrap
rm -rf bootstrap-4.4.1
rm -f v4.4.1.zip

echo "getting pouchdb"
wget -c -O $VENDORS_PATH/pouchdb.min.js https://cdn.jsdelivr.net/npm/pouchdb@7.1.1/dist/pouchdb.min.js
wget -c -O $VENDORS_PATH/pouchdb.find.min.js https://cdn.jsdelivr.net/npm/pouchdb@7.1.1/dist/pouchdb.find.min.js

echo "getting ScrollMagic"
wget -c -O $VENDORS_PATH/ScrollMagic.min.js https://cdnjs.cloudflare.com/ajax/libs/ScrollMagic/2.0.7/ScrollMagic.min.js

echo "getting SugarJS"
wget -c -O $VENDORS_PATH/sugar.min.js https://raw.githubusercontent.com/andrewplummer/Sugar/2.0.4/dist/sugar.min.js


echo "getting vector icons"
wget -c https://github.com/dmhendricks/file-icon-vectors/releases/download/1.0/file-icon-vectors-1.0.zip
rm -rf $VENDORS_PATH/ext-icons
mkdir -p file-icon-vectors
unzip -o file-icon-vectors-1.0.zip -d file-icon-vectors
mv file-icon-vectors/dist/icons/square-o $VENDORS_PATH/ext-icons
cp -v $VENDORS_PATH/ext-icons/ppt.svg $VENDORS_PATH/ext-icons/odp.svg
rm -rf file-icon-vectors
rm -f file-icon-vectors-1.0.zip
