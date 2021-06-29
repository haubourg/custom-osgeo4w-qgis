#! python3  # noqa: E265

"""
    Main plugin module.
"""

# standard library
import json
import logging

# PyQGIS
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeedback,
    QgsLocatorContext,
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsPointXY,
    QgsProject,
)
from qgis.PyQt.QtCore import QCoreApplication

# project
from french_locator_filter.toolbelt import (
    NetworkRequestsManager,
    PlgLogger,
    PlgOptionsManager,
)

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class FrenchBanGeocoderLocatorFilter(QgsLocatorFilter):
    def __init__(self, iface):
        self.iface = iface
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager.get_plg_settings()

        super(QgsLocatorFilter, self).__init__()

    def name(self) -> str:
        """Returns the unique name for the filter. This should be an untranslated \
        string identifying the filter.

        :return: filter unique name
        :rtype: str
        """
        return self.__class__.__name__

    def clone(self) -> QgsLocatorFilter:
        """Creates a clone of the filter. New requests are always executed in a clone \
        of the original filter.

        :return: clone of the actual filter
        :rtype: QgsLocatorFilter
        """
        return FrenchBanGeocoderLocatorFilter(self.iface)

    def displayName(self) -> str:
        """Returns a translated, user-friendly name for the filter.

        :return: user-friendly name to be displayed
        :rtype: str
        """
        return self.tr("French Adress geocoder")

    def prefix(self) -> str:
        """Returns the search prefix character(s) for this filter. Prefix a search with \
        these characters will restrict the locator search to only include results from \
        this filter.

        :return: search prefix for the filter
        :rtype: str
        """
        return "fra"

    def fetchResults(
        self, search: str, context: QgsLocatorContext, feedback: QgsFeedback
    ):
        """Retrieves the filter results for a specified search string. The context \
        argument encapsulates the context relating to the search (such as a map extent \
        to prioritize). \

        Implementations of fetchResults() should emit the resultFetched() signal \
        whenever they encounter a matching result. \
        Subclasses should periodically check the feedback object to determine whether \
        the query has been canceled. If so, the subclass should return from this method \
        as soon as possible. This will be called from a background thread unless \
        flags() returns the QgsLocatorFilter.FlagFast flag.

        :param search: text entered by the end-user into the locator line edit
        :type search: str
        :param context: [description]
        :type context: QgsLocatorContext
        :param feedback: [description]
        :type feedback: QgsFeedback
        """
        # ignore if search terms is inferior than 3 chars or equal to the prefix
        if (
            len(search) < self.plg_settings.min_search_length
            or search.rstrip() == self.prefix
        ):
            return

        # request
        try:
            qntwk = NetworkRequestsManager()
            qurl = qntwk.build_url(additional_query=f"&q={search}")
            response_content = qntwk.get_url(url=qurl)
        except Exception as err:
            self.log(message=err, log_level=1, push=True)
            return

        # process response
        try:
            # load response as a dict
            locations = json.loads(str(response_content, "UTF8"))

            # loop on features in json collection
            for loc in locations.get("features"):
                result = QgsLocatorResult()
                result.filter = self
                label = loc.get("properties").get("label")
                if loc.get("properties").get("type") == "municipality":
                    # add city code to label
                    label += " " + loc.get("properties").get("citycode")
                result.displayString = label
                result.group = loc.get("properties").get("type")

                # use the json full item as userData, so all info is in it:
                result.userData = loc
                self.resultFetched.emit(result)
        except Exception:
            self.log(message="Response processing failed.", log_level=1, push=True)
            return

    def triggerResult(self, result: QgsLocatorResult):
        """Triggers a filter result from this filter. This is called when one of the \
        results obtained by a call to fetchResults() is triggered by a user. \
        The filter subclass must implement logic here to perform the desired operation \
        for the search result. E.g. a file search filter would open file associated \
        with the triggered result.

        :param result: [description]
        :type result: QgsLocatorResult
        """
        if __debug__:
            self.log(
                message=f"DEBUG - Selected address: {result.displayString}", log_level=4
            )
        doc = result.userData
        x = doc["geometry"]["coordinates"][0]
        y = doc["geometry"]["coordinates"][1]

        centerPoint = QgsPointXY(x, y)
        dest_crs = QgsProject.instance().crs()
        results_crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        aTransform = QgsCoordinateTransform(
            results_crs, dest_crs, QgsProject.instance()
        )
        centerPointProjected = aTransform.transform(centerPoint)
        aTransform.transform(centerPoint)

        # centers to adress coordinates
        self.iface.mapCanvas().setCenter(centerPointProjected)

        # zoom policy has we don't have extent in the results
        scale = 25000

        type_adress = doc["properties"]["type"]

        if type_adress == "housenumber":
            scale = 2000
        elif type_adress == "street":
            scale = 5000
        elif type_adress == "locality":
            scale = 5000

        # finally zoom actually
        self.iface.mapCanvas().zoomScale(scale)
        self.iface.mapCanvas().refresh()

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(self.__class__.__name__, message)
