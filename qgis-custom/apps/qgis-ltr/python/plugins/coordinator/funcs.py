from math import floor

from PyQt5.Qt import QLocale, QCoreApplication

from qgis.core import QgsMessageLog

def coordinatorDmsStringsToDecimal(deg, minute, sec):
    result = 0.0
    if(len(deg)>0): result += QLocale().toFloat(deg)[0]
    if(len(minute)>0): result += QLocale().toFloat(minute)[0]/60
    if(len(sec)>0): result += QLocale().toFloat(sec)[0]/3600
    return result

def coordinatorDecimalToDms(deg):
    isNegative = deg < 0
    degree = int(floor(abs(deg)))
    deg2 = abs(deg)-degree
    minute = int(floor(deg2 * 60))
    seconds = ( deg2 % (1/60) ) * 3600

    return (isNegative, degree, minute, seconds)


def coordinatorLog(message):
    QgsMessageLog.logMessage(message, "Coordinator")

class CoordinatorTranslator:
    # noinspection PyMethodMayBeStatic
    def tr(message, disambugation = None):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString
        :param disambugation: an identifying string, for when the same sourceText is used in different roles within the same context
        :type disambugation: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CT', message, disambugation)
