# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SpreadsheetLayersPluginDialog
                                 A QGIS plugin
 Load layers from MS Excel and OpenOffice spreadsheets
                             -------------------
        begin                : 2014-10-30
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Camptocamp
        email                : info@camptocamp.com
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
from builtins import str
from builtins import range

import os
import datetime
import re
from tempfile import gettempdir
from osgeo import ogr
from qgis.core import Qgis, QgsVectorDataProvider, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar
from qgis.PyQt import QtCore, QtGui, QtWidgets, uic

from SpreadsheetLayers.util.gdal_util import GDAL_COMPAT


class FieldsModel(QtCore.QAbstractListModel):
    '''FieldsModel provide a ListModel class to display fields in QComboBox.
    '''
    def __init__(self, fields, parent=None):
        super(FieldsModel, self).__init__(parent)
        self._fields = fields

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._fields)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        field = self._fields[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return field['name']
        if role == QtCore.Qt.EditRole:
            return field['src']


class OgrTableModel(QtGui.QStandardItemModel):
    '''OgrTableModel provide a TableModel class
    for displaying OGR layers data.

    OGR layer is read at creation or by setLayer().
    All data are stored in parent QtCore.QStandardItemModel object.
    No reference to any OGR related object is kept.
    '''
    def __init__(self, layer=None, fields=None, parent=None, maxRowCount=None):
        super(OgrTableModel, self).__init__(parent)
        self.maxRowCount = maxRowCount
        self.setLayer(layer)
        self.fields = fields

    def setLayer(self, layer):
        self.clear()
        if layer is None:
            return

        layerDefn = layer.GetLayerDefn()

        rows = min(layer.GetFeatureCount(), self.maxRowCount)
        columns = layerDefn.GetFieldCount()

        self.setRowCount(rows)
        self.setColumnCount(columns)

        # Headers
        for column in range(0, columns):
            fieldDefn = layerDefn.GetFieldDefn(column)
            fieldName = fieldDefn.GetNameRef()
            item = QtGui.QStandardItem(fieldName)
            self.setHorizontalHeaderItem(column, item)

        # Lines
        for row in range(0, rows):
            for column in range(0, columns):
                layer.SetNextByIndex(row)
                feature = layer.GetNextFeature()
                item = self.createItem(layerDefn, feature, column)
                self.setItem(row, column, item)

        # No header for column format line
        for column in range(0, columns):
            item = QtGui.QStandardItem("")
            self.setVerticalHeaderItem(rows, item)

    def createItem(self, layerDefn, feature, iField):
        fieldDefn = layerDefn.GetFieldDefn(iField)

        value = None
        if fieldDefn.GetType() == ogr.OFTDate:
            if feature.IsFieldSet(iField):
                value = datetime.date(*feature.GetFieldAsDateTime(iField)[:3])
            hAlign = QtCore.Qt.AlignCenter

        elif fieldDefn.GetType() == ogr.OFTInteger:
            if feature.IsFieldSet(iField):
                value = feature.GetFieldAsInteger(iField)
            hAlign = QtCore.Qt.AlignRight

        elif fieldDefn.GetType() == ogr.OFTReal:
            if feature.IsFieldSet(iField):
                value = feature.GetFieldAsDouble(iField)
            hAlign = QtCore.Qt.AlignRight

        elif fieldDefn.GetType() == ogr.OFTString:
            if feature.IsFieldSet(iField):
                value = feature.GetFieldAsString(iField)
            hAlign = QtCore.Qt.AlignLeft

        else:
            if feature.IsFieldSet(iField):
                value = feature.GetFieldAsString(iField)
            hAlign = QtCore.Qt.AlignLeft

        if value is None:
            item = QtGui.QStandardItem(u'NULL')
            item.setForeground(QtGui.QBrush(QtCore.Qt.gray))
            font = item.font()
            font.setItalic(True)
            item.setFont(font)
        else:
            item = QtGui.QStandardItem(str(value))
        item.setTextAlignment(hAlign | QtCore.Qt.AlignVCenter)
        return item


ogrFieldTypes = []
for fieldType in [
    ogr.OFTInteger,
    ogr.OFTIntegerList,
    ogr.OFTReal,
    ogr.OFTRealList,
    ogr.OFTString,
    ogr.OFTStringList,
    #ogr.OFTWideString,
    #ogr.OFTWideStringList,
    ogr.OFTBinary,
    ogr.OFTDate,
    ogr.OFTTime,
    ogr.OFTDateTime]:
    #ogr.OFTInteger64,
    #ogr.OFTInteger64List
    ogrFieldTypes.append((fieldType, ogr.GetFieldTypeName(fieldType)))


class OgrFieldTypeDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(OgrFieldTypeDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        for value, text in ogrFieldTypes:
            editor.addItem(text, value)
        editor.setAutoFillBackground(True)
        return editor

    def setEditorData(self, editor, index):
        if not editor:
            return
        type = index.model().fields[index.column()]['type']
        editor.setCurrentIndex(editor.findData(type))

    def setModelData(self, editor, model, index):
        if not editor:
            return
        type = editor.itemData(editor.currentIndex())
        model.fields[index.column()]['type'] = type


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'ui_SpreadsheetLayersDialog.ui'))


