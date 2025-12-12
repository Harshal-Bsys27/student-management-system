from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

# ------------------------------
# Project folder paths
# ------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # root folder
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")  # backend/db

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
    return render_template("students.html")

@app.route("/add_student")
def add_student_page():
    return render_template("add_student.html")

@app.route("/student/<int:id>")
def student_profile_page(id):
    return render_template("student_profile.html")

# ------------------------------
# API ROUTES
# ------------------------------

# Get all students
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()

    students = [{"id": r[0], "name": r[1], "roll": r[2], "branch": r[3], "year": r[4]} for r in rows]
    return jsonify(students)

# Get a single student
@app.route("/api/students/<int:id>", methods=["GET"])
def get_student(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Student not found"}), 404

    student = {"id": row[0], "name": row[1], "roll": row[2], "branch": row[3], "year": row[4]}
    return jsonify(student)

# Add student
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.json
    if not all(k in data for k in ("name", "roll", "branch", "year")):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO students (name, roll, branch, year) VALUES (?, ?, ?, ?)",
              (data["name"], data["roll"], data["branch"], data["year"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student added successfully"}), 201

# Update student
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE students SET name=?, roll=?, branch=?, year=? WHERE id=?",
              (data["name"], data["roll"], data["branch"], data["year"], id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated successfully"})

# Delete student
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted successfully"})

# Analytics route for dashboard charts
@app.route("/api/students/analytics", methods=["GET"])
def students_analytics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Count students per branch
    c.execute("SELECT branch, COUNT(*) FROM students GROUP BY branch")
    branch_counts = c.fetchall()
    # Count students per year
    c.execute("SELECT year, COUNT(*) FROM students GROUP BY year")
    year_counts = c.fetchall()
    conn.close()

    return jsonify({
        "branches": {b: count for b, count in branch_counts},
        "years": {y: count for y, count in year_counts}
    })

# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
