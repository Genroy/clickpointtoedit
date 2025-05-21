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


from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QPushButton, QVBoxLayout, QFormLayout, QLineEdit, QMessageBox, QWidget, QScrollArea, QFileDialog
from qgis.gui import QgsMapToolIdentifyFeature, QgsHighlight
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsFeatureRequest
from PyQt5.QtCore import QVariant
import os.path
import csv
from datetime import datetime
import codecs


class CustomIdentifyTool(QgsMapToolIdentifyFeature):
    feature_clicked = pyqtSignal(object)

    def __init__(self, canvas, layer):
        super().__init__(canvas)
        self.canvas = canvas
        self._layer = layer
        self.setLayer(layer)

    def canvasReleaseEvent(self, event):
        results = self.identify(event.x(), event.y(), [self._layer], self.TopDownStopAtFirst)
        if results:
            feature = results[0].mFeature
            self.feature_clicked.emit(feature)


class Clickpointtoedit:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&Clickpointtoedit')
        self.first_start = None
        self.tool = None
        self.dock = None
        self.fields = []
        self.highlight = None
        self.saved_highlights = []
        self.action = None
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
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu(self.menu, self.action)
        self.action = self.add_action(
            icon_path,
            text=self.tr(u'Turn on Edit เปิดโหมดแก้ไขข้อมูล'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock = None

    def run(self):
        if self.first_start:
            self.first_start = False
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            self.iface.messageBar().pushWarning("No vector layer", "Please select a vector layer first.")
            return
        self.tool = CustomIdentifyTool(self.canvas, layer)
        self.tool.feature_clicked.connect(self.onFeatureIdentified)
        self.canvas.setMapTool(self.tool)

    def onFeatureIdentified(self, feature):
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            return
        if self.highlight:
            self.highlight.hide()
            self.highlight = None
        self.saved_highlights = []
        self.highlight = QgsHighlight(self.canvas, feature.geometry(), layer)
        self.highlight.setColor(Qt.red)
        self.highlight.setWidth(3)
        self.highlight.show()
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
        save_btn.clicked.connect(lambda: self.confirm_save(layer, feature.id(), feature))
        layout.addWidget(save_btn)

        export_btn = QPushButton("Export Log Report Edit")
        export_btn.clicked.connect(self.export_layer_and_log)
        layout.addWidget(export_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_action)
        layout.addWidget(cancel_btn)

        container = QWidget()
        container.setLayout(layout)
        self.dock.setWidget(container)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()

    def save_data(self, layer, feature_id, feature):
        if not layer.isEditable():
            return
        fields = layer.fields()
        for name, widget in self.fields:
            value_str = widget.text()
            if value_str.strip() == "":
                continue
            idx = fields.indexFromName(name)
            field = fields[idx]
            try:
                field_type = field.typeName().lower()
                if field_type in ['date', 'datetime']:
                    continue
                elif field_type in ['integer', 'int']:
                    value = int(value_str)
                elif field_type in ['double', 'real', 'float']:
                    value = float(value_str)
                else:
                    value = value_str
                layer.changeAttributeValue(feature_id, idx, value)
            except:
                pass
        layer.commitChanges()

        green_highlight = QgsHighlight(self.canvas, feature.geometry(), layer)
        green_highlight.setColor(Qt.green)
        green_highlight.setWidth(3)
        green_highlight.show()
        self.saved_highlights.append(green_highlight)

        log_path = os.path.join(os.path.expanduser("~"), "edit_log.csv")
        with open(log_path, "a", newline="", encoding="utf-8") as logfile:
            writer = csv.writer(logfile)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), layer.name(), feature_id])

        QMessageBox.information(self.iface.mainWindow(), "Ok บันทึกสำเร็จ", "Data have saved ข้อมูลถูกบันทึกเรียบร้อยแล้ว")
        self.dock.close()

    def confirm_save(self, layer, feature_id, feature):
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Confirm ? ยืนยันการบันทึก",
            "Do you Confirm to save ? คุณแน่ใจหรือไม่ว่าต้องการบันทึกการแก้ไขนี้?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.save_data(layer, feature_id, feature)

    def cancel_action(self):
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Cancle ? ยกเลิกการแก้ไข",
            "Do you Confirm to cancle ? คุณแน่ใจหรือไม่ว่าต้องการยกเลิกการแก้ไข?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            layer = self.iface.activeLayer()
            layer.rollBack()
            QMessageBox.information(self.iface.mainWindow(), "Cancled ยกเลิกแล้ว", "Edit to cancle การแก้ไขถูกยกเลิกเรียบร้อยแล้ว")
            self.dock.close()

    def export_layer_and_log(self):
        log_path = os.path.join(os.path.expanduser("~"), "edit_log.csv")
        edited_data = {}  # {feature_id: timestamp}

        # อ่านข้อมูล log
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as logfile:
                for line in logfile:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        try:
                            fid = int(parts[2])
                            timestamp = parts[0]
                            edited_data[fid] = timestamp
                        except ValueError:
                            continue

        layer = self.iface.activeLayer()
        if not layer:
            QMessageBox.warning(self.iface.mainWindow(), "No Feature layer ไม่มีชั้นข้อมูล", "Please select layers before Export please. กรุณาเลือกชั้นข้อมูลก่อน export")
            return

        # เลือกตำแหน่งบันทึก CSV
        csv_path, _ = QFileDialog.getSaveFileName(None, "Save CSV File", "", "CSV Files (*.csv)")
        if not csv_path:
            return  # ผู้ใช้ยกเลิก

        # เขียน CSV
        try:
            with codecs.open(csv_path, "w", "utf-8-sig") as file:
                writer = csv.writer(file)
                headers = [field.name() for field in layer.fields()] + ["edited_at"]
                writer.writerow(headers)

                for feature in layer.getFeatures():
                    if feature.id() in edited_data:
                        values = [feature[field.name()] for field in layer.fields()]
                        values.append(edited_data[feature.id()])
                        writer.writerow(values)

            # ✅ ถามว่าจะล้าง log หรือไม่
            reply = QMessageBox.question(
                self.iface.mainWindow(),
                "Clear Log ? ล้าง Log?",
                "Do you clear to log after Export log ? คุณต้องการล้างประวัติการแก้ไข (log) หลังจาก export หรือไม่?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    with open(log_path, "w", encoding="utf-8") as logfile:
                        logfile.write("")
                    QMessageBox.information(self.iface.mainWindow(), "ล้าง Log สำเร็จ", "Log ถูกล้างเรียบร้อยแล้ว")
                except Exception as e:
                    QMessageBox.warning(self.iface.mainWindow(), "Error เกิดข้อผิดพลาด", f"Canot to clear logs ไม่สามารถล้าง log ได้:\n{str(e)}")

        except Exception as e:
            QMessageBox.warning(self.iface.mainWindow(), "Error เกิดข้อผิดพลาด", f"Can/t export to CSV. ไม่สามารถ export CSV ได้:\n{str(e)}")

