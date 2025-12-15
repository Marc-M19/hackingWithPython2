# Hydra Brute-Force Testing Tool

Automatisiertes Brute-Force-Testing-Framework für HTTP-POST-basierte Login-Formulare mit THC-Hydra.

## Überblick

Dieses Tool verwendet **THC-Hydra**, einen der schnellsten Netzwerk-Login-Cracker, um Brute-Force-Angriffe auf HTTP-POST-Formulare durchzuführen. Es wurde speziell für Penetrationstests der Flask-Webapp "Hebeln Mit Kopf" entwickelt.

## Eigenschaften

- **Automatisiertes Testen**: Vollständig skriptbasierter Angriff mit Bash-Script
- **Konfigurierbar**: JSON-basierte Konfiguration für flexible Anpassungen
- **Analyse-Tool**: Python-Script zur strukturierten Auswertung der Ergebnisse
- **Wordlist-Support**: Anpassbare Listen für Usernames und Passwords
- **Logging**: Detaillierte Protokollierung aller Versuche und Ergebnisse

## Voraussetzungen

### Software-Anforderungen

1. **THC-Hydra** (zwingend erforderlich)
2. **Python 3.6+** (für Analyzer)
3. **jq** (optional, für JSON-Parsing im Bash-Script)

### Installation

#### macOS
```bash
brew install hydra
brew install jq  # optional
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install hydra
sudo apt-get install jq  # optional
```

#### Linux (Arch)
```bash
sudo pacman -S hydra
sudo pacman -S jq  # optional
```

#### Python-Abhängigkeiten
```bash
pip install requests  # optional, für Credential-Verifizierung
```

## Projekt-Struktur

```
hydra_bruteforce/
├── README.md                     # Diese Datei
├── config.json                   # Konfigurationsdatei
├── run_hydra_attack.sh           # Hauptscript für Hydra-Angriff
├── analyze_results.py            # Python-Analyzer für Ergebnisse
├── wordlists/
│   ├── usernames.txt             # Username-Wordlist
│   └── passwords.txt             # Password-Wordlist
└── results/
    ├── hydra_output.txt          # Hydra Raw-Output
    ├── hydra_detailed.log        # Detailliertes Log
    └── successful_logins.json    # Erfolgreiche Credentials (JSON)
```

## Konfiguration

Die Datei `config.json` enthält alle wichtigen Einstellungen:

```json
{
  "target": {
    "host": "127.0.0.1",
    "port": 5001,
    "path": "/login"
  },
  "form_parameters": {
    "username_field": "username",
    "password_field": "password",
    "failure_string": "Ungültige Anmeldedaten"
  },
  "attack_settings": {
    "threads": 4,
    "timeout": 30
  }
}
```

### Wichtige Parameter

- **failure_string**: String, der im Response erscheint, wenn Login fehlschlägt
- **threads**: Anzahl paralleler Threads (Vorsicht: zu viele Threads können Server überlasten)
- **timeout**: Timeout in Sekunden pro Versuch

## Verwendung

### 1. Wordlists vorbereiten

Bearbeite die Dateien in `wordlists/`:

**usernames.txt:**
```
admin
test
user
```

**passwords.txt:**
```
password
123456
admin
```

### 2. Flask-App starten

Stelle sicher, dass die Ziel-Webapp läuft:

```bash
cd ../
python app.py
```

Die App sollte unter `http://127.0.0.1:5001` erreichbar sein.

### 3. Hydra-Angriff starten

```bash
cd hydra_bruteforce
./run_hydra_attack.sh
```

Das Script führt folgende Schritte aus:
1. Prüft Abhängigkeiten (Hydra, jq)
2. Lädt Konfiguration
3. Zeigt Rechtshinweis
4. Startet Hydra-Angriff
5. Analysiert Ergebnisse
6. Generiert JSON-Output

### 4. Ergebnisse analysieren

Der Python-Analyzer wird automatisch aufgerufen, kann aber auch manuell gestartet werden:

```bash
python3 analyze_results.py

# Mit Credential-Verifizierung
python3 analyze_results.py --verify
```

## Ausgabe-Dateien

### hydra_output.txt
Hydra's Standard-Output mit gefundenen Credentials:
```
[5001][http-post-form] host: 127.0.0.1   login: admin   password: admin123
[5001][http-post-form] host: 127.0.0.1   login: test    password: test123
```

### successful_logins.json
Strukturierte JSON-Ausgabe:
```json
{
  "metadata": {
    "timestamp": "2025-11-17T16:30:00",
    "target": "http://127.0.0.1:5001/login"
  },
  "successful_logins": [
    {
      "username": "admin",
      "password": "admin123",
      "verified": true
    }
  ]
}
```

## Hydra vs. Selenium

Vergleich der beiden Brute-Force-Ansätze:

| Feature | Hydra | Selenium |
|---------|-------|----------|
| **Geschwindigkeit** | Sehr schnell | Langsam |
| **Ressourcen** | Minimal | Hoch (Browser) |
| **JavaScript** | Nein | Ja |
| **CSRF-Token** | Manuell | Automatisch |
| **Stealth** | Niedrig | Mittel |
| **Flexibilität** | Protokoll-begrenzt | Hoch |
| **Setup** | Binary | WebDriver |

