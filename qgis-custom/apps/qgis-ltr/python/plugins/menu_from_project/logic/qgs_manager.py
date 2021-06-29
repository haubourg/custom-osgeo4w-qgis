#! python3  # noqa: E265

"""
    Functions used to manage QGIS Projects: read, extract, get properties.
"""

# Standard library
import logging
import os
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

# PyQGIS
from qgis.core import QgsFileDownloader, QgsReadWriteContext
from qgis.PyQt import QtXml
from qgis.PyQt.QtCore import (
    QDir,
    QEventLoop,
    QFile,
    QFileInfo,
    QIODevice,
    QTemporaryDir,
    QTemporaryFile,
    QUrl,
)

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Functions #############
# ##################################


def is_absolute(doc: QtXml.QDomDocument) -> bool:
    """Return true if the given XML document is using absolute path.

    :param doc: The QGIS project as XML document.
    :type doc: QDomDocument
    """
    absolute = False
    try:
        props = doc.elementsByTagName("properties")
        if props.count() == 1:
            node = props.at(0)
            pathNode = node.namedItem("Paths")
            absNode = pathNode.namedItem("Absolute")
            absolute = "true" == absNode.firstChild().toText().data()
    except Exception:
        pass

    return absolute


def get_project_title(doc: QtXml.QDomDocument) -> str:
    """Return the project title defined in the XML document.

    :param doc: The QGIS project as XML document. Default to None.
    :type doc: QDomDocument

    :return: The title or None.
    :rtype: string
    """
    tags = doc.elementsByTagName("qgis")
    if tags.count():
        node = tags.at(0)
        title_node = node.namedItem("title")
        return title_node.firstChild().toText().data()

    return None


def read_from_file(uri: str) -> Tuple[QtXml.QDomDocument, str]:
    """Read a QGIS project (.qgs and .qgz) from a file path and returns d

    :param uri: path to the file
    :type uri: str

    :return: a tuple with XML document and the filepath.
    :rtype: Tuple[QtXml.QDomDocument, str]
    """
    doc = QtXml.QDomDocument()
    file = QFile(uri)
    if (
        file.exists()
        and file.open(QIODevice.ReadOnly | QIODevice.Text)
        and QFileInfo(file).suffix() == "qgs"
    ):
        doc.setContent(file)
        project_path = uri

    elif file.exists() and (QFileInfo(file).suffix() == "qgz"):
        temporary_unzip = QTemporaryDir()
        temporary_unzip.setAutoRemove(False)
        with zipfile.ZipFile(uri, "r") as zip_ref:
            zip_ref.extractall(temporary_unzip.path())

        project_filename = QDir(temporary_unzip.path()).entryList(["*.qgs"])[0]
        project_path = os.path.join(temporary_unzip.path(), project_filename)
        xml = QFile(project_path)
        if xml.open(QIODevice.ReadOnly | QIODevice.Text):
            doc.setContent(xml)

    return doc, project_path


def read_from_database(uri: str, project_registry) -> Tuple[QtXml.QDomDocument, str]:
    """Read a QGIS project stored into a (PostgreSQL) database.

    :param uri: connection string to QGIS project stored into a database.
    :type uri: str

    :return: a tuple with XML document and the filepath.
    :rtype: Tuple[QtXml.QDomDocument, str]
    """
    doc = QtXml.QDomDocument()
    # uri PG
    project_storage = project_registry.projectStorageFromUri(uri)

    temporary_zip = QTemporaryFile()
    temporary_zip.open()
    zip_project = temporary_zip.fileName()

    project_storage.readProject(uri, temporary_zip, QgsReadWriteContext())

    temporary_unzip = QTemporaryDir()
    temporary_unzip.setAutoRemove(False)
    with zipfile.ZipFile(zip_project, "r") as zip_ref:
        zip_ref.extractall(temporary_unzip.path())

    project_filename = QDir(temporary_unzip.path()).entryList(["*.qgs"])[0]
    project_path = os.path.join(temporary_unzip.path(), project_filename)
    xml = QFile(project_path)
    if xml.open(QIODevice.ReadOnly | QIODevice.Text):
        doc.setContent(xml)

    return doc, project_path


@lru_cache()
def read_from_http(uri: str, cache_folder: Path):
    """Read a QGIS project stored into on a remote web server accessible through HTTP.

    :param uri: web URL to the QGIS project
    :type uri: str

    :return: a tuple with XML document and the filepath.
    :rtype: Tuple[QtXml.QDomDocument, str]
    """
    # get filename from URL parts
    parsed = urlparse(uri)
    if not parsed.path.rpartition("/")[2].endswith((".qgs", ".qgz")):
        raise ValueError(
            "URI doesn't ends with QGIS project extension (.qgs or .qgz): {}".format(
                uri
            )
        )
    cached_filepath = cache_folder / parsed.path.rpartition("/")[2]

    # download it
    loop = QEventLoop()
    project_download = QgsFileDownloader(
        url=QUrl(uri), outputFileName=str(cached_filepath), delayStart=True
    )
    project_download.downloadExited.connect(loop.quit)
    project_download.startDownload()
    loop.exec_()

    return read_from_file(str(cached_filepath))
