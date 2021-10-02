import sys
from qgis.PyQt.QtWidgets import QTextEdit, QDialog, QToolTip
from qgis.PyQt.QtCore import QEvent
from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt.Qt import QDesktopServices, QUrl, QApplication, Qt, QBrush, QTextCharFormat
from qgis.PyQt import uic
from os import path



class QTextEditEnhanced(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setMouseTracking(True)
        pluginPath = path.dirname(path.abspath(__file__))
        self.link_window = uic.loadUi(path.join(pluginPath, "ui/ui_hyperlink.ui"))

    def event(self, e):
        if e.type() == QEvent.ToolTip:
            pos = e.pos()
            pos.setX(pos.x() - self.viewportMargins().left())
            pos.setY(pos.y() - self.viewportMargins().top())
            cursor = self.cursorForPosition(pos)
            cursor.select(QTextCursor.WordUnderCursor)
            text = self.anchorAt(e.pos())
            if text:
                QToolTip.showText(e.globalPos(), f"{text} [Ctrl + click]" )
            else:
                QToolTip.hideText()
            return True
        return super().event(e)

    def mouseMoveEvent(self, e): 
        if self.anchorAt(e.pos()):
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            menu = self.createStandardContextMenu()
            menu.addSeparator()
            addHyperLinkAction = menu.addAction("Add Hyperlink")
            action = menu.exec_(self.mapToGlobal(e.pos()))
            if action == addHyperLinkAction:
                self.showAddHyperLinkUi()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.modifiers() == Qt.ControlModifier:
            url = QUrl.fromLocalFile(self.anchorAt(e.pos()))
            QDesktopServices.openUrl(url)
        super().mouseReleaseEvent(e)

    def showAddHyperLinkUi(self):
        self.link_window.eText.setText(self.textCursor().selectedText())
        self.link_window.eLink.clear()
        if self.link_window.exec_() == QDialog.Accepted:
            linkName = self.link_window.eText.text()
            linkAddress = self.link_window.eLink.text()
            cursor = self.textCursor()
            cursor.insertHtml(
                '<a href="%s">%s</a>' % (linkAddress, linkName))
            charFormat = QTextCharFormat()
            charFormat.setForeground(QBrush())
            cursor.insertText(" ", charFormat)
