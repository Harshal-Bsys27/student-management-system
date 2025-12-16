from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")

# -------------------------------------------------
# APP INIT
# -------------------------------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "super_secret_key_change_later"
CORS(app)

# -------------------------------------------------
# DATABASE INIT
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT UNIQUE NOT NULL,
            branch TEXT NOT NULL,
            year TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------
# GLOBAL TEMPLATE CONTEXT
# -------------------------------------------------
@app.context_processor
def inject_user():
    return dict(
        logged_in=("user_id" in session),
        username=session.get("username"),
        role=session.get("role")
    )

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def is_logged_in():
    return "user_id" in session

def is_admin():
    return session.get("role") == "admin"

# -------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (data["username"],))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], data["password"]):
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[4]
            return jsonify({"message": "Login successful", "role": user[4]})

        return jsonify({"error": "Invalid credentials"}), 401

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.json
        password_hash = generate_password_hash(data["password"])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # First registered user becomes ADMIN
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        role = "admin" if user_count == 0 else "user"

        try:
            c.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (data["username"], data["email"], password_hash, role))
            conn.commit()
        except:
            conn.close()
            return jsonify({"error": "User already exists"}), 400

        conn.close()
        return jsonify({"message": "Registration successful", "role": role})

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------------------------------
# PAGES
# -------------------------------------------------
@app.route("/")
def index():
    if not is_logged_in():
        return redirect("/login")
    return render_template("index.html")


@app.route("/students")
def students_page():
    if not is_logged_in():
        return redirect("/login")
    return render_template("students.html")


@app.route("/add_student")
def add_student_page():
    if not is_logged_in():
        return redirect("/login")
    return render_template("add_student.html")

# -------------------------------------------------
# STUDENT APIs
# -------------------------------------------------
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "name": r[1], "roll": r[2], "branch": r[3], "year": r[4]}
        for r in rows
    ])


@app.route("/api/students", methods=["POST"])
def add_student():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO students (name, roll, branch, year)
            VALUES (?, ?, ?, ?)
        """, (data["name"], data["roll"], data["branch"], data["year"]))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Roll number already exists"}), 400

    conn.close()
    return jsonify({"message": "Student added successfully"}), 201

# -------------------------------------------------
# ANALYTICS API
# -------------------------------------------------
@app.route("/api/students/analytics")
def analytics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT branch, COUNT(*) FROM students GROUP BY branch")
    branches = dict(c.fetchall())

    c.execute("SELECT year, COUNT(*) FROM students GROUP BY year")
    years = dict(c.fetchall())

    conn.close()

    return jsonify({
        "branches": branches,
        "years": years
    })

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
