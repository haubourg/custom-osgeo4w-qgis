# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from PyQt5.Qt import QDialog
import time
from PyQt5.QtTest import QTest
from PyQt5 import QtCore

__author__ = 'qgis@ag99.de'
__date__ = '2019-05-04'
__copyright__ = 'Copyright 2019, Jonas Küpper'

import unittest

from PyQt5.QtWidgets  import QDockWidget
from PyQt5.Qt import QLocale, Qt

from coordinator.coordinator_dockwidget import CoordinatorDockWidget
from coordinator.test.utilities import get_qgis_app, helperFormatCoordinates

class CoordinatorDockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""
    
    @classmethod
    def setUpClass(cls):
        super(CoordinatorDockWidgetTest, cls).setUpClass()
        # some tests may have used objects and the C++ objects
        # might have been deleted. lets make sure we have a clean 
        # slate.
        global IFACE
        QGIS_APP, IFACE, CANVAS = get_qgis_app()

    def setUp(self):
        """Runs before each test."""
        self.dw = CoordinatorDockWidget()
        IFACE.addDockWidget(Qt.LeftDockWidgetArea, self.dw)
        self.dw.show()

    def tearDown(self):
        """Runs after each test."""
        self.dw.hide()
        self.dw = None

    def testGeographicInput(self):
        """Tests if display is correct after setting input to geographic"""
        self.dw.setSectionIsGeographic(CoordinatorDockWidget.SectionInput, True)
        self.assertTrue(self.dw.geographicPanel.isEnabled())
        QTest.mouseClick(self.dw.inputAsDMS, QtCore.Qt.LeftButton)
        self.assertTrue(self.dw.inputAsDMS.isChecked())
        self.assertFalse(self.dw.inputAsDec.isChecked())

        self.assertTrue(self.dw.inLeft.isVisible())
        self.assertTrue(self.dw.inLeftMin.isVisible())
        self.assertTrue(self.dw.inLeftSec.isVisible())

        self.assertTrue(self.dw.inRight.isVisible())
        self.assertTrue(self.dw.inRightMin.isVisible())
        self.assertTrue(self.dw.inRightSec.isVisible())

        self.assertFalse(self.dw.inLeftDec.isVisible())
        self.assertFalse(self.dw.inRightDec.isVisible())

        QTest.mouseClick(self.dw.inputAsDec, QtCore.Qt.LeftButton)
        self.assertFalse(self.dw.inputAsDMS.isChecked())
        self.assertTrue(self.dw.inputAsDec.isChecked())
        
    def testClearAll(self):
        QTest.keyClicks(self.dw.inLeft, "22")
        QTest.keyClicks(self.dw.inLeftMin, "22")
        QTest.keyClicks(self.dw.inLeftSec, "22")
        QTest.keyClicks(self.dw.inRight, "22")
        QTest.keyClicks(self.dw.inRightMin, "22")
        QTest.keyClicks(self.dw.inRightSec, "22")
        QTest.mouseClick(self.dw.leftDirButton, QtCore.Qt.LeftButton)
        QTest.mouseClick(self.dw.rightDirButton, QtCore.Qt.LeftButton)
        
        QTest.mouseClick(self.dw.clearInput, QtCore.Qt.LeftButton)
        self.assertEqual("", self.dw.inLeft.text())
        self.assertEqual("", self.dw.inLeftMin.text())
        self.assertEqual("", self.dw.inLeftSec.text())
        self.assertEqual("", self.dw.inRight.text())
        self.assertEqual("", self.dw.inRightMin.text())
        self.assertEqual("", self.dw.inRightSec.text())
        
        self.assertEqual(self.dw.tr("W"),self.dw.leftDirButton.text())
        self.assertEqual(self.dw.tr("S"),self.dw.rightDirButton.text())
        self.assertFalse(self.dw.hasInput())

    def testIncrementorBasic(self):
        self.dw.setSectionIsGeographic(CoordinatorDockWidget.SectionInput, True)
 
        QTest.mouseClick(self.dw.inputAsDMS, QtCore.Qt.LeftButton)
 
        self.assertEqual("", self.dw.inLeft.text())
        self.assertTrue(self.dw.inLeft.isVisible())
        self.assertTrue(self.dw.inLeft.isEnabled())
 
        QTest.keyClick(self.dw.inLeft, QtCore.Qt.Key_Up)
        self.assertEqual("1", self.dw.inLeft.text())
        QTest.keyClick(self.dw.inLeft, QtCore.Qt.Key_Down)
        self.assertEqual("0", self.dw.inLeft.text())
 
        self.assertEqual("", self.dw.inLeftSec.text())
        QTest.keyClick(self.dw.inLeftSec, QtCore.Qt.Key_Up)
        self.assertEqual(helperFormatCoordinates("1.000"), self.dw.inLeftSec.text())
        QTest.keyClick(self.dw.inLeftSec, QtCore.Qt.Key_Down)
        self.assertEqual(helperFormatCoordinates("0.000"), self.dw.inLeftSec.text())
  
        self.dw.setInputToDMS(False)
 
        self.assertFalse(self.dw.inLeftSec.isVisible())
        self.assertFalse(self.dw.inLeft.isVisible())
        self.assertTrue(self.dw.inLeftDec.isVisible())
        self.assertTrue(self.dw.inLeftDec.isEnabled())
 
        self.assertEqual(helperFormatCoordinates("0.000000000"), self.dw.inLeftDec.text())
        QTest.keyClick(self.dw.inLeftDec, QtCore.Qt.Key_Up)
        self.assertEqual(helperFormatCoordinates("1.00000000"), self.dw.inLeftDec.text())
        QTest.keyClick(self.dw.inLeftDec, QtCore.Qt.Key_Down)
        self.assertEqual(helperFormatCoordinates("0.00000000"), self.dw.inLeftDec.text())

    def testIncrementorOverflowDms(self):
        QTest.keyClicks(self.dw.inLeftMin, "59" )
        QTest.keyClicks(self.dw.inLeftSec, "59" )
        
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Up )
        self.assertEqual("0", self.dw.inLeftMin.text())
        self.assertEqual("1", self.dw.inLeft.text())
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Down )
        self.assertEqual("59", self.dw.inLeftMin.text())
        self.assertEqual("0", self.dw.inLeft.text())
        
        QTest.keyClick(self.dw.inLeftSec, QtCore.Qt.Key_Up )
        self.assertEqual(helperFormatCoordinates("0.000"), self.dw.inLeftSec.text())
        self.assertEqual("0", self.dw.inLeftMin.text())
        self.assertEqual("1", self.dw.inLeft.text())
    
    def testIncrementorThreeDigits(self):
        QTest.keyClicks(self.dw.inLeft, "99" )
        self.assertEqual("99", self.dw.inLeft.text())
        QTest.keyClick(self.dw.inLeft, QtCore.Qt.Key_Up )
        self.assertEqual("100", self.dw.inLeft.text())
    
    def testIncrementorNoWrap(self):
        QTest.keyClicks(self.dw.inLeft, "179" )
        QTest.keyClick(self.dw.inLeft, QtCore.Qt.Key_Up )
        self.assertEqual("180", self.dw.inLeft.text())
        QTest.keyClick(self.dw.inLeft, QtCore.Qt.Key_Up )
        self.assertEqual("180", self.dw.inLeft.text())   
        
        QTest.keyClicks(self.dw.inRight, "89" )
        QTest.keyClick(self.dw.inRight, QtCore.Qt.Key_Up )
        self.assertEqual("90", self.dw.inRight.text())
        QTest.keyClick(self.dw.inRight, QtCore.Qt.Key_Up )
        self.assertEqual("90", self.dw.inRight.text())
        
    def testIncrementorClampMaxByInput(self):
        QTest.keyClicks(self.dw.inLeft, "180" )
        QTest.keyClicks(self.dw.inLeftMin, "1" )
        self.assertEqual("180", self.dw.inLeft.text())
        self.assertEqual("0", self.dw.inLeftMin.text())
        self.assertEqual(helperFormatCoordinates("180.000000000"), self.dw.inLeftDec.text())     
        
    def testIncrementorClampMaxByIncrementor(self):
        QTest.keyClicks(self.dw.inLeft, "179" )
        QTest.keyClicks(self.dw.inLeftMin, "59" )
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Up )
        self.assertEqual("180", self.dw.inLeft.text())
        self.assertEqual("0", self.dw.inLeftMin.text())
        self.assertEqual(helperFormatCoordinates("180.000000000"), self.dw.inLeftDec.text())
        
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Up )
        self.assertEqual("180", self.dw.inLeft.text())
        self.assertEqual("0", self.dw.inLeftMin.text())
        self.assertEqual(helperFormatCoordinates("180.000000000"), self.dw.inLeftDec.text())
    
    def testIncrementorAtMaximumMin(self):
        QTest.keyClicks(self.dw.inLeft, "180" )
        QTest.keyClicks(self.dw.inLeftMin, "0" )
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Down )
        self.assertEqual("179", self.dw.inLeft.text())
        self.assertEqual("59", self.dw.inLeftMin.text())
    
    def testIncrementorAtMaximumSec(self):
        QTest.keyClicks(self.dw.inLeft, "180" )
        QTest.keyClicks(self.dw.inLeftMin, "0" )
        QTest.keyClick(self.dw.inLeftSec, QtCore.Qt.Key_Down )
        self.assertEqual("179", self.dw.inLeft.text())
        self.assertEqual("59", self.dw.inLeftMin.text())
        self.assertEqual(helperFormatCoordinates("59.000"), self.dw.inLeftSec.text())
    
    def testIncrementorAtMinimumMin(self):
        QTest.keyClick(self.dw.inLeftMin, QtCore.Qt.Key_Down )
        self.assertEqual("", self.dw.inLeft.text())
        self.assertEqual("", self.dw.inLeftMin.text())
    
    def testIncrementorAtMinimumSec(self):
        QTest.keyClick(self.dw.inLeftSec, QtCore.Qt.Key_Down )
        self.assertEqual("", self.dw.inLeft.text())
        self.assertEqual("", self.dw.inLeftMin.text())
        self.assertEqual("", self.dw.inLeftSec.text())
        

if __name__ == "__main__":
    suite = unittest.makeSuite(CoordinatorDockWidgetTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
