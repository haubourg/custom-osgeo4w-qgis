"""
/***************************************************************************
Name                  : Mask
Description          : Aide à la création de masque
Date                 : Feb/12
copyright            : (C) 2011 by AEAG
                       (c) 2014 Oslandia
email                : geocatalogue@eau-adour-garonne.fr
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
import os
import base64
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QObject,
    QSettings,
    QTranslator,
    QUrl,
    QVariant,
    QFileInfo,
)
from qgis.PyQt.QtGui import QIcon, QDesktopServices
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (
    Qgis,
    QgsExpression,
    QgsExpressionFunction,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsMapLayer,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsLayerTreeLayer,
    QgsField,
    QgsFeature,
    QgsVectorFileWriter,
    QgsRectangle,
    QgsMapToPixelSimplifier,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsVectorSimplifyMethod,
    QgsMessageLog,
    QgsExpressionContextUtils,
    QgsLayoutItemMap,
)
from qgis.utils import showPluginHelp

from .ui.maindialog import MainDialog
from .logic import mask_filter
from .logic.mask_parameters import MaskParameters
from .logic import style_tools
from functools import partial
from .__about__ import DIR_PLUGIN_ROOT

aeag_mask_instance = None

# to be called from another plugin
# from mask import aeag_mask
# aeag_mask.do()
def do(crs=None, poly=None, name=None):
    # crs = QgsCoordinateReferenceSystem
    # poly = list of geometries
    global aeag_mask_instance
    this = aeag_mask_instance
    this.layer = this.apply_mask_parameters(
        this.layer, this.parameters, crs, poly, name, keep_layer=False
    )
    this.save_to_project(this.layer, this.parameters)


def is_in_qgis_core(sym):
    import qgis.core

    return sym in dir(qgis.core)


class MaskGeometryFunction(QgsExpressionFunction):

    def __init__(self, mask):
        QgsExpressionFunction.__init__(
            self,
            "$mask_geometry",
            0,
            "Python",
            self.tr(
                """<h1>$mask_geometry</h1>
Variable filled by mask plugin.<br/>
When mask has been triggered on some polygon, mask_geometry is filled with the
mask geometry and can be reused for expression/python calculation. in_mask
variable uses that geometry to compute a boolean.
<h2>Return value</h2>
The geometry of the current mask
        """
            ),
        )
        self.mask = mask

    def tr(self, message):
        return QCoreApplication.translate("MaskGeometryFunction", message)

    def func(self, values, feature, parent, node):
        return self.mask.mask_geometry()[0]


class InMaskFunction(QgsExpressionFunction):
    def __init__(self, mask):
        QgsExpressionFunction.__init__(
            self,
            "in_mask",
            1,
            "Python",
            self.tr(
                """<h1>in_mask function</h1>
