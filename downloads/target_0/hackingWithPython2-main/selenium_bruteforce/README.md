# Selenium Brute-Force Tool

## WICHTIGER RECHTLICHER HINWEIS

**Dieses Tool ist ausschließlich für autorisierte Penetrationstests und Sicherheitsanalysen gedacht!**

- Erlaubt: Tests auf **eigenen Systemen** oder mit **schriftlicher Genehmigung**
- Verboten: Unbefugte Tests gegen fremde Systeme (STRAFBAR!)
- Kontext: Educational purposes, CTF-Challenges, autorisierte Pentests

**Die Verantwortung für die Nutzung liegt beim Anwender!**

---

## Übersicht

Ein leistungsstarkes Selenium-basiertes Brute-Force-Tool zum Testen der Login-Sicherheit von Webanwendungen.

### Features

- Unterstützt Chrome und Firefox
- Headless-Mode verfügbar
- Detailliertes Logging aller Versuche
- Automatische Screenshots bei erfolgreichen Logins
- Konfigurierbare Verzögerung zwischen Versuchen
- Flexible Erfolgs-Indikatoren (URL-basiert)
- Speichert erfolgreiche Credentials als JSON
- Progress-Anzeige während des Tests
- Vollständig konfigurierbar via JSON

---

## Installation

### Voraussetzungen

- Python 3.7+
- Selenium WebDriver
- Chrome/ChromeDriver oder Firefox/GeckoDriver

### Schritt 1: Python-Dependencies installieren

```bash
pip install selenium
```

### Schritt 2: WebDriver installieren

#### Chrome (empfohlen)

**macOS (Homebrew):**
```bash
brew install chromedriver
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Oder manuell von: https://chromedriver.chromium.org/
```

**Windows:**
- Download von https://chromedriver.chromium.org/
- Füge ChromeDriver zum PATH hinzu

#### Firefox

**macOS (Homebrew):**
```bash
brew install geckodriver
```

**Linux:**
```bash
# Download von: https://github.com/mozilla/geckodriver/releases
sudo mv geckodriver /usr/local/bin/
```

---

## Projektstruktur

```
selenium_bruteforce/
│
├── brute_force_selenium.py    # Haupt-Script
├── config.json                # Konfigurationsdatei
├── README.md                  # Diese Datei
│
├── wordlists/                 # Wörterbücher
│   ├── usernames.txt         # Benutzernamen-Liste
│   └── passwords.txt         # Passwort-Liste
│
└── results/                   # Ergebnisse (wird automatisch erstellt)
    ├── brute_force_log.txt   # Detailliertes Log
    ├── successful_credentials.json
    └── screenshots/          # Screenshots erfolgreicher Logins
```

---

## Konfiguration

Bearbeite `config.json` für deine Zielanwendung:

```json
{
  "target_url": "http://127.0.0.1:5001/login",
  "username_field": "username",
  "password_field": "password",
  "submit_button_type": "submit",
  "success_indicators": {
    "url_contains": "/",
    "url_not_contains": "/login"
  },
  "browser": "chrome",
  "headless": false,
  "delay_between_attempts": 1.0,
  "page_load_timeout": 10,
  "usernames_file": "wordlists/usernames.txt",
  "passwords_file": "wordlists/passwords.txt",
  "log_file": "results/brute_force_log.txt",
  "screenshots_dir": "results/screenshots",
  "max_attempts": 0
}
```

### Wichtige Parameter

| Parameter | Beschreibung |
|-----------|--------------|
| `target_url` | URL des Login-Formulars |
| `username_field` | Name-Attribut des Username-Felds |
| `password_field` | Name-Attribut des Password-Felds |
| `success_indicators` | Kriterien für erfolgreichen Login |
| `browser` | `chrome` oder `firefox` |
| `headless` | Browser ohne GUI (`true`/`false`) |
| `delay_between_attempts` | Sekunden zwischen Versuchen |
| `max_attempts` | Maximale Versuche (0 = unbegrenzt) |

---

## Verwendung

### Grundlegende Nutzung

```bash
cd selenium_bruteforce
python brute_force_selenium.py
```

### Mit Optionen

```bash
# Headless-Mode (schneller, keine GUI)
python brute_force_selenium.py --headless

# Firefox verwenden
python brute_force_selenium.py --browser firefox

# Verzögerung ändern (2 Sekunden)
python brute_force_selenium.py --delay 2.0

# Eigene Config-Datei
python brute_force_selenium.py --config my_config.json

# Kombinationen
python brute_force_selenium.py --headless --browser chrome --delay 0.5
```

### Hilfe anzeigen

```bash
python brute_force_selenium.py --help
```

---

## Wörterbücher anpassen

### Usernames hinzufügen

Bearbeite `wordlists/usernames.txt`:

```text
# Kommentare mit # werden ignoriert
admin
test
user
myusername
```

### Passwords hinzufügen

Bearbeite `wordlists/passwords.txt`:

```text
# Häufige schwache Passwörter
password
123456
admin123
mypassword
```

