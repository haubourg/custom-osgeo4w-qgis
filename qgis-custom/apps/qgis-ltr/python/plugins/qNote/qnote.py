# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qNote
                                 A QGIS plugin
 Save notes in QGIS projects
                              -------------------
        begin                : 2012-03-31
        copyright            : (C) 2012 by Piotr Pociask
        email                : opengis84 (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries

from builtins import object
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from qgis.PyQt import uic
from os import path

from .qnote_panel import MainPanel

class qNote(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        proj = QgsProject.instance()
        proj.readProject.connect(self.loadData)
        proj.writeProject.connect(self.saveData)
        self.iface.newProjectCreated.connect(self.clearEdit)
        
        self.dock = MainPanel()
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        
        self.loadData()

    def unload(self):
        self.iface.removeDockWidget(self.dock)
        del self.dock

    def run(self):
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dock)
        self.loadData()

    def saveData(self):
        proj = QgsProject.instance()
        if self.dock.edit.toPlainText():
            proj.writeEntry('qnote', 'data', self.dock.edit.toHtml())
            proj.writeEntryBool('qnote', 'is_html', True)
        else:
            proj.removeEntry('qnote', 'data')
            proj.removeEntry('qnote', 'is_html')

    def loadData(self):
        proj = QgsProject.instance()
        text, has_note = proj.readEntry('qnote', 'data', '')
        is_html = proj.readEntry('qnote', 'is_html', "false")[0]
        if is_html == "true":
            self.dock.edit.setHtml( text )
        else:
            self.dock.edit.setText( text )
        self.dock.undo.setEnabled( False )
        self.dock.redo.setEnabled( False )
        if has_note:
            self.dock.show()
    
    def clearEdit(self):
        self.dock.edit.setHtml('')