### Wann welches Tool verwenden?

**Hydra:**
- Einfache HTML-Formulare ohne JavaScript
- Hohe Performance erforderlich
- Große Wordlists
- Standard HTTP/HTTPS

**Selenium:**
- JavaScript-basierte Formulare
- CSRF-Token automatisch handhaben
- Komplexe Interaktionen
- Browser-Fingerprinting umgehen

## Sicherheitshinweise

### Rechtliche Aspekte

**WARNUNG**: Dieses Tool ist ausschließlich für autorisierte Penetrationstests gedacht!

- NUR auf eigenen Systemen verwenden
- Schriftliche Genehmigung einholen für fremde Systeme
- Unbefugtes Testen ist illegal
- Rate-Limiting beachten
- Logs auf sensible Daten prüfen

### Best Practices

1. **Rate-Limiting**: Verwende moderate Thread-Anzahl
2. **Delays**: Füge Verzögerungen ein mit `-w` Parameter
3. **Logs**: Schütze Log-Dateien (enthalten Passwörter!)
4. **Cleanup**: Lösche Credentials nach Test
5. **Testing**: Teste nur in isolierten Umgebungen

## Hydra-Parameter erklärt

```bash
hydra -L users.txt -P pass.txt 127.0.0.1 -s 5001 \
  http-post-form "/login:username=^USER^&password=^PASS^:F=Fehler" \
  -t 4 -w 30 -o output.txt
```

- `-L users.txt`: Username-Wordlist
- `-P pass.txt`: Password-Wordlist
- `-s 5001`: Port
- `http-post-form`: Modul für HTTP POST
- `^USER^`, `^PASS^`: Platzhalter für Credentials
- `F=Fehler`: Failure String (F= prefix)
- `-t 4`: 4 parallele Threads
- `-w 30`: 30 Sekunden Timeout
- `-o output.txt`: Output-Datei

## Fehlerbehebung

### Hydra findet nichts

1. Prüfe `failure_string` in config.json
2. Teste Login manuell mit Browser DevTools
3. Prüfe ob CSRF-Token erforderlich ist
4. Verifiziere Form-Parameter (username/password Feldnamen)

### "Connection refused"

1. Prüfe ob Flask-App läuft
2. Verifiziere Port (5001)
3. Prüfe Firewall-Einstellungen

### Rate-Limiting triggert

1. Reduziere Threads: `-t 1` oder `-t 2`
2. Füge Delay hinzu: `-w 60`
3. Implementiere Proxy-Rotation (fortgeschritten)

## Erweiterte Verwendung

### Custom Wordlists

Verwende bekannte Wordlist-Sammlungen:

```bash
# SecLists (empfohlen)
git clone https://github.com/danielmiessler/SecLists.git

# Verwende in Hydra
hydra -L SecLists/Usernames/top-usernames-shortlist.txt \
      -P SecLists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt \
      ...
```

### Mit Proxy

```bash
hydra -L users.txt -P pass.txt 127.0.0.1 \
  http-post-form "..." \
  -x MIN:MAX:CHARSET  # Custom charset generation
```

### Debugging

Verwende `-d` für Debug-Output:
```bash
hydra -d -V -L users.txt -P pass.txt ...
```

## Performance-Optimierung

### Threads anpassen

```bash
# Langsam, stealthy
-t 1

# Standard
-t 4

# Schnell (Vorsicht: kann detected werden)
-t 16
```

### Wordlist-Optimierung

1. **Sortiere nach Wahrscheinlichkeit**: Häufige Passwörter zuerst
2. **Filtere Duplikate**: `sort -u passwords.txt`
3. **Verwende gezielte Listen**: Kontextbasierte Wordlists

## Vergleich mit anderen Tools

| Tool | Typ | Geschwindigkeit | Komplexität |
|------|-----|----------------|-------------|
| **Hydra** | CLI | Sehr schnell | Niedrig |
| **Selenium** | Browser | Langsam | Mittel |
| **Burp Suite** | GUI | Mittel | Hoch |
| **Medusa** | CLI | Schnell | Niedrig |
| **Patator** | CLI/Python | Mittel | Mittel |

## Zusätzliche Ressourcen

- [THC-Hydra GitHub](https://github.com/vanhauser-thc/thc-hydra)
- [Hydra Cheat Sheet](https://github.com/frizb/Hydra-Cheatsheet)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [SecLists Wordlists](https://github.com/danielmiessler/SecLists)

## Lizenz und Haftung

Dieses Tool ist für Bildungszwecke und autorisierte Sicherheitstests gedacht.

**Keine Haftung** für missbräuchliche Verwendung oder Schäden.

Verwende dieses Tool verantwortungsvoll und nur mit ausdrücklicher Genehmigung.

## Support

Bei Problemen oder Fragen:
1. Prüfe die Fehlerbehebung-Sektion
2. Teste mit `-d` Debug-Flag
3. Prüfe Hydra-Logs

## Changelog

- **v1.0** (2025-11-17): Initiale Version
  - Bash-Script für automatisierte Angriffe
  - Python-Analyzer für Ergebnisse
  - JSON-Konfiguration
  - Wordlist-Templates
