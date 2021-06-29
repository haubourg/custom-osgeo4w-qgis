#! python3  # noqa: E265

"""
    Main plugin module.
"""

# standard library
from string import Template

# PyQGIS
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication

# project
from french_locator_filter.__about__ import __title__, __version__
from french_locator_filter.core import FrenchBanGeocoderLocatorFilter
from french_locator_filter.gui.dlg_settings import PlgOptionsFactory
from french_locator_filter.toolbelt import PlgLogger, PlgTranslator

# ############################################################################
# ########## Classes ###############
# ##################################


class LocatorFilterPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        plg_translation_mngr = PlgTranslator(
            tpl_filename=Template("french_locator_filter_$locale.qm")
        )
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr

        # install locator filter
        self.filter = FrenchBanGeocoderLocatorFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter)

        if __debug__:
            self.log(
                message=(
                    "DEBUG - French (BAN Geocoder) Locator Filter"
                    f" ({__title__} {__version__}) installed."
                ),
                log_level=4,
            )

    def initGui(self):
        """Set up plugin UI elements."""
        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove filter from locator
        self.iface.deregisterLocatorFilter(self.filter)
