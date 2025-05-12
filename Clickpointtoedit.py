# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Clickpointtoedit
                                 A QGIS plugin
 Clickpointtoedit
 Create Plugin By: https://github.com/Genroy
                              -------------------
        begin                : 2025-05-01
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Thamoon Kedkaew (CeJ)
        Author               : Thamoon Kedkaew (CeJ)
        email                : pongsakornche@gmail.com
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QPushButton, QVBoxLayout, QFormLayout, QLineEdit, QMessageBox, QWidget, QScrollArea
from .resources import *
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.core import QgsProject, QgsVectorLayer
import os.path
from datetime import datetime


class Clickpointtoedit:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', f'Clickpointtoedit_{locale}.qm')
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Clickpointtoedit')
        self.first_start = None
        self.tool = None
        self.dock = None
        self.fields = []

        self.initGui()

    def tr(self, message):
        return QCoreApplication.translate('Clickpointtoedit', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip:
            action.setStatusTip(status_tip)
        if whats_this:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/Clickpointtoedit/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Clickpointtoedit'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Clickpointtoedit'), action)
            self.iface.removeToolBarIcon(action)
        if self.dock:
            self.iface.removeDockWidget(self.dock)

    def run(self):
        if self.first_start:
            self.first_start = False

        layer = self.iface.activeLayer()

        if not isinstance(layer, QgsVectorLayer):
            self.iface.messageBar().pushWarning("No vector layer", "Please select a vector layer first.")
            return

        self.tool = QgsMapToolIdentifyFeature(self.canvas)
        self.tool.setLayer(layer)
        self.tool.featureIdentified.connect(self.onFeatureIdentified)
        self.canvas.setMapTool(self.tool)

    def onFeatureIdentified(self, feature):
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            return

        if not layer.isEditable():
            layer.startEditing()

        if self.dock:
            self.iface.removeDockWidget(self.dock)

        self.dock = QDockWidget("Edit Feature", self.iface.mainWindow())
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        form = QFormLayout()
        self.fields = []

        form_widget = QWidget()
        form_widget.setLayout(form)

        for field in layer.fields():
            value = feature[field.name()]
            line_edit = QLineEdit(str(value))
            self.fields.append((field.name(), line_edit))
            form.addRow(field.name(), line_edit)

        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_data(layer, feature.id(), feature))
        layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_action)
        layout.addWidget(cancel_btn)

        container = QWidget()
        container.setLayout(layout)
        self.dock.setWidget(container)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()

    def save_data(self, layer, feature_id, feature):
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "ยืนยันการบันทึก",
            "คุณต้องการบันทึกข้อมูลหรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        fields = layer.fields()
        success = True
        error_fields = []

        for name, widget in self.fields:
            value_str = widget.text()
            idx = fields.indexFromName(name)
            field = fields[idx]

            try:
                field_type = field.typeName().lower()

                # ❗❗❗ ข้าม Date และ DateTime ไปเลย ❗❗❗
                if field_type in ['date', 'datetime']:
                    continue

                if field_type in ['integer', 'int']:
                    value = int(value_str)
                elif field_type in ['double', 'real', 'float']:
                    value = float(value_str)
                else:
                    value = value_str

                layer.changeAttributeValue(feature_id, idx, value)

            except Exception:
                error_fields.append((name, field.typeName()))
                success = False

        if success:
            layer.commitChanges()
            QMessageBox.information(self.iface.mainWindow(), "บันทึกสำเร็จ", "ข้อมูลถูกบันทึกเรียบร้อยแล้ว")
            self.dock.close()
        else:
            message = "ข้อมูลบางช่องไม่ถูกต้อง:\n"
            for name, type_name in error_fields:
                message += f"• {name} (ต้องเป็น {type_name})\n"
            QMessageBox.warning(self.iface.mainWindow(), "เกิดข้อผิดพลาด", message)

    def cancel_action(self):
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "ยกเลิกการแก้ไข",
            "คุณแน่ใจหรือไม่ว่าต้องการยกเลิกการแก้ไข?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            layer = self.iface.activeLayer()
            layer.rollBack()
            QMessageBox.information(self.iface.mainWindow(), "ยกเลิกแล้ว", "การแก้ไขถูกยกเลิกเรียบร้อยแล้ว")
            self.dock.close()
