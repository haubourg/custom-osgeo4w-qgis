#!/bin/bash
set -e

# Building script of the custom package
# gets version from setup.ini and build a osgeo4w tar.bz2 ready to be deployed

cd qgis-custom 
# gets version 
VERSION=$(grep -i version setup.hint | awk '{printf $2}') 

# fix tar.bz2 name with real version replacing @@ marker with version

sed -i "/install: x86_64/s/.*/install: x86_64\/release\/qgis\/qgis-custom\/qgis-custom-$VERSION.tar.bz2/" setup.hint

# pushes version as a environment variable. Helps to diagnose which package version is installed quickly from QGIS settings
sed -i "s/qgis-custom-VERSION=.*/qgis-custom-VERSION=$VERSION/" apps/qgis-custom/qgis-ltr-custom.bat.template

# compression
tar cvjSf ../qgis-custom-$VERSION.tar.bz2 .

# restores @@ marker  
sed -i "s/qgis-custom-VERSION=.*/qgis-custom-VERSION=@@/" apps/qgis-custom/qgis-ltr-custom.bat.template







