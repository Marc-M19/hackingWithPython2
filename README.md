# Hacking with Python - Schulprojekt

Dieses Projekt demonstriert **Web-Security-Konzepte** für Bildungszwecke.

⚠️ **NUR FÜR LOKALE TESTS UND BILDUNG!**

---

## 📋 Projekt-Übersicht

Dies ist eine Flask-Web-Anwendung mit **absichtlich eingebauten Schwachstellen** für Security-Testing.

### ✅ Abgeschlossene Anforderungen:

1. ✅ **SQL Injection Fixes** - Alle Schwachstellen mit Prepared Statements behoben
2. ✅ **Bruteforce mit Burp** - Vorbereitet (manuell zu testen)
3. ✅ **Bruteforce mit Hydra** - Skript verfügbar
4. ✅ **Bruteforce mit Selenium** - Skript verfügbar
5. ✅ **Vergleichsdokumentation** - Ausführlicher Vergleich aller Tools

---

## 🚀 Schnellstart

### 1. Installation

```bash
# Python-Dependencies installieren
pip install -r requirements.txt

# Hydra installieren (Linux/macOS/WSL)
sudo apt-get install hydra      # Linux
brew install hydra              # macOS
```

### 2. Datenbank einrichten

```bash
# MySQL starten und Datenbank erstellen
mysql -u root -p < schema.sql
mysql -u root -p < test.sql
```

### 3. Flask-App starten

```bash
python app.py
# App läuft auf: http://127.0.0.1:5001
```

---

## 🔐 SQL Injection (BEHOBEN)

### Vorher (unsicher):
```python
# VERWUNDBAR!
cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### Nachher (sicher):
```python
# SICHER: Prepared Statement
cur.execute("SELECT * FROM users WHERE username = %s", (username,))
```

### Behobene Schwachstellen:
- ✅ Login-Formular (app.py:60)
- ✅ Registrierung (app.py:38)
- ✅ Suche (app.py:189)
- ✅ Bio bearbeiten (app.py:145)
- ✅ Posts (app.py:104)

---

## 🔨 Bruteforce-Tools

### 1. **Burp Suite** (Manuell)
```
1. Browser-Proxy einstellen: 127.0.0.1:8080
2. Login-Request aufzeichnen
3. Request an Intruder senden
4. Payload-Positionen markieren
5. Passwortliste laden (passwords.txt)
6. Attack starten
```

### 2. **Hydra** (Automatisiert)
```bash
# Linux/macOS
bash bruteforce_hydra.sh

# Windows (WSL)
bruteforce_hydra.bat
```

### 3. **Selenium** (Browser-Automatisierung)
```bash
python bruteforce_selenium.py
```

---

## 📊 Vergleich

| Tool | Geschwindigkeit | Einfachheit | JavaScript |
|------|----------------|-------------|------------|
| **Burp** | Mittel | ⭐⭐⭐⭐⭐ | ⚠️ |
| **Hydra** | Sehr schnell | ⭐⭐ | ❌ |
| **Selenium** | Langsam | ⭐⭐⭐ | ✅ |

➡️ **Detaillierter Vergleich:** [BRUTEFORCE_VERGLEICH.md](BRUTEFORCE_VERGLEICH.md)

---

## 📁 Projektstruktur

```
hackingWithPython2/
├── app.py                      # Flask-Hauptanwendung (JETZT SICHER!)
├── schema.sql                  # Datenbank-Schema
├── test.sql                    # Test-Daten
├── requirements.txt            # Python-Dependencies
├── passwords.txt               # Passwortliste für Bruteforce-Tests
│
├── bruteforce_hydra.sh         # Hydra-Skript (Linux/Mac)
├── bruteforce_hydra.bat        # Hydra-Skript (Windows)
├── bruteforce_selenium.py      # Selenium-Skript
│
├── BRUTEFORCE_VERGLEICH.md     # Ausführlicher Tool-Vergleich
└── templates/                  # HTML-Templates
    ├── base.html
    ├── login.html
    ├── register.html
    ├── search.html
    ├── edit_bio.html
    └── ...
```

---

## 🎯 Für die Abnahme

### Checkliste:
- ✅ SQL Injection gefixt
- ✅ Burp Suite vorbereitet
- ✅ Hydra-Skript erstellt
- ✅ Selenium-Skript erstellt
- ✅ Vergleichsdokumentation geschrieben

### Demo-Reihenfolge:
1. **SQL Injection Fix** zeigen (Vorher/Nachher Code-Vergleich)
2. **Burp Suite** starten und Login-Request intercepten
3. **Hydra** ausführen und Geschwindigkeit zeigen
4. **Selenium** ausführen und Browser-Automatisierung zeigen
5. **Vergleich** präsentieren (BRUTEFORCE_VERGLEICH.md)

---

## 🛡️ Sicherheitshinweise

Dieses Projekt enthält **absichtlich unsichere Code-Beispiele** (inzwischen behoben) für Bildungszwecke.

**NIEMALS in Produktion verwenden!**

### Zusätzliche Schutzmaßnahmen (für echte Apps):
```python
# Rate Limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # ...
```

- 🔒 Rate Limiting
- 🔒 Account Lockout
- 🔒 CAPTCHA
- 🔒 2FA/MFA
- 🔒 Passwort-Hashing (bcrypt, nicht Klartext!)
- 🔒 HTTPS (TLS/SSL)
- 🔒 CSRF-Tokens
- 🔒 Content Security Policy (CSP)

---

## 📚 Ressourcen

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Burp Suite Docs](https://portswigp.net/burp/documentation)
- [Hydra GitHub](https://github.com/vanhauser-thc/thc-hydra)
- [Selenium Python](https://selenium-python.readthedocs.io/)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)

---

## ⚖️ Rechtliches

**Nur für Bildungszwecke!**

Das Testen von fremden Systemen ohne Erlaubnis ist **illegal**.

✅ **Erlaubt:**
- Eigene Test-Systeme
- Mit schriftlicher Genehmigung
- CTF-Wettbewerbe
- Bug Bounty Programme (im Scope)

❌ **Verboten:**
- Fremde Systeme ohne Erlaubnis
- Produktiv-Systeme
- Schädigung von Systemen

---

## 👨‍🎓 Autor

Schulprojekt - Hacking with Python
Datum: 2025-01-07

---

## 📄 Lizenz

Nur für Bildungszwecke. Keine Garantie oder Haftung.
