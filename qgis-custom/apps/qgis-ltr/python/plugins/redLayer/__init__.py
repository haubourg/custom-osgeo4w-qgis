#! python3  # noqa: E265

"""
/***************************************************************************
 redLayer
                                 A QGIS plugin
 fast georeferenced annotation
                             -------------------
        begin                : 2015-03-10
        copyright            : (C) 2015 by Enrico Ferreguti
        email                : enricofer@gmail.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load redLayer class from file redLayer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .redLayerModule import redLayer
    return redLayer(iface)