**Tipp:** Verwende größere Wörterbücher für umfangreichere Tests:
- [SecLists](https://github.com/danielmiessler/SecLists)
- [RockYou.txt](https://github.com/brannondorsey/naive-hashcat/releases)

---

## Ergebnisse

### Log-Datei

Alle Versuche werden in `results/brute_force_log.txt` protokolliert:

```
================================================================================
BRUTE-FORCE SESSION GESTARTET: 2025-01-11 15:30:00
Target URL: http://127.0.0.1:5001/login
================================================================================

[2025-01-11 15:30:05] [FEHLGESCHLAGEN] | User: admin | Pass: password
[2025-01-11 15:30:07] [FEHLGESCHLAGEN] | User: admin | Pass: 123456
[2025-01-11 15:30:09] [ERFOLG] | User: test | Pass: test123 | Screenshot: results/screenshots/...
```

### Erfolgreiche Credentials

Bei erfolgreichen Logins wird `results/successful_credentials.json` erstellt:

```json
[
  {
    "username": "test",
    "password": "test123",
    "timestamp": "2025-01-11T15:30:09",
    "screenshot": "results/screenshots/success_test_20250111_153009.png"
  }
]
```

### Screenshots

Erfolgreiche Logins werden automatisch als PNG gespeichert:
- Pfad: `results/screenshots/`
- Format: `success_{username}_{timestamp}.png`

---

## Sicherheitshinweise

### Für Pentester

1. **Autorisierung:** Hole **immer** schriftliche Genehmigung ein
2. **Scope:** Halte dich an den vereinbarten Test-Scope
3. **Rate-Limiting:** Erhöhe `delay_between_attempts` um Server nicht zu überlasten
4. **Logging:** Bewahre alle Logs als Nachweis auf
5. **Cleanup:** Lösche Test-Accounts nach dem Pentest

### Für Entwickler (Verteidigung)

**Dein System gegen Brute-Force schützen:**

1. **Rate-Limiting implementieren**
   - Max. Login-Versuche pro IP/User
   - Exponentielles Backoff

2. **Account-Lockout**
   - Temporäre Sperrung nach X Fehlversuchen
   - CAPTCHA nach 3-5 Fehlversuchen

3. **Starke Passwort-Policy**
   - Mindestlänge (12+ Zeichen)
   - Komplexitätsanforderungen
   - Passwort-Blacklist (häufige Passwörter)

4. **Monitoring & Alerts**
   - Log alle Login-Versuche
   - Alert bei verdächtigen Mustern

5. **Multi-Factor Authentication (MFA)**
   - SMS, Authenticator-App, Hardware-Token

6. **Web Application Firewall (WAF)**
   - ModSecurity, Cloudflare, AWS WAF

---

## Erweiterte Anpassungen

### Eigene Erfolgs-Indikatoren

Passe `success_indicators` in `config.json` an:

```json
"success_indicators": {
  "url_contains": "/dashboard",
  "url_not_contains": "/login"
}
```

Oder prüfe auf Text-Elemente (erfordert Code-Änderung in `check_login_success()`):

```python
def check_login_success(self):
    try:
        welcome_element = self.driver.find_element(By.CSS_SELECTOR, ".welcome-message")
        return True
    except NoSuchElementException:
        return False
```

### Andere Formular-Struktur

Falls das Login-Formular anders strukturiert ist:

```json
{
  "username_field": "email",
  "password_field": "pass",
  "submit_button_type": "button"
}
```

---

## Troubleshooting

### Problem: "WebDriver not found"

**Lösung:**
```bash
# Chrome
brew install chromedriver

# Firefox
brew install geckodriver
```

### Problem: "Element not found"

**Ursache:** Formularfelder haben andere Namen/IDs

**Lösung:** Inspiziere das Login-Formular (F12 in Browser):
```html
<input name="username" ...>  <!-- Verwende diesen Namen in config.json -->
<input name="password" ...>
```

### Problem: "Timeout waiting for element"

**Lösung:** Erhöhe `page_load_timeout` in `config.json`:
```json
"page_load_timeout": 20
```

### Problem: Tool erkennt erfolgreiche Logins nicht

**Lösung:** Passe `success_indicators` an:
1. Logge dich manuell ein
2. Prüfe die URL nach dem Login
3. Aktualisiere `url_contains` entsprechend

---

## Performance-Optimierung

### Schnellere Tests

```bash
# Headless-Mode (20-30% schneller)
python brute_force_selenium.py --headless --delay 0.5
```

### Weniger aggressive Tests

```bash
# Langsamer, um Rate-Limiting zu umgehen
python brute_force_selenium.py --delay 3.0
```

### Maximale Versuche limitieren

In `config.json`:
```json
"max_attempts": 100
```

---

## Weiterführende Ressourcen

### Tools
- [Hydra](https://github.com/vanhauser-thc/thc-hydra) - CLI Brute-Force-Tool
- [Burp Suite](https://portswigger.net/burp) - Web Application Testing
- [OWASP ZAP](https://www.zaproxy.org/) - Security Scanner

### Wörterbücher
- [SecLists](https://github.com/danielmiessler/SecLists)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)

### Lernressourcen
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

---

## Lizenz

Dieses Tool ist für **educational purposes** und **autorisierte Sicherheitstests**.

**Haftungsausschluss:** Der Autor übernimmt keine Verantwortung für Missbrauch dieses Tools.

---

## Beitragen

Verbesserungsvorschläge? Erstelle ein Issue oder Pull Request!

---

**Happy (ethical) Hacking!**
