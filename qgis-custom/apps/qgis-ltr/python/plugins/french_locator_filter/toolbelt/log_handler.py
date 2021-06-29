#! python3  # noqa: E265

# standard library
import logging

# PyQGIS
from qgis.core import QgsMessageLog
from qgis.utils import iface

# project package
from french_locator_filter.__about__ import __title__

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgLogger(logging.Handler):
    """Python logging handler supercharged with QGIS useful methods."""

    @staticmethod
    def log(
        message: str,
        application: str = __title__,
        log_level: int = 0,
        push: bool = False,
    ):
        """Send messages to QGIS messages windows and to the user as a message bar. \
        Plugin name is used as title.

        :param message: message to display
        :type message: str
        :param application: name of the application sending the message. \
        Defaults to __about__.__title__
        :type application: str, optional
        :param log_level: message level. Possible values: 0 (info), 1 (warning), \
        2 (critical), 3 (success), 4 (none - grey). Defaults to 0 (info)
        :type log_level: int, optional
        :param push: also display the message in the QGIS message bar in addition to \
        the log, defaults to False
        :type push: bool, optional

        :Example:

        .. code-block:: python

            log(message="Plugin loaded - INFO", log_level=0, push=1)
            log(message="Plugin loaded - WARNING", log_level=1, push=1)
            log(message="Plugin loaded - ERROR", log_level=2, push=1)
            log(message="Plugin loaded - SUCCESS", log_level=3, push=1)
            log(message="Plugin loaded - TEST", log_level=4, push=1)
        """
        # ensure message is a string
        if not isinstance(message, str):
            try:
                message = str(message)
            except Exception as err:
                err_msg = "Log message must be a string, not: {}. Trace: {}".format(
                    type(message), err
                )
                logging.error(err_msg)
                message = err_msg

        # send it to QGIS messages panel
        QgsMessageLog.logMessage(
            message=message, tag=application, notifyUser=push, level=log_level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push:
            iface.messageBar().pushMessage(
                title=application,
                text=message,
                level=log_level,
                duration=(log_level + 1) * 3,
            )
