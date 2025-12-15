#!/usr/bin/env python3

"""
Hydra Results Analyzer
Parst Hydra-Output und generiert strukturierte JSON-Ergebnisse
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class HydraResultsAnalyzer:
    """Analysiert Hydra Brute-Force Ergebnisse"""

    def __init__(self, output_file="results/hydra_output.txt"):
        """Initialisiert den Analyzer"""
        self.script_dir = Path(__file__).parent
        self.output_file = self.script_dir / output_file
        self.json_output = self.script_dir / "results" / "successful_logins.json"
        self.successful_logins = []
        self.statistics = {
            "total_attempts": 0,
            "successful_logins": 0,
            "failed_attempts": 0,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0
        }

    def parse_hydra_output(self):
        """Parst die Hydra-Output-Datei"""
        print(f"Analysiere Datei: {self.output_file}")

        if not self.output_file.exists():
            print(f"FEHLER: Output-Datei nicht gefunden: {self.output_file}")
            return False

        with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Parse erfolgreiche Logins
        # Format: [PORT][FORM] host: IP login: USERNAME password: PASSWORD
        pattern = r'\[(\d+)\]\[(.*?)\].*?login:\s*(\S+)\s+password:\s*(\S+)'
        matches = re.findall(pattern, content)

        for match in matches:
            port, protocol, username, password = match
            self.successful_logins.append({
                "username": username,
                "password": password,
                "port": port,
                "protocol": protocol,
                "timestamp": datetime.now().isoformat(),
                "verified": False
            })

        self.statistics["successful_logins"] = len(self.successful_logins)

        # Parse Statistiken aus dem Output
        self._parse_statistics(content)

        return True

    def _parse_statistics(self, content):
        """Extrahiert Statistiken aus dem Hydra-Output"""
        # Suche nach "Hydra finished" oder ähnlichen Zeilen
        if "Hydra" in content:
            lines = content.split('\n')
            for line in lines:
                # Parse Start-Zeit
                if "starting" in line.lower():
                    self.statistics["start_time"] = datetime.now().isoformat()

                # Parse Ende-Zeit
                if "finished" in line.lower():
                    self.statistics["end_time"] = datetime.now().isoformat()

    def verify_credentials(self, target_url="http://192.168.1.188:5001/login"):
        """Verifiziert gefundene Credentials (optional)"""
        print("\nVerifiziere gefundene Credentials...")

        try:
            import requests
        except ImportError:
            print("WARNUNG: requests-Modul nicht installiert, überspringe Verifizierung")
            return

        for i, cred in enumerate(self.successful_logins):
            username = cred["username"]
            password = cred["password"]

            try:
                response = requests.post(
                    target_url,
                    data={
                        "username": username,
                        "password": password
                    },
                    allow_redirects=False,
                    timeout=5
                )

                # Prüfe ob Login erfolgreich (Redirect oder kein Fehler)
                if response.status_code in [200, 302, 303] and "Ungültige" not in response.text:
                    cred["verified"] = True
                    print(f"  [{i+1}] {username}:{password} - VERIFIZIERT")
                else:
                    print(f"  [{i+1}] {username}:{password} - FEHLGESCHLAGEN")

            except Exception as e:
                print(f"  [{i+1}] {username}:{password} - FEHLER: {e}")

    def save_json_results(self):
        """Speichert Ergebnisse als JSON"""
        print(f"\nSpeichere JSON-Ergebnisse...")

        # Erstelle Output-Verzeichnis falls nicht vorhanden
        self.json_output.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "metadata": {
                "analyzer": "HydraResultsAnalyzer",
                "timestamp": datetime.now().isoformat(),
                "source_file": str(self.output_file),
                "target": "http://192.168.1.188:5001/login"
            },
            "statistics": self.statistics,
            "successful_logins": self.successful_logins
        }

        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"JSON-Ergebnisse gespeichert: {self.json_output}")

    def print_summary(self):
        """Gibt Zusammenfassung aus"""
        print("\n" + "="*80)
        print("HYDRA ERGEBNIS-ANALYSE")
        print("="*80)

        print(f"Erfolgreiche Logins: {self.statistics['successful_logins']}")

        if self.successful_logins:
            print("\nGEFUNDENE CREDENTIALS:")
            print("-" * 80)
            for i, cred in enumerate(self.successful_logins, 1):
                verified_status = "VERIFIZIERT" if cred.get("verified") else "NICHT VERIFIZIERT"
                print(f"  [{i}] Username: {cred['username']}")
                print(f"      Password: {cred['password']}")
                print(f"      Status:   {verified_status}")
                print("-" * 80)
        else:
            print("\nKeine erfolgreichen Logins gefunden.")

        print(f"\nJSON-Output: {self.json_output}")
        print("="*80 + "\n")

    def run(self, verify=False):
        """Hauptfunktion"""
        print("\n" + "="*80)
        print("HYDRA RESULTS ANALYZER")
        print("="*80 + "\n")

        # Parse Output
        success = self.parse_hydra_output()
        if not success:
            return False

        # Optional: Verifiziere Credentials
        if verify and self.successful_logins:
            self.verify_credentials()

        # Speichere JSON
        self.save_json_results()

        # Zusammenfassung
        self.print_summary()

        return True


def main():
    """Hauptfunktion mit Argument-Parsing"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Hydra Results Analyzer - Parst und analysiert Hydra-Output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python analyze_results.py
  python analyze_results.py --verify
  python analyze_results.py --output results/hydra_output.txt

        """
    )

    parser.add_argument(
        '--output',
        default='results/hydra_output.txt',
        help='Pfad zur Hydra-Output-Datei (default: results/hydra_output.txt)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verifiziere gefundene Credentials durch HTTP-Requests'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Überspringe Verifizierung (default)'
    )

    args = parser.parse_args()

    try:
        analyzer = HydraResultsAnalyzer(output_file=args.output)
        verify = args.verify and not args.no_verify
        success = analyzer.run(verify=verify)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nWARNUNG: Abbruch durch Benutzer (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\nFEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
