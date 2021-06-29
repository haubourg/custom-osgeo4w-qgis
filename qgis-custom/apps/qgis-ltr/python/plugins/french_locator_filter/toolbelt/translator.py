#! python3  # noqa: E265

# standard library
import logging
from functools import lru_cache
from inspect import currentframe
from pathlib import Path
from string import Template

# PyQGIS
from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QLocale, QTranslator
from qgis.PyQt.QtWidgets import QApplication

# project package
from french_locator_filter.__about__ import DIR_PLUGIN_ROOT, __email__, __title__
from french_locator_filter.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################


class PlgTranslator:
    """Helper module to manage plugin translations.

    :param qm_search_start_path: folder where to search fro QM files. \
    Defaults to DIR_PLUGIN_ROOT
    :type qm_search_start_path: Path, optional
    :param tpl_filename: pattern of translations filenames. \
    Defaults to Template(f"{__title__.lower()}_.qm")
    :type tpl_filename: str, optional
    """

    AVAILABLE_TRANSLATIONS: tuple = None

    def __init__(
        self,
        qm_search_start_path: Path = DIR_PLUGIN_ROOT,
        tpl_filename: str = Template(f"{__title__.lower()}_$locale.qm"),
    ):
        """Initialize method."""

        self.log = PlgLogger().log

        # list .qm files
        qm_files = tuple(qm_search_start_path.glob("**/*.qm"))
        self.AVAILABLE_TRANSLATIONS = tuple(q.name for q in qm_files)

        # get locale and identify the compiled translation file (*.qm) to use
        locale = QgsSettings().value("locale/userLocale", QLocale().name())[0:2]
        locale_filename = tpl_filename.substitute(locale=locale)

        self.qm_filepath = None
        for qm in qm_files:
            if qm.name == locale_filename:
                self.qm_filepath = qm
                break

        if not self.qm_filepath:
            info_msg = self.tr(
                "Your selected locale ({}) is not available. "
                "Please consider to contribute with your own translation :). "
                "Contact the plugin maintener(s): {}".format(locale, __email__)
            )
            self.log(message=str(info_msg), log_level=1, push=0)
            logger.info(info_msg)

    def get_translator(self) -> QTranslator:
        """Load translation file into QTranslator.

        :return: translator instance
        :rtype: QTranslator
        """
        if self.AVAILABLE_TRANSLATIONS is None:
            warn_msg = self.tr(
                text="No translation found among plugin files and folders.",
                context="PlgTranslator",
            )
            logger.warning(warn_msg)
            self.log(message=warn_msg, log_level=1)
            return None

        if not self.qm_filepath:
            return None

        # load translation
        self.translator = QTranslator()
        self.translator.load(str(self.qm_filepath.resolve()))
        return self.translator

    @lru_cache(maxsize=128)
    def tr(self, text: str, context: str = None) -> str:
        """Translate a text using the installed translator.

        :param text: text to translate, defaults to None.
        :type text: str
        :param context: where the text is located. In Python code, it's the class name. \
        If None, it tries to automatically retrieve class name. Defaults to None.
        :type context: str, optional

        :return: translated text.
        :rtype: str
        """
        if not context:
            frame = currentframe().f_back
            if "self" in frame.f_locals:
                context = type(frame.f_locals["self"]).__name__

        return QApplication.translate(context, text)
