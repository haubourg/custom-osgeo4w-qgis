from PyQt5.QtCore import (QSettings, QUrl, Qt)
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox)

import os


class HtmlDialog(QDialog):

    def __init__(self, parent, url):
        QDialog.__init__(self, parent)

        self.resize(800, 600)

        l = QVBoxLayout()

        self.te = QTextBrowser(self)
        self.te.sourceChanged.connect(self.onSourceChanged)
        self.te.setOpenExternalLinks(True)
        if not url.startswith('http'):
            pwd = os.path.dirname(__file__)
            locale = QSettings().value("locale/userLocale")[0:2]
            file = "{}/doc/{}/{}".format(pwd, locale, url)
            if not os.path.isfile(file):
                file = "{}/doc/en/{}".format(pwd, url)
            self.te.setSource(QUrl.fromLocalFile(file))
        else:
            self.te.setSource(QUrl(url))

        btn = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal, self)
        btn.clicked.connect(self.close)

        l.addWidget(self.te)
        l.addWidget(btn)

        self.setLayout(l)

    def onSourceChanged(self, url):
        self.setWindowTitle(self.te.documentTitle())
