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
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import
def name():
    return "qNote"
def author():
    return "GIS Support, Piotr Pociask"
def email():
    return "piotr.pociask@gis-support.pl"
def description():
    return "Save notes in QGIS projects"
def version():
    return "Version 1.0"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.0"
def qgisMaximumVersion():
    return "2.99"
def classFactory(iface):
    # load qNote class from file qNote
    from .qnote import qNote
    return qNote(iface)
