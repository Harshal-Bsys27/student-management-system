from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "profiles")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            year TEXT NOT NULL,
            profile_picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(marked_by) REFERENCES users(id),
            UNIQUE(student_id, attendance_date)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            marks REAL NOT NULL,
            grade TEXT,
            semester TEXT NOT NULL,
            added_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(added_by) REFERENCES users(id)
        )
    """)

    # Add migration for profile_picture column if it doesn't exist
    try:
        c.execute("ALTER TABLE students ADD COLUMN profile_picture TEXT")
        print("✓ Added profile_picture column to students table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ profile_picture column already exists")
        else:
            print(f"Migration error: {e}")

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

def log_audit(action, details=""):
    """Log admin actions for audit trail"""
    try:
        if "user_id" in session:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
            """, (session["user_id"], action, details))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Audit logging error: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.json
            
            if not data.get("username") or not data.get("password"):
                return jsonify({"error": "Username and password required"}), 400

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (data["username"],))
            user = c.fetchone()
            conn.close()

            if user:
                print(f"User found: {user[1]}, checking password...")
                if check_password_hash(user[3], data["password"]):
                    session["user_id"] = user[0]
                    session["username"] = user[1]
                    session["role"] = user[4]
                    print(f"Login successful for {user[1]}")
                    return jsonify({"message": "Login successful", "role": user[4]}), 200
                else:
                    print(f"Password mismatch for {user[1]}")
            else:
                print(f"User not found: {data['username']}")

            return jsonify({"error": "Invalid credentials"}), 401

        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Login error: {str(e)}"}), 500

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.json
            
            if not data.get("username") or not data.get("email") or not data.get("password"):
                return jsonify({"error": "All fields are required"}), 400

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
                print(f"User registered: {data['username']} as {role}")
            except sqlite3.IntegrityError as ie:
                conn.close()
                print(f"Registration error: {ie}")
                return jsonify({"error": "Username or email already exists"}), 400

            conn.close()
            return jsonify({"message": "Registration successful", "role": role}), 200

        except Exception as e:
            print(f"Register error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Registration error: {str(e)}"}), 500

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------------------------------
# PAGES
# -------------------------------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("admin_dashboard.html")


@app.route("/user/dashboard")
def user_dashboard():
    if not is_logged_in():
        return redirect("/login")
    return render_template("user_dashboard.html")


@app.route("/")
def index():
    if not is_logged_in():
        return redirect("/login")
    
    # Redirect based on role
    if is_admin():
        return redirect("/admin/dashboard")
    else:
        return redirect("/user/dashboard")


@app.route("/dashboard")
def dashboard():
    """Generic dashboard - shows based on role"""
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
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("add_student.html")


@app.route("/edit_student/<int:student_id>")
def edit_student_page(student_id):
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("edit_student.html", student_id=student_id)


@app.route("/admin/users")
def admin_users_page():
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("admin_users.html")


@app.route("/admin/audit-logs")
def admin_audit_page():
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("admin_audit.html")


@app.route("/student/<int:student_id>")
def student_profile(student_id):
    if not is_logged_in():
        return redirect("/login")
    return render_template("student_profile.html", student_id=student_id)

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
        {
            "id": r[0], 
            "name": r[1], 
            "roll": r[2], 
            "branch": r[3], 
            "year": r[4],
            "profile_picture": r[5]
        }
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
        log_audit("ADD_STUDENT", f"Added student: {data['name']} ({data['roll']})")
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Roll number already exists"}), 400

    conn.close()
    return jsonify({"message": "Student added successfully"}), 201


@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (student_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "id": row[0], 
        "name": row[1], 
        "roll": row[2], 
        "branch": row[3], 
        "year": row[4],
        "profile_picture": row[5]
    })


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT * FROM students WHERE id=?", (student_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    try:
        c.execute("""
            UPDATE students 
            SET name=?, roll=?, branch=?, year=?
            WHERE id=?
        """, (data["name"], data["roll"], data["branch"], data["year"], student_id))
        conn.commit()
        log_audit("UPDATE_STUDENT", f"Updated student ID: {student_id}")
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Roll number already exists"}), 400

    conn.close()
    return jsonify({"message": "Student updated successfully"}), 200


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT name, roll FROM students WHERE id=?", (student_id,))
    student = c.fetchone()
    
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    log_audit("DELETE_STUDENT", f"Deleted student: {student[0]} ({student[1]})")
    conn.close()

    return jsonify({"message": "Student deleted successfully"}), 200

