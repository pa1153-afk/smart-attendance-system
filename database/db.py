import psycopg2
from datetime import datetime, timezone

# ===============================
# DATABASE CONFIG
# ===============================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "attendance_db",
    "user": "postgres",
    "password": "1234"
}

DUPLICATE_WINDOW_SECONDS = 30


# ===============================
# CONNECTION
# ===============================
def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print("[DB ERROR] Connection failed:", e)
        return None


# ===============================
# 👤 ADD STUDENT
# ===============================
def add_student(student_id, student_name):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO students (student_id, student_name)
            VALUES (%s, %s)
            ON CONFLICT (student_id) DO NOTHING
        """, (student_id, student_name))

        conn.commit()
        cur.close()
        conn.close()

        print(f"[STUDENT ADDED] {student_id} - {student_name}")
        return True

    except Exception as e:
        print("[DB ERROR] add_student:", e)
        if conn:
            conn.close()
        return False


# ===============================
# 📊 GET ALL STUDENTS
# ===============================
def get_all_students():
    conn = get_connection()
    if conn is None:
        return []

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT student_id, student_name, created_at
            FROM students
            ORDER BY created_at DESC
        """)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records

    except Exception as e:
        print("[DB ERROR] get_all_students:", e)
        if conn:
            conn.close()
        return []


# ===============================
# 🟢 MARK ATTENDANCE
# ===============================
def mark_attendance(student_id):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cur = conn.cursor()

        # Get last record
        cur.execute("""
            SELECT timestamp
            FROM attendance
            WHERE student_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (student_id,))

        result = cur.fetchone()

        now = datetime.now(timezone.utc)

        if result:
            last_time = result[0]

            # ensure timezone-safe
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)

            diff = (now - last_time).total_seconds()

            if diff < DUPLICATE_WINDOW_SECONDS:
                print(f"[SKIP] {student_id} already marked ({int(diff)}s ago)")
                cur.close()
                conn.close()
                return False

        # Insert new attendance
        cur.execute("""
            INSERT INTO attendance (student_id, timestamp)
            VALUES (%s, %s)
        """, (student_id, now))

        conn.commit()

        cur.close()
        conn.close()

        print(f"[MARKED] {student_id} at {now.strftime('%H:%M:%S')}")
        return True

    except Exception as e:
        print("[DB ERROR] mark_attendance:", e)
        if conn:
            conn.close()
        return False


# ===============================
# 📊 GET ALL ATTENDANCE
# ===============================
def get_all_attendance():
    conn = get_connection()
    if conn is None:
        return []

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, student_id, timestamp
            FROM attendance
            ORDER BY timestamp DESC
        """)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return records

    except Exception as e:
        print("[DB ERROR] fetch attendance:", e)
        if conn:
            conn.close()
        return []


# ===============================
# 📊 DASHBOARD STATS
# ===============================
def get_dashboard_stats():
    conn = get_connection()
    if conn is None:
        return {
            "total_students": 0,
            "today_attendance": 0
        }

    try:
        cur = conn.cursor()

        # total students
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0] or 0

        # today attendance
        cur.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE DATE(timestamp AT TIME ZONE 'UTC') = CURRENT_DATE
        """)
        today_attendance = cur.fetchone()[0] or 0

        cur.close()
        conn.close()

        return {
            "total_students": total_students,
            "today_attendance": today_attendance
        }

    except Exception as e:
        print("[DB ERROR] stats:", e)
        if conn:
            conn.close()
        return {
            "total_students": 0,
            "today_attendance": 0
        }


# ===============================
# TEST
# ===============================
if __name__ == "__main__":
    print("=== DB TEST ===")

    add_student("S001", "Test User")
    mark_attendance("S001")

    print("Students:", get_all_students())
    print("Attendance:", get_all_attendance())
    print("Stats:", get_dashboard_stats())