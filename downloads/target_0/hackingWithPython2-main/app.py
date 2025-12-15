from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, abort
import mysql.connector
import os
from pathlib import Path

app = Flask(__name__)

# Projekt-Verzeichnis für Directory Listing
PROJECT_DIR = Path(__file__).parent
app.secret_key = os.urandom(24)  # for sessions


# ══════════════════════════════════════════════════════════════════════════════
app.config['SESSION_COOKIE_HTTPONLY'] = True  # <-- XSS FIX #1: War False, jetzt True!
# ══════════════════════════════════════════════════════════════════════════════



# --- CONFIG: Datenbank-Einstellungen für "Hebeln Mit Kopf" ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "example",   # Ändere dies für deine lokale DB
    "database": "hackingdb",
    "port": 3306,
    "consume_results": True  # Automatically consume unread results
}
# ---------------------------------------------------------------

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

# --- AUTOR REGISTRIERUNG ---
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")[:150]
        password = request.form.get("password", "")  # intentionally plain (für Demo)
        bio = request.form.get("bio", "")[:512]      # Trading-Fokus / Über dich
        # Secure: using parameterized queries to prevent SQL Injection
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password, bio) VALUES (%s, %s, %s)", (username, password, bio))
            conn.commit()
            flash("Autor-Account erfolgreich erstellt! Du kannst dich jetzt anmelden.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            conn.rollback()
            flash("Fehler bei der Registrierung: " + str(e), "danger")
        finally:
            cur.close()
            conn.close()
    return render_template("register.html")

# --- AUTOR LOGIN ---
@app.route("/login", methods=["GET","POST"])
#@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        try:
            # Secure: using parameterized queries to prevent SQL Injection
            query = "SELECT * FROM users WHERE username = %s AND password = %s LIMIT 1"
            cur.execute(query, (username, password))
            row = cur.fetchone()
            # Consume any remaining results to prevent "Unread result" errors
            try:
                while cur.nextset():
                    pass
            except:
                pass

            if row:
                session["user"] = {"id": row["id"], "username": row["username"]}
                flash("Erfolgreich angemeldet! Willkommen zurück, " + row["username"] + ".", "success")
                cur.close()
                conn.close()
                return redirect(url_for("index"))
            else:
                flash("Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.", "danger")
        except Exception as e:
            flash(f"SQL Fehler: {str(e)}", "danger")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass
    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- MARKTANALYSEN: Zeigt alle Posts/Analysen (intentionally unsafe für Demo) ---
@app.route("/users")
def users():
    if not session.get("user"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    # Zeigt alle Autoren/Posts - in Zukunft könnte dies eine echte "posts" Tabelle sein
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("users.html", users=rows, me=session.get("user"))

# --- VULNERABLE SEARCH ENDPOINT (UNION-based SQL Injection Demo) ---
@app.route("/search")
def search():
    if not session.get("user"):
        return redirect(url_for("login"))

    query = request.args.get("q", "")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    results = []
    error = None

    if query:
        try:
            # Secure: using parameterized queries with LIKE to prevent SQL Injection
            sql = "SELECT id, username, bio FROM users WHERE username LIKE %s OR bio LIKE %s"
            search_pattern = f"%{query}%"
            cur.execute(sql, (search_pattern, search_pattern))
            results = cur.fetchall()
        except Exception as e:
            error = str(e)

    cur.close()
    conn.close()
    return render_template("search.html", query=query, results=results, error=error, user=session.get("user"))

# --- DIRECTORY LISTING (Absichtlich unsicher für Security-Testing!) ---
# Direkte Datei-Routen für Brute-Force Scanner (z.B. /app.py, /.env)
@app.route("/<path:filename>")
def serve_root_file(filename):
    """Liefert Dateien direkt aus dem Projektverzeichnis (UNSICHER!)"""
    # Nur bestimmte Dateiendungen erlauben
    allowed_extensions = ['.py', '.txt', '.json', '.yaml', '.yml', '.sql', '.env', '.md', '.sh', '.cfg', '.ini', '.conf']

    # Prüfe ob Datei existiert und erlaubt ist
    filepath = PROJECT_DIR / filename

    # Auch versteckte Dateien wie .env, .git/config erlauben
    if filepath.exists() and filepath.is_file():
        # Prüfe Extension oder spezielle Dateien
        if any(filename.endswith(ext) for ext in allowed_extensions) or filename.startswith('.'):
            try:
                return send_from_directory(PROJECT_DIR, filename)
            except:
                pass

    abort(404)

@app.route("/files")
@app.route("/files/")
@app.route("/files/<path:subpath>")
def directory_listing(subpath=""):
    """
    Directory Listing - zeigt alle Dateien im Projektverzeichnis.
    ABSICHTLICH UNSICHER für Security-Testing-Zwecke!
    """
    # Basis-Pfad
    base_path = PROJECT_DIR
    target_path = base_path / subpath if subpath else base_path

    # Sicherheits-Check: Verhindere Path Traversal außerhalb des Projekts
    try:
        target_path = target_path.resolve()
        if not str(target_path).startswith(str(base_path.resolve())):
            abort(403)
    except:
        abort(404)

    # Wenn es eine Datei ist -> direkt ausliefern
    if target_path.is_file():
        return send_from_directory(target_path.parent, target_path.name)

    # Wenn es ein Verzeichnis ist -> Liste anzeigen
    if target_path.is_dir():
        items = []

        # Parent-Link (wenn nicht im Root)
        if subpath:
            parent = str(Path(subpath).parent)
            if parent == ".":
                parent = ""
            items.append({
                "name": "../",
                "path": f"/files/{parent}" if parent else "/files",
                "is_dir": True,
                "size": "-"
            })

        # Dateien und Ordner auflisten
        for item in sorted(target_path.iterdir()):
            # Versteckte Ordner wie __pycache__ überspringen (aber .env etc. zeigen!)
            if item.name == "__pycache__":
                continue

            rel_path = item.relative_to(base_path)
            items.append({
                "name": item.name + ("/" if item.is_dir() else ""),
                "path": f"/files/{rel_path}",
                "is_dir": item.is_dir(),
                "size": f"{item.stat().st_size:,} B" if item.is_file() else "-"
            })

        # Einfaches HTML für Directory Listing (Apache-Style)
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Index of /{subpath}</title>
    <style>
        body {{ font-family: monospace; margin: 20px; }}
        h1 {{ border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
        table {{ border-collapse: collapse; }}
        td, th {{ padding: 5px 15px; text-align: left; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .dir {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Index of /{subpath}</h1>
    <table>
        <tr><th>Name</th><th>Size</th></tr>
"""
        for item in items:
            css_class = 'dir' if item['is_dir'] else ''
            html += f'        <tr><td class="{css_class}"><a href="{item["path"]}">{item["name"]}</a></td><td>{item["size"]}</td></tr>\n'

        html += """    </table>
    <hr>
    <p><em>Directory Listing enabled for security testing</em></p>
</body>
</html>"""
        return html

    abort(404)

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