# -------------------------------------------------
# USER APIs
# -------------------------------------------------
@app.route("/api/users", methods=["GET"])
def get_users():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "id": row[0], 
                "username": row[1], 
                "email": row[2], 
                "role": row[3], 
                "created_at": row[4]
            })
        
        print(f"Users fetched: {len(result)}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error fetching users: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>/role", methods=["PUT"])
def change_user_role(user_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    if user_id == session.get("user_id"):
        return jsonify({"error": "Cannot change your own role"}), 400

    data = request.json
    new_role = data.get("role")

    if new_role not in ["admin", "user"]:
        return jsonify({"error": "Invalid role"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404

        c.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
        conn.commit()
        log_audit("CHANGE_USER_ROLE", f"Changed {user[0]} role to {new_role}")
        conn.close()

        return jsonify({"message": "User role updated successfully"}), 200
    except Exception as e:
        print(f"Error changing user role: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# AUDIT LOGS APIs
# -------------------------------------------------
@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            SELECT al.id, u.username, al.action, al.details, al.timestamp 
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC
            LIMIT 100
        """)
        rows = c.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "id": row[0], 
                "username": row[1] or "Unknown", 
                "action": row[2], 
                "details": row[3] or "", 
                "timestamp": row[4]
            })
        
        print(f"Audit logs fetched: {len(result)}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# -------------------------------------------------
# ANALYTICS API
# -------------------------------------------------
@app.route("/api/students/analytics")
def analytics():
    try:
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
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# ATTENDANCE ROUTES
# -------------------------------------------------
@app.route("/admin/attendance")
def attendance_page():
    if not is_logged_in() or not is_admin():
        return redirect("/login")
    return render_template("attendance.html")


@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    date = request.args.get("date", default=None)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if date:
            c.execute("""
                SELECT a.id, s.id, s.name, s.roll, a.status, a.attendance_date
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.attendance_date = ?
                ORDER BY s.name
            """, (date,))
        else:
            c.execute("""
                SELECT a.id, s.id, s.name, s.roll, a.status, a.attendance_date
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                ORDER BY a.attendance_date DESC, s.name
                LIMIT 50
            """)
        
        rows = c.fetchall()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "student_id": r[1],
                "name": r[2],
                "roll": r[3],
                "status": r[4],
                "date": r[5]
            }
            for r in rows
        ])
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/attendance", methods=["POST"])
def mark_attendance():
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            INSERT OR REPLACE INTO attendance (student_id, attendance_date, status, marked_by)
            VALUES (?, ?, ?, ?)
        """, (data["student_id"], data["date"], data["status"], session["user_id"]))
        
        conn.commit()
        log_audit("MARK_ATTENDANCE", f"Marked attendance for student {data['student_id']} on {data['date']}")
        conn.close()
        
        return jsonify({"message": "Attendance marked successfully"}), 201
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/attendance/student/<int:student_id>", methods=["GET"])
def get_student_attendance(student_id):
    """Get attendance for any student - accessible to all logged-in users"""
    if not is_logged_in():
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            SELECT a.id, a.attendance_date, a.status, u.username
            FROM attendance a
            LEFT JOIN users u ON a.marked_by = u.id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC
        """, (student_id,))
        
        rows = c.fetchall()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "date": r[1],
                "status": r[2],
                "marked_by": r[3] or "System"
            }
            for r in rows
        ])
    except Exception as e:
        print(f"Error fetching student attendance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/grades/student/<int:student_id>", methods=["GET"])
def get_student_grades(student_id):
    """Get grades for any student - accessible to all logged-in users"""
    if not is_logged_in():
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, subject, marks, grade, semester
            FROM grades
            WHERE student_id = ?
            ORDER BY semester DESC, subject
            LIMIT 5
        """, (student_id,))
        
        rows = c.fetchall()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "subject": r[1],
                "marks": r[2],
                "grade": r[3],
                "semester": r[4]
            }
            for r in rows
        ])
    except Exception as e:
        print(f"Error fetching student grades: {e}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# ATTENDANCE DELETE ENDPOINT
# -------------------------------------------------
@app.route("/api/attendance/<int:attendance_id>", methods=["DELETE"])
def delete_attendance(attendance_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("DELETE FROM attendance WHERE id=?", (attendance_id,))
        conn.commit()
        log_audit("DELETE_ATTENDANCE", f"Deleted attendance record ID: {attendance_id}")
        conn.close()

        return jsonify({"message": "Attendance record deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting attendance: {e}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# GRADES UPDATE ENDPOINT
# -------------------------------------------------
@app.route("/api/grades/<int:grade_id>", methods=["PUT"])
def update_grade(grade_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    data = request.json
    marks = float(data.get("marks", 0))

    # Calculate grade based on marks
    if marks >= 90:
        grade = "A+"
    elif marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 60:
        grade = "C"
    elif marks >= 50:
        grade = "D"
    else:
        grade = "F"

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("UPDATE grades SET marks=?, grade=? WHERE id=?", (marks, grade, grade_id))
        conn.commit()
        log_audit("UPDATE_GRADE", f"Updated grade ID: {grade_id} with marks: {marks}")
        conn.close()

        return jsonify({"message": "Grade updated successfully", "grade": grade}), 200
    except Exception as e:
        print(f"Error updating grade: {e}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# GRADES DELETE ENDPOINT
# -------------------------------------------------
@app.route("/api/grades/<int:grade_id>", methods=["DELETE"])
def delete_grade(grade_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("DELETE FROM grades WHERE id=?", (grade_id,))
        conn.commit()
        log_audit("DELETE_GRADE", f"Deleted grade record ID: {grade_id}")
        conn.close()

        return jsonify({"message": "Grade record deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting grade: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# PROFILE PICTURE UPLOAD
# -------------------------------------------------
@app.route("/api/students/<int:student_id>/profile-picture", methods=["POST"])
def upload_profile_picture(student_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use PNG, JPG, JPEG, or GIF"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM students WHERE id=?", (student_id,))
        student = c.fetchone()

        if not student:
            conn.close()
            return jsonify({"error": "Student not found"}), 404

        # Generate clean filename without special characters
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"student_{student_id}_{timestamp}.{file_ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        file.save(filepath)

        # Update database
        c.execute("UPDATE students SET profile_picture=? WHERE id=?", (filename, student_id))
        conn.commit()
        conn.close()

        log_audit("UPLOAD_PROFILE_PICTURE", f"Uploaded profile picture for student {student_id}")

        return jsonify({
            "message": "Profile picture uploaded successfully",
            "filename": filename,
            "url": f"/static/uploads/profiles/{filename}"
        }), 200

    except Exception as e:
        print(f"Error uploading profile picture: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/students/<int:student_id>/profile-picture", methods=["DELETE"])
def delete_profile_picture(student_id):
    if not is_admin():
        return jsonify({"error": "Admin access only"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT profile_picture FROM students WHERE id=?", (student_id,))
        result = c.fetchone()

        if not result:
            conn.close()
            return jsonify({"error": "Student not found"}), 404

        if result[0]:
            filepath = os.path.join(UPLOAD_FOLDER, result[0])
            if os.path.exists(filepath):
                os.remove(filepath)

        c.execute("UPDATE students SET profile_picture=NULL WHERE id=?", (student_id,))
        conn.commit()
        conn.close()

        log_audit("DELETE_PROFILE_PICTURE", f"Deleted profile picture for student {student_id}")

        return jsonify({"message": "Profile picture deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting profile picture: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# DEBUG ENDPOINTS (Remove in production)
# -------------------------------------------------
@app.route("/api/debug/db-status")
def db_status():
    """Check database tables and data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        
        status = {}
        for table in tables:
            table_name = table[0]
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = c.fetchone()[0]
            status[table_name] = count
        
        conn.close()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
