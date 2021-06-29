# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'W:\GitHub\mask\mask\ui_layer_list.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LayerListWidget(object):
    def setupUi(self, LayerListWidget):
        LayerListWidget.setObjectName("LayerListWidget")
        LayerListWidget.resize(768, 438)
        self.verticalLayout = QtWidgets.QVBoxLayout(LayerListWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(LayerListWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.polygonOperatorCombo = QtWidgets.QComboBox(LayerListWidget)
        self.polygonOperatorCombo.setObjectName("polygonOperatorCombo")
        self.polygonOperatorCombo.addItem("")
        self.polygonOperatorCombo.addItem("")
        self.polygonOperatorCombo.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.polygonOperatorCombo)
        self.label_2 = QtWidgets.QLabel(LayerListWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineOperatorCombo = QtWidgets.QComboBox(LayerListWidget)
        self.lineOperatorCombo.setObjectName("lineOperatorCombo")
        self.lineOperatorCombo.addItem("")
        self.lineOperatorCombo.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineOperatorCombo)
        self.verticalLayout.addLayout(self.formLayout)
        self.layerTable = QtWidgets.QTableWidget(LayerListWidget)
        self.layerTable.setObjectName("layerTable")
        self.layerTable.setColumnCount(2)
        self.layerTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.layerTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.layerTable.setHorizontalHeaderItem(1, item)
        self.layerTable.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.layerTable)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectAllBtn = QtWidgets.QPushButton(LayerListWidget)
        self.selectAllBtn.setObjectName("selectAllBtn")
        self.horizontalLayout.addWidget(self.selectAllBtn)
        self.unselectAllBtn = QtWidgets.QPushButton(LayerListWidget)
        self.unselectAllBtn.setObjectName("unselectAllBtn")
        self.horizontalLayout.addWidget(self.unselectAllBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(LayerListWidget)
        self.polygonOperatorCombo.setCurrentIndex(0)
        self.lineOperatorCombo.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(LayerListWidget)

    def retranslateUi(self, LayerListWidget):
        _translate = QtCore.QCoreApplication.translate
        LayerListWidget.setWindowTitle(_translate("LayerListWidget", "Form"))
        self.label.setText(_translate("LayerListWidget", "Function used for labeling filtering on polygons"))
        self.polygonOperatorCombo.setItemText(0, _translate("LayerListWidget", "Exact (slow and will disable simplification)"))
        self.polygonOperatorCombo.setItemText(1, _translate("LayerListWidget", "The mask geometry contains the centroid"))
        self.polygonOperatorCombo.setItemText(2, _translate("LayerListWidget", "The mask geometry contains a point on the polygon surface"))
        self.label_2.setText(_translate("LayerListWidget", "Function used for labeling filtering on lines"))
        self.lineOperatorCombo.setItemText(0, _translate("LayerListWidget", "The mask geometry intersects the line"))
        self.lineOperatorCombo.setItemText(1, _translate("LayerListWidget", "The mask geometry contains the line"))
        item = self.layerTable.horizontalHeaderItem(0)
        item.setText(_translate("LayerListWidget", "Limit"))
        item = self.layerTable.horizontalHeaderItem(1)
        item.setText(_translate("LayerListWidget", "Layer"))
        self.selectAllBtn.setText(_translate("LayerListWidget", "Select all"))
        self.unselectAllBtn.setText(_translate("LayerListWidget", "Unselect all"))

