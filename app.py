from database.db import get_all_attendance, add_student, get_dashboard_stats
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    Response
)

import subprocess
import sys

app = Flask(__name__)
app.secret_key = "smart_attendance_secret_key"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ===============================
# HELPER
# ===============================
def is_logged_in():
    return session.get("logged_in", False)


# ===============================
# AUTH ROUTES
# ===============================
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===============================
# MAIN ROUTES
# ===============================
@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    stats = get_dashboard_stats()  # 🔥 NEW

    return render_template("dashboard.html", stats=stats)


@app.route("/register")
def register():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("register_student.html")


@app.route("/attendance")
def attendance():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("start_attendance.html")


# ===============================
# REGISTER STUDENT
# ===============================
@app.route("/register_student", methods=["POST"])
def register_student():
    if not is_logged_in():
        return jsonify({"success": False}), 401

    data = request.get_json()
    student_id = data.get("student_id")
    student_name = data.get("student_name")

    print(f"[REGISTER] {student_id} - {student_name}")

    try:
        # SAVE TO DB
        add_student(student_id, student_name)

        # RUN FACE CAPTURE
        subprocess.Popen([
            sys.executable,
            "face_recognition_module/register_face.py"
        ])

        return jsonify({
            "success": True,
            "message": f"{student_name} registration started"
        })

    except Exception as e:
        print("[ERROR REGISTER]", e)
        return jsonify({
            "success": False,
            "message": str(e)
        })


# ===============================
# STATUS
# ===============================
@app.route("/registration_status/<student_id>")
def registration_status(student_id):
    return jsonify({"status": "done"})


# ===============================
# START ATTENDANCE
# ===============================
@app.route("/start_attendance", methods=["POST"])
def start_attendance_api():
    if not is_logged_in():
        return jsonify({"success": False}), 401

    try:
        subprocess.Popen([
            sys.executable,
            "-m",
            "face_recognition_module.recognize_face"
        ])

        return jsonify({
            "success": True,
            "message": "Attendance started"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/stop_attendance", methods=["POST"])
def stop_attendance_api():
    return jsonify({
        "success": True,
        "message": "Press 'q' in camera window to stop"
    })


# ===============================
# VIEW ATTENDANCE
# ===============================
@app.route("/view_attendance")
def view_attendance():
    if not is_logged_in():
        return redirect(url_for("login"))

    raw_records = get_all_attendance()

    records = []
    for r in raw_records:
        records.append({
            "id": r[0],
            "student_id": r[1],
            "timestamp": r[2]
        })

    return render_template("view_attendance.html", records=records)


# ===============================
# EXPORT CSV
# ===============================
@app.route("/export")
def export():
    if not is_logged_in():
        return redirect(url_for("login"))

    raw_records = get_all_attendance()

    def generate():
        yield "ID,Student ID,Timestamp\n"
        for r in raw_records:
            yield f"{r[0]},{r[1]},{r[2]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )


# ===============================
# TEST ROUTE
# ===============================
@app.route("/test")
def test():
    return jsonify({
        "status": "ok",
        "message": "Server is running."
    })


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    print("🔥 FINAL SYSTEM WITH STATS READY 🔥")
    app.run(debug=True)