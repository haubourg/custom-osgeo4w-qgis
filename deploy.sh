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

PACKAGE_DIR="/x/OSGEO4W_DEPLOY_TEST/PAQUETS/http%3a%2f%2fwww.norbit.de%2fosgeo4w%2f"

echo "-Target package directory : 
$PACKAGE_DIR
"

echo "-PAckage metadata : 
------------
$SETUP_TEXT
------------"


if [ ! -d "$PACKAGE_DIR" ] 
then
   echo "Target directory doesn't exists"
#    e  xit 2 
fi


VERSION=$(grep -i version setup.hint | awk '{printf $2}') 

echo "package version found:  $VERSION"

mkdir -p "$PACKAGE_DIR/x86_64/release/qgis/qgis-custom/"

cd - 

cp -p qgis-custom-$VERSION.tar.bz2 $PACKAGE_DIR/x86_64/release/qgis/qgis-custom/

# md5 and size  
MD5=$(md5sum qgis-custom-$VERSION.tar.bz2 | awk -F'[ ]'  '{print $1}')
size=$(stat -c "%s" qgis-custom-$VERSION.tar.bz2)

# adds metadata into setup.ini, from setup.hint template

echo -e "
- Modification du setup.ini cible" 

# deletes previous entry
sed -i  '/@ qgis-custom/,+8d;' $PACKAGE_DIR/x86_64/setup.ini

# append to the end of the file

echo "@ qgis-custom
$SETUP_TEXT $size $MD5 
" >>  $PACKAGE_DIR/x86_64/setup.ini 

echo -e "--------"

echo -e "** Package deployed **"

echo -e "--------"
