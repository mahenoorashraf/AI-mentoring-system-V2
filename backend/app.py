import os

print("RUNNING FILE:", os.path.abspath(__file__))
from flask import send_file
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    jsonify,
    abort,
    flash
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import check_password_hash
from flask import send_from_directory
import pandas as pd
import os
from database import get_connection
from dotenv import load_dotenv
from openai import OpenAI

# =========================================================
# Load Environment Variables
# =========================================================
load_dotenv()

# =========================================================
# Paths
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = BASE_DIR   # templates and static are inside backend/

# =========================================================
# Flask App Setup
# =========================================================
app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static")
)

app.secret_key = os.getenv("SECRET_KEY", "final_ai_project_secret_key")
# =========================================================
# Flask-Login Setup
# =========================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# =========================================================
# User Class
# =========================================================
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role
@login_manager.user_loader
def load_user(user_id):
    print("========== LOAD USER ==========")
    print("user_id from session:", user_id)
    conn = get_connection()

    query = """
    SELECT UserID, Username, Role
    FROM Users
    WHERE UserID = ?
    """

    user_df = pd.read_sql(query, conn, params=[user_id])

    conn.close()

    if user_df.empty:
        return None

    row = user_df.iloc[0]

    return User(
        id=row["UserID"],
        username=row["Username"],
        role=row["Role"]
    )
# =========================================================
# OpenAI Client
# =========================================================
client = None
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# =========================================================
# Automatically Find students.csv
# =========================================================
def find_students_csv():
    possible_paths = [
        # backend/data/students.csv
        os.path.join(BASE_DIR, "data", "students.csv"),

        # backend/students.csv
        os.path.join(BASE_DIR, "students.csv"),

        # project_root/data/students.csv
        os.path.join(os.path.dirname(BASE_DIR), "data", "students.csv"),

        # project_root/students.csv
        os.path.join(os.path.dirname(BASE_DIR), "students.csv"),
    ]

    print("\nSearching for students.csv...")
    for path in possible_paths:
        print("Checking:", path)
        if os.path.exists(path):
            print("Found students.csv at:", path)
            return path

    raise FileNotFoundError(
        "\nstudents.csv not found.\n\n"
        "Please place the file in one of these locations:\n"
        f"1. {os.path.join(BASE_DIR, 'data', 'students.csv')}\n"
        f"2. {os.path.join(BASE_DIR, 'students.csv')}\n"
        f"3. {os.path.join(os.path.dirname(BASE_DIR), 'data', 'students.csv')}\n"
        f"4. {os.path.join(os.path.dirname(BASE_DIR), 'students.csv')}\n"
    )

# =========================================================
# Load Student Data
# =========================================================
#DATA_PATH = find_students_csv()
#print(f"\nLoading students data from: {DATA_PATH}")

#students_df = pd.read_csv(DATA_PATH)

#if "student_id" not in students_df.columns:
 #   raise ValueError("students.csv must contain a 'student_id' column.")

#students_df["student_id"] = students_df["student_id"].astype(str)
# Load Student Data from SQL Server
conn = get_connection()

students_df = pd.read_sql("SELECT * FROM students", conn)

students_df["StudentID"] = students_df["StudentID"].astype(str)

print(f"\nStudents loaded from SQL Server: {len(students_df)}")

# =========================================================
# Helper Functions
# =========================================================
def get_logged_in_student():
    student_id = session.get("student_id")

    if not student_id:
        return None

    row = students_df[students_df["StudentID"] == str(student_id)]

    if row.empty:
        return None

    return row.iloc[0].to_dict()


def get_chat_history():
    if "chat_history" not in session:
        session["chat_history"] = []
    return session["chat_history"]

# =========================================================
# Routes
# =========================================================
@app.route("/")
def home():
    return redirect("/login")


# =========================================================
# Login
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("student_id", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_connection()

        query = """
        SELECT UserID,
               Username,
               PasswordHash,
               Role
        FROM Users
        WHERE Username = ?
        """

        user_df = pd.read_sql(
            query,
            conn,
            params=[username]
        )

        conn.close()

        if user_df.empty:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

        user = user_df.iloc[0]
        print("Username:", username)
        print("Entered Password:", password)
        print("Database User:", user["Username"])
        print("Stored Hash:", user["PasswordHash"])
        result = check_password_hash(
            user["PasswordHash"],
            password
        )
        print("Password Match:", result)
        if not result:
    
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

        login_user(
            User(
                id=user["UserID"],
                username=user["Username"],
                role=user["Role"]
            )
        )

        session["student_id"] = user["Username"]
        session["category"] = "Academic"
        session["chat_history"] = []

        if user["Role"] == "Admin":
            return redirect("/admin")

        return redirect("/dashboard")

    return render_template("login.html")
# =========================================================
# Logout
# =========================================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/login")

# 
# Admin Dashboard=========================================================
# =========================================================
@app.route("/admin")
@login_required
def admin():

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()

    # Total Students
    students_count = pd.read_sql(
        "SELECT COUNT(*) AS Total FROM students",
        conn
    ).iloc[0]["Total"]

    # Total Mentors
    mentors_count = pd.read_sql(
        "SELECT COUNT(*) AS Total FROM mentors",
        conn
    ).iloc[0]["Total"]

    # Average Attendance
    avg_attendance = round(
        pd.read_sql(
            "SELECT AVG(Attendance) AS AvgAttendance FROM students",
            conn
        ).iloc[0]["AvgAttendance"],
        1
    )

    # Average GPA
    avg_gpa = round(
        pd.read_sql(
            "SELECT AVG(GPA) AS AvgGPA FROM students",
            conn
        ).iloc[0]["AvgGPA"],
        2
    )

    # High Risk Students
    high_risk = pd.read_sql("""
        SELECT COUNT(*) AS Total
        FROM students
        WHERE Attendance < 75
           OR GPA < 6
    """, conn).iloc[0]["Total"]

    # Pending Mentor Booking Count
    pending_requests = pd.read_sql("""
        SELECT COUNT(*) AS Total
        FROM MentorSessions
        WHERE Status = 'Pending'
    """, conn).iloc[0]["Total"]

    # Pending Mentor Booking Details
    notifications = pd.read_sql("""
        SELECT
            ms.SessionID,
            ms.StudentID,
            m.MentorName,
            ms.BookingDate
        FROM MentorSessions ms
        JOIN Mentors m
            ON ms.MentorID = m.MentorID
        WHERE ms.Status = 'Pending'
        ORDER BY ms.SessionID DESC
    """, conn)

    # Recent Students
    recent_students = pd.read_sql("""
        SELECT
            StudentID,
            Program,
            Semester,
            GPA,
            Attendance
        FROM students
        ORDER BY StudentID
    """, conn)

    conn.close()

    return render_template(
        "admin.html",
        students_count=students_count,
        mentors_count=mentors_count,
        avg_attendance=avg_attendance,
        avg_gpa=avg_gpa,
        high_risk=high_risk,
        recent_students=recent_students.to_dict("records"),
        pending_requests=pending_requests,
        notifications=notifications.to_dict("records")
    )
@app.route("/admin/student/<student_id>")
@login_required
def view_student(student_id):

    if current_user.role != "Admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_connection()

    query = """
    SELECT *
    FROM students
    WHERE StudentID = ?
    """

    df = pd.read_sql(query, conn, params=[student_id])

    conn.close()

    if df.empty:
        return jsonify({"error": "Student not found"}), 404

    student = df.iloc[0]

    # --------------------------
    # AI Recommendation
    # --------------------------

    recommendations = []

    if float(student["Attendance"]) < 75:
        recommendations.append(
            "Improve attendance by attending classes regularly."
        )

    if float(student["GPA"]) < 6:
        recommendations.append(
            "Focus on academics to improve your GPA."
        )

    stress = float(student.get("StressLevel") or 0)
    sleep = float(student.get("SleepHours") or 0)
    mental = float(student.get("MentalWellBeing") or 0)
    productivity = float(student.get("ProductivityScore") or 0)
    distractions = float(student.get("Distractions") or 0)

    if stress > 7: 
        risk = "High"
    elif stress > 4:
        risk = "Medium"
    else:
        risk = "Low"
        recommendations.append(
            "High stress detected. Meet your mentor or counselor."
        )

    if sleep < 6:
        recommendations.append(
        "Increase your daily sleep to at least 7 hours."
    )

    if productivity < 60:
        recommendations.append(
        "Reduce distractions and follow a study schedule."
    )
    if not recommendations:
        recommendations.append(
            "Excellent performance! Keep up the good work."
        )

    return jsonify({

    "StudentID": str(student["StudentID"]),
    "Program": str(student["Program"]),
    "Semester": int(student["Semester"]),
    "Attendance": float(student["Attendance"]),
    "GPA": float(student["GPA"]),
    "RiskLevel": risk,
    "AIRecommendation": " ".join(recommendations)

})
@app.route("/settings")
@login_required
def settings():

    conn = get_connection()

    admin = pd.read_sql("""
        SELECT Username, Email, Role
        FROM Users
        WHERE Username = ?
    """, conn, params=[current_user.username])

    conn.close()

    return render_template(
        "settings.html",
        admin=admin.iloc[0]
    )
# =========================================================
# Chatbot
# =========================================================
@app.route("/chatbot")
def chatbot():
    student = get_logged_in_student()

    if not student:
        return redirect("/login")

    return render_template(
        "chatbot.html",
        category=session.get("category", "Academic")
    )
@app.route("/students")
@login_required
def students():

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()

    students_df = pd.read_sql("""

        SELECT *
        FROM students
        ORDER BY StudentID

    """, conn)

    conn.close()

    return render_template(
        "students.html",
        students=students_df.to_dict("records")
    )

@app.route("/student/add", methods=["POST"])
@login_required
def add_student():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO students
        (
            StudentID,
            Program,
            Semester,
            Age,
            Attendance,
            GPA,
            AssignmentsCompletion,
            EngagementScore
        )

        VALUES (?,?,?,?,?,?,?,?)

    """,

    request.form["StudentID"],
    request.form["Program"],
    request.form["Semester"],
    request.form["Age"],
    request.form["Attendance"],
    request.form["GPA"],
    request.form["AssignmentsCompletion"],
    request.form["EngagementScore"]

    )

    conn.commit()
    conn.close()

    return jsonify({
    "success": True,
    "message": "Student added successfully."
})
@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "Student":
        return redirect("/admin")

    student = get_logged_in_student()

    if not student:
        return redirect("/login")

    # Basic calculations
    attendance = float(student.get("Attendance", 0))
    gpa = float(student.get("GPA", 0))

    if attendance < 75 or gpa < 6:
        risk_category = "High Risk"
        risk_status = "Needs Attention"
        performance_summary = "Your academic performance needs improvement."
        suggestions = "Improve attendance, study regularly and meet your mentor."
    else:
        risk_category = "Low Risk"
        risk_status = "Good"
        performance_summary = "You are performing well."
        suggestions = "Keep maintaining your performance."

    sri = round((attendance + (gpa * 10)) / 2, 2)

    return render_template(
        "dashboard.html",
        student=student,
        sri=sri,
        risk_category=risk_category,
        risk_status=risk_status,
        performance_summary=performance_summary,
        suggestions=suggestions
    )
@app.route("/student/edit", methods=["POST"])
@login_required
def edit_student():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE students

        SET

            Program=?,
            Semester=?,
            Attendance=?,
            GPA=?

        WHERE StudentID=?

    """,

    request.form["Program"],
    request.form["Semester"],
    request.form["Attendance"],
    request.form["GPA"],
    request.form["StudentID"]

    )

    conn.commit()
    conn.close()

    return jsonify({
    "success": True,
    "message": "Student updated successfully."
})
@app.route("/student/delete", methods=["POST"])
@login_required
def delete_student():
    print("DELETE ROUTE CALLED")
    print(request.form)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM students

        WHERE StudentID=?

    """,

    request.form["StudentID"]

    )

    conn.commit()
    conn.close()

    return jsonify({
    "success": True,
    "message": "Student deleted successfully."
})

@app.route("/mentors")
@login_required
def mentors():

    conn = get_connection()

    mentors_df = pd.read_sql("""
        SELECT *
        FROM mentors
        ORDER BY CAST(SUBSTRING(MentorID,2,LEN(MentorID)) AS INT)
    """, conn)

    student_id = session.get("student_id")

    booked = pd.read_sql("""
        SELECT MentorID
        FROM MentorSessions
        WHERE StudentID = ?
          AND Status IN ('Pending','Approved')
    """, conn, params=[student_id])

    conn.close()

    booked_ids = booked["MentorID"].tolist()

    return render_template(
        "mentors.html",
        mentors=mentors_df.to_dict("records"),
        booked_ids=booked_ids
    )
@app.route("/book_session", methods=["POST"])
@login_required
def book_session():

    if current_user.role != "Student":
        return jsonify({
            "success": False,
            "message": "Only students can book sessions."
        }), 403

    data = request.get_json()

    mentor_id = data.get("mentor_id")
    student_id = session.get("student_id")

    conn = get_connection()
    cursor = conn.cursor()

    # Check for an active booking
    cursor.execute("""
    SELECT COUNT(*)
    FROM MentorSessions
    WHERE StudentID = ?
      AND MentorID = ?
      AND Status IN ('Pending','Approved')
