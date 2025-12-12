from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            branch TEXT,
            year TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/students", methods=["GET"])
def get_students():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()

    students = [{"id": r[0], "name": r[1], "roll": r[2], "branch": r[3], "year": r[4]} for r in rows]
    return jsonify(students)

@app.route("/students", methods=["POST"])
def add_student():
    data = request.json
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("INSERT INTO students (name, roll, branch, year) VALUES (?,?,?,?)",
              (data["name"], data["roll"], data["branch"], data["year"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student added"})

@app.route("/students/<id>", methods=["PUT"])
def update_student(id):
    data = request.json
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("UPDATE students SET name=?, roll=?, branch=?, year=? WHERE id=?",
              (data["name"], data["roll"], data["branch"], data["year"], id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated"})

@app.route("/students/<id>", methods=["DELETE"])
def delete_student(id):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"})

if __name__ == "__main__":
    app.run(debug=True)