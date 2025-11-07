# Bruteforce-Vergleich: Burp Suite vs. Hydra vs. Selenium

## Übersicht

Dieser Vergleich zeigt die Unterschiede zwischen drei gängigen Bruteforce-Tools für Web-Anwendungen.

---

## 🔍 Die Tools im Detail

### 1. **Burp Suite** (Intruder)
**Tool-Typ:** GUI-basiertes Web Security Testing Tool

**Funktionsweise:**
- Interceptet HTTP/HTTPS-Traffic über einen Proxy
- Intruder-Modul sendet modifizierte Requests
- Zeigt Responses mit Länge, Status-Code, etc.
- Erkennt erfolgreiche Logins durch Response-Analyse

**Installation:**
- Download: https://portswigp.net/burp/communitydownload
- Kostenlose Community Edition verfügbar
- Professional Edition für erweiterte Features

**Verwendung:**
1. Browser-Proxy auf Burp einstellen (127.0.0.1:8080)
2. Login-Request aufzeichnen (Proxy > HTTP History)
3. Request an Intruder senden (Right-Click > Send to Intruder)
4. Payload-Positionen markieren (§username§, §password§)
5. Payload-Liste laden
6. Attack starten

---

### 2. **Hydra**
**Tool-Typ:** Kommandozeilen-basiertes Bruteforce-Tool

**Funktionsweise:**
- Sendet direkte HTTP-POST-Requests
- Keine GUI, rein CLI-basiert
- Unterstützt viele Protokolle (HTTP, FTP, SSH, etc.)
- Sehr schnell durch Multi-Threading

**Installation:**
```bash
# Linux (Debian/Ubuntu)
sudo apt-get install hydra

# macOS
brew install hydra

# Windows
# Via WSL oder Cygwin
```

**Verwendung:**
```bash
# Skript ausführen (bereits vorbereitet)
bash bruteforce_hydra.sh

# Oder manuell:
hydra -l admin -P passwords.txt 127.0.0.1 -s 5001 \
  http-post-form "/login:username=^USER^&password=^PASS^:Ungültige Eingabedaten"
```

---

### 3. **Selenium**
**Tool-Typ:** Browser-Automatisierungs-Framework

**Funktionsweise:**
- Steuert einen echten Browser (Chrome, Firefox, etc.)
- Simuliert menschliches Verhalten
- Kann JavaScript ausführen und mit dynamischen Seiten arbeiten
- Python-Skript mit Selenium WebDriver

**Installation:**
```bash
pip install selenium webdriver-manager
```

**Verwendung:**
```bash
# Skript ausführen (bereits vorbereitet)
python bruteforce_selenium.py
```

---

## 📊 Vergleichstabelle

| Kriterium | Burp Suite | Hydra | Selenium |
|-----------|-----------|-------|----------|
| **Geschwindigkeit** | Mittel (1-10 req/s) | Sehr schnell (10-100+ req/s) | Langsam (1-2 req/s) |
| **Benutzerfreundlichkeit** | ⭐⭐⭐⭐⭐ GUI, einfach | ⭐⭐ CLI, technisch | ⭐⭐⭐ Code, mittel |
| **Setup-Zeit** | Schnell (5 min) | Sehr schnell (1 min) | Mittel (10 min) |
| **Multithreading** | ✅ Ja (nur Pro) | ✅ Ja (Standard) | ⚠️ Begrenzt |
| **JavaScript-Support** | ⚠️ Begrenzt | ❌ Nein | ✅ Vollständig |
| **CAPTCHA-Bypass** | ❌ Schwierig | ❌ Unmöglich | ⚠️ Möglich mit OCR |
| **Rate Limiting Detection** | ✅ Ja | ⚠️ Manuell | ✅ Ja |
| **Protokolle** | HTTP(S) | 50+ Protokolle | Nur Browser |
| **Kosten** | Free/Paid | Kostenlos | Kostenlos |
| **Stealth** | Mittel | Hoch (erkennbar) | Niedrig (wie User) |
| **Lernkurve** | Niedrig | Mittel | Mittel-Hoch |
| **Plattform** | Win/Mac/Linux | Linux/Mac/(WSL) | Win/Mac/Linux |

---

## 🎯 Wann welches Tool verwenden?

### **Burp Suite** - Beste Wahl für:
- ✅ Manuelle Penetration Tests
- ✅ Anfänger (GUI ist intuitiv)
- ✅ Komplexe Request-Analyse (Headers, Cookies, etc.)
- ✅ Wenn du den Traffic inspizieren möchtest
- ✅ Web Application Security Testing allgemein

**Nachteile:**
- ❌ Langsamer als Hydra
- ❌ Community Edition hat Limits (kein Multi-Threading)
- ❌ Nur für HTTP(S)

---

### **Hydra** - Beste Wahl für:
- ✅ Schnelle Bruteforce-Angriffe
- ✅ Viele Protokolle (SSH, FTP, SMTP, etc.)
- ✅ Automatisierung (Scripting)
- ✅ Große Passwortlisten (Millionen Einträge)
- ✅ Professionelle Penetration Tests

