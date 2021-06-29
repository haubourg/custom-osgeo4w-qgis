#! python3  # noqa: E265

"""
    Plugin settings dialog.
"""

# standard
import logging
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QHBoxLayout, QWidget
from qgis.utils import showPluginHelp

# project
from french_locator_filter.__about__ import (
    DIR_PLUGIN_ROOT,
    __title__,
    __uri_tracker__,
    __version__,
)
from french_locator_filter.toolbelt import PlgLogger, PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

# ############################################################################
# ########## Classes ###############
# ##################################


class DlgSettings(QWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DlgSettings, self).__init__(parent)
        self.setupUi(self)
        self.log = PlgLogger().log

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # customization
        self.btn_help.setIcon(QIcon(":/images/themes/default/mActionHelpContents.svg"))
        self.btn_help.pressed.connect(
            partial(showPluginHelp, filename=f"{DIR_PLUGIN_ROOT}/resources/help/index")
        )

        self.btn_report.setIcon(
            QIcon(":images/themes/default/console/iconSyntaxErrorConsole.svg")
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_tracker__))
        )

        # load previously saved settings
        self.plg_settings = PlgOptionsManager()
        self.load_settings()

    def closeEvent(self, event):
        """Map on plugin close.

        :param event: [description]
        :type event: [type]
        """
        self.closingPlugin.emit()
        event.accept()

    def load_settings(self) -> dict:
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # features
        self.lbl_url_path_value.setText(settings.request_url)
        self.lbl_url_query_value.setText(settings.request_url_query)
        self.lbl_http_content_type_value.setText(settings.http_content_type)
        self.lbl_http_user_agent_value.setText(settings.http_user_agent)
        self.sbx_min_search_length.setValue(settings.min_search_length)

        # misc
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

    def save_settings(self):
        """Save options from UI form into QSettings."""
        # save user settings
        self.plg_settings.set_value_from_key(
            "min_search_length", self.sbx_min_search_length.value()
        )

        # save miscellaneous
        self.plg_settings.set_value_from_key("debug_mode", self.opt_debug.isChecked())
        self.plg_settings.set_value_from_key("version", __version__)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(str(DIR_PLUGIN_ROOT / "resources/images/icon.svg"))

    def createWidget(self, parent):
        return ConfigOptionsPage(parent)

    def title(self):
        return __title__


class ConfigOptionsPage(QgsOptionsPageWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dlg_settings = DlgSettings(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.dlg_settings.setLayout(layout)
        self.setLayout(layout)
        self.setObjectName("mOptionsPage{}".format(__title__))

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        self.dlg_settings.save_settings()
