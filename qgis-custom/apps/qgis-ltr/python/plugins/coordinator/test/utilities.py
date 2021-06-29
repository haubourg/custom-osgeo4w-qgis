# coding=utf-8
"""Common functionality used by regression tests."""

import sys
import logging
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QMainWindow, QDialog, QWindow, QLocale
from time import sleep
from qgis.core import QgsCoordinateReferenceSystem
from qgis.PyQt import sip


LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from PyQt5 import QtGui, QtCore
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas
        import qgis.utils
        from .qgis_interface import QgisStubInterface
    except ImportError as error:
        print("Failed to import QGIS libs %s"  % error)
        return None, None, None
   
    global QGIS_APP, IFACE, CANVAS, PARENT
    
    if CANVAS and sip.isdeleted(CANVAS):
        CANVAS = None
        IFACE = None
    
    if not IFACE or not CANVAS:
        if qgis.utils.iface:
            # we are probably running in the QGIS Applications Python console.
            # so we have all we need:
            IFACE = qgis.utils.iface
            CANVAS = IFACE.mapCanvas()
            QGIS_APP = QgsApplication.instance()
            PARENT = CANVAS.parentWidget()
        else:            
            try:
                sysargsUtf8 = [sysarg.encode("utf-8") for sysarg in sys.argv]
            except AttributeError:
                sysargsUtf8 = []
            QGIS_APP = QgsApplication(sysargsUtf8, True)
            QGIS_APP.initQgis()
            PARENT = QWidget()
            CANVAS = QgsMapCanvas(PARENT)
            CANVAS.resize(QtCore.QSize(400, 400))
            CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
            IFACE = QgisStubInterface(CANVAS)
    
    return QGIS_APP, IFACE, CANVAS


DEC_POINT = QLocale().decimalPoint()
GROUP_SEPARATOR = QLocale().groupSeparator()
TRANSLATION = str.maketrans(".,", "%s%s" % (DEC_POINT, GROUP_SEPARATOR) )

def helperFormatCoordinates(coordinate):
    # if the locale does not use grouping, we need to remove the grouping
    # separator before translation:
    if QLocale.OmitGroupSeparator & QLocale().numberOptions():
        coordinate = coordinate.replace(",", "")
    return coordinate.translate(TRANSLATION)

