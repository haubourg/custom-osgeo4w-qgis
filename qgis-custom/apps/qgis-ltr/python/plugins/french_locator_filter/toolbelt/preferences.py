#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
import logging
from typing import NamedTuple

# PyQGIS
from qgis.core import QgsSettings

# package
from french_locator_filter.__about__ import __title__, __version__

from .log_handler import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
plg_logger = PlgLogger()

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgSettingsStructure(NamedTuple):
    """Plugin settings structure and defaults values."""

    # misc
    debug_mode: bool = False
    version: str = __version__

    # network
    http_content_type: str = "application/json"
    http_user_agent: str = f"{__title__}/{__version__}"
    min_search_length: int = 2
    request_url: str = "https://api-adresse.data.gouv.fr/search/"
    request_url_query: str = "limit=10&autocomplete=1"


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        options = PlgSettingsStructure(
            # misc
            debug_mode=settings.value(key="debug_mode", defaultValue=False, type=bool),
            version=settings.value(key="version", defaultValue=__version__, type=str),
            # network
            http_content_type=settings.value(
                key="http_content_type",
                defaultValue="application/json",
                type=str,
            ),
            http_user_agent=settings.value(
                key="http_user_agent",
                defaultValue=f"{__title__}/{__version__}",
                type=str,
            ),
            min_search_length=settings.value(
                key="min_search_length",
                defaultValue=2,
                type=int,
            ),
            request_url=settings.value(
                key="request_url",
                defaultValue="https://api-adresse.data.gouv.fr/search/",
                type=str,
            ),
            request_url_query=settings.value(
                key="request_url_query",
                defaultValue="limit=10&autocomplete=1",
                type=str,
            ),
        )

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            logger.error(
                "Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                )
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            logger.error(err)
            plg_logger.log(err)
            out_value = None

        settings.endGroup()

        return out_value

    @staticmethod
    def set_value_from_key(key: str, value):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            logger.error(
                "Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                )
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
        except Exception as err:
            logger.error(err)
            plg_logger.log(err)
            out_value = False

        settings.endGroup()

        return out_value
