# clickpointtoedit
When click spatial vector in map canvas will be open edit to record to change 

# 🖱️ Clickpointtoedit - A QGIS Plugin

**EN:**  
Clickpointtoedit is a QGIS plugin that allows users to click on a feature (point, line, or polygon) on the map and directly edit its attribute values through a user-friendly dock panel. The plugin is especially useful for fast data correction workflows without using the attribute table.

🔧 Features
Identify and edit vector feature attributes by clicking on the map

Displays a scrollable form with all editable fields

Supports Integer, Float, and String field types

Automatically skips unsupported types like Date and DateTime

Safe editing with Save and Cancel buttons

🚀 Getting Started
Open QGIS and load a vector layer

Activate the plugin by clicking the Clickpointtoedit icon from the toolbar

Click on any feature in the map canvas

A dock panel will appear with editable fields

Make your changes and click Save or Cancel

📁 Installation
Clone or download this repository:

bash
Copy
Edit
git clone https://github.com/Genroy/Clickpointtoedit.git
Copy the plugin folder into your QGIS plugin directory:

On Windows:
C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins

On macOS/Linux:
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins

Open QGIS and enable the plugin from Plugins > Manage and Install Plugins


Author / ผู้พัฒนา
Thamoon Kedkaew (CeJ)
Email: pongsakornche@gmail.com
GitHub: https://github.com/Genroy

📝 License
-

**TH:**  
Clickpointtoedit เป็นปลั๊กอินสำหรับ QGIS ที่ให้ผู้ใช้สามารถคลิกที่ Feature บนแผนที่ เพื่อแก้ไขข้อมูลคุณลักษณะ (Attribute) ได้ทันทีผ่านแถบด้านข้าง (Dock Panel) โดยไม่ต้องเปิดตารางคุณลักษณะ ใช้งานง่าย เหมาะสำหรับงานแก้ไขข้อมูลภาคสนามหรืองานตรวจสอบข้อมูล

---

## 🔧 Features / ฟีเจอร์หลัก

- Identify and edit vector feature attributes by clicking on the map  
  คลิกที่ Feature แล้วแก้ไขข้อมูลได้ทันที
- Shows all editable fields in a scrollable form  
  แสดงฟอร์มสำหรับกรอกข้อมูลที่เลื่อนดูได้
- Supports `Integer`, `Float`, and `String` fields  
  รองรับข้อมูลประเภท ตัวเลข จำนวนเต็ม ทศนิยม และข้อความ
- Automatically skips non-editable types like `Date` and `DateTime`  
  ข้ามช่องวันที่หรือชนิดข้อมูลที่ไม่เหมาะสมโดยอัตโนมัติ
- Safe data editing with **Save** and **Cancel** actions  
  มีปุ่มบันทึกและยกเลิกเพื่อความปลอดภัยของข้อมูล

---

## 🚀 Getting Started / การใช้งานเบื้องต้น

1. Open QGIS and load a vector layer  
   เปิด QGIS แล้วโหลดชั้นข้อมูลเวกเตอร์
2. Activate the plugin via the **Clickpointtoedit** icon  
   คลิกเปิดปลั๊กอินจากแถบเครื่องมือ
3. Click on any feature to open the edit form  
   คลิกที่ Feature เพื่อเรียกแบบฟอร์มแก้ไข
4. Edit the fields and press **Save** or **Cancel**  
   แก้ไขข้อมูลแล้วกด "Save" หรือ "Cancel"

---

## 📁 Installation / การติดตั้ง

1. Clone or download this repository  
   ดาวน์โหลดหรือโคลนโปรเจกต์นี้:
   ```bash
   git clone https://github.com/Genroy/Clickpointtoedit.git

Copy the folder into your QGIS plugins directory
คัดลอกโฟลเดอร์ไปไว้ในโฟลเดอร์ปลั๊กอินของ QGIS:

Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\

Restart QGIS and enable the plugin from the Plugin Manager
รีสตาร์ท QGIS แล้วเปิดใช้งานปลั๊กอินจาก Plugin Manager


Author / ผู้พัฒนา
Thamoon Kedkaew (CeJ)
Email: pongsakornche@gmail.com
GitHub: https://github.com/Genroy

📝 License
-

