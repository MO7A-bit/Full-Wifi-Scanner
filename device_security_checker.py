import sys
import platform
import socket
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QProgressBar,
    QFileDialog, QHBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer

LANGS = {
    "English": {
        "title": "🔒 Simple Security Scanner",
        "scan": "Run Security Scan",
        "save": "Save Report",
        "os_info": "=== OS Information ===",
        "firewall": "=== Firewall Status ===",
        "network": "=== Network Information ===",
        "disk": "=== Disk Usage ===",
        "process": "=== Top Processes ===",
        "choose_lang": "Choose your language:",
        "welcome": "Welcome! Please select your language and click Start.",
        "start": "Start",
        "logo_alt": "App Logo"
    },
    "العربية": {
        "title": "🔒 فاحص الأمان البسيط",
        "scan": "ابدأ الفحص",
        "save": "حفظ التقرير",
        "os_info": "=== معلومات النظام ===",
        "firewall": "=== حالة الجدار الناري ===",
        "network": "=== معلومات الشبكة ===",
        "disk": "=== استخدام القرص ===",
        "process": "=== أكثر العمليات استهلاكًا للذاكرة ===",
        "choose_lang": "اختر لغتك:",
        "welcome": "مرحبًا! اختر اللغة واضغط بدء.",
        "start": "بدء",
        "logo_alt": "شعار التطبيق"
    },
    "Français": {
        "title": "🔒 Scanner de Sécurité Simple",
        "scan": "Lancer l'analyse",
        "save": "Enregistrer le rapport",
        "os_info": "=== Informations Système ===",
        "firewall": "=== État du Pare-feu ===",
        "network": "=== Informations Réseau ===",
        "disk": "=== Utilisation du Disque ===",
        "process": "=== Top Processus (mémoire) ===",
        "choose_lang": "Choisissez votre langue :",
        "welcome": "Bienvenue ! Choisissez la langue et cliquez sur Démarrer.",
        "start": "Démarrer",
        "logo_alt": "Logo de l'application"
    }
}

def get_os_info(lang):
    info = []
    info.append(f"{LANGS[lang]['os_info']}")
    info.append(f"System: {platform.system()}")
    info.append(f"Node Name: {platform.node()}")
    info.append(f"Release: {platform.release()}")
    info.append(f"Version: {platform.version()}")
    info.append(f"Machine: {platform.machine()}")
    info.append(f"Processor: {platform.processor()}")
    return "\n".join(info)

def get_firewall_status(lang):
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output('netsh advfirewall show allprofiles', shell=True, text=True)
            if "State ON" in output:
                return f"{LANGS[lang]['firewall']}\nFirewall: Enabled ✅"
            else:
                return f"{LANGS[lang]['firewall']}\nFirewall: Disabled ❌"
        except Exception:
            return f"{LANGS[lang]['firewall']}\nFirewall: Error checking status"
    return f"{LANGS[lang]['firewall']}\nFirewall: Not supported on this OS"

def get_network_info(lang):
    info = [LANGS[lang]['network']]
    hostname = socket.gethostname()
    info.append(f"Hostname: {hostname}")
    try:
        ip = socket.gethostbyname(hostname)
        info.append(f"Local IP: {ip}")
    except Exception:
        info.append("Local IP: Unknown")
    return "\n".join(info)

def get_disk_usage(lang):
    import shutil
    info = [LANGS[lang]['disk']]
    # Use correct root for Windows and Unix
    root = "C:\\" if platform.system() == "Windows" else "/"
    total, used, free = shutil.disk_usage(root)
    info.append(f"Disk Total: {round(total/(1024**3),2)} GB")
    info.append(f"Disk Used: {round(used/(1024**3),2)} GB")
    info.append(f"Disk Free: {round(free/(1024**3),2)} GB")
    return "\n".join(info)

def get_top_processes(lang):
    try:
        import psutil
    except ImportError:
        return "psutil not installed. Run: pip install psutil"
    info = [LANGS[lang]['process']]
    try:
        procs = [(p.info['name'], p.info['pid'], p.info['memory_info'].rss)
                 for p in psutil.process_iter(['name', 'pid', 'memory_info'])]
        procs = sorted(procs, key=lambda x: x[2], reverse=True)[:5]
        for name, pid, mem in procs:
            info.append(f"PID: {pid} | Name: {name} | RAM: {round(mem/(1024**2),2)} MB")
    except Exception:
        info.append("Could not retrieve process info.")
    return "\n".join(info)

