#!/bin/bash
set -e

# Building script of the custom package
# gets version from setup.ini and build a osgeo4w tar.bz2 ready to be deployed

cd qgis-custom

REF_PLUGINS_PATH="$1"

# get version 
VERSION=$(grep -i version setup.hint | awk '{printf $2}')

# fix tar.bz2 name with real version replacing @@ marker with version
sed -i "/install: x86_64/s/.*/install: x86_64\/release\/qgis\/qgis-custom\/qgis-custom-$VERSION.tar.bz2/" setup.hint

# pushes version as a environment variable. Helps to diagnose which package version is installed quickly from QGIS settings
sed -i "s/QGIS-CUSTOM-VERSION=.*/QGIS-CUSTOM-VERSION=$VERSION/" apps/qgis-custom/qgis-ltr-custom.bat.template

# set plugin ref path 
sed -i "s@PLUGINS_PATH =.*@PLUGINS_PATH = Path(\"$REF_PLUGINS_PATH\")@" bin/data/QGIS/QGIS3/startup.py

# compression
tar cvjSf ../qgis-custom-$VERSION.tar.bz2 .

# restores @@ markers
sed -i "s/QGIS-CUSTOM-VERSION=.*/QGIS-CUSTOM-VERSION=@@/" apps/qgis-custom/qgis-ltr-custom.bat.template
sed -i "s/PLUGINS_PATH =.*/PLUGINS_PATH = Path(\"to_be_defined\")/" bin/data/QGIS/QGIS3/startup.py
