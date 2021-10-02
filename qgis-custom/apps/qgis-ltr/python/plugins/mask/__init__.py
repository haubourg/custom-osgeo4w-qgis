"""
/***************************************************************************
Name            : Mask plugin
Description          : Help to create mask
Date                 : 08/Feb/12
copyright            : (C) 2011 by AEAG
email                : xavier.culos@eau-adour-garonne.fr
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


def classFactory(iface):
    # load aeag_mask class from file aeag_mask
    from .aeag_mask import aeag_mask

    return aeag_mask(iface)