def get_antivirus_status(lang):
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                'powershell "Get-MpComputerStatus | Select-Object -Property AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled"',
                shell=True, text=True
            )
            return f"=== Antivirus Status ===\n{output.strip()}"
        except Exception:
            return "=== Antivirus Status ===\nCould not retrieve antivirus status."
    return "=== Antivirus Status ===\nNot supported on this OS."

def get_uptime(lang):
    try:
        import psutil
        import datetime, time
        uptime_seconds = int(time.time() - psutil.boot_time())
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        return f"=== System Uptime ===\nUptime: {uptime_str}"
    except Exception:
        return "=== System Uptime ===\nCould not retrieve uptime."

class LanguageSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Scanner - Language")
        self.setGeometry(350, 250, 400, 300)
        layout = QVBoxLayout()
        # Logo
        logo = QLabel()
        try:
            pixmap = QPixmap("logo.png")
            logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            logo.setText("🔒")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        # Welcome
        self.welcome = QLabel(LANGS["English"]["welcome"])
        self.welcome.setAlignment(Qt.AlignCenter)
        self.welcome.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(self.welcome)
        # Language Combo
        self.combo = QComboBox()
        self.combo.addItems(LANGS.keys())
        layout.addWidget(QLabel(LANGS["English"]["choose_lang"]))
        layout.addWidget(self.combo)
        # Start Button
        self.start_btn = QPushButton(LANGS["English"]["start"])
        self.start_btn.setStyleSheet("font-size: 18px; background: #388e3c; color: white; border-radius: 8px;")
        self.start_btn.clicked.connect(self.launch_main)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.selected_lang = "English"
        self.combo.currentTextChanged.connect(self.update_lang)

    def update_lang(self, lang):
        self.selected_lang = lang
        self.welcome.setText(LANGS[lang]["welcome"])
        self.start_btn.setText(LANGS[lang]["start"])

    def launch_main(self):
        self.hide()
        self.main = SimpleSecurityScanner(self.selected_lang)
        self.main.show()

class SimpleSecurityScanner(QWidget):
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.setWindowTitle(LANGS[lang]["title"])
        self.setGeometry(200, 200, 600, 650)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Logo
        logo = QLabel()
        try:
            pixmap = QPixmap("logo.png")
            logo.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            logo.setText("🔒")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        # Title
        title = QLabel(LANGS[self.lang]["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2d415a; margin-bottom: 10px;")
        layout.addWidget(title)
        # Scan Button
        self.scan_btn = QPushButton(LANGS[self.lang]["scan"])
        self.scan_btn.setStyleSheet("font-size: 18px; background: #388e3c; color: white; border-radius: 8px;")
        self.scan_btn.clicked.connect(self.run_scan)
        layout.addWidget(self.scan_btn)
        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("font-size: 15px; font-family: Consolas; background: #f7f7fa;")
        layout.addWidget(self.output)
        # Save Button
        self.save_btn = QPushButton(LANGS[self.lang]["save"])
        self.save_btn.setStyleSheet("font-size: 15px; background: #1976d2; color: white; border-radius: 8px;")
        self.save_btn.clicked.connect(self.save_report)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def run_scan(self):
        self.output.clear()
        self.progress.setValue(0)
        self.scan_btn.setEnabled(False)
        QTimer.singleShot(200, self.scan_step1)

    def scan_step1(self):
        self.output.append(get_os_info(self.lang))
        self.output.append(get_uptime(self.lang))
        self.progress.setValue(15)
        QTimer.singleShot(200, self.scan_step2)

    def scan_step2(self):
        self.output.append(get_firewall_status(self.lang))
        self.output.append(get_antivirus_status(self.lang))
        self.progress.setValue(35)
        QTimer.singleShot(200, self.scan_step3)

    def scan_step3(self):
        self.output.append(get_network_info(self.lang))
        self.progress.setValue(55)
        QTimer.singleShot(200, self.scan_step4)

    def scan_step4(self):
        self.output.append(get_disk_usage(self.lang))
        self.progress.setValue(75)
        QTimer.singleShot(200, self.scan_step5)

    def scan_step5(self):
        self.output.append(get_top_processes(self.lang))
        self.progress.setValue(100)
        self.scan_btn.setEnabled(True)

    def save_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, LANGS[self.lang]["save"], "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.output.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.png"))
    lang_selector = LanguageSelector()
    lang_selector.show()
    sys.exit(app.exec_())