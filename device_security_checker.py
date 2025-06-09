import sys
import platform
import socket
import subprocess
import time
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

def animated_message(widget, message, delay=0.03):
    widget.clear()
    for char in message:
        widget.insertPlainText(char)
        QApplication.processEvents()
        time.sleep(delay)

def get_virus_removal_guide(lang):
    guides = {
        "English": (
            "=== Virus Removal Guide ===\n"
            "If a virus or suspicious process is detected, try these steps:\n"
            "1. Disconnect from the internet to prevent further spread.\n"
            "2. Boot into Safe Mode (Windows: F8 during startup).\n"
            "3. Open your antivirus and run a full system scan.\n"
            "4. Follow the antivirus instructions to remove/quarantine threats.\n"
            "5. Delete suspicious files manually if needed (be careful!).\n"
            "6. Clear your browser cache and temporary files.\n"
            "7. Change your passwords after cleaning.\n"
            "8. Reconnect to the internet and update your system and antivirus.\n"
            "9. If the virus persists, seek professional help or reinstall your OS.\n"
            "\n"
            "Other possibilities:\n"
            "- If you can't boot: Use a rescue disk or bootable antivirus USB.\n"
            "- If antivirus can't remove it: Try a different antivirus or malware remover.\n"
            "- If system is unstable: Backup your data and consider a clean OS reinstall.\n"
            "- For ransomware: Do NOT pay. Seek professional help and report it.\n"
            "- For persistent browser popups: Reset or reinstall your browser.\n"
            "- For unknown processes: Search the process name online before deleting.\n"
            "\n"
            "Stay safe! Always keep backups and your system updated."
        ),
        "العربية": (
            "=== دليل إزالة الفيروسات ===\n"
            "إذا تم اكتشاف فيروس أو عملية مشبوهة، جرب الخطوات التالية:\n"
            "1. افصل الإنترنت لمنع الانتشار.\n"
            "2. ادخل إلى الوضع الآمن (ويندوز: F8 أثناء التشغيل).\n"
            "3. افتح برنامج الحماية وافحص النظام بالكامل.\n"
            "4. اتبع تعليمات البرنامج لإزالة أو عزل التهديدات.\n"
            "5. احذف الملفات المشبوهة يدويًا إذا لزم الأمر (كن حذرًا!).\n"
            "6. امسح ذاكرة المتصفح والملفات المؤقتة.\n"
            "7. غيّر كلمات المرور بعد التنظيف.\n"
            "8. أعد الاتصال بالإنترنت وحدّث النظام وبرنامج الحماية.\n"
            "9. إذا استمر الفيروس، اطلب مساعدة مختص أو أعد تثبيت النظام.\n"
            "\n"
            "احتمالات أخرى:\n"
            "- إذا لم يقلع النظام: استخدم قرص إنقاذ أو USB حماية.\n"
            "- إذا لم يستطع البرنامج إزالة الفيروس: جرب برنامج حماية آخر.\n"
            "- إذا كان النظام غير مستقر: انسخ بياناتك وجرّب تثبيت نظيف.\n"
            "- في حالة برامج الفدية: لا تدفع. اطلب مساعدة مختص وأبلغ الجهات المختصة.\n"
            "- في حال ظهور نوافذ منبثقة: أعد ضبط أو تثبيت المتصفح.\n"
            "- للعمليات غير المعروفة: ابحث عن اسم العملية قبل الحذف.\n"
            "\n"
            "ابقَ آمنًا! احتفظ بنسخ احتياطية وحدّث نظامك دائمًا."
        ),
        "Français": (
            "=== Guide de Suppression des Virus ===\n"
            "Si un virus ou un processus suspect est détecté, essayez ces étapes :\n"
            "1. Déconnectez-vous d'internet pour éviter la propagation.\n"
            "2. Démarrez en mode sans échec (Windows : F8 au démarrage).\n"
            "3. Ouvrez votre antivirus et lancez une analyse complète.\n"
            "4. Suivez les instructions de l'antivirus pour supprimer/quarantaine les menaces.\n"
            "5. Supprimez manuellement les fichiers suspects si nécessaire (attention !).\n"
            "6. Videz le cache du navigateur et les fichiers temporaires.\n"
            "7. Changez vos mots de passe après le nettoyage.\n"
            "8. Reconnectez-vous à internet et mettez à jour votre système et antivirus.\n"
            "9. Si le virus persiste, demandez l'aide d'un professionnel ou réinstallez le système.\n"
            "\n"
            "Autres possibilités :\n"
            "- Si le système ne démarre pas : Utilisez un disque de secours ou une clé USB antivirus.\n"
            "- Si l'antivirus ne peut pas supprimer : Essayez un autre antivirus ou outil anti-malware.\n"
            "- Si le système est instable : Sauvegardez vos données et envisagez une réinstallation propre.\n"
            "- Pour les ransomwares : Ne payez pas. Demandez de l'aide et signalez-le.\n"
            "- Pour les pop-ups persistants : Réinitialisez ou réinstallez le navigateur.\n"
            "- Pour les processus inconnus : Cherchez le nom du processus avant suppression.\n"
            "\n"
            "Restez prudent ! Faites des sauvegardes et gardez votre système à jour."
        )
    }
    return guides.get(lang, guides["English"])

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
        # Show the animated virus removal guide in the selected language
        guide = get_virus_removal_guide(self.lang)
        animated_message(self.output, guide)
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