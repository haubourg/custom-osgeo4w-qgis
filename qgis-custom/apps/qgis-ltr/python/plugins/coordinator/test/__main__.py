import unittest, sys, os

from . import run_all

if sys.platform == "win32" and 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
    if 'QT_PLUGIN_PATH' in os.environ:
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.environ['QT_PLUGIN_PATH']
    else:
        if "OSGEO4W_ROOT" in os.environ:
            qtPluginPath = os.path.join(os.path.normpath(os.environ["OSGEO4W_ROOT"].strip()),'apps/qt5/plugins')
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qtPluginPath
        else:
            print("Cannot set QT_QPA_PLATFORM")
            sys.exit(1)

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

run_all()
