#/***************************************************************************
#                             -------------------
#        begin                : 2014-02-20
#        copyright            : (C) 2014 by Oslandia
#        email                : hugo.mercier@oslandia.com
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

QGISDIR=.qgis2

# Makefile for a PyQGIS plugin 

# global

PLUGINNAME = mask

#
SOURCES = aeag_mask.py maindialog.py __init__.py layerlist.py mask_filter.py mask_parameters.py style_tools.py htmldialog.py
TRANSLATIONS = mask_fr.ts

EXTRAS = aeag_mask.png metadata.txt default_mask_style.qml
UI_FILES = ui_plugin_mask.py ui_layer_list.py

RESOURCE_FILES = resources_rc.py

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease-qt4 $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(QGISDIR)/python/plugins
deploy: compile transcompile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/db
	cp -vf $(SOURCES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf *.ts *.qm $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr doc/ $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean 
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip. 
# This requires use of git (your plugin development directory must be a 
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 $(SOURCES) $(UI_FILES:.py=.ui) -ts $(TRANSLATIONS)

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f *.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
#doc: 
#	cd help; make html
