import unittest
import qgis

from coordinator.test.utilities import get_qgis_app, helperFormatCoordinates
from coordinator.coordinator import Coordinator
from coordinator.test import CoordinatorTestCase
from qgis._core import QgsCoordinateReferenceSystem, QgsPointXY
from PyQt5.QtTest import QTest
from PyQt5 import QtCore
from PyQt5.Qt import QLocale

class CoordinatorIntegrationTest(CoordinatorTestCase):
   
    @classmethod
    def setUpClass(cls):
        super(CoordinatorTestCase, CoordinatorIntegrationTest).setUpClass()
        # some tests may have used objects and the C++ objects
        # might have been deleted. lets make sure we have a clean 
        # slate.
        global CANVAS, IFACE
        QGIS_APP, IFACE, CANVAS = get_qgis_app()
    
    def setUp(self):
        super().setUp()
        
        self.coordinator = Coordinator(IFACE)
        self.coordinator.run()
        self.dw = self.coordinator.dockwidget

        self.initialCanvasCrsAuthid = CANVAS.mapSettings().destinationCrs().authid()

    def tearDown(self):
        self.dw.close()
            
        self.coordinator = None
        self.dw = None
        
        super().tearDown()
        

    def test_openPlugin(self):
        self.assertTrue(self.coordinator.dockwidget.isVisible())
        
    def testInitialValues(self):
        
        expectedOutputCrsAuthid = "" if self.initialCanvasCrsAuthid == None else self.initialCanvasCrsAuthid
        
        self.assertEqual("EPSG:4326", self.coordinator._inputCrs.authid())
        self.assertEqual(expectedOutputCrsAuthid, self.coordinator._outputCrs.authid() )
        self.assertEqual("EPSG:4326", self.coordinator._transform.sourceCrs().authid())
        self.assertEqual(expectedOutputCrsAuthid, self.coordinator._transform.destinationCrs().authid())
        self.assertEqual(self.initialCanvasCrsAuthid, self.coordinator._canvasTransform.destinationCrs().authid())
        self.assertEqual("EPSG:4326", self.coordinator._canvasTransform.sourceCrs().authid())
        
        self.assertEqual("EPSG:4326", self.coordinator.dockwidget.selectCrsButton.text())
    
    def testCanvasTransformation(self):
        
        currentCanvasCrs = CANVAS.mapSettings().destinationCrs()
        self.assertEqual(currentCanvasCrs, self.coordinator._canvasTransform.destinationCrs())
        
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:32615"))
        self.assertEqual("EPSG:32615", self.coordinator._canvasTransform.destinationCrs().authid())
        
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem(currentCanvasCrs))
        self.assertEqual(currentCanvasCrs, self.coordinator._canvasTransform.destinationCrs())
        
    
    def testLayerLock(self):
        outputCrs = self.coordinator._outputCrs
        
        newCrs = QgsCoordinateReferenceSystem("EPSG:32615")
        CANVAS.setDestinationCrs(newCrs)
        
        self.dw.outputCrsConn.setEnabled(True)
        QTest.mouseClick(self.dw.outputCrsConn, QtCore.Qt.LeftButton)
        QTest.qWait(100)
        QTest.mouseClick(self.dw.outputCrsConn, QtCore.Qt.LeftButton)
        
        self.assertEqual(self.coordinator._outputCrs, newCrs)
        
        QTest.qWait(100)
        # Simulate a click, but nothing should happen
        QTest.mouseClick(self.dw.outputCrs, QtCore.Qt.LeftButton)
         
        
    def testTransformIdentity(self):
        
        crsIn = QgsCoordinateReferenceSystem("EPSG:4326")
        crsOut = QgsCoordinateReferenceSystem("EPSG:4326")
        
        self.coordinator.setInputCrs(crsIn)
        self.dw.outputCrsConn.setEnabled(False)
        self.coordinator.setOutputCrs(crsOut)
        
        QTest.keyPress(self.dw.inLeft, "2")
        self.assertEqual(helperFormatCoordinates("2°0′0.000″E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("0°0′0.000″"), self.dw.resultRight.text())

        QTest.keyPress(self.dw.inLeft, "3")
        self.assertEqual(helperFormatCoordinates("23°0′0.000″E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("0°0′0.000″"), self.dw.resultRight.text())

        
        QTest.keyPress(self.dw.inRightMin, "2")
        self.assertEqual(helperFormatCoordinates("23°0′0.000″E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("0°2′0.000″N"), self.dw.resultRight.text())
        
        
    def testTransformGeographicToGeodesic(self):
        self.coordinator.setInputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        self.dw.outputCrsConn.setEnabled(False)
        self.coordinator.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:32633"))
        
        QTest.keyClicks(self.dw.inLeft, "14")
        QTest.keyClicks(self.dw.inLeftMin, "30")
        QTest.keyClicks(self.dw.inLeftSec, "45")
        QTest.keyClicks(self.dw.inRight, "45")
        QTest.keyClicks(self.dw.inRightMin, "10")
        QTest.keyClicks(self.dw.inRightSec, "5")

        self.assertEqual(helperFormatCoordinates("461,690.03"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5,001,735.10"), self.dw.resultRight.text())
        
        self.coordinator.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:32632"))
        self.assertEqual(helperFormatCoordinates("933,193.62"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5,016,421.01"), self.dw.resultRight.text())
        
        
    def testTransformGeodesicToGeographic(self):
        self.coordinator.setInputCrs(QgsCoordinateReferenceSystem("EPSG:32633"))
        self.dw.outputCrsConn.setEnabled(False)
        self.coordinator.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        
        QTest.keyClicks(self.dw.inLeftDec, "560000")
        QTest.keyClicks(self.dw.inRightDec, "5400000")
        self.assertEqual(helperFormatCoordinates("15°48′58.480″E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("48°45′0.440″N"), self.dw.resultRight.text())
        
        QTest.mouseClick(self.dw.resultAsDec, QtCore.Qt.LeftButton)
        self.assertEqual(helperFormatCoordinates("15.816244426°E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("48.750122268°N"), self.dw.resultRight.text())


    def testSwitchHemispheres(self):
        crsIn = QgsCoordinateReferenceSystem("EPSG:4326")
        crsOut = QgsCoordinateReferenceSystem("EPSG:4326")
        
        self.coordinator.setInputCrs(crsIn)
        self.dw.outputCrsConn.setEnabled(False)
        self.coordinator.setOutputCrs(crsOut)
        
        self.assertEqual("E", self.dw.leftDirButton.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        
        self.dw.inLeft.insert("10")
        self.dw.inLeftMin.insert("5")
        self.dw.inLeftSec.insert("1")
        
        self.dw.inRight.insert("5")
        self.dw.inRightMin.insert("10")
        self.dw.inRightSec.insert("45")
        
        self.assertEqual(helperFormatCoordinates("10°5′1.000″E"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5°10′45.000″N"), self.dw.resultRight.text())
        
        QTest.mouseClick(self.dw.leftDirButton, QtCore.Qt.LeftButton)
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        self.assertEqual(helperFormatCoordinates("10°5′1.000″W"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5°10′45.000″N"), self.dw.resultRight.text())
        
        QTest.mouseClick(self.dw.rightDirButton, QtCore.Qt.LeftButton)
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertEqual("S", self.dw.rightDirButton.text())
        self.assertEqual(helperFormatCoordinates("10°5′1.000″W"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5°10′45.000″S"), self.dw.resultRight.text())

        QTest.mouseClick(self.dw.rightDirButton, QtCore.Qt.LeftButton)
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        self.assertEqual(helperFormatCoordinates("10°5′1.000″W"), self.dw.resultLeft.text())
        self.assertEqual(helperFormatCoordinates("5°10′45.000″N"), self.dw.resultRight.text())
        
    
    def testGeographicInputDisplay(self):
        crsIn = QgsCoordinateReferenceSystem("EPSG:4326")
        
        QTest.mouseClick(self.dw.inputAsDec, QtCore.Qt.LeftButton)
        self.assertFalse(self.dw.inputAsDMS.isChecked())
        self.assertTrue(self.dw.inputAsDec.isChecked())
        
        QTest.qSleep(3000)
        
        self.assertFalse(self.dw.inLeft.isVisible())
        self.assertFalse(self.dw.inLeftMin.isVisible())
        self.assertFalse(self.dw.inLeftSec.isVisible())
        
        self.assertFalse(self.dw.inRight.isVisible())
        self.assertFalse(self.dw.inRightMin.isVisible())
        self.assertFalse(self.dw.inRightSec.isVisible())
        
        self.assertTrue(self.dw.inLeftDec.isVisible())
        self.assertTrue(self.dw.inRightDec.isVisible())
        
        QTest.mouseClick(self.dw.inputAsDMS, QtCore.Qt.LeftButton)
        self.assertTrue(self.dw.inputAsDMS.isChecked())
        self.assertFalse(self.dw.inputAsDec.isChecked())
        
        self.dw.inLeft.insert("10")
        self.dw.inLeftMin.insert("5")
        self.dw.inLeftSec.insert("1")
        
        self.dw.inRight.insert("5")
        self.dw.inRightMin.insert("10")
        self.dw.inRightSec.insert("45")
        
        QTest.mouseClick(self.dw.inputAsDec, QtCore.Qt.LeftButton)
        self.assertEqual(helperFormatCoordinates("10.083611111"),self.dw.inLeftDec.text())
        self.assertEqual(helperFormatCoordinates("5.179166667"),self.dw.inRightDec.text())
        
    def testInputInDecimalMode(self):
        QTest.mouseClick(self.dw.inputAsDec, QtCore.Qt.LeftButton)
        
        self.dw.setInputPoint(QgsPointXY(1,1))
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inLeftDec.text())
        self.assertEqual("E", self.dw.leftDirButton.text())
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inRightDec.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        
        self.dw.setInputPoint(QgsPointXY(-1,1))
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inLeftDec.text())
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inRightDec.text())
        self.assertEqual("N", self.dw.rightDirButton.text())
        
        self.dw.setInputPoint(QgsPointXY(1,-1))
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inLeftDec.text())
        self.assertEqual("E", self.dw.leftDirButton.text())
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inRightDec.text())
        self.assertEqual("S", self.dw.rightDirButton.text())
        
        self.dw.setInputPoint(QgsPointXY(-1,-1))
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inLeftDec.text())
        self.assertEqual("W", self.dw.leftDirButton.text())
        self.assertEqual(helperFormatCoordinates("1.000000000"), self.dw.inRightDec.text())
        self.assertEqual("S", self.dw.rightDirButton.text())
        
    def testCrsChangeOnLayer(self):
        """[GITHUB #1] CRS change of selected layer"""
        
        eLayer = self.addEuropeLayer()
        self.assertEqual("EPSG:4326", eLayer.crs().authid())
        global IFACE
        IFACE.setActiveLayer(eLayer)
        
        self.assertEqual("EPSG:4326", self.coordinator.outputCrs().authid())
        
        eLayer.setCrs(QgsCoordinateReferenceSystem("EPSG:32633"))
        self.assertEqual("EPSG:32633", eLayer.crs().authid())
        self.assertEqual("EPSG:32633", self.coordinator.outputCrs().authid())
        self.project.removeMapLayer(eLayer)
        
        
    
if __name__ == "__main__":
    suite = unittest.makeSuite(CoordinatorIntegrationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
        
        
    
