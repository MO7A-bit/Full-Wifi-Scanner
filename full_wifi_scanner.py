import sys
import subprocess
import re
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QMessageBox, QListWidgetItem, QTextEdit, QFileDialog,
    QHBoxLayout, QComboBox, QLabel, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from reportlab.pdfgen import canvas

# --- Language Dictionary ---
LANGUAGES = {
    "ENG": {
        "scan": "Scan WiFi Networks",
        "save": "Save Info",
        "copy": "Copy Info",
        "export": "Export All Networks",
        "dark": "Toggle Dark Mode",
        "saved_pw": "Saved Password",
        "not_found": "(not found)",
        "not_connected": "You didn't connect to this WiFi before.",
        "no_info": "No WiFi info to save.",
        "no_data": "No WiFi networks to export.",
        "copied": "Current WiFi info copied to clipboard.",
        "saved": "WiFi info saved to:\n",
        "exported": "All networks exported to:\n",
        "title": "Full WiFi Scanner"
    },
    "FR": {
        "scan": "Scanner les réseaux WiFi",
        "save": "Enregistrer les infos",
        "copy": "Copier les infos",
        "export": "Exporter tous les réseaux",
        "dark": "Mode sombre",
        "saved_pw": "Mot de passe enregistré",
        "not_found": "(introuvable)",
        "not_connected": "Vous ne vous êtes pas encore connecté à ce WiFi.",
        "no_info": "Aucune info WiFi à enregistrer.",
        "no_data": "Aucun réseau WiFi à exporter.",
        "copied": "Les infos WiFi ont été copiées dans le presse-papiers.",
        "saved": "Infos WiFi enregistrées dans :\n",
        "exported": "Tous les réseaux ont été exportés vers :\n",
        "title": "Scanner WiFi Complet"
    },
    "ARB": {
        "scan": "مسح الشبكات اللاسلكية",
        "save": "حفظ المعلومات",
        "copy": "نسخ المعلومات",
        "export": "تصدير جميع الشبكات",
        "dark": "الوضع الداكن",
        "saved_pw": "كلمة المرور المحفوظة",
        "not_found": "(غير موجود)",
        "not_connected": "لم تتصل بهذه الشبكة من قبل.",
        "no_info": "لا توجد معلومات WiFi للحفظ.",
        "no_data": "لا توجد شبكات WiFi للتصدير.",
        "copied": "تم نسخ معلومات WiFi إلى الحافظة.",
        "saved": "تم حفظ معلومات WiFi في:\n",
        "exported": "تم تصدير جميع الشبكات إلى:\n",
        "title": "فاحص الشبكات اللاسلكية"
    }
}

# --- Utility Functions ---
def parse_networks():
    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            encoding="utf-8", errors='ignore'
        )
    except Exception:
        return []
    blocks = result.split("SSID ")[1:]
    networks = []
    for block in blocks:
        ssid_match = re.search(r": (.+)", block)
        ssid = ssid_match.group(1).strip() if ssid_match else "Unknown"
        auth = re.search(r"Authentication\s+:\s(.+)", block)
        encryption = re.search(r"Encryption\s+:\s(.+)", block)
        signal = re.search(r"Signal\s+:\s(\d+)%", block)
        radio_type = re.search(r"Radio type\s+:\s(.+)", block)
        channel = re.search(r"Channel\s+:\s(\d+)", block)
        network_type = re.search(r"Network type\s+:\s(.+)", block)
        signal_strength = int(signal.group(1)) if signal else 0
        estimated_speed = estimate_speed(signal_strength)
        networks.append({
            "SSID": ssid,
            "Authentication": auth.group(1).strip() if auth else "",
            "Encryption": encryption.group(1).strip() if encryption else "",
            "Signal": f"{signal_strength}%",
            "Estimated Speed": estimated_speed,
            "Radio Type": radio_type.group(1).strip() if radio_type else "",
            "Channel": channel.group(1).strip() if channel else "",
            "Network Type": network_type.group(1).strip() if network_type else ""
        })
    return networks

