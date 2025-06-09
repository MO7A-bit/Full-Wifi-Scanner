# 🔒 Simple Security Scanner

A simple, cross-platform desktop app built with Python and PyQt5 to scan your device for basic security info.

## Features
- Multi-language support: English, العربية, Français
- Shows OS and hardware info
- Checks firewall and antivirus status (Windows)
- Displays network and disk usage
- Lists top memory-consuming processes
- Save scan results as a text report

## Requirements
- Python 3.7+
- PyQt5
- psutil

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/MO7A-bit/checking_app.git
   cd checking_app
   ```

2. **Install dependencies:**
   ```
   pip install PyQt5 psutil
   ```

## Usage

Run the app with:
```
python device_security_checker.py
```

---

**Note:**  
Antivirus and firewall checks are supported on Windows only.