Expression function added by mask plugin. Returns true if current feature
crosses mask geometry.<br/>
The spatial expression to use is set from the mask UI button (exact, fast
using centroids, intermediate using point on surface).<br/>
in_mask takes a CRS EPSG code as first parameter, which is the CRS code of the
evaluated features.<br/>
It can be used to filter labels only in that area, or since QGIS 2.13, legend
items only visible in mask area.<br/>
<h2>Return value</h2>
true/false (0/1)<br/>
<h2>Usage</h2>
in_mask(2154)"""
            ),
        )
        self.mask = mask

    @staticmethod
    def tr(message):
        return QCoreApplication.translate("InMaskFunction", message)

    def func(self, values, context, parent, node):
        return self.mask.in_mask(context.feature(), values[0])


class aeag_mask(QObject):
    WRITE_ERRORS = {
        QgsVectorFileWriter.NoError : "Ok",
        QgsVectorFileWriter.ErrDriverNotFound : "Driver not found",
        QgsVectorFileWriter.ErrCreateDataSource : "Cannot create data source",
        QgsVectorFileWriter.ErrCreateLayer : "Cannot create layer",
        QgsVectorFileWriter.ErrAttributeTypeUnsupported : "Attribute type unsupported",
        QgsVectorFileWriter.ErrAttributeCreationFailed : "Attribute creation failed",
        QgsVectorFileWriter.ErrProjection : "Projection error",
        QgsVectorFileWriter.ErrFeatureWriteFailed : "Feature write failed",
        QgsVectorFileWriter.ErrInvalidLayer : "Invalid layer",
        # QgsVectorFileWriter.ErrSavingMetadata : "Metadata saving error",
        QgsVectorFileWriter.Canceled : "Canceled"
    }

    def __init__(self, iface):
        QObject.__init__(self)
        # Save reference to the QGIS interface

        global aeag_mask_instance
        aeag_mask_instance = self
        self.iface = iface
        self.path = QFileInfo(os.path.realpath(__file__)).path()

        try:
            # install translator
            self.myLocale = QSettings().value("locale/userLocale")[0:2]
            # dictionary
            localePath = self.path + "/i18n/" + self.myLocale + ".qm"
            # translator
            if QFileInfo(localePath).exists():
                self.translator = QTranslator()
                self.translator.load(localePath)
                QCoreApplication.installTranslator(self.translator)
        except Exception:
            # no translation
            pass

        try:
            self.toolBar = None
            self.act_aeag_mask = None
            self.act_aeag_toolbar_help = None
            self.canvas = self.iface.mapCanvas()
            self.old_active_layer = None

            # test qgis version for the presence of the simplifier
            self.has_simplifier = is_in_qgis_core("QgsMapToPixelSimplifier")
            # test qgis version for the presence of pointOnSurface
            self.has_point_on_surface = "pointOnSurface" in dir(QgsGeometry)

            self.MASK_NAME = "Mask"

        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(m, "Extensions")

        try:
            self.reset_mask_layer(False)
        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(m, "Extensions")

    def reset_mask_layer(self, toSave=True):
        self.layer = None
        # mask parameters
        self.parameters = MaskParameters()

        if toSave:
            self.save_to_project(self.layer, self.parameters)

        for name, layer in QgsProject.instance().mapLayers().items():
            if mask_filter.has_mask_filter(layer):
                # remove mask filter from layer, if any
                mask_filter.remove_mask_filter(layer)

        self.simplified_geometries = {}

    def initGui(self):
        self.mask_geometry_function = MaskGeometryFunction(self)
        QgsExpression.registerFunction(self.mask_geometry_function)
        self.in_mask_function = InMaskFunction(self)
        QgsExpression.registerFunction(self.in_mask_function)

        #
        self.disable_remove_mask_signal = False
        self.disable_add_layer_signal = False
        self.project = QgsProject.instance()
        self.project.layerWillBeRemoved.connect(self.on_remove_mask)

        self.act_aeag_mask = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/aeag_mask.png")),
            self.tr("Create a mask"),
            self.iface.mainWindow(),
        )

        self.toolBar = self.iface.pluginToolBar()
        self.toolBar.addAction(self.act_aeag_mask)
        self.iface.addPluginToMenu("&Mask", self.act_aeag_mask)

        # turn it to true to enable test
        if False:
            self.act_test = QAction(
                 QIcon(str(DIR_PLUGIN_ROOT / "resources/aeag_mask.png")), "Test", self.iface.mainWindow()
            )
            self.toolBar.addAction(self.act_test)
            self.iface.addPluginToMenu("&Mask", self.act_test)
            self.act_test.triggered.connect(self.do_test)

        # Add documentation links to the menu
        self.act_aeag_doc = QAction(self.tr("Documentation"), self.iface.mainWindow())
        self.act_aeag_doc.triggered.connect(lambda: showPluginHelp(filename="doc/index"))
        self.iface.addPluginToMenu("&Mask", self.act_aeag_doc)

        # Add actions to the toolbar
        self.act_aeag_mask.triggered.connect(self.run)

        # look for an existing mask layer
        mask_id, ok = QgsProject.instance().readEntry("Mask", "layer_id")
        self.layer = self.project.mapLayer(mask_id)

        # register layout signals
        lm = QgsProject.instance().layoutManager()
        lm.layoutAdded.connect(self.on_layout_added)
        lm.layoutAboutToBeRemoved.connect(self.on_layout_removed)

        # register already existing layouts
        for layout in lm.printLayouts():
            self.on_layout_added(layout.name())

        # register to the change of active layer for enabling/disabling
        #   of the action
        self.old_active_layer = None
        self.iface.mapCanvas().currentLayerChanged.connect(
            self.on_current_layer_changed
        )
        self.on_current_layer_changed(None)

        # register to project reading
        # connect to QgisApp::projectRead to make sure MemoryLayerSaver has
        # been called before (it connects to QgsProject::readProject)
        self.iface.mainWindow().projectRead.connect(self.on_project_open)

    def load_from_project(self):
        parameters = MaskParameters()
        try:
            # return layer, parameters
            ok = parameters.load_from_project()
            if not ok:
                # no parameters in the project
                # look for a vector layer called 'Mask'
                for _id, l in list(QgsProject.instance().mapLayers().items()):
                    if l.type() == QgsMapLayer.VectorLayer and l.name() == "Mask":
                        return self.load_from_layer(l)

            layer_id, ok = QgsProject.instance().readEntry("Mask", "layer_id")
            layer = QgsProject.instance().mapLayer(layer_id)
            return layer, parameters

        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(
                    "Mask error when loading - {}".format(m), "Extensions"
                )

            return None, parameters

    def save_to_project(self, layer, parameters):
        try:
            QgsProject.instance().writeEntry(
                "Mask", "layer_id", layer.id() if layer else ""
            )
            parameters.save_to_project()
        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(
                    "Mask error when saving - {}".format(m), "Extensions"
                )

    def on_project_open(self):
        self.layer, self.parameters = self.load_from_project()

        if self.layer is not None:
            self.layer = self.apply_mask_parameters(
                self.layer,
                self.parameters,
                dest_crs=None,
                poly=None,
                name=self.layer.name(),
                keep_layer=True,
            )
            self.act_aeag_mask.setEnabled(True)

    def on_current_layer_changed(self, layer):
        if self.layer is None:
            _, poly = self.get_selected_polygons()
            self.act_aeag_mask.setEnabled(poly != [])
        else:
            self.act_aeag_mask.setEnabled(True)

        if layer and layer.type() != QgsMapLayer.VectorLayer:
            self.old_active_layer = None
            return

        try:
            if self.old_active_layer is not None:
                self.old_active_layer.selectionChanged.disconnect(
                    self.on_current_layer_selection_changed
                )

        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(
                    "on_current_layer_changed - {}".format(m), "Extensions"
                )

        if layer is not None:
            layer.selectionChanged.connect(self.on_current_layer_selection_changed)

        if layer != self.old_active_layer:
            self.old_active_layer = layer

    def on_current_layer_selection_changed(self):
        if self.layer is None:
            _, poly = self.get_selected_polygons()
            self.act_aeag_mask.setEnabled(poly != [])

    def unload(self):
        self.toolBar.removeAction(self.act_aeag_mask)
        self.iface.removePluginMenu("&Mask", self.act_aeag_mask)

        # remove doc links
        self.iface.removePluginMenu("&Mask", self.act_aeag_doc)

        QgsExpression.unregisterFunction("$mask_geometry")
        QgsExpression.unregisterFunction("in_mask")

        self.project.layerWillBeRemoved.disconnect(self.on_remove_mask)

        lm = QgsProject.instance().layoutManager()
        lm.layoutAdded.disconnect(self.on_layout_added)
        lm.layoutAboutToBeRemoved.disconnect(self.on_layout_removed)

        # remove layout signals
        for layout in lm.printLayouts():
            self.on_layout_removed(layout.name())

        self.iface.mapCanvas().currentLayerChanged.disconnect(
            self.on_current_layer_changed
        )
        self.iface.mainWindow().projectRead.disconnect(self.on_project_open)

    # force loading of parameters from a layer
    # for backward compatibility with older versions
    def load_from_layer(self, layer):
        # return layer, parameters
        parameters = MaskParameters()
        ok = parameters.load_from_layer(layer)
        if not ok:
            return layer, parameters
        QgsProject.instance().writeEntry("Mask", "layer_id", layer.id())
        layer = self.apply_mask_parameters(
            layer,
            parameters,
            dest_crs=None,
            poly=None,
            name=layer.name(),
            keep_layer=False,
        )
        return layer, parameters

    def connect_layout_events(self, layout):
        try:
            layout.atlas().renderBegun.connect(self.on_atlas_begin_render)
            layout.atlas().renderEnded.connect(self.on_atlas_end_render)

            for item in layout.items():
                if isinstance(item, QgsLayoutItemMap):
                    item.preparedForAtlas.connect(
                        partial(self.on_prepared_for_atlas, layout)
                    )
        except Exception:
            pass

    def disconnect_layout_events(self, layout):
        try:
            layout.atlas().renderBegun.disconnect(self.on_atlas_begin_render)
            layout.atlas().renderEnded.disconnect(self.on_atlas_end_render)

            for item in layout.items():
                if isinstance(item, QgsLayoutItemMap):
                    item.preparedForAtlas.disconnect()
        except Exception:
            pass

    def refreshEvents(self, layout):
        self.disconnect_layout_events(layout)
        self.connect_layout_events(layout)

    def on_layout_added(self, layoutName):
        layout = QgsProject.instance().layoutManager().layoutByName(layoutName)

        # It is impossible to detect the addition of a 'map' item to the layout (first time case).
        # The user is forced to close the composer then, open it again so that the mask works with the atlas.
        # layout.refreshed.connect(self.on_layout_refreshed)
        self.iface.layoutDesignerClosed.connect(partial(self.refreshEvents, layout))

        self.connect_layout_events(layout)

    def on_layout_removed(self, layoutName):
        layout = QgsProject.instance().layoutManager().layoutByName(layoutName)
        self.disconnect_layout_events(layout)

    def compute_mask_geometries(self, parameters, poly):
        geom = None
        for g in poly:
            if geom is None:
                geom = QgsGeometry(g)
            else:
                # do an union here
                geom = geom.combine(g)

        if parameters.do_buffer:
            geom = geom.buffer(parameters.buffer_units, parameters.buffer_segments)

        # reset the simplified geometries dict
        self.simplified_geometries = {}

        return geom

    def on_prepared_for_atlas(self, layout):
        # called for each atlas feature
        if not self.layer:
            return

        if not self.parameters.do_atlas_interaction:
            return

        geom = QgsExpressionContextUtils.atlasScope(layout.atlas()).variable(
            "atlas_geometry"
        )
        if not geom:
            return

        masked_atlas_geometry = [geom]
        # no need to zoom, it has already been scaled by atlas
        self.layer = self.apply_mask_parameters(
            self.layer,
            self.parameters,
            dest_crs=self.layer.crs(),
            poly=masked_atlas_geometry,
            name=self.layer.name(),
            cleanup_and_zoom=False,
        )

        # update maps
        QCoreApplication.processEvents()

    def on_atlas_begin_render(self):
        if not self.layer:
            return

        if not self.parameters.do_atlas_interaction:
            return

        # save the mask geometry
        self.geometries_backup = [QgsGeometry(g) for g in self.parameters.orig_geometry]

    def on_atlas_end_render(self):
        if not self.layer:
            return

        if not self.parameters.do_atlas_interaction:
            return

        # restore the mask geometry
        self.parameters.orig_geometry = self.geometries_backup
        # no need to zoom, it has already been scaled by atlas
        self.layer = self.apply_mask_parameters(
            self.layer,
            self.parameters,
            dest_crs=None,
            poly=None,
            name=self.layer.name(),
            cleanup_and_zoom=False,
        )
        self.simplified_geometries = {}

        # process events to go out of the current rendering, if any
        QCoreApplication.processEvents()

        # update maps
        # for layout in QgsProject.instance().layoutManager().printLayouts():
        #    layout.refreshItems()

    def apply_mask_parameters(
        self,
        layer,
        parameters,
        dest_crs=None,
        poly=None,
        name=None,
        cleanup_and_zoom=True,
        keep_layer=True,
    ):

        # Apply given mask parameters to the given layer. Returns the new layer
        # The given layer is removed and then recreated in the layer tree
        # if poly is not None, it is used as the mask geometry
        # else, the geometry is taken from parameters.geometry

        if name is None:
            mask_name = self.MASK_NAME
        else:
            mask_name = name

        if poly is None:
            dest_crs, poly = self.get_selected_polygons()
            if (
                poly == []
                and (parameters.orig_geometry is not None)
                and (layer is not None)
            ):
                dest_crs = layer.crs()
                poly = parameters.orig_geometry

        if layer is None and poly is None:
            self.iface.messageBar().pushMessage(self.tr("Mask plugin error"), self.tr("No polygon selection !"), level=Qgis.Warning)
            return

        if layer is None:
            # create a new layer
            layer = QgsVectorLayer(
                "MultiPolygon?crs=%s" % dest_crs.authid(), mask_name, "memory"
            )
            style_tools.set_default_layer_symbology(layer)
            # add a mask filter to all layer
            for name, l in self.project.mapLayers().items():
                if not isinstance(l, QgsVectorLayer):
                    continue

                mask_filter.add_mask_filter(l)

        parameters.layer = layer
        # compute the geometry
        parameters.orig_geometry = [QgsGeometry(g) for g in poly]
        parameters.geometry = self.compute_mask_geometries(parameters, poly)

        # disable rendering
        self.canvas.setRenderFlag(False)
        try:

            if not keep_layer:
                # save layer's style
                layer_style = self.get_layer_style(layer)
                # remove the old layer
                self.disable_remove_mask_signal = True
                self.project.removeMapLayer(layer.id())
                self.disable_remove_mask_signal = False

                # (re)create the layer
                is_mem = not parameters.do_save_as
                nlayer = None
                try:
                    nlayer = self.create_layer(
                        parameters, mask_name, is_mem, dest_crs, layer_style
                    )
                except Exception as e:
                    for m in e.args:
                        QgsMessageLog.logMessage(
                            "apply_mask_parameters - {}".format(m), "Extensions"
                        )
                    self.iface.messageBar().pushMessage(self.tr("Mask plugin error"), 
                        self.tr("Unknown error. The mask is lost."), level=Qgis.Critical)
                    return

                # add the new layer
                layer = nlayer
                QgsProject.instance().writeEntry("Mask", "layer_id", layer.id())
                self.add_layer(layer)
                parameters.layer = layer
            else:
                # replace the mask geometry
                pr = layer.dataProvider()
                fid = 0
                for f in pr.getFeatures():
                    fid = f.id()

                pr.truncate()
                fet1 = QgsFeature(fid)
                fet1.setFields(layer.fields())
                fet1.setGeometry(parameters.geometry)
                pr.addFeatures([fet1])

            if cleanup_and_zoom:
                layer.updateExtents()

                # RH 04 05 2015 > clean up selection of all layers
                for l in self.canvas.layers():
                    if l.type() != QgsMapLayer.VectorLayer:
                        # Ignore this layer as it's not a vector
                        continue
                    if l.featureCount() == 0:
                        # There are no features - skip
                        continue
                    l.removeSelection()

                # RH 04 05 2015 > zooms to mask layer
                canvas = self.iface.mapCanvas()
                extent = layer.extent()
                extent.scale(1.1)  # scales extent by 10% unzoomed
                canvas.setExtent(extent)

            self.update_menus()

            # refresh
            self.canvas.clearCache()

        finally:
            self.canvas.setRenderFlag(True)  # will call refresh

        return layer

    # run method that performs all the real work
    def run(self):
        dest_crs, poly = self.get_selected_polygons()
        is_new = False

        layer, parameters = self.load_from_project()

        if not layer:
            if not poly:
                self.iface.messageBar().pushMessage(
                    self.tr("Mask plugin error"),
                    self.tr("No polygon selection !"),
                    level=Qgis.Info
                )
                return
            layer = QgsVectorLayer(
                "MultiPolygon?crs=%s" % dest_crs.authid(), self.MASK_NAME, "memory"
            )
            style_tools.set_default_layer_symbology(layer)
            is_new = True

        parameters.layer = layer

        dlg = MainDialog(parameters, is_new)

        # for "Apply" and "Ok"
        self.layer = layer

        def on_applied_():
            keep_layer = not is_new and self.parameters.have_same_layer_options(
                parameters
            )
            new_layer = self.apply_mask_parameters(
                self.layer, parameters, keep_layer=keep_layer
            )
            self.save_to_project(new_layer, parameters)
            self.layer = new_layer
            self.parameters = parameters

        # connect apply
        dlg.applied.connect(on_applied_)
        r = dlg.exec_()
        if r == 1:  # Ok
            on_applied_()

        self.update_menus()

    def update_menus(self):
        # update menus based on whether the layer mask exists or not
        if self.layer is not None:
            self.act_aeag_mask.setText(self.tr("Update the current mask"))
        else:
            self.act_aeag_mask.setText(self.tr("Create a mask"))
        # update icon state
        self.on_current_layer_changed(self.iface.activeLayer())

    def on_remove_mask(self, layer_id):
        if self.disable_remove_mask_signal:
            return

        if self.layer is not None and layer_id == self.layer.id():
            self.reset_mask_layer()

        self.update_menus()

    def get_selected_polygons(self):
        "return array of (polygon_feature,crs) from current selection"
        geos = []
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            return None, []
        for feature in layer.selectedFeatures():
            if (
                feature.geometry()
                and feature.geometry().type() == QgsWkbTypes.PolygonGeometry
            ):
                geos.append(QgsGeometry(feature.geometry()))
        return layer.crs(), geos

    def add_layer(self, layer):
        # add a layer to the registry, if not already there
        layers = self.project.mapLayers()
        for name, alayer in layers.items():
            if alayer == layer:
                return

        self.project.addMapLayer(layer, False)
        # make sure the mask layer is on top of other layers
        lt = QgsProject.instance().layerTreeRoot()
        # insert a new on top
        self.disable_add_layer_signal = True
        lt.insertChildNode(0, QgsLayerTreeLayer(layer))
        self.disable_add_layer_signal = False

    def get_layer_style(self, layer):
        if layer is None:
            return None
        return (
            layer.opacity(),
            layer.featureBlendMode(),
            layer.blendMode(),
            layer.renderer().clone(),
        )

    def set_layer_style(self, nlayer, style):
        nlayer.setOpacity(style[0])
        nlayer.setFeatureBlendMode(style[1])
        nlayer.setBlendMode(style[2])
        nlayer.setRenderer(style[3])

    def set_default_layer_style(self, layer):
        settings = QSettings()

        parameters = MaskParameters()
        defaults = settings.value("mask/defaults", None)
        if defaults is not None:
            parameters.unserialize(defaults)
        else:
            default_style = os.path.join(
                os.path.dirname(__file__), "/resources/default_mask_style.qml"
            )
            layer.loadNamedStyle(default_style)

    def create_layer(self, parameters, name, is_memory, dest_crs, layer_style=None):
        save_as = parameters.file_path
        file_format = parameters.file_format
        # save paramaters
        serialized = base64.b64encode(
            parameters.serialize(with_style=False)
        )

        # save geometry
        layer = QgsVectorLayer(
            "MultiPolygon?crs=%s" % dest_crs.authid(), name, "memory"
        )
        pr = layer.dataProvider()
        layer.startEditing()
        layer.addAttribute(QgsField("params", QVariant.String))
        fet1 = QgsFeature(0)
        fet1.setFields(layer.fields())
        fet1.setAttribute("params", str(serialized)[2:-1])
        fet1.setGeometry(parameters.geometry)
        pr.addFeatures([fet1])
        layer.commitChanges()

        # copy layer style
        if layer_style is not None:
            self.set_layer_style(layer, layer_style)

        if is_memory:
            return layer

        if os.path.isfile(save_as):
            # delete first if already exists
            if save_as.endswith(".shp"):
                QgsVectorFileWriter.deleteShapeFile(save_as)
            else:
                os.unlink(save_as)

        # create the disk layer
        QgsMessageLog.logMessage(
            "Mask saving '{}' as {}".format(save_as, file_format), "Extensions"
        )
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = file_format
        #save_options.fileEncoding = "UTF-8"
        transform_context = QgsProject.instance().transformContext()
        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer, save_as, transform_context, save_options
        )

        if error[0] == QgsVectorFileWriter.NoError:
            nlayer = QgsVectorLayer(save_as, name, "ogr")
            if not nlayer.dataProvider().isValid():
                self.iface.messageBar().pushMessage(self.tr("Mask plugin error"), self.tr("Invalid dataProvider. The mask remains in memory. Check file name, format and extension."), level=Qgis.Warning)
                return layer
            if not nlayer.isSpatial():
                self.iface.messageBar().pushMessage(self.tr("Mask plugin error"), self.tr("No GeometryType. The mask remains in memory. Check file name, format and extension."), level=Qgis.Warning)
                return layer

            # force CRS
            nlayer.setCrs(dest_crs)

            # copy layer style
            layer_style = self.get_layer_style(layer)
            self.set_layer_style(nlayer, layer_style)
            return nlayer
        else:
            self.iface.messageBar().pushMessage(self.tr("Mask plugin error"), self.tr(self.WRITE_ERRORS[error]) + ", " + self.tr("The mask remains in memory. Check file name, format and extension."), level=Qgis.Warning)
            return layer

    def mask_geometry(self):
        if not self.parameters.geometry:
            geom = QgsGeometry()
            return geom, QgsRectangle()

        geom = QgsGeometry(self.parameters.geometry)  # COPY !!

        if self.parameters.do_simplify:
            if hasattr(self.canvas, "mapSettings"):
                tol = (
                    self.parameters.simplify_tolerance
                    * self.canvas.mapSettings().mapUnitsPerPixel()
                )
            else:
                tol = (
                    self.parameters.simplify_tolerance
                    * self.canvas.mapRenderer().mapUnitsPerPixel()
                )

            if tol in list(self.simplified_geometries.keys()):
                geom, bbox = self.simplified_geometries[tol]
            else:
                if self.has_simplifier:
                    simplifier = QgsMapToPixelSimplifier(
                        QgsMapToPixelSimplifier.SimplifyGeometry, tol
                    )
                    geom = simplifier.simplify(geom)
                    if not geom.isGeosValid():
                        # make valid
                        geom = geom.buffer(0.0, 1)
                bbox = geom.boundingBox()
                self.simplified_geometries[tol] = (
                    QgsGeometry(geom),
                    QgsRectangle(bbox),
                )
        else:
            bbox = geom.boundingBox()

        return geom, bbox

    def in_mask(self, feature, srid=None):
        if feature is None:  # expression overview
            return False

        if self.layer is None:
            return False

        try:
            # layer is not None but destroyed ?
            self.layer.id()
        except:
            self.reset_mask_layer()
            return False

        # mask layer empty due to unloaded memlayersaver plugin > no filtering
        if self.layer.featureCount() == 0:
            return True

        mask_geom, bbox = self.mask_geometry()
        geom = QgsGeometry(feature.geometry())
        if not geom.isGeosValid():
            geom = geom.buffer(0.0, 1)

        if geom is None:
            return False

        if srid is not None and self.layer.crs().postgisSrid() != srid:
            src_crs = QgsCoordinateReferenceSystem(srid)
            dest_crs = self.layer.crs()
            xform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
            try:
                geom.transform(xform)

            except Exception as e:
                for m in e.args:
                    QgsMessageLog.logMessage("in_mask - {}".format(m), "Extensions")
                    # transformation error. Check layer projection.
                    pass

        if geom.type() == QgsWkbTypes.PolygonGeometry:
            if (
                self.parameters.polygon_mask_method == 2
                and not self.has_point_on_surface
            ):
                self.parameters.polygon_mask_method = 1

            if self.parameters.polygon_mask_method == 0:
                # this method can only work when no geometry simplification is involved
                return mask_geom.overlaps(geom) or mask_geom.contains(geom)
            elif self.parameters.polygon_mask_method == 1:
                # the fastest method, but with possible inaccuracies
                pt = geom.vertexAt(0)
                return bbox.contains(QgsPointXY(pt)) and mask_geom.contains(
                    geom.centroid()
                )
            elif self.parameters.polygon_mask_method == 2:
                # will always work
                pt = geom.vertexAt(0)
                return bbox.contains(QgsPointXY(pt)) and mask_geom.contains(
                    geom.pointOnSurface()
                )
            else:
                return False
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if self.parameters.line_mask_method == 0:
                return mask_geom.intersects(geom)
            elif self.parameters.line_mask_method == 1:
                return mask_geom.contains(geom)
            else:
                return False
        elif geom.type() == QgsWkbTypes.PointGeometry:
            return mask_geom.intersects(geom)
        else:
            return False

    def do_test(self):
        # This test is hard to run without a full QGIS app running
        # with renderer, canvas
        # a layer with labeling filter enabled must be the current layer
        import time

        parameters = [
            # simplify mask layer, simplify label layer, mask_method
            (False, False, 0),
            (True, True, 0),  # cannot be used, for reference only
            (False, False, 1),
            (False, False, 2),
            (True, False, 1),
            (True, False, 2),
            (False, True, 1),
            (False, True, 2),
            (True, True, 1),
            (True, True, 2),
        ]

        # (False, False, 0) 0.3265
        # (True, True, 0) 0.1790
        # (False, False, 1) 0.2520
        # (False, False, 2) 0.3000
        # (True, False, 1) 0.1950
        # (True, False, 2) 0.2345
        # (False, True, 1) 0.2195
        # (False, True, 2) 0.2315
        # (True, True, 1) 0.1550 <--
        # (True, True, 2) 0.1850 <--

        # layer with labels to filter
        layer = self.iface.activeLayer()

        class RenderCallback:
            # this class deals with asyncrhonous render signals
            def __init__(self, parent, params, layer):
                self.it = 0
                self.nRefresh = 20
                self.start = time.clock()
                self.parent = parent
                self.params = params
                self.param_it = 0
                self.layer = layer

                self.setup(0)
                self.parent.canvas.renderComplete.connect(self.update_render)
                self.parent.canvas.refresh()

            def setup(self, idx):
                simplify_mask, simplify_label, mask_method = self.params[idx]
                self.parent.parameters.do_simplify = simplify_mask
                self.parent.parameters.simplify_tolerance = 1.0

                m = self.layer.simplifyMethod()
                m.setSimplifyHints(
                    QgsVectorSimplifyMethod.SimplifyHints(1 if simplify_label else 0)
                )
                self.layer.setSimplifyMethod(m)

                self.parent.mask_method = mask_method

            def update_render(self, painter):
                self.it = self.it + 1
                if self.it < self.nRefresh:
                    self.parent.canvas.refresh()
                else:
                    end = time.clock()
                    print(
                        self.params[self.param_it],
                        "%.4f" % ((end - self.start) / self.nRefresh),
                    )
                    self.param_it += 1
                    if self.param_it < len(self.params):
                        self.setup(self.param_it)
                        self.it = 0
                        self.start = end
                        self.parent.canvas.refresh()
                    else:
                        print("end")
                        self.parent.canvas.renderComplete.disconnect(self.update_render)

        self.cb = RenderCallback(self, parameters, layer)
