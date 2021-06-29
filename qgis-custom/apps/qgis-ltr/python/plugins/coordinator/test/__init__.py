# import qgis libs so that ve set the correct sip api version
import os, sys, qgis   # pylint: disable=W0611  # NOQA
from PyQt5.Qt import QLocale
from qgis.testing import unittest
from qgis.core import QgsProject, QgsVectorLayer

def run_all(): 
    loader = unittest.TestLoader()
    
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir)
      
    runner = unittest.TextTestRunner(verbosity = 3, stream=sys.stdout)
    runner.run(suite)
    
class CoordinatorTestCase(unittest.TestCase):

  def __init__(self, testCase):
    super(unittest.TestCase, self).__init__(testCase)
    self.project = None
    
    self._addedLayers = []
    

  def setUp(self):
    self.project = QgsProject.instance()
    
    
  def tearDown(self):
    while len(self._addedLayers) > 0:
        layerName = self._addedLayers.pop() 
        layers = self.project.mapLayersByName(layerName)
        self.project.removeMapLayers([layer.id() for layer in layers])
        
    
  def addMapLayer(self, mapLayer):
    self.project.addMapLayer(mapLayer, True)
    self._addedLayers.append(mapLayer.name())
    
    
  def addVectorLayerFile(self, vectorLayerFile, vectorLayerName):
    vectorLayer = QgsVectorLayer(vectorLayerFile, vectorLayerName, "ogr")
    self.addMapLayer(vectorLayer)
    return vectorLayer


  def addEuropeLayer(self):
    return self.addVectorLayerFile(os.path.join(os.path.dirname(__file__), "data/europe.geojson" ), "europe")


  def assertTextFieldCloseTo(self, expected, textField, tolerance = 1, msg = None):
      textFieldValue = QLocale().toFloat(textField.text())[0]
      
      result = ( (expected - tolerance) <= textFieldValue <= (expected + tolerance) )
      
      if(not result):
          if msg == None:
              msg = "value '%f' of QTextField is not close to %f±%f)" % (textFieldValue, expected, tolerance)
        
          raise AssertionError(msg)
      
      
  def assertTextFieldBetween(self, lower, upper, textField, msg = None):
      textFieldValue = QLocale().toFloat(textField.text())[0]
      
      result = (lower < textFieldValue < upper)
      
      if msg == None:
          msg = "value '%f' of QTextField is not between %f and %f)" % (textFieldValue, lower, upper)
      
      self.assertTrue(result, msg)
