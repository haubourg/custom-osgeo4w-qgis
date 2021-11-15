#!/bin/bash
set -e 

# auteur : Régis Haubourg - GrenobleAlpesMetropole
# Licence GPLV3
# 26/05/2021

# this script takes your locally built tar.bz2 package and push it to the local repository hosting your osgeo4W binaries

echo "** Deploying osgeo4W custom package **
"

cd qgis-custom

SETUP_TEXT=$(cat setup.hint)

PACKAGE_DIR=$1

echo "- Target package directory : 
$PACKAGE_DIR
"

echo "- Package metadata : 
------------
$SETUP_TEXT
------------"


if [ ! -d "$PACKAGE_DIR" ] 
then
   echo "Target directory doesn't exists!"
   exit 1
fi


VERSION=$(grep -i version setup.hint | awk '{printf $2}') 

echo "Package version found: $VERSION"

mkdir -p "$PACKAGE_DIR/x86_64/release/qgis/qgis-custom/"

cd - 

sudo cp -p qgis-custom-$VERSION.tar.bz2 $PACKAGE_DIR/x86_64/release/qgis/qgis-custom/

# md5 and size  
MD5=$(md5sum qgis-custom-$VERSION.tar.bz2 | awk -F'[ ]'  '{print $1}')
size=$(stat -c "%s" qgis-custom-$VERSION.tar.bz2)

# adds metadata into setup.ini, from setup.hint template

echo -e "- Modification of setup.ini"

cp -p $PACKAGE_DIR/x86_64/setup.ini setup.ini
chmod +w setup.ini

# deletes previous entry
sed -i '/@ qgis-custom/,+8d;' setup.ini

# append to the end of the file
echo "@ qgis-custom
$SETUP_TEXT $size $MD5 
" >>  setup.ini 

sudo cp -fp setup.ini $PACKAGE_DIR/x86_64/setup.ini
rm -f setup.ini

echo -e "--------"

echo -e "** Package deployed **"

echo -e "--------\n"

echo -e "- Copy osgeo4w-setup.exe and .bat install"
sudo cp -p install/install_QGIS.bat $PACKAGE_DIR/../
sudo cp -p install/osgeo4w-setup.exe $PACKAGE_DIR/../
echo -e "Done"