class SpreadsheetLayersDialog(QtWidgets.QDialog, FORM_CLASS):

    pluginKey = 'SpreadsheetLayers'
    sampleRowCount = 20

    def __init__(self, parent=None):
        """Constructor."""
        super(SpreadsheetLayersDialog, self).__init__(parent)
        self.setupUi(self)

        self.dataSource = None
        self.layer = None
        self.fields = None
        self.sampleDatasource = None
        self.ogrHeadersLabel.setText('')

        self.messageBar = QgsMessageBar(self)
        self.layout().insertWidget(0, self.messageBar)

        self.geometryBox.setChecked(False)
        self.sampleRefreshDisabled = False
        self.sampleView.setItemDelegate(OgrFieldTypeDelegate())

    def info(self, msg):
        self.messageBar.pushMessage(msg, Qgis.Info, 5)

    def warning(self, msg):
        self.messageBar.pushMessage(msg, Qgis.Warning, 5)

    def filePath(self):
        return self.filePathEdit.text()

    def setFilePath(self, path):
        self.filePathEdit.setText(path)

    @QtCore.pyqtSlot(name='on_filePathEdit_editingFinished')
    def on_filePathEdit_editingFinished(self):
        self.afterOpenFile()

    @QtCore.pyqtSlot(name='on_filePathButton_clicked')
    def on_filePathButton_clicked(self):
        settings = QtCore.QSettings()
        s, filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Choose a spreadsheet file to open"),
            settings.value(self.pluginKey + "/directory", "./"),
            self.tr("Spreadsheet files") + " (*.ods *.xls *.xlsx);;"
                + self.tr("GDAL Virtual Format") + " (*.vrt);;"
                + self.tr("All files") + " (* *.*)".format())
        if s == '':
            return
        settings.setValue(self.pluginKey + "/directory", os.path.dirname(s))
        self.filePathEdit.setText(s)

        self.afterOpenFile()

    def afterOpenFile(self):
        self.sampleRefreshDisabled = True

        self.openDataSource()
        self.updateSheetBox()
        self.readVrt()

        self.sampleRefreshDisabled = False
        self.updateSampleView()

    def layerName(self):
        return self.layerNameEdit.text()

    def setLayerName(self, name):
        self.layerNameEdit.setText(name)

    def closeDataSource(self):
        if self.dataSource is not None:
            self.dataSource = None
            self.updateSheetBox()

    def openDataSource(self):
        self.closeDataSource()

        filePath = self.filePath()
        self.finfo = QtCore.QFileInfo(filePath)
        if not self.finfo.exists():
            return

        dataSource = ogr.Open(filePath, 0)
        if dataSource is None:
            self.messageBar.pushMessage(u"Could not open {}".format(filePath),
                                        Qgis.Warning, 5)
        self.dataSource = dataSource

        if self.dataSource and self.dataSource.GetDriver().GetName() in ['XLS']:
            self.setEofDetection(True)
        else:
            self.setEofDetection(False)

    def closeSampleDatasource(self):
        if self.sampleDatasource is not None:
            self.sampleDatasource = None

    def openSampleDatasource(self):
        self.closeSampleDatasource()

        filePath = self.samplePath()
        finfo = QtCore.QFileInfo(filePath)
        if not finfo.exists():
            return False
        dataSource = ogr.Open(filePath, 0)
        if dataSource is None:
            self.messageBar.pushMessage(u"Could not open {}".format(filePath),
                                       Qgis.Warning, 5)
        self.sampleDatasource = dataSource

    def sheet(self):
        return self.sheetBox.currentText()

    def setSheet(self, sheetName):
        self.sheetBox.setCurrentIndex(self.sheetBox.findText(sheetName))

    def updateSheetBox(self):
        self.sheetBox.clear()
        dataSource = self.dataSource
        if dataSource is None:
            return

        for i in range(0, dataSource.GetLayerCount()):
            layer = dataSource.GetLayer(i)
            self.sheetBox.addItem(layer.GetName(), layer)

    @QtCore.pyqtSlot(int)
    def on_sheetBox_currentIndexChanged(self, index):
        if index is None:
            self.layer = None
        else:
            self.layer = self.sheetBox.itemData(index)
            self.setLayerName(u"{}-{}".format(self.finfo.completeBaseName(),
                                              self.sheetBox.itemText(index)))

        self.countNonEmptyRows()
        self.updateFields()
        self.updateFieldBoxes()
        self.updateSampleView()

    def linesToIgnore(self):
        return self.linesToIgnoreBox.value()

    def setLinesToIgnore(self, value):
        self.linesToIgnoreBox.setValue(value)

    @QtCore.pyqtSlot(int)
    def on_linesToIgnoreBox_valueChanged(self, value):
        self.updateFields()
        self.updateFieldBoxes()
        self.updateSampleView()

    def header(self):
        return self.headerBox.checkState() == QtCore.Qt.Checked

    def setHeader(self, value):
        self.headerBox.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)

    @QtCore.pyqtSlot(int)
    def on_headerBox_stateChanged(self, state):
        self.updateFields()
        self.updateFieldBoxes()
        self.updateSampleView()

    def offset(self):
        offset = self.linesToIgnore()
        if self.header():
            offset += 1
        return offset

    def setOffset(self, value):
        try:
            value = int(value)
        except:
            return False
        if self.header():
            value -= 1
        self.setLinesToIgnore(value)

    def limit(self):
        return self._non_empty_rows - self.offset()

    def eofDetection(self):
        return self.eofDetectionBox.checkState() == QtCore.Qt.Checked

    def setEofDetection(self, value):
        self.eofDetectionBox.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)

    @QtCore.pyqtSlot(int)
    def on_eofDetectionBox_stateChanged(self, state):
        self.countNonEmptyRows()
        self.updateSampleView()

    def countNonEmptyRows(self):
        if self.layer is None:
            return
        if self.eofDetection():
            self._non_empty_rows = 0

            layer = self.layer
            layerDefn = layer.GetLayerDefn()
            layer.SetNextByIndex(0)
            feature = layer.GetNextFeature()
            current_row = 1
            while feature is not None:
                values = []

                for iField in range(0, layerDefn.GetFieldCount()):
                    # values.append(feature.GetFieldAsString(iField))
                    if feature.IsFieldSet(iField):
                        self._non_empty_rows = current_row

                feature = layer.GetNextFeature()
                current_row += 1
        else:
            self._non_empty_rows = self.layer.GetFeatureCount()

    def sql(self):
        sql = (u'SELECT * FROM \'{}\''
               u' LIMIT {} OFFSET {}'
               ).format(self.sheet(),
                        self.limit(),
                        self.offset())
        return sql

    def updateGeometry(self):
        if GDAL_COMPAT or self.offset() == 0:
            self.geometryBox.setEnabled(True)
            self.geometryBox.setToolTip('')
        else:
            self.geometryBox.setEnabled(False)
            msg = self.tr(u"Used GDAL version doesn't support VRT layers with sqlite dialect"
                          u" mixed with PointFromColumn functionality.\n"
                          u"For more informations, consult the plugin documentation.")
            self.geometryBox.setToolTip(msg)

    def geometry(self):
        return (self.geometryBox.isEnabled()
                and self.geometryBox.isChecked())

    def xField(self):
        index = self.xFieldBox.currentIndex()
        if index == -1:
            return ''
        return self.xFieldBox.itemData(index, QtCore.Qt.EditRole)

    def setXField(self, fieldName):
        self.xFieldBox.setCurrentIndex(self.xFieldBox.findData(fieldName, QtCore.Qt.EditRole))

    def yField(self):
        index = self.yFieldBox.currentIndex()
        if index == -1:
            return ''
        return self.yFieldBox.itemData(index, QtCore.Qt.EditRole)

    def setYField(self, fieldName):
        self.yFieldBox.setCurrentIndex(self.yFieldBox.findData(fieldName, QtCore.Qt.EditRole))

    def updateFieldBoxes(self):
        if self.offset() > 0:
            # return
            pass

        if self.layer is None:
            self.xFieldBox.clear()
            self.yFieldBox.clear()
            return

        model = FieldsModel(self.fields)

        xField = self.xField()
        yField = self.yField()

        self.xFieldBox.setModel(model)
        self.yFieldBox.setModel(model)

        self.setXField(xField)
        self.setYField(yField)

        if self.xField() != '' and self.yField() != '':
            return

        self.tryFields("longitude", "latitude")
        self.tryFields("lon", "lat")
        self.tryFields("x", "y")

    def tryFields(self, xName, yName):
        if self.xField() == '':
            for i in range(0, self.xFieldBox.count()):
                xField = self.xFieldBox.itemText(i)
                if xField.lower().find(xName.lower()) != -1:
                    self.xFieldBox.setCurrentIndex(i)
                    break;

        if self.yField() == '':
            for i in range(0, self.yFieldBox.count()):
                yField = self.yFieldBox.itemText(i)
                if yField.lower().find(yName.lower()) != -1:
                    self.yFieldBox.setCurrentIndex(i)
                    break;

    def showGeometryFields(self):
        return self.showGeometryFieldsBox.isChecked()

    def crs(self):
        return self.crsWidget.crs().authid()

    def setCrs(self, authid):
        crs = QgsCoordinateReferenceSystem()
        crs.createFromString(authid)
        self.crsWidget.setCrs(crs)

    def updateSampleView(self):
        if self.sampleRefreshDisabled:
            return

        self.updateGeometry()

        if self.layer is not None:
            self.writeSampleVrt()
            self.openSampleDatasource()

        layer = None
        dataSource = self.sampleDatasource
        if dataSource is not None:
            for i in range(0, dataSource.GetLayerCount()):
                layer = dataSource.GetLayer(i)

        if layer is None:
            self.sampleView.setModel(None)
            return

        self.sampleView.reset()
        model = OgrTableModel(layer,
                              self.fields,
                              parent=self,
                              maxRowCount=self.sampleRowCount)
        self.sampleView.setModel(model)

        # Open persistent editor on last line (column format)
        for column in range(0, model.columnCount()):
            self.sampleView.openPersistentEditor(model.index(model.rowCount()-1, column))
        # Restore rows initial order
        vheader = self.sampleView.verticalHeader()
        for row in range(0, model.rowCount()):
            position = vheader.sectionPosition(row)
            if position != row:
                vheader.moveSection(position, row)
        # Move column format line at first
        vheader.moveSection(model.rowCount()-1, 0)


    def validate(self):
        try:
            if self.dataSource is None:
                raise ValueError(self.tr("Please select an input file"))

            if self.layer is None:
                raise ValueError(self.tr("Please select a sheet"))

            if self.xField == '':
                raise ValueError(self.tr("Please select an x field"))

            if self.yField == '':
                raise ValueError(self.tr("Please select an y field"))

        except ValueError as e:
            self.messageBar.pushMessage(str(e), Qgis.Warning, 5)
            return False

        return True

    def vrtPath(self):
        return u'{}.{}.vrt'.format(self.filePath(), self.sheet())

    def samplePath(self):
        filename = u'{}.tmp.vrt'.format(os.path.basename(self.filePath()))
        return os.path.join(gettempdir(), filename)

    def readVrt(self):
        if self.dataSource is None:
            return False

        vrtPath = self.vrtPath()
        if not os.path.exists(vrtPath):
            return False

        file = QtCore.QFile(vrtPath)
        if not file.open(QtCore.QIODevice.ReadOnly | QtCore. QIODevice.Text):
            self.warning(u"Impossible to open VRT file {}".format(vrtPath))
            return False

        self.geometryBox.setChecked(False)

        try:
            self.readVrtStream(file)
        except Exception:
            self.warning("An error occurs during existing VRT file loading")
            return False

        finally:
            file.close()

        # self.info("Existing VRT file has been loaded")
        return True

    def readVrtStream(self, file):
        stream = QtCore.QXmlStreamReader(file)

        stream.readNextStartElement()
        if stream.name() == "OGRVRTDataSource":

            stream.readNextStartElement()
            if stream.name() == "OGRVRTLayer":
                self.setLayerName(stream.attributes().value("name"))

                while stream.readNext() != QtCore.QXmlStreamReader.EndDocument:
                    if stream.isComment():
                        text = stream.text()
                        pattern = re.compile(r"Header=(\w+)")
                        match = pattern.search(text)
                        if match:
                            self.setHeader(eval(match.group(1)))

                    if stream.isStartElement():
                        if stream.name() == "SrcDataSource":
                            # do nothing : datasource should be already set
                            pass

                        elif stream.name() == "SrcLayer":
                            text = stream.readElementText()
                            self.setSheet(text)
                            self.setOffset(0)

                        elif stream.name() == "SrcSql":
                            text = stream.readElementText()

                            pattern = re.compile(r"FROM '(.+)'")
                            match = pattern.search(text)
                            if match:
                                self.setSheet(match.group(1))

                            pattern = re.compile(r'OFFSET (\d+)')
                            match = pattern.search(text)
                            if match:
                                self.setOffset(int(match.group(1)))

                        elif stream.name() == "GeometryType":
                            self.geometryBox.setChecked(True)

                        elif stream.name() == "LayerSRS":
                            text = stream.readElementText()
                            self.setCrs(text)

                        elif stream.name() == "GeometryField":
                            self.setXField(stream.attributes().value("x"))
                            self.setYField(stream.attributes().value("y"))

                        if not stream.isEndElement():
                            stream.skipCurrentElement()

            stream.skipCurrentElement()

        stream.skipCurrentElement()

    def updateFields(self):
        if self.layer is None:
            self.fields = []
            return

        # Select header line
        if self.header() or self.offset() >= 1:
            self.layer.SetNextByIndex(self.offset() - 1)
            feature = self.layer.GetNextFeature()

        fields = []
        layerDefn = self.layer.GetLayerDefn()
        for iField in range(0, layerDefn.GetFieldCount()):
            fieldDefn = layerDefn.GetFieldDefn(iField)
            src = fieldDefn.GetNameRef()
            name = src
            if self.header() or self.offset() >= 1:
                name = feature.GetFieldAsString(iField) or name
            fields.append({'src': src,
                           'name': name,
                           'type': fieldDefn.GetType()
                           })
        self.fields = fields

    def prepareVrt(self, sample=False, without_fields=False):
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)

        stream = QtCore.QXmlStreamWriter(buffer)
        stream.setAutoFormatting(True)
        stream.writeStartDocument()
        stream.writeStartElement("OGRVRTDataSource")

        stream.writeStartElement("OGRVRTLayer")
        stream.writeAttribute("name", self.layerName())

        stream.writeStartElement("SrcDataSource")
        if sample:
            stream.writeCharacters(self.filePath())
        else:
            stream.writeAttribute("relativeToVRT", "1")
            stream.writeCharacters(os.path.basename(self.filePath()))
        stream.writeEndElement()

        stream.writeComment('Header={}'.format(self.header()))

        if (self.offset() > 0
            or self._non_empty_rows != self.layer.GetFeatureCount()
        ):
            stream.writeStartElement("SrcSql")
            stream.writeAttribute("dialect", "sqlite")
            stream.writeCharacters(self.sql())
            stream.writeEndElement()
        else:
            stream.writeStartElement("SrcLayer")
            stream.writeCharacters(self.sheet())
            stream.writeEndElement()

        if not without_fields:
            for field in self.fields:
                if (self.geometry() and not sample):
                    if field['src'] in (self.xField(), self.yField()):
                        if not self.showGeometryFields():
                            continue
                stream.writeStartElement("Field")
                stream.writeAttribute("name", field['name'])
                stream.writeAttribute("src", field['src'])
                stream.writeAttribute("type", ogr.GetFieldTypeName(field['type']))
                stream.writeEndElement()

        if (self.geometry() and not sample):
            stream.writeStartElement("GeometryType")
            stream.writeCharacters("wkbPoint")
            stream.writeEndElement()

            if self.crs():
                stream.writeStartElement("LayerSRS")
                stream.writeCharacters(self.crs())
                stream.writeEndElement()

            stream.writeStartElement("GeometryField")
            stream.writeAttribute("encoding", "PointFromColumns")
            stream.writeAttribute("x", self.xField())
            stream.writeAttribute("y", self.yField())
            stream.writeEndElement()

        stream.writeEndElement()  # OGRVRTLayer
        stream.writeEndElement()  # OGRVRTDataSource
        stream.writeEndDocument()

        buffer.reset()
        content = buffer.readAll()
        buffer.close

        return content

    def writeVrt(self):
        content = self.prepareVrt()

        vrtPath = self.vrtPath()
        file = QtCore.QFile(vrtPath)
        if file.exists():
            if file.open(QtCore.QIODevice.ReadOnly | QtCore. QIODevice.Text):
                oldContent = file.readAll()
                file.close()
                if content == oldContent:
                    return True

            msgBox = QtWidgets.QMessageBox()
            msgBox.setText(u"The file {} already exist.".format(vrtPath))
            msgBox.setInformativeText(u"Do you want to overwrite ?");
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.Cancel:
                return False
            QtCore.QFile.remove(vrtPath)

        if not file.open(QtCore.QIODevice.ReadWrite | QtCore. QIODevice.Text):
            self.warning(u"Impossible to open VRT file {}".format(vrtPath))
            return False

        file.write(content)
        file.close()
        return True

    def writeSampleVrt(self, without_fields=False):
        content = self.prepareVrt(sample=True,
                                  without_fields=without_fields)

        vrtPath = self.samplePath()
        file = QtCore.QFile(vrtPath)
        if file.exists():
            QtCore.QFile.remove(vrtPath)

        if not file.open(QtCore.QIODevice.ReadWrite | QtCore. QIODevice.Text):
            self.warning(u"Impossible to open VRT file {}".format(vrtPath))
            return False

        file.write(content)
        file.close()
        return True

    def accept(self, *args, **kwargs):
        if not self.validate():
            return False

        if not self.writeVrt():
            return False

        return super(SpreadsheetLayersDialog, self).accept(*args, **kwargs)

    @QtCore.pyqtSlot()
    def on_helpButton_clicked(self):
        html_path = os.path.join(os.path.dirname(__file__),
                                 "..", "help", "build", "html")
        user_locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(html_path, user_locale)
        if not os.path.exists(locale_path):
            locale_path = os.path.join(html_path, 'en')
        path = os.path.join(locale_path, "index.html")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))