""", (student_id, mentor_id))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return jsonify({
            "success": False,
            "message": "You already have an active booking with this mentor."
        })

    # Create new booking
    cursor.execute("""
        INSERT INTO MentorSessions
        (
            StudentID,
            MentorID,
            BookingDate,
            BookingTime,
            Status
        )
        VALUES
        (
            ?, ?, CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME), 'Pending'
        )
    """, (student_id, mentor_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Session booked successfully."
    })
@app.route("/admin/mentor_bookings")
@login_required
def mentor_bookings():
    print("Username:", current_user.username)
    print("Role:", current_user.role)


    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()

    sessions = pd.read_sql("""
        SELECT
            ms.SessionID,
            ms.StudentID,
            m.MentorName,
            ms.BookingDate,
            ms.BookingTime,
            ms.Status
        FROM MentorSessions ms
        JOIN Mentors m
            ON ms.MentorID = m.MentorID
        ORDER BY ms.BookingDate DESC
    """, conn)

    conn.close()

    return render_template(
        "mentor_bookings.html",
        sessions=sessions.to_dict("records")
    )
@app.route("/approve_session/<int:session_id>")
@login_required
def approve_session(session_id):

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE MentorSessions
        SET Status='Approved'
        WHERE SessionID=?
    """, (session_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/mentor_bookings")
@app.route("/reject_session/<int:session_id>")
@login_required
def reject_session(session_id):

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE MentorSessions
        SET Status='Rejected'
        WHERE SessionID=?
    """, (session_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/mentor_bookings")
@app.route("/complete_session/<int:session_id>")
@login_required
def complete_session(session_id):

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE MentorSessions
        SET Status='Completed'
        WHERE SessionID=?
    """, (session_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/mentor_bookings")


# =========================================================
# Reports
# =========================================================
@app.route("/reports")
@login_required
def student_reports():

    if current_user.role != "Student":
        return redirect("/admin_reports")

    student = get_logged_in_student()

    return render_template(
        "reports.html",
        student=student
    )
@app.route("/admin_reports")
@login_required
def admin_reports():

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()

    students = pd.read_sql("SELECT * FROM students", conn)

    conn.close()

    return render_template(
        "admin_reports.html",
        students=students.to_dict("records")
    )

# =========================================================
# Save Preferences
# =========================================================
@app.route("/set_preferences", methods=["POST"])
def set_preferences():
    data = request.get_json(silent=True) or {}
    category = data.get("category", "Academic")

    session["category"] = category
    session.modified = True

    return jsonify({
        "status": "success",
        "category": category
    })
@app.route("/analytics")
@login_required
def analytics():

    if current_user.role != "Admin":
        return "Access Denied", 403

    conn = get_connection()

    students = pd.read_sql("SELECT * FROM students", conn)

    # Summary cards
    students_count = len(students)
    avg_gpa = round(students["GPA"].mean(), 2)
    avg_attendance = round(students["Attendance"].mean(), 1)

    high_risk = len(
        students[
            (students["Attendance"] < 75) |
            (students["GPA"] < 6)
        ]
    )

    low_risk = students_count - high_risk

    # Program Distribution
    program = students["Program"].value_counts()

    program_labels = program.index.tolist()
    program_values = program.values.tolist()

    # Semester-wise Attendance
    attendance = (
        students.groupby("Semester")["Attendance"]
        .mean()
        .round(1)
    )

    attendance_labels = attendance.index.astype(str).tolist()
    attendance_values = attendance.values.tolist()

    # Semester-wise GPA
    gpa = (
        students.groupby("Semester")["GPA"]
        .mean()
        .round(2)
    )

    gpa_labels = gpa.index.astype(str).tolist()
    gpa_values = gpa.values.tolist()

    # High-risk student list
    high_risk_students = students[
        (students["Attendance"] < 75) |
        (students["GPA"] < 6)
    ][["StudentID", "Program", "Semester", "Attendance", "GPA"]]

    conn.close()

    return render_template(
        "analytics.html",
        students_count=students_count,
        avg_gpa=avg_gpa,
        avg_attendance=avg_attendance,
        high_risk=high_risk,
        low_risk=low_risk,
        program_labels=program_labels,
        program_values=program_values,
        attendance_labels=attendance_labels,
        attendance_values=attendance_values,
        gpa_labels=gpa_labels,
        gpa_values=gpa_values,
        high_risk_students=high_risk_students.to_dict("records")
    )
@app.route("/export_excel")
@login_required
def export_excel():

    conn = get_connection()

    students = pd.read_sql("SELECT * FROM students", conn)

    conn.close()

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        students.to_excel(writer, index=False, sheet_name="Students")

    output.seek(0)

    return send_file(
        output,
        download_name="Student_Report.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.route("/export_pdf")
@login_required
def export_pdf():

    conn = get_connection()

    students = pd.read_sql(
        "SELECT StudentID,Program,Semester,GPA,Attendance FROM students",
        conn
    )

    conn.close()

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(buffer)

    data = [students.columns.tolist()]

    data += students.values.tolist()

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("FONTSIZE",(0,0),(-1,-1),8)

    ]))

    pdf.build([table])

    buffer.seek(0)

    return send_file(
        buffer,
        download_name="Student_Report.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )
@app.route("/admin/profile")
@login_required
def admin_profile():

    conn = get_connection()

    admin = pd.read_sql("""
        SELECT
            Username,
            Email,
            Role
        FROM Users
        WHERE Username = ?
    """, conn, params=[current_user.username])

    conn.close()

    return render_template(
        "admin_profile.html",
        admin=admin.iloc[0]
    )
@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():

    email = request.form["email"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Users
        SET Email=?
        WHERE Username=?
    """,
    (email, current_user.username))

    conn.commit()
    conn.close()

    flash("Profile updated successfully.", "success")

    return redirect("/admin/profile")
# =========================================================
# AI Chat API
# =========================================================
@app.route("/ask", methods=["POST"])
def ask():
    if "student_id" not in session:
        return jsonify({"response": "Please login first."})

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Please enter a message."})

    category = session.get("category", "Academic")

    if client is None:
        return jsonify({
            "response": "⚠️ OPENAI_API_KEY not found in .env file."
        })

    chat_history = get_chat_history()

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an expert AI mentor specializing in {category}. "
                    "Provide concise, practical, student-friendly guidance."
                )
            }
        ]

        # Add recent conversation history
        messages.extend(chat_history[-10:])

        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()

        # Save conversation
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": reply})

        # Keep only recent messages
        session["chat_history"] = chat_history[-20:]
        session.modified = True

        return jsonify({"response": reply})

    except Exception as e:
        print("OpenAI Error:", e)
        return jsonify({
            "response": "⚠️ AI service is temporarily unavailable."
        })


# =========================================================
# Voice Assistant Endpoint
# =========================================================
@app.route("/voice", methods=["POST"])
def voice():
    return jsonify({
        "status": "Voice processing is handled in the browser."
    })


# =========================================================
# Health Check
# =========================================================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "students_loaded": len(students_df),
        "openai_configured": client is not None
    })




# =========================================================
# Serve Report Images from backend/outputs
# =========================================================
@app.route("/outputs/<path:filename>")
def serve_output_file(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "outputs"),
        filename
    )
print("\n===== REGISTERED ROUTES =====")
for rule in app.url_map.iter_rules():
    print(rule)
print("=============================\n")


# =========================================================
# Run Application
# =========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("AI Mentoring System Starting...")
    print(f"Students loaded: {len(students_df)}")
    print("Data Source: SQL Server")
    print(f"OpenAI configured: {'Yes' if client else 'No'}")
    print("Server URL: http://127.0.0.1:5000")
    print("=" * 60)


app.run(host="127.0.0.1", port=5000, debug=False)