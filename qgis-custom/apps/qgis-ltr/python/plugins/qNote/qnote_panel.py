# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QDockWidget, QAction
from qgis.PyQt.QtGui import QIcon, QFont, QTextListFormat
from qgis.PyQt.Qt import Qt
from qgis.PyQt import uic
from os import path


pluginPath = path.dirname(path.abspath(__file__))
FORM_CLASS, _ = uic.loadUiType(path.join(pluginPath, 'ui/ui_panel.ui'))

class MainPanel(QDockWidget, FORM_CLASS):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.bold_action = QAction( QIcon(path.join(pluginPath, "icons/bold.png")), "Bold" )
        self.bold_action.triggered.connect(self.setBold)
        self.toolbar.addAction( self.bold_action )

        self.italic_action = QAction( QIcon(path.join(pluginPath, "icons/italic.png")), "Italic" )
        self.italic_action.triggered.connect(self.setItalic)
        self.toolbar.addAction( self.italic_action )

        self.underline_action = QAction( QIcon(path.join(pluginPath, "icons/underline.png")), "Underline" )
        self.underline_action.triggered.connect(self.setUnderline)
        self.toolbar.addAction( self.underline_action )

        self.strike_action = QAction( QIcon(path.join(pluginPath, "icons/strikethrough.png")), "Strike" )
        self.strike_action.triggered.connect(self.setStrike)
        self.toolbar.addAction( self.strike_action )

        self.toolbar.addSeparator()

        self.bullet_list_action = QAction( QIcon(path.join(pluginPath, "icons/bullet_list.png")), "Insert bullet list" )
        self.bullet_list_action.triggered.connect(self.setBulletList)
        self.toolbar.addAction( self.bullet_list_action )

        self.number_list_action = QAction( QIcon(path.join(pluginPath, "icons/number_list.png")), "Insert number list" )
        self.number_list_action.triggered.connect(self.setNumberList)
        self.toolbar.addAction( self.number_list_action )

        self.toolbar.addSeparator()

        self.add_hyperlink = QAction( QIcon(path.join(pluginPath, "icons/hyperlink.jpg")), "Add hyperlink" )
        self.add_hyperlink.triggered.connect(self.addHyperlink)
        self.toolbar.addAction( self.add_hyperlink )

        self.toolbar.addSeparator()

        self.undo = QAction( QIcon(path.join(pluginPath, "icons/undo.png")), "Undo" )
        self.undo.triggered.connect(self.edit.undo )
        self.toolbar.addAction( self.undo )
        self.edit.undoAvailable.connect( self.undo.setEnabled )

        self.redo = QAction( QIcon(path.join(pluginPath, "icons/redo.png")), "Redo" )
        self.redo.triggered.connect(self.edit.redo )
        self.toolbar.addAction( self.redo )
        self.edit.redoAvailable.connect( self.redo.setEnabled )
    
    def addHyperlink(self):
        self.edit.showAddHyperLinkUi()
    
    def setBold(self):
        if self.edit.fontWeight() == QFont.Bold:
            self.edit.setFontWeight(QFont.Normal)
        else:
            self.edit.setFontWeight(QFont.Bold)
    
    def setItalic(self):
        state = self.edit.fontItalic()
        self.edit.setFontItalic(not state)

    def setUnderline(self):
        state = self.edit.fontUnderline()
        self.edit.setFontUnderline(not state)

    def setStrike(self):
        fmt = self.edit.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.edit.setCurrentCharFormat(fmt)

    def setBulletList(self):
        cursor = self.edit.textCursor()
        cursor.insertList(QTextListFormat.ListDisc)

    def setNumberList(self):
        cursor = self.edit.textCursor()
        cursor.insertList(QTextListFormat.ListDecimal)
