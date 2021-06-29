#! python3  # noqa: E265

"""
    Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from functools import lru_cache
from urllib.parse import urlparse, urlunparse

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.Qt import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from french_locator_filter.toolbelt.log_handler import PlgLogger
from french_locator_filter.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class NetworkRequestsManager:
    """Helper on network operations."""

    def __init__(self):
        """Initialization."""
        self.log = PlgLogger().log
        self.ntwk_requester = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    @lru_cache(maxsize=128)
    def build_url(self, additional_query: str = None) -> QUrl:
        """Build URL using plugin settings and returns it as QUrl.

        :return: complete URL
        :rtype: QUrl
        """
        parsed_url = urlparse(self.plg_settings.request_url)

        if additional_query:
            url_query = self.plg_settings.request_url_query + additional_query
        else:
            url_query = self.plg_settings.request_url_query

        clean_url = parsed_url._replace(query=url_query)
        return QUrl(urlunparse(clean_url))

    def build_request(self, url: QUrl = None) -> QNetworkRequest:
        """Build request object using plugin settings.

        :return: network request object.
        :rtype: QNetworkRequest
        """
        # if URL is not specified, let's use the default one
        if not url:
            url = self.build_url()

        # create network object
        qreq = QNetworkRequest(url=url)

        # headers
        headers = {
            b"Accept": bytes(self.plg_settings.http_content_type, "utf8"),
            b"User-Agent": bytes(self.plg_settings.http_user_agent, "utf8"),
        }
        for k, v in headers.items():
            qreq.setRawHeader(k, v)

        return qreq

    def get_url(self, url: QUrl = None, headers: dict = None) -> QByteArray:
        """Send a get method., using cache and plugin settings.

        :raises ConnectionError: if any problem occurs during feed fetching.
        :raises TypeError: if response mime-type is not valid

        :return: feed response in bytes
        :rtype: QByteArray

        :example:

        .. code-block:: python

            import json
            response_as_dict = json.loads(str(response, "UTF8"))
        """
        # prepare request
        try:
            req = self.build_request(url=url)
            if headers:
                for k, v in headers.items():
                    req.setRawHeader(k, v)
        except Exception as err:
            self.log(
                message=f"Something went wrong during request preparation: {err}",
                log_level=2,
                push=False,
            )

        # send request
        try:
            req_status = self.ntwk_requester.get(
                request=req,
                forceRefresh=False,
            )

            # check if request is fine
            if req_status != QgsBlockingNetworkRequest.NoError:
                self.log(
                    message=self.ntwk_requester.errorMessage(), log_level=2, push=1
                )
                raise ConnectionError(self.ntwk_requester.errorMessage())

            if __debug__:
                self.log(
                    message=f"DEBUG - Request to {self.build_url()} succeeded.",
                    log_level=4,
                    push=False,
                )

            # check reply
            req_reply = self.ntwk_requester.reply()
            if b"application/json" not in req_reply.rawHeader(b"Content-Type"):
                raise TypeError(
                    "Response mime-type is '{}' not 'application/json' as required.".format(
                        req_reply.rawHeader(b"Content-type")
                    )
                )

            return req_reply.content()

        except Exception as err:
            err_msg = "Houston, we've got a problem: {}".format(err)
            self.log(message=err_msg, log_level=2, push=1)
