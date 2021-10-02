from qgis.PyQt.QtCore import Qt, QUrl, QSettings, QDir
from qgis.PyQt import QtCore

from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from qgis.PyQt.QtGui import QDoubleValidator, QIntValidator, QDesktopServices, QPixmap

from qgis.core import (
    QgsVectorLayer,
    QgsMessageLog,
    QgsStyle,
    QgsProject,
    QgsVectorFileWriter,
    QgsRenderContext,
    QgsGeometry,
    QgsVectorSimplifyMethod,
)
from qgis.gui import QgsRendererPropertiesDialog
from qgis.utils import showPluginHelp

from mask.__about__ import DIR_PLUGIN_ROOT
from qgis.PyQt import uic
Ui_MainDialog, _ = uic.loadUiType(DIR_PLUGIN_ROOT / "ui/ui_plugin_mask.ui")

from mask.ui.layerlist import LayerListWidget
from mask.logic.mask_parameters import MaskParameters

from mask.logic import style_tools
import locale


def is_in_qgis_core(sym):
    import qgis.core

    return sym in dir(qgis.core)


class MainDialog(QDialog):

    applied = QtCore.pyqtSignal()

    def __init__(self, parameters, is_new):
        QDialog.__init__(self, None)

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)
        self.ui.layer_list = LayerListWidget(self.ui.labelingGroup)
        self.ui.labelingLayout.addWidget(self.ui.layer_list)

        self.ui.bufferUnits.setValidator(QDoubleValidator())
        self.ui.bufferSegments.setValidator(QIntValidator())
        self.ui.simplifyTolerance.setValidator(QDoubleValidator())

        self.parameters = parameters
        if self.parameters.file_format is None:
            self.parameters.file_format = "ESRI Shapefile"
        self.style = QgsStyle()

        # connect edit style
        self.ui.editStyleBtn.clicked.connect(self.on_style_edit)
        # connect file browser
        self.ui.browseBtn.clicked.connect(self.on_file_browse)
        # add a "save as defaults" button
        self.ui.saveDefaultsBtn = QPushButton(
            self.tr("Save as defaults"), self.ui.buttonBox
        )
        self.ui.buttonBox.addButton(
            self.ui.saveDefaultsBtn, QDialogButtonBox.ActionRole
        )
        self.ui.saveDefaultsBtn.clicked.connect(self.on_save_defaults)
        # add a "load defaults" button
        self.ui.loadDefaultsBtn = QPushButton(
            self.tr("Load defaults"), self.ui.buttonBox
        )
        self.ui.buttonBox.addButton(
            self.ui.loadDefaultsBtn, QDialogButtonBox.ActionRole
        )
        self.ui.loadDefaultsBtn.clicked.connect(self.load_defaults)
        # connect the "help" button
        self.ui.buttonBox.helpRequested.connect(lambda: showPluginHelp(filename="../doc/index"))

        self.ui.layer_list.ui.polygonOperatorCombo.currentIndexChanged[int].connect(
            self.on_polygon_operator_changed
        )

        # connect the "apply" button
        for btn in self.ui.buttonBox.buttons():
            if self.ui.buttonBox.buttonRole(btn) == QDialogButtonBox.ApplyRole:
                btn.clicked.connect(self.on_apply)
                break

        # save current style
        self.save_style_parameters = MaskParameters()
        self.update_parameters_from_style(self.save_style_parameters)
        self.update_parameters_from_style(self.parameters)

        self.is_new = is_new
        if self.is_new:
            self.setWindowTitle(self.tr("Create a mask"))
        else:
            self.setWindowTitle(self.tr("Update the current mask"))

    def on_polygon_operator_changed(self, idx):
        if idx == 0 and self.ui.simplifyGroup.isChecked():
            self.ui.simplifyGroup.setChecked(False)

    def update_style_from_parameters(self, parameters):
        try:
            style_tools.set_layer_symbology(self.parameters.layer, parameters.style)
            self.update_style_preview(self.parameters.layer)
        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(
                    "Mask error update_style_from_parameters - {}".format(m),
                    "Extensions",
                )

    def update_parameters_from_style(self, parameters):
        try:
            parameters.style = style_tools.get_layer_symbology(self.parameters.layer)
        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(
                    "Mask error update_parameters_from_style - {}".format(m),
                    "Extensions",
                )

    def update_ui_from_parameters(self, parameters):
        self.update_style_from_parameters(parameters)
        self.ui.bufferGroup.setChecked(parameters.do_buffer)
        self.ui.saveLayerGroup.setChecked(parameters.do_save_as)
        self.ui.bufferUnits.setText(locale.str(parameters.buffer_units))
        self.ui.bufferSegments.setText(str(parameters.buffer_segments))
        self.ui.formatLbl.setText(
            "" if parameters.file_format is None else parameters.file_format
        )
        self.ui.filePath.setText(parameters.file_path)
        self.ui.simplifyGroup.setChecked(parameters.do_simplify)
        self.ui.simplifyTolerance.setText(locale.str(parameters.simplify_tolerance))
        self.ui.layer_list.ui.polygonOperatorCombo.setCurrentIndex(
            parameters.polygon_mask_method
        )
        self.ui.layer_list.ui.lineOperatorCombo.setCurrentIndex(
            parameters.line_mask_method
        )
        self.ui.atlasInteraction.setChecked(parameters.do_atlas_interaction)

    def update_parameters_from_ui(self, parameters):
        self.update_parameters_from_style(parameters)
        parameters.do_buffer = self.ui.bufferGroup.isChecked()
        try:
            parameters.buffer_units = locale.atof(self.ui.bufferUnits.text() or "0.0")
        except:
            parameters.buffer_units = float(
                self.ui.bufferUnits.text().replace(",", ".") or "0.0"
            )

        parameters.buffer_segments = int(self.ui.bufferSegments.text() or 0)
        parameters.do_save_as = self.ui.saveLayerGroup.isChecked()
        parameters.file_format = self.parameters.file_format
        parameters.file_path = self.ui.filePath.text()
        parameters.do_simplify = self.ui.simplifyGroup.isChecked()
        try:
            parameters.simplify_tolerance = locale.atof(
                self.ui.simplifyTolerance.text() or "0.0"
            )
        except:
            parameters.simplify_tolerance = float(
                self.ui.simplifyTolerance.text().replace(",", ".") or "0.0"
            )

        parameters.polygon_mask_method = (
            self.ui.layer_list.ui.polygonOperatorCombo.currentIndex()
        )
        parameters.line_mask_method = (
            self.ui.layer_list.ui.lineOperatorCombo.currentIndex()
        )
        parameters.do_atlas_interaction = self.ui.atlasInteraction.isChecked()

    def load_defaults(self):
        settings = QSettings()

        mlayer = self.parameters.layer
        self.parameters = MaskParameters()
        defaults = settings.value("mask/defaults", None)
        if defaults is not None:
            self.parameters.unserialize(defaults)

        self.parameters.layer = mlayer
        self.update_ui_from_parameters(self.parameters)

    def on_save_defaults(self):
        settings = QSettings()

        parameters = MaskParameters()
        self.update_parameters_from_ui(parameters)
        defaults = parameters.serialize()
        settings.setValue("mask/defaults", defaults)

    def on_file_browse(self):
        settings = QSettings()

        # look for directory
        path = QgsProject.instance().homePath()
        if path == "":
            path = settings.value("mask/file_dir", "")
            if path == "":
                path = QDir.homePath()

        drivers = QgsVectorFileWriter.ogrDriverList()
        filterList = []
        filterMap = {}
        for driver in drivers:
            # grrr, driverMetadata is not really consistent
            if driver.driverName == "ESRI Shapefile":
                ext = "shp"
                glob = "*.shp"
            else:
                md = QgsVectorFileWriter.MetaData()
                if QgsVectorFileWriter.driverMetadata(driver.driverName, md):
                    ext = md.ext
                    glob = md.glob
                else:
                    continue

            fn = "%s (%s)" % (driver.longName, glob)
            filterMap[fn] = (driver.driverName, ext, glob)
            filterList += [fn]

        fileFilters = ";;".join(filterList)
        fd = QFileDialog(
            None,
            self.tr("Select a filename to save the mask layer to"),
            path,
            fileFilters,
        )
        save_format_name = self.parameters.file_format
        self.save_format = None
        for k, v in filterMap.items():
            if v[0] == save_format_name:
                self.save_format = v
                fd.selectNameFilter(k)
                break

        def on_filter_selected(ff):
            self.save_format = filterMap[ff]

        fd.filterSelected.connect(on_filter_selected)
        fd.setAcceptMode(QFileDialog.AcceptSave)
        r = fd.exec_()
        if r == 1:
            fn = fd.selectedFiles()[0]
            driver, ext, glob = self.save_format
            if not fn.endswith("." + ext):
                fn += "." + ext

            self.ui.filePath.setText(fn)
            self.ui.formatLbl.setText(self.save_format[0])
            self.parameters.file_format = self.save_format[0]
            self.parameters.file_path = fn

    def on_style_edit(self):
        # QgsRenderV2PropertiesDialog has a Cancel button that is not correctly plugged
        # rewrap the widget with a buttonbox
        dlg = QDialog(self)

        dlg.layout = QVBoxLayout(dlg)
        dlg.widget = QgsRendererPropertiesDialog(
            self.parameters.layer, self.style, True
        )
        dlg.widget.setLayout(dlg.layout)
        dlg.buttons = QDialogButtonBox(dlg)

        dlg.layout.addWidget(dlg.widget)
        dlg.layout.addWidget(dlg.buttons)

        dlg.buttons.setOrientation(Qt.Horizontal)
        dlg.buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        def on_style_edit_accept(d):
            # this will update the layer's style
            dlg.widget.onOK()
            dlg.accept()

        dlg.buttons.accepted.connect(lambda d=dlg: on_style_edit_accept(d))
        dlg.buttons.rejected.connect(dlg.reject)

        r = dlg.exec_()
        if r == 1:
            self.update_style_preview(self.parameters.layer)

    def update_style_preview(self, layer):
        syms = layer.renderer().symbols(QgsRenderContext())

        # only display the first symbol
        if len(syms) > 0:
            pix = QPixmap()
            pix.convertFromImage(syms[0].bigSymbolPreviewImage())
            self.ui.stylePreview.setPixmap(pix)

    def exec_(self):
        self.ui.layer_list.update_from_layers(self.is_new)

        if self.parameters.style is None:
            self.load_defaults()
        else:
            self.update_ui_from_parameters(self.parameters)

        # disable simplification if the simplifier is not available
        if not is_in_qgis_core("QgsMapToPixelSimplifier"):
            self.ui.simplifyGroup.setEnabled(False)
            self.parameters.do_simplify = False
        # disable pointOnSurface if not available
        if "pointOnSurface" not in dir(QgsGeometry):
            self.ui.layer_list.ui.polygonOperatorCombo.removeItem(2)
            if self.parameters.polygon_mask_method == 2:
                self.parameters.polygon_mask_method = 1

        try:
            self.update_style_preview(self.parameters.layer)
        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(m, "Extensions")

        return QDialog.exec_(self)

    def reject(self):
        # restore layer's style on cancel
        self.update_style_from_parameters(self.save_style_parameters)
        QDialog.reject(self)

    def accept(self):
        self.apply()
        QDialog.accept(self)

    def apply(self):
        # get data before closing
        self.update_parameters_from_ui(self.parameters)

        # update labeling from parameters
        self.ui.layer_list.update_labeling_from_list()

        if self.parameters.polygon_mask_method == 0:
            # test if some limited layers have simplification turned on
            limited = self.ui.layer_list.get_limited_layers()
            slayers = []
            for name, layer in QgsProject.instance().mapLayers().items():
                if not isinstance(layer, QgsVectorLayer):
                    continue
                if (
                    layer.id() in limited
                    and int(layer.simplifyMethod().simplifyHints()) > 0
                ):
                    # simplification is enabled
                    slayers.append(layer)

            if len(slayers) > 0:
                r = QMessageBox.question(
                    None,
                    self.tr("Warning"),
                    self.tr(
                        "Some layer have rendering simplification turned on, \
                    which is not compatible with the labeling filtering you choose. \
                    Force simplification disabling ?"
                    ),
                    buttons=QMessageBox.Yes | QMessageBox.No,
                )

                if r == QMessageBox.Yes:
                    for l in slayers:
                        m = layer.simplifyMethod()
                        m.setSimplifyHints(QgsVectorSimplifyMethod.SimplifyHints(0))
                        layer.setSimplifyMethod(m)

    def on_apply(self):
        self.apply()
        self.applied.emit()