**Nachteile:**
- ❌ Keine GUI
- ❌ Kein JavaScript-Support
- ❌ Schwierig bei komplexen Web-Apps (CSRF-Tokens, etc.)
- ❌ Auffällig (viele Requests erkennbar)

---

### **Selenium** - Beste Wahl für:
- ✅ JavaScript-intensive Seiten (SPAs, React, Angular)
- ✅ CAPTCHA-Tests (mit OCR-Erweiterungen)
- ✅ Komplexe Login-Flows (Multi-Step)
- ✅ Umgehen von Bot-Detection
- ✅ Wenn du menschliches Verhalten simulieren musst

**Nachteile:**
- ❌ Sehr langsam
- ❌ Ressourcen-intensiv (jeder Browser-Instanz)
- ❌ Komplexer Code
- ❌ Nicht für große Passwortlisten geeignet

---

## 🔬 Praktischer Vergleich (Beispiel: 100 Passwörter)

### **Burp Suite**
```
Dauer: ~2-5 Minuten
CPU: Niedrig
RAM: 500 MB
Erkennbarkeit: Mittel
Erfolgsrate: Hoch (bei einfachen Login-Forms)
```

### **Hydra**
```
Dauer: ~10-30 Sekunden
CPU: Mittel
RAM: 50 MB
Erkennbarkeit: Hoch (viele schnelle Requests)
Erfolgsrate: Hoch (bei Standard-Forms)
```

### **Selenium**
```
Dauer: ~10-20 Minuten
CPU: Hoch
RAM: 1-2 GB (pro Browser)
Erkennbarkeit: Niedrig (sieht aus wie normaler User)
Erfolgsrate: Sehr hoch (auch bei JavaScript)
```

---

## 🛡️ Erkennung & Abwehr

### Wie erkennt man Bruteforce-Angriffe?

1. **Viele fehlgeschlagene Login-Versuche** von einer IP
2. **Hohe Request-Rate** (besonders Hydra)
3. **User-Agent Patterns** (Standard-Tools haben typische User-Agents)
4. **Zeitliche Muster** (zu regelmäßig, zu schnell)

### Abwehrmaßnahmen:

```python
# Rate Limiting (Flask-Limiter)
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Max 5 Logins pro Minute
def login():
    # ...
```

- ✅ **Rate Limiting** (max. X Versuche pro Minute)
- ✅ **Account Lockout** (nach Y Fehlversuchen)
- ✅ **CAPTCHA** (reCAPTCHA, hCaptcha)
- ✅ **2FA/MFA** (Two-Factor Authentication)
- ✅ **IP-Blacklisting** (automatisch bei verdächtigem Traffic)
- ✅ **Honeypots** (Fake-Login-Felder)
- ✅ **Delayed Responses** (bei falschen Logins 2-5 Sekunden warten)

---

## 📝 Fazit

**Für dein Schulprojekt:**

1. **Burp Suite** - Am besten für die Demo (GUI, einfach zu zeigen)
2. **Hydra** - Zeigt die rohe Kraft von CLI-Tools
3. **Selenium** - Zeigt moderne Browser-Automatisierung

**Empfehlung für die Präsentation:**
- Zeige alle drei Tools in Aktion
- Vergleiche die Geschwindigkeit live
- Demonstriere wie Rate Limiting Hydra stoppt
- Zeige wie Selenium "menschlicher" aussieht

**Aussage für den Prof:**
> "Burp ist ideal für manuelle Tests und Analyse, Hydra für schnelle automatisierte Angriffe auf viele Protokolle, und Selenium für komplexe Web-Apps mit JavaScript. Jedes Tool hat seine Stärken - die Wahl hängt vom Ziel ab. In der Praxis kombiniert man oft mehrere Tools."

---

## 🚀 Schnellstart

### 1. Installation
```bash
# Python-Dependencies
pip install -r requirements.txt

# Hydra (WSL/Linux)
sudo apt-get install hydra
```

### 2. Flask-App starten
```bash
python app.py
```

### 3. Bruteforce ausführen

**Hydra:**
```bash
bash bruteforce_hydra.sh          # Linux/Mac
bruteforce_hydra.bat              # Windows
```

**Selenium:**
```bash
python bruteforce_selenium.py
```

**Burp:**
- Siehe detaillierte Anleitung oben

---

## ⚠️ Rechtlicher Hinweis

**NUR FÜR BILDUNGSZWECKE UND EIGENE SYSTEME!**

Das unbefugte Testen von fremden Systemen ist **illegal** und kann strafrechtlich verfolgt werden.

- ✅ Eigene Test-Systeme
- ✅ Mit schriftlicher Erlaubnis (Pentest-Vertrag)
- ✅ CTF-Wettbewerbe
- ✅ Bug Bounty Programme (mit Scope-Berechtigung)

**Immer ethisch und legal handeln!**

---

## 📚 Weiterführende Links

- **Burp Suite:** https://portswigp.net/burp/documentation
- **Hydra:** https://github.com/vanhauser-thc/thc-hydra
- **Selenium:** https://selenium-python.readthedocs.io/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

**Stand:** 2025-01-07
**Autor:** Schulprojekt Hacking with Python
**Version:** 1.0
