import unittest
import qgis

from coordinator.coordinator import Coordinator
from coordinator.test.utilities import get_qgis_app, IFACE,\
    helperFormatCoordinates
from coordinator.test import CoordinatorTestCase
from coordinator.test.qgis_interface import QgisStubInterface

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog, QMainWindow, QDockWidget, QWidget
from PyQt5.Qt import Qt, QSize, QLocale
from PyQt5 import QtCore
import os
from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle, QgsPointXY
from qgis.gui import QgsMapToolPan, QgsMapToolCapture, QgsAdvancedDigitizingDockWidget
from pkg_resources._vendor.packaging import version



class CoordinatorCanvasTest(CoordinatorTestCase):
    def setUp(self):
        
        super().setUp()
        
        global CANVAS, IFACE
        QGIS_APP, IFACE, CANVAS = get_qgis_app()
        
        if isinstance(IFACE, QgisStubInterface):
            self.window = QMainWindow()
            self.window.resize(QSize(800,400))
            self.window.setCentralWidget(CANVAS)
        else:
            self.window = None
        
        # try to get the current instance of coordinator:
        try:
            self.coordinator = qgis.utils.plugins['coordinator']
        except KeyError:
            self.coordinator = Coordinator(IFACE, self.window)
            
        
        self.pluginWasOpen = self.coordinator.pluginIsActive
        
        if not self.coordinator.pluginIsActive:
            self.coordinator.run()
        
        
        self.coordinator.reset()
        self.coordinator.captureCoordsButtonToggled(False)
            
        self.dw = self.coordinator.dockwidget
        
        if self.window:
            self.window.show()
            
        self.addEuropeLayer()
        QTest.qWait(50)


    def clickCanvasCoordinate(self, coordinatePointXY):
        mapToPixel = CANVAS.getCoordinateTransform()
        testPositionPixels = mapToPixel.transform(coordinatePointXY)
        QTest.mouseClick(CANVAS.viewport(), Qt.LeftButton, pos = testPositionPixels.toQPointF().toPoint())


    def tearDown(self):
        super().tearDown()
        self.project.clear()
        
        if not self.pluginWasOpen:
            self.dw.close()
        else:
            self.coordinator.reset()
            
        QTest.qWait(200)
        try:
            self.window.close()
        except:
            pass
        
    def testMarkerGeographicOnGeodesic(self):
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:32632"))
        QTest.qWait(100)
        CANVAS.zoomToFeatureExtent(QgsRectangle(150000, 4800000, 850000, 5500000 ))
        QTest.qWait(100)
        
        QTest.mouseClick(self.dw.inputAsDec, Qt.LeftButton)
        
        marker = self.coordinator.marker
        mapToPixel = CANVAS.getCoordinateTransform()
        
        # set point to 8°E but 0°N
        QTest.keyClicks(self.dw.inLeftDec, "8" )
        QTest.qWait(1000)
        # check non visible 
        self.assertFalse(CANVAS.sceneRect().contains(marker.scenePos()))
        self.assertTrue(self.dw.messageIcon.isVisible())
        
        # add 45°N
        QTest.keyClicks(self.dw.inRightDec, "45" )
        QTest.qWait(200)
        # now point should be visible
        self.assertTrue(CANVAS.sceneRect().contains(marker.scenePos()))
        self.assertFalse(self.dw.messageIcon.isVisible())
        
        # check the actual position on the map
        coords = mapToPixel.toMapCoordinates(marker.pos().x(), marker.pos().y())
        expectedPixelPos = mapToPixel.transform(QgsPointXY(421184, 4983436))
        self.assertAlmostEqual(expectedPixelPos.x(), marker.pos().x(), 0)
        self.assertAlmostEqual(expectedPixelPos.y(), marker.pos().y(), 0)
        
        # remove latitude coordinates
        QTest.mouseDClick(self.dw.inRightDec, Qt.LeftButton)
        QTest.keyClick(self.dw.inRightDec, Qt.Key_Delete)
        QTest.qWait(200)
        self.assertFalse(CANVAS.sceneRect().contains(marker.scenePos()))
        self.assertTrue(self.dw.messageIcon.isVisible())
        
        # set 80°N
        QTest.keyClicks(self.dw.inRightDec, "80" )
        QTest.qWait(200)
        # check non visible 
        self.assertFalse(CANVAS.sceneRect().contains(marker.scenePos()))
        self.assertTrue(self.dw.messageIcon.isVisible())
        
        # clear input and set coordinates on western hemisphere but with correct Latitude
        QTest.mouseClick(self.dw.clearInput, Qt.LeftButton)
        QTest.mouseClick(self.dw.leftDirButton, Qt.LeftButton)
        QTest.keyClicks(self.dw.inLeftDec, "8" )
        QTest.keyClicks(self.dw.inRightDec, "45" )
         # check non visible 
        self.assertFalse(CANVAS.sceneRect().contains(marker.scenePos()))
        self.assertTrue(self.dw.messageIcon.isVisible())
        
    def testCaptureWest4326(self):
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        #self.dw.setMinimumWidth(self.dw.width() + 50)
        QTest.qWait(100)
        CANVAS.zoomToFeatureExtent(QgsRectangle(-99.7, 70.3, -99.3, 70.7 ))
        QTest.qWait(100)
        
        QTest.mouseClick(self.dw.captureCoordButton, Qt.LeftButton)
        QTest.qWait(100)
        
        testPosition = QgsPointXY(-99.5, 70.5)
        self.clickCanvasCoordinate(testPosition)
        
        QTest.qWait(100)
         # recalculate and click again, because the GUI might have moved a bit:
        self.clickCanvasCoordinate(testPosition)
        QTest.qWait(100)
                
        self.assertEqual("99", self.dw.inLeft.text())
        self.assertTextFieldBetween(28, 31, self.dw.inLeftMin)
        #self.assertEqual(helperFormatCoordinates("0.00"), self.dw.inLeftSec.text())
        self.assertEqual("W", self.dw.leftDirButton.text())
        
        self.assertEqual("70", self.dw.inRight.text())
        self.assertTextFieldBetween(28, 31, self.dw.inRightMin)
        #self.assertEqual(helperFormatCoordinates("0.00"), self.dw.inRightSec.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        
        QTest.mouseClick(self.dw.inputAsDec, Qt.LeftButton)
        
        self.assertAlmostEqual(99.5, QLocale().toFloat(self.dw.inLeftDec.text())[0], places = 2)
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertAlmostEqual(70.5, QLocale().toFloat(self.dw.inRightDec.text())[0], places = 2)
        self.assertEqual("N", self.dw.rightDirButton.text())

        # repeat test while in decimal mode:
        self.clickCanvasCoordinate(testPosition)
        QTest.qWait(100)
                
        self.assertAlmostEqual(99.5, QLocale().toFloat(self.dw.inLeftDec.text())[0], places = 2)
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertAlmostEqual(70.5, QLocale().toFloat(self.dw.inRightDec.text())[0], places = 2)
        self.assertEqual("N", self.dw.rightDirButton.text())


    def testMapToolChange(self):

        if isinstance(IFACE, QgisStubInterface):
            advDigitizeWidget = QgsAdvancedDigitizingDockWidget(CANVAS, CANVAS)

            if ( version.parse(QtCore.qVersion()) < version.parse("5.11.0") ):
                toolMode = QgsMapToolCapture.CaptureLine
            else:
                toolMode = QgsMapToolCapture.CaptureMode.CaptureLine

            captureMapTool = QgsMapToolCapture(CANVAS, advDigitizeWidget, toolMode)

            self.coordinator.reset()
            CANVAS.setMapTool(QgsMapToolPan(CANVAS))
            self.assertFalse(self.dw.addFeatureButton.isEnabled())
            QTest.keyClicks(self.dw.inLeft, "8" )
            self.assertFalse(self.dw.addFeatureButton.isEnabled())

            CANVAS.setMapTool(captureMapTool)

            self.assertTrue(self.dw.addFeatureButton.isEnabled())

            CANVAS.setMapTool(QgsMapToolPan(CANVAS))
            self.assertFalse(self.dw.addFeatureButton.isEnabled())

            self.coordinator.reset()
            self.assertFalse(self.dw.addFeatureButton.isEnabled())
            CANVAS.setMapTool(captureMapTool)
            # add Feature Button should not be enabled when there is no input
            self.assertFalse(self.dw.addFeatureButton.isEnabled())
        else:
            self.skipTest("not yet implemented for QGIS GUI tests")


    def testGeodeticNegative(self):
        """[GITHUB #12] Negative Values in Geodetic CRS"""
        
        crsIn = QgsCoordinateReferenceSystem("EPSG:31254")
        self.coordinator.setInputCrs(crsIn)
        
        CANVAS.setDestinationCrs(crsIn)
        
        QTest.qWait(100)
        CANVAS.zoomToFeatureExtent(QgsRectangle(-80000, 200000, 80000, 250000 ))
        QTest.qWait(100)
        
        QTest.mouseClick(self.dw.captureCoordButton, Qt.LeftButton)
        QTest.qWait(100)
        
        testPosition = QgsPointXY(50000, 230000)
        self.clickCanvasCoordinate(testPosition)
        QTest.qWait(500)
        self.assertTextFieldCloseTo(230000, self.dw.inRightDec, 300)
        self.assertTextFieldCloseTo(50000, self.dw.inLeftDec, 300)
        
        testPosition = QgsPointXY(-50000, 230000)
        self.clickCanvasCoordinate(testPosition)
        QTest.qWait(500)
        self.assertTextFieldCloseTo(230000, self.dw.inRightDec, 300)
        self.assertTextFieldCloseTo(-50000, self.dw.inLeftDec, 300)



def runTest():
    suite = unittest.makeSuite(CoordinatorCanvasTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    runTest()