def estimate_speed(signal_strength):
    if signal_strength > 80:
        return "600+ Mbps"
    elif signal_strength > 60:
        return "300 Mbps"
    elif signal_strength > 40:
        return "150 Mbps"
    elif signal_strength > 20:
        return "75 Mbps"
    else:
        return "<50 Mbps"

def get_saved_profiles():
    try:
        profiles_output = subprocess.check_output(
            ["netsh", "wlan", "show", "profiles"], encoding="utf-8"
        )
        return re.findall(r"All User Profile\s*:\s(.*)", profiles_output)
    except Exception:
        return []

def get_wifi_password(profile_name):
    try:
        profile_info = subprocess.check_output(
            ["netsh", "wlan", "show", "profile", profile_name, "key=clear"],
            encoding="utf-8"
        )
        password_match = re.search(r"Key Content\s*:\s(.*)", profile_info)
        return password_match.group(1) if password_match else None
    except subprocess.CalledProcessError:
        return None

def get_connected_network_info():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"], encoding="utf-8"
        )
        ssid = re.search(r"^\s*SSID\s*:\s(.+)$", output, re.MULTILINE)
        signal = re.search(r"^\s*Signal\s*:\s(\d+)%", output, re.MULTILINE)
        speed = re.search(r"^\s*Receive rate \(Mbps\)\s*:\s(.+)$", output, re.MULTILINE)
        if ssid and signal:
            return {
                "SSID": ssid.group(1).strip(),
                "Signal": f"{signal.group(1)}%",
                "Speed": f"{speed.group(1).strip()} Mbps" if speed else "Unknown"
            }
    except Exception:
        pass
    return None

