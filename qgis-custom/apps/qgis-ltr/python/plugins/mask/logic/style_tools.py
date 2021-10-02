import os

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtXml import QDomDocument, QDomImplementation
from qgis.core import QgsReadWriteContext

from .mask_parameters import MaskParameters


def set_layer_symbology(layer, symbology):
    if symbology is not None:
        doc = QDomDocument("qgis")
        doc.setContent(symbology)
        errorMsg = ""
        ctx = QgsReadWriteContext()
        layer.readSymbology(doc.firstChildElement("qgis"), errorMsg, ctx)


def get_layer_symbology(layer):
    doc = QDomDocument(
        QDomImplementation().createDocumentType(
            "qgis", "http://mrcc.com/qgis.dtd", "SYSTEM"
        )
    )
    rootNode = doc.createElement("qgis")
    doc.appendChild(rootNode)
    errorMsg = ""
    ctx = QgsReadWriteContext()
    layer.writeSymbology(rootNode, doc, errorMsg, ctx)
    return doc.toByteArray()


def set_default_layer_symbology(layer):
    settings = QSettings()

    parameters = MaskParameters()
    defaults = settings.value("mask/defaults", None)
    if defaults is not None:
        parameters.unserialize(defaults)
        set_layer_symbology(layer, parameters.style)
    else:
        default_style = os.path.join(
            os.path.dirname(__file__), "../resources/default_mask_style.qml"
        )
        layer.loadNamedStyle(default_style)
