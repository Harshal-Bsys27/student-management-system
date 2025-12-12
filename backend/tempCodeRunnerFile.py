from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

# ------------------------------
# Project folder paths
# ------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # student-management-system root
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")  # backend/students.db

# ------------------------------
# Flask app initialization
# ------------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# ------------------------------
# Database setup
# ------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            branch TEXT NOT NULL,
            year TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------------
# FRONTEND PAGE ROUTES
# ------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/students")
def students_page():
    return render_template("students.html")  # student table page

@app.route("/add_student")
def add_student_page():
    return render_template("add_student.html")  # form page

# ------------------------------
# API ROUTES (for JS)
# ------------------------------

# GET all students
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()

    students = [
        {"id": r[0], "name": r[1], "roll": r[2], "branch": r[3], "year": r[4]}
        for r in rows
    ]
    return jsonify(students)

# ADD student
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.json

    if not all(k in data for k in ("name", "roll", "branch", "year")):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO students (name, roll, branch, year) VALUES (?, ?, ?, ?)",
        (data["name"], data["roll"], data["branch"], data["year"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201

# UPDATE student
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.json

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE students SET name=?, roll=?, branch=?, year=? WHERE id=?",
        (data["name"], data["roll"], data["branch"], data["year"], id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Student updated successfully"})

# DELETE student
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully"})

# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