# --- Main App Class ---
class WifiScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "ENG"
        self.dark_mode = False
        self.network_data = []
        self.full_text = ""
        self.displayed_text = ""
        self.char_index = 0

        self.setWindowTitle(LANGUAGES[self.lang]["title"])
        self.setGeometry(100, 100, 800, 750)
        self.setMinimumSize(600, 600)

        # --- Layouts ---
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        button_row = QHBoxLayout()

        # --- Header ---
        self.title_label = QLabel(LANGUAGES[self.lang]["title"])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(self.title_label)

        # --- Language Selector ---
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["ENG", "FR", "ARB"])
        self.lang_selector.currentTextChanged.connect(self.set_language)
        self.lang_selector.setMaximumWidth(120)
        header_layout.addWidget(self.lang_selector)

        main_layout.addLayout(header_layout)

        # --- Buttons ---
        self.scan_button = QPushButton()
        self.scan_button.clicked.connect(self.scan_wifi)
        self.save_button = QPushButton()
        self.save_button.clicked.connect(self.save_to_file)
        self.save_button.setEnabled(False)
        self.copy_button = QPushButton()
        self.copy_button.clicked.connect(self.copy_info)
        self.copy_button.setEnabled(False)
        self.export_all_button = QPushButton()
        self.export_all_button.clicked.connect(self.export_all_networks)
        self.dark_button = QPushButton()
        self.dark_button.clicked.connect(self.toggle_dark_mode)

        for btn in [self.scan_button, self.save_button, self.copy_button, self.export_all_button, self.dark_button]:
            btn.setMinimumHeight(32)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_row.addWidget(btn)

        main_layout.addLayout(button_row)

        # --- Network List ---
        self.network_list = QListWidget()
        self.network_list.itemClicked.connect(self.display_info)
        self.network_list.setMaximumHeight(180)
        main_layout.addWidget(self.network_list)

        # --- Output Box ---
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("font-family: Courier; font-size: 13pt; background: #f7f7fa;")
        main_layout.addWidget(self.output_box)

        # --- Chart ---
        self.chart = PlotWidget()
        self.chart.setBackground('w')
        main_layout.addWidget(self.chart)

        self.setLayout(main_layout)

        # --- Typing Animation ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_char)

        self.set_language(self.lang)

    def set_language(self, lang):
        self.lang = lang
        t = LANGUAGES[lang]
        self.setWindowTitle(t["title"])
        self.title_label.setText(t["title"])
        self.scan_button.setText(t["scan"])
        self.save_button.setText(t["save"])
        self.copy_button.setText(t["copy"])
        self.export_all_button.setText(t["export"])
        self.dark_button.setText(t["dark"])

    def scan_wifi(self):
        self.network_list.clear()
        self.output_box.clear()
        self.chart.clear()
        self.save_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.network_data = parse_networks()
        for net in self.network_data:
            self.network_list.addItem(QListWidgetItem(net["SSID"]))
        # Plot signal strengths
        if self.network_data:
            ssids = [n["SSID"] for n in self.network_data]
            signals = [int(n["Signal"].replace('%', '')) for n in self.network_data]
            bg = 'k' if self.dark_mode else 'w'
            self.chart.setBackground(bg)
            bargraph = pg.BarGraphItem(x=range(len(ssids)), height=signals, width=0.6, brush='g')
            self.chart.clear()
            self.chart.addItem(bargraph)
            self.chart.getAxis('bottom').setTicks([list(enumerate(ssids))])

    def display_info(self, item):
        ssid = item.text()
        net_info = next((n for n in self.network_data if n["SSID"] == ssid), None)
        if not net_info:
            return
        t = LANGUAGES[self.lang]
        # Try to get real info if this is the connected network
        connected = get_connected_network_info()
        if connected and connected["SSID"] == ssid:
            net_info["Signal"] = connected["Signal"]
            net_info["Estimated Speed"] = connected["Speed"]
        info = (
            f"SSID: {net_info['SSID']}\n"
            f"Signal: {net_info['Signal']}\n"
            f"Estimated Speed: {net_info['Estimated Speed']}\n"
            f"Authentication: {net_info['Authentication']}\n"
            f"Encryption: {net_info['Encryption']}\n"
            f"Radio Type: {net_info['Radio Type']}\n"
            f"Channel: {net_info['Channel']}\n"
            f"Network Type: {net_info['Network Type']}\n"
        )
        saved_profiles = get_saved_profiles()
        if ssid in saved_profiles:
            password = get_wifi_password(ssid)
            info += f"{t['saved_pw']}: {password if password else t['not_found']}\n"
        else:
            info += t["not_connected"] + "\n"
        self.start_typing(info)
        self.save_button.setEnabled(True)
        self.copy_button.setEnabled(True)

    def start_typing(self, text):
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        self.output_box.clear()
        self.timer.start(10)

    def type_next_char(self):
        if self.char_index < len(self.full_text):
            self.displayed_text += self.full_text[self.char_index]
            self.output_box.setPlainText(self.displayed_text)
            self.char_index += 1
        else:
            self.timer.stop()

    def save_to_file(self):
        t = LANGUAGES[self.lang]
        text = self.output_box.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Info", t["no_info"])
            return
        path, _ = QFileDialog.getSaveFileName(self, t["save"], "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Info", t["saved"] + path)

    def copy_info(self):
        t = LANGUAGES[self.lang]
        text = self.output_box.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Info", t["no_info"])
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Info", t["copied"])

    def export_all_networks(self):
        t = LANGUAGES[self.lang]
        if not self.network_data:
            QMessageBox.information(self, "Info", t["no_data"])
            return
        path, _ = QFileDialog.getSaveFileName(self, t["export"], "", "PDF Files (*.pdf);;All Files (*)")
        if path:
            c = canvas.Canvas(path)
            y = 800
            for net in self.network_data:
                c.drawString(30, y, f"SSID: {net['SSID']}, Signal: {net['Signal']}, Speed: {net['Estimated Speed']}")
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 800
            c.save()
            QMessageBox.information(self, "Info", t["exported"] + path)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("background-color: #222; color: #eee;")
            self.output_box.setStyleSheet("background-color: #222; color: #eee; font-family: Courier; font-size: 13pt;")
            self.chart.setBackground('k')
        else:
            self.setStyleSheet("")
            self.output_box.setStyleSheet("font-family: Courier; font-size: 13pt; background: #f7f7fa;")
            self.chart.setBackground('w')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WifiScannerApp()
    window.show()
    sys.exit(app.exec_())