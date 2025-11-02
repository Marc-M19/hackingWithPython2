from flask import Flask, render_template, request, redirect, session, url_for, flash

import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for sessions

# --- CONFIG:
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "mysql",   
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
def register():
    if request.method == "POST":
        username = request.form.get("username", "")[:150]
        password = request.form.get("password", "")  # intentionally plain
        bio = request.form.get("bio", "")[:512]      # 512 char input
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(f"INSERT INTO users (username, password, bio) VALUES ('{username}','{password}','{bio}')")
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
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 1")
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
            # Kein Escaping - verwundbar!
            cur.execute(f"INSERT INTO posts (user_id, content) VALUES ({user_id}, '{content}')")
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
        cur.execute(f"SELECT username FROM users WHERE id = {r['user_id']} LIMIT 1")
        u = cur.fetchone()
        r["username"] = u["username"] if u else "unknown"

    cur.close()
    conn.close()
    return render_template("posts.html", posts=rows)

    # GET: alle Posts anzeigen
    # hier erstmal ohne Join, Username holen wir separat unten)
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT p.id, p.user_id, p.content, p.created_at FROM posts p ORDER BY p.created_at DESC")
    rows = cur.fetchall()

    # Benutzername pro Post nachladen
    for r in rows:
        cur.execute(f"SELECT username FROM users WHERE id = {r['user_id']} LIMIT 1")
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
        # Kein Replace für Demo-Zwecke!
        
        # NEUE VARIANTE: Führe die Query aus und zeige Ergebnis direkt
        try:
            # Versuche das Bio-Update
            cur.execute(f"UPDATE users SET bio = '{bio}' WHERE id = {uid}")
            conn.commit()
            
            # NEU: Zusätzliche Query für Datenextraktion
            # Wenn Bio einen UNION SELECT enthält, führe ihn separat aus
            if "UNION" in bio.upper() or "SELECT" in bio.upper():
                # Extrahiere und führe SELECT aus
                try:
                    # Führe eine separate Query aus um Daten anzuzeigen
                    cur.execute(f"SELECT '{bio}' as result")
                    result = cur.fetchone()
                    if result:
                        flash(f"Query Result: {result}", "info")
                except:
                    pass
                    
            flash("Bio aktualisiert.", "success")
        except Exception as e:
            conn.rollback()
            flash("Fehler beim Aktualisieren: " + str(e), "danger")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("users"))

    # GET bleibt gleich
    try:
        cur.execute(f"SELECT * FROM users WHERE id = {uid} LIMIT 1")
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
            # VERWUNDBAR: Direkte String-Konkatenation ohne Escaping!
            # Query gibt 3 Spalten zurück: id, username, bio
            query = f"SELECT id, username, bio FROM users WHERE username LIKE '%{search_term}%'"
            cur.execute(query)
            results = cur.fetchall()
        except Exception as e:
            flash(f"Fehler: {e}", "danger")
        finally:
            cur.close()
            conn.close()
    
    return render_template("search.html", results=results, search_term=search_term)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
