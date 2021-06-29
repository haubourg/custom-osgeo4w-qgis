#! python3  # noqa: E265

# Standard library
import logging
from functools import lru_cache

# PyQGIS
from qgis.core import QgsApplication, QgsLayerItem

# project
from menu_from_project.__about__ import DIR_PLUGIN_ROOT

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


@lru_cache()
def guess_type_from_uri(qgs_uri: str) -> str:
    """Return project storage type based on the QGS URI.

    :param qgs_uri: QGS project URI (filepath, url or connection string)
    :type qgs_uri: str

    :return: storage type: "database", "file" or "http"
    :rtype: str
    """
    if qgs_uri.startswith("postgresql"):
        return "database"
    elif qgs_uri.startswith("http"):
        return "http"
    else:
        return "file"


@lru_cache()
def icon_per_storage_type(type_storage: str) -> str:
    """Returns the icon for a storage type,

    :param type_storage: [description]
    :type type_storage: str

    :return: icon path
    :rtype: str
    """
    if type_storage == "file":
        return QgsApplication.iconPath("mIconFile.svg")
    elif type_storage == "database":
        return QgsApplication.iconPath("mIconPostgis.svg")
    elif type_storage == "http":
        return str(DIR_PLUGIN_ROOT / "resources/globe.svg")
    else:
        return QgsApplication.iconPath("mIconFile.svg")


@lru_cache()
def icon_per_geometry_type(geometry_type: str):
    """Return the icon for a geometry type.

    If not found, it will return the default icon.

    :param geometry_type: The geometry as a string.
    :type geometry_type: basestring

    :return: The icon.
    :rtype: QIcon
    """
    geometry_type = geometry_type.lower()
    if geometry_type == "raster":
        return QgsLayerItem.iconRaster()
    elif geometry_type == "mesh":
        return QgsLayerItem.iconMesh()
    elif geometry_type == "point":
        return QgsLayerItem.iconPoint()
    elif geometry_type == "line":
        return QgsLayerItem.iconLine()
    elif geometry_type == "polygon":
        return QgsLayerItem.iconPolygon()
    elif geometry_type == "no geometry":
        return QgsLayerItem.iconTable()
    else:
        return QgsLayerItem.iconDefault()
