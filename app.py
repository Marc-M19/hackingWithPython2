from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for sessions

# --- CONFIG: change to your MySQL settings ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "example",   # change for your local DB
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
        # Insecure: string formatting used on purpose so you can practice SQLi
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
        # insecure: direct string formatting (on purpose)
        cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            session["user"] = {"id": row["id"], "username": row["username"]}
            flash("Logged in.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- USERS: shows ALL info about all users (intentionally unsafe) ---
@app.route("/users")
def users():
    if not session.get("user"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    # This returns ALL columns for all users. Good for experimenting.
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("users.html", users=rows, me=session.get("user"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
