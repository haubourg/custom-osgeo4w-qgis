#! python3  # noqa: E265

"""
/***************************************************************************
 redLayer
                                 A QGIS plugin
 quick georeferenced sketches and annotation
                              -------------------
        begin                : 2015-03-10
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Enrico Ferreguti
        email                : enricofer@gmail.com
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

# standard library
import logging
import math
from pathlib import Path
from os import path

# PyQGIS
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsMessageLog,
    QgsPoint,
    QgsProject,
    QgsRectangle,
    QgsSettings,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem
)
from qgis.gui import QgsColorDialog, QgsMapTool, QgsRubberBand
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QFile,
    QFileInfo,
    Qt,
    QTranslator,
    QVariant,
)
from qgis.PyQt.QtGui import QColor, QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMenu
from qgis.utils import iface

# project package
from .note_class_dialog import sketchNoteDialog

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################

class redLayer(QgsMapTool):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = path.dirname(__file__)
        # initialize locale
        locale = QgsSettings().value('locale/userLocale')[0:2]
        locale_path = path.join(
            self.plugin_dir,
            'i18n',
            'redLayer_{}.qm'.format(locale)
        )

        if path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr('&Red Layer')
        self.toolbar = self.iface.addToolBar('redLayer')
        self.toolbar.setObjectName('redLayer')
        QgsMapTool.__init__(self, self.canvas)

    @staticmethod
    def log(
        message: str,
        application: str = "Red Layer",
        log_level: int = 0,
        push: bool = False,
    ):
        """Send messages to QGIS messages windows and to the user as a message bar. \
        Plugin name is used as title.

        :param message: message to display
        :type message: str
        :param application: name of the application sending the message, defaults to "Red Layer"
        :type application: str, optional
        :param log_level: message level. Possible values: 0 (info), 1 (warning), \
            2 (critical), 3 (success), 4 (none - grey). Defaults to 0 (info)
        :type log_level: int, optional
        :param push: also display the message in the QGIS message bar in addition to the log, defaults to False
        :type push: bool, optional

        :Example:

        . code-block:: python

                self.log(message="Plugin loaded - INFO", log_level=0, push=1)
                self.log(message="Plugin loaded - WARNING", log_level=1, push=1)
                self.log(message="Plugin loaded - ERROR", log_level=2, push=1)
                self.log(message="Plugin loaded - SUCCESS", log_level=3, push=1)
                self.log(message="Plugin loaded - TEST", log_level=4, push=1)
        """
        # send it to QGIS messages panel
        QgsMessageLog.logMessage(
            message=message, tag=application, notifyUser=push, level=log_level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push:
            iface.messageBar().pushMessage(
                title=application, text=message, level=log_level, duration=(log_level+1)*3
            )

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('redLayer', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        object_name=None
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :param object_name: Optional name to identify objects during customization
        :type object_name: str

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if callback:
            action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        if object_name is not None:
            action.setObjectName(object_name)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.sketchButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'sketch.svg'),
            text=self.tr('Sketch on map'),
            callback=self.sketchAction,
            parent=self.iface.mainWindow(),
            object_name='mSketchAction')
        self.penButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'pen.svg'),
            text=self.tr('Draw line on map'),
            callback=self.penAction,
            parent=self.iface.mainWindow(),
            object_name='mPenAction')
        self.canvasButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'canvas.svg'),
            text=self.tr('Color and width canvas'),
            callback=None,
            parent=self.iface.mainWindow())
        self.eraseButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'erase.svg'),
            text=self.tr('Erase sketches'),
            callback=self.eraseAction,
            parent=self.iface.mainWindow(),
            object_name='mEraseAction')
        self.removeButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'remove.svg'),
            text=self.tr('Remove all sketches'),
            callback=self.removeSketchesAction,
            parent=self.iface.mainWindow(),
            object_name='mRemoveAllSketches')
        self.noteButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'note.svg'),
            text=self.tr('Add text annotations to sketches'),
            callback=None,
            parent=self.iface.mainWindow(),
            object_name='mAddTextAnnotations')
        self.convertButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'toLayer.svg'),
            text=self.tr('Convert annotations to Memory Layer'),
            callback=self.toMemoryLayerAction,
            parent=self.iface.mainWindow(),
            object_name='mConvertAnnotationsToMemoryLayer')
        self.saveButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'inbox.svg'),
            text=self.tr('Save sketches to file'),
            callback=self.saveAction,
            parent=self.iface.mainWindow(),
            object_name='mSaveSketchesToFile')
        self.loadButton = self.add_action(
            path.join(self.plugin_dir, 'icons', 'outbox.svg'),
            text=self.tr('Load sketches from file'),
            callback=self.loadAction,
            parent=self.iface.mainWindow(),
            object_name='mLoadSketchesFromFile')
        self.canvasButton.setMenu(self.canvasMenu())
        self.noteButton.setCheckable(True)
        self.penButton.setCheckable(True)
        self.sketchButton.setCheckable(True)
        self.eraseButton.setCheckable(True)
        self.geoSketches = []
        self.dumLayer = QgsVectorLayer("Point?crs=EPSG:4326", "temporary_points", "memory")
        self.pressed = None
        self.previousPoint = None
        self.previousMoved = None
        self.gestures = 0
        self.points = 0
        self.currentColor = QColor("#aa0000")
        self.currentWidth = 5
        self.annotation = sketchNoteDialog(self.iface)
        self.annotatatedSketch = None
        self.sketchEnabled(None)
        self.iface.projectRead.connect(self.projectReadAction)
        self.iface.newProjectCreated.connect(self.newProjectCreatedAction)
        QgsProject.instance().legendLayersAdded.connect(self.notSavedProjectAction)

    def canvasMenu(self):
        contextMenu = QMenu()
        contextMenu.setObjectName('mColorAndWidth')
        self.colorPaletteAction = contextMenu.addAction(QIcon(path.join(self.plugin_dir, "icons", "colorPalette.png")), self.tr("color palette"))
        self.colorPaletteAction.setObjectName('mColorPalette')
        self.colorPaletteAction.triggered.connect(self.colorPaletteFunc)
        self.width2Action = contextMenu.addAction(QIcon(path.join(self.plugin_dir, "icons", "width2.png")), "2 pixels")
        self.width2Action.setObjectName('mWidth2size')
        self.width2Action.triggered.connect(self.width2Func)
        self.width4Action = contextMenu.addAction(QIcon(path.join(self.plugin_dir, "icons", "width4.png")), "4 pixels")
        self.width4Action.setObjectName('mWidth4size')
        self.width4Action.triggered.connect(self.width4Func)
        self.width8Action = contextMenu.addAction(QIcon(path.join(self.plugin_dir, "icons", "width8.png")), "8 pixels")
        self.width8Action.setObjectName('mWidth8size')
        self.width8Action.triggered.connect(self.width8Func)
        self.width16Action = contextMenu.addAction(QIcon(path.join(self.plugin_dir, "icons", "width16.png")), "16 pixels")
        self.width16Action.setObjectName('mWidth16size')
        self.width16Action.triggered.connect(self.width16Func)
        return contextMenu

    def sketchEnabled(self, enabled):
        self.enabled = enabled
        if enabled:
            self.sketchButton.setEnabled(True)
            self.penButton.setEnabled(True)
            self.canvasButton.setEnabled(True)
            self.eraseButton.setEnabled(True)
            self.removeButton.setEnabled(True)
            self.noteButton.setEnabled(True)
            self.convertButton.setEnabled(True)
            self.loadButton.setEnabled(True)
            self.saveButton.setEnabled(True)
        else:
            self.sketchButton.setDisabled(True)
            self.penButton.setDisabled(True)
            self.canvasButton.setDisabled(True)
            self.eraseButton.setDisabled(True)
            self.removeButton.setDisabled(True)
            self.noteButton.setDisabled(True)
            self.convertButton.setDisabled(True)
            self.loadButton.setDisabled(True)
            self.saveButton.setDisabled(True)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.removeSketchesAction()
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&Red Layer'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def sketchAction(self):
        """Run method that performs all the real work"""
        gsvMessage = "Click on map to draw geo sketches"
        self.iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.canvas.setMapTool(self)
        self.canvasAction = "sketch"

    def penAction(self):
        gsvMessage = "Click on map and drag to draw a line"
        self.iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.canvas.setMapTool(self)
        self.canvasAction = "pen"

    def canvasAction(self):
        pass

    def colorPaletteFunc(self):
        self.currentColor = QgsColorDialog.getColor(self.currentColor, None)

    def width2Func(self):
        self.currentWidth = 2

    def width4Func(self):
        self.currentWidth = 4

    def width8Func(self):
        self.currentWidth = 8

    def width16Func(self):
        self.currentWidth = 16

    def eraseAction(self):
        gsvMessage = "Click on map to erase geo sketches"
        self.iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.canvas.setMapTool(self)
        self.canvasAction = "erase"

    def exportAction(self):
        pass

    def loadAction(self):
        self.loadSketches(userFile=True)

    def saveAction(self):
        self.saveSketches(userFile=True)

    def removeSketchesAction(self):
        for sketch in self.geoSketches:
            sketch[2].reset()
            if sketch[3]:
                try:
                    self.iface.mapCanvas().scene().removeItem(sketch[3])
                    del(sketch[3])
                except Exception as err:
                    self.log(message=self.tr("Remove sketches failed."), log_level=1)
                    logger.error(err)
        self.removeAllAnnotations()
        self.geoSketches = []
        self.gestures = 0
        self.annotatatedSketch = None

    def ex_activate(self):
        if self.canvasAction == "sketch":
            self.sketchButton.setChecked(True)
        if self.canvasAction == "pen":
            self.penButton.setChecked(True)

    def deactivate(self):
        if self.canvasAction == "sketch":
            self.sketchButton.setChecked(False)
            self.points = 0
        if self.canvasAction == "pen":
            self.penButton.setChecked(False)
            self.previousPoint = None
            self.previousMoved = None
            self.gestures += 1
            self.points = 0
        if self.canvasAction == "erase":
            self.eraseButton.setChecked(False)

    def canvasPressEvent(self, event):
        # Press event handler inherited from QgsMapTool
        if event.button() == Qt.RightButton:
            if self.noteButton.isChecked():
                midIdx = -int(self.points/2)
                if midIdx == 0:
                    midIdx = -1
                annotation = sketchNoteDialog.newPoint(self.iface, self.geoSketches[midIdx][2].asGeometry())
                if annotation:
                    self.geoSketches[-1][3] = annotation
                    self.geoSketches[-1][4] = annotation.document().toPlainText()
                self.annotatatedSketch = True
            self.gestures += 1
            self.points = 0
            self.penAction()
            self.previousPoint = None
            self.previousMoved = None
            self.movedPoint = None
            self.pressed = None
            self.dragged = None
        else:
            self.pressed = True
            self.dragged = None
            self.movedPoint = None
            self.px = event.pos().x()
            self.py = event.pos().y()
            self.pressedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(self.px, self.py)
            if self.canvasAction == "sketch":
                self.points = 0
            if self.canvasAction == "pen":
                self.snapSys = self.iface.mapCanvas().snappingUtils()
                snappedPoint = self.snapSys.snapToMap(self.pressedPoint)
                if snappedPoint.isValid():
                    self.pressedPoint = snappedPoint.point()
                self.sketch = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
                self.sketch.setWidth(self.currentWidth)
                self.sketch.setColor(self.currentColor)
                self.sketch.addPoint(self.pressedPoint)

    def canvasMoveEvent(self, event):
        # Moved event handler inherited from QgsMapTool needed to highlight the direction that is giving by the user
        if self.pressed:
            x = event.pos().x()
            y = event.pos().y()
            self.movedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            if self.canvasAction == "sketch":
                if abs(x-self.px) > 3 or abs(y-self.py) > 3:
                    sketch = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
                    sketch.setWidth(self.currentWidth)
                    sketch.setColor(self.currentColor)
                    sketch.addPoint(self.pressedPoint)
                    sketch.addPoint(self.movedPoint)
                    self.pressedPoint = self.movedPoint
                    self.points += 1
                    self.geoSketches.append([self.currentColor.name(), str(self.currentWidth), sketch, None, "", self.gestures])
                    self.px = x
                    self.py = y
            if self.canvasAction == "pen":
                if not QgsGeometry.fromPointXY(self.movedPoint).equals(QgsGeometry.fromPointXY(self.pressedPoint)):
                    self.dragged = True
                    self.snapSys = self.iface.mapCanvas().snappingUtils()
                    snappedPoint = self.snapSys.snapToMap(self.movedPoint)
                    if snappedPoint.isValid():
                        self.movedPoint = snappedPoint.point()
                    self.sketch.reset()
                    if self.previousPoint:
                        self.sketch.addPoint(self.previousPoint)
                    else:
                        self.sketch.addPoint(self.pressedPoint)
                    self.sketch.addPoint(self.movedPoint)
                    self.iface.mainWindow().statusBar().showMessage("Sketch lenght: %s" % math.sqrt(self.pressedPoint.sqrDist(self.movedPoint)))
                else:
                    self.dragged = None

            if self.canvasAction == "erase":
                cursor = QgsRectangle(self.canvas.getCoordinateTransform().toMapCoordinates(x-7,y-7), self.canvas.getCoordinateTransform().toMapCoordinates(x+7,y+7))
                for sketch in self.geoSketches:
                    if sketch[2].asGeometry() and sketch[2].asGeometry().boundingBox().intersects(cursor):
                        sketch[2].reset()
                        if sketch[3]:
                            try:
                                self.iface.mapCanvas().scene().removeItem(sketch[3])
                            except Exception as err:
                                self.log(message=self.tr("Erase sketch failed."), log_level=1)
                                logger.error(err)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        self.pressed = None
        QgsProject.instance().setDirty(True)
        if self.canvasAction == "pen":
            if not self.dragged:
                if self.previousPoint:
                    self.sketch.addPoint(self.previousPoint)
                    self.sketch.addPoint(self.pressedPoint)
                    self.previousPoint = self.pressedPoint
                else:
                    self.previousPoint = self.pressedPoint
                    return
            elif self.previousMoved:
                self.previousMoved = None
                self.sketch.addPoint(self.previousPoint)
                self.sketch.addPoint(self.movedPoint)
                self.previousPoint = self.movedPoint
            else:
                self.previousPoint = self.movedPoint
                self.previousMoved = True
            self.geoSketches.append([self.currentColor.name(), str(self.currentWidth), self.sketch, None, "", self.gestures])
            self.points += 1

        if self.canvasAction == "sketch" and self.noteButton.isChecked():
            if self.points > 0:
                midIdx = -int(self.points/2)
                annotation = sketchNoteDialog.newPoint(self.iface, self.geoSketches[midIdx][2].asGeometry())
                if annotation:
                    self.geoSketches[midIdx][3] = annotation
                    self.geoSketches[midIdx][4] = annotation.annotation().document().toPlainText()
                self.annotatatedSketch = True
                self.gestures += 1

    def notSavedProjectAction(self):
        self.sketchEnabled(True)
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.notSavedProjectAction)
        except Exception as err:
            self.log(message=self.tr("Remove unsaved action failed."), log_level=1)
            logger.error(err)

    def newProjectCreatedAction(self):
        # remove current sketches
        try:
            QgsProject.instance().legendLayersAdded.connect(self.notSavedProjectAction)
        except Exception as err:
            self.log(message=self.tr("Remove current sketches failed."), log_level=1)
            logger.error(err)
        self.removeSketchesAction()
        self.sketchEnabled(None)

    def projectReadAction(self):
        # remove current sketches
        try:
            QgsProject.instance().layerLoaded.disconnect(self.notSavedProjectAction)
        except Exception as err:
            self.log(message=self.tr("Remove current sketches failed."), log_level=1)
            logger.error(err)

        try:
            self.removeSketchesAction()
            # connect to signal to save sketches along with project file
            QgsProject.instance().projectSaved.connect(self.afterSaveProjectAction)
            QgsProject.instance().writeProject.connect(self.beforeSaveProjectAction)
            self.projectFileInfo = QFileInfo(QgsProject.instance().fileName())
            self.sketchFileInfo = QFileInfo(path.join(self.projectFileInfo.path(), self.projectFileInfo.baseName()+'.sketch'))
            # load project.sketch if file exists
            self.loadSketches()
            self.sketchEnabled(True)
        except Exception as err:
            self.log(message=self.tr("Error connecting to project signals."), log_level=1)
            logger.error("Error connecting to project signals: {}".format(err))

    def beforeSaveProjectAction(self, domDoc):
        # method to expunge redlayer annotation from annotation ready to to save
        if self.annotatatedSketch:
            annotationStrings = []
            for sketch in self.geoSketches:
                if sketch[4] != "":
                    annotationStrings.append(sketch[4])
            nodes = domDoc.elementsByTagName("TextAnnotationItem")
            for i in range(0, nodes.count()):
                node = nodes.at(i)
                annotationDocumentNode = node.attributes().namedItem("document")
                annotationDocument = QTextDocument()
                annotationDocument.setHtml(annotationDocumentNode.nodeValue())
                if annotationDocument.toPlainText() in annotationStrings:  # erase only redlayer annotations
                    parent = node.parentNode()
                    parent.removeChild(node)

    def afterSaveProjectAction(self):
        # method used for saving sketches file along with project file
        self.projectFileInfo = QFileInfo(QgsProject.instance().fileName())
        self.sketchFileInfo = QFileInfo(path.join(self.projectFileInfo.path(), self.projectFileInfo.baseName() +'.sketch'))
        self.saveSketches()

    def saveSketches(self, userFile=None):
        if self.geoSketches != []:
            if userFile:
                workDir = QgsProject.instance().readPath("./")

                # use Qt custom FileDialog to be more consistent with QGIS ui
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog

                # assk user where he wants to save his annotations
                sketch_filepath, sketch_suffix_filter = QFileDialog().getSaveFileName(
                    parent=None,
                    caption=self.tr("Save RedLayer sketches"),
                    directory=workDir,
                    filter="All Files (*);;Annotations (*.sketch)",
                    initialFilter="Annotations (*.sketch)",
                    options=options,
                )

                # check user has entered something
                if sketch_filepath:
                    out_sketch_path = Path(sketch_filepath)
                    if out_sketch_path.suffix != ".sketch":
                        out_sketch_path = Path(str(out_sketch_path) + ".sketch")
                    self.log(
                        message=self.tr("Saving sketches to {}".format(out_sketch_path.resolve())),
                        log_level=2
                    )
                else:
                    self.log(message=self.tr("No file selected"), log_level=0)
                    return
            else:
                out_sketch_path = self.sketchFileInfo.absoluteFilePath()

            # write annotations into the file in a context manager
            with open(out_sketch_path, mode="w", encoding="UTF8") as f:
                f.write("srs|"+QgsProject.instance().crs().toProj4()+'\n')
                for sketch in self.geoSketches:
                    if sketch[2].asGeometry():
                        try:
                            note = sketch[3].annotation().document().toPlainText().replace("\n", "%%N%%")
                        except Exception as err:
                            self.log(message=self.tr("Error connecting to project signals."), log_level=1)
                            logger.error(err)
                            note = ""
                        f.write(sketch[0]+'|'+sketch[1]+'|'+sketch[2].asGeometry().asWkt() + "|" + note + "|"+str(sketch[5])+'\n')
        else:
            if self.sketchFileInfo.exists():
                sketchFile = QFile(self.sketchFileInfo.absoluteFilePath())
                if sketchFile:
                    sketchFile.remove()

    def removeAllAnnotations(self):
        # erase all annotation to prevent saving them along with project file
        annotationsList = self.iface.mapCanvas().annotationItems()
        for item in annotationsList:
            try:
                self.iface.mapCanvas().scene().removeItem(item)
                del item
            except Exception as err:
                self.log(message=self.tr("Remove all annotations failed."), log_level=1)
                logger.error(err)

    def recoverAllAnnotations(self):
        for sketch in self.geoSketches:
            if sketch[4] != "":
                sketch[3] = sketchNoteDialog.newPoint(self.iface, sketch[2].asGeometry(), txt=sketch[4])
                self.annotatatedSketch = True

    def loadSketches(self, userFile=None):
        self.geoSketches = []
        self.annotatatedSketch = None
        if userFile:
            workDir = QgsProject.instance().readPath("./")
            fileNameInfo = QFileInfo(QFileDialog.getOpenFileName(
                None,
                "Open RedLayer sketches file",
                workDir,
                "*.sketch")[0]
            )
        else:
            fileNameInfo = self.sketchFileInfo
        if fileNameInfo.exists():
            infile = open(fileNameInfo.filePath(), 'r')
            canvas = self.iface.mapCanvas()
            srs = canvas.mapSettings().destinationCrs()
            dumLayer = QgsVectorLayer("Line?crs="+str(srs.authid()), "temporary_lines", "memory")
            self.geoSketches = []
            self.srs = QgsProject.instance().crs()
            transformation = None
            for line in infile:
                if line.startswith("srs|"):
                    source_srs_def = line.replace("srs|","").replace("\n","")
                    source_srs = QgsCoordinateReferenceSystem(source_srs_def)
                    if not source_srs.isValid():
                        source_srs = QgsCoordinateReferenceSystem.fromProj4(source_srs_def)
                    transformation = QgsCoordinateTransform(source_srs, QgsProject.instance().crs(), QgsProject.instance())
                    print (line.replace("srs|","").replace("\n",""),source_srs, QgsProject.instance().crs())
                    continue
                inline = line.split("|")
                sketch = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
                sketch.setWidth(int(inline[1]))
                sketch.setColor(QColor(inline[0]))
                load_geom = QgsGeometry.fromWkt(inline[2])
                if transformation:
                    res = load_geom.transform(transformation)
                    #print (res, load_geom.asWkt())
                sketch.setToGeometry(load_geom, dumLayer)
                annotationText = inline[3].replace("%%N%%", "\n") if inline[3] else ""
                self.geoSketches.append([inline[0], inline[1], sketch, None, annotationText, int(inline[4])])
            self.gestures = int(inline[4])+1
            infile.close()
            self.recoverAllAnnotations()

    def toMemoryLayerAction(self):
        polyGestures = {}
        lastPoint = None
        gestureId = 0
        # cycle to classify elementary sketches in gestures
        for sketch in self.geoSketches:
            if sketch[2].asGeometry():
                if not lastPoint or sketch[2].asGeometry().vertexAt(0) == lastPoint:
                    try:
                        polyGestures[gestureId].append(sketch[:-1])
                    except Exception as err:
                        self.log(message=self.tr("Adding sketch to memory layer failed."), log_level=1)
                        logger.error(err)
                        polyGestures[gestureId] = [sketch[:-1]]
                    lastPoint = sketch[2].asGeometry().vertexAt(1)
                else:
                    lastPoint = None
                    gestureId += 1
        sketchLayer = QgsVectorLayer("LineString", "Sketch Layer", "memory")
        sketchLayer.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        sketchLayer.startEditing()
        sketchLayer.addAttribute(QgsField("note", QVariant.String))
        sketchLayer.addAttribute(QgsField("color", QVariant.String))
        sketchLayer.addAttribute(QgsField("width", QVariant.Double))
        for gestureId, gestureLine in polyGestures.items():
            note = ""
            polygon = []
            for segment in gestureLine:
                vertex = segment[2].asGeometry().vertexAt(0)
                polygon.append(QgsPoint(vertex.x(), vertex.y()))
                if segment[4] != "":
                    note = segment[4]
            polygon.append(segment[2].asGeometry().vertexAt(1))
            polyline = QgsGeometry.fromPolyline(polygon)
            newFeat = QgsFeature()
            newFeat.setGeometry(polyline)
            newFeat.setAttributes([note, QColor(segment[0]).name(), float(segment[1])/3.5])
            sketchLayer.addFeatures([newFeat])
        sketchLayer.commitChanges()
        sketchLayer.loadNamedStyle(path.join(self.plugin_dir, "sketchLayerStyle.qml"))
        QgsProject.instance().addMapLayer(sketchLayer)
        sketchLayer.selectByIds([])
        self.removeSketchesAction()
