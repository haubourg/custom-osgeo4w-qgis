#! python3  # noqa: E265


def classFactory(iface):  # pylint: disable=invalid-name
    """Load NominatimFilterPlugin class from file nominatimfilter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin_main import LocatorFilterPlugin

    return LocatorFilterPlugin(iface)
