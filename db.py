import mysql.connector
import os
def get_conn():
    return mysql.connector.connect(
        host=os.environ.get('MYSQLHOST', 'localhost'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', 'root123'),
        database=os.environ.get('MYSQL_DATABASE', 'clinic_db')
        
    )
# ─── Auth ─────────────────────────────────────────────────────────────────────

def get_user(username, password):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()
    conn.close()
    return user

# ─── Dashboard stats ──────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    stats = {}
    cur.execute("SELECT COUNT(*) AS cnt FROM patient")
    stats['patients'] = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM doctor")
    stats['doctors'] = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM appointment")
    stats['appointments'] = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM medicine")
    stats['medicines'] = cur.fetchone()['cnt']
    cur.execute("SELECT SUM(quantity_available) AS total FROM stock")
    row = cur.fetchone()
    stats['stock'] = row['total'] if row['total'] else 0
    cur.execute("""
        SELECT a.appointment_id, p.name AS patient, d.doctor_name AS doctor,
               a.date, a.time
        FROM appointment a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN doctor d ON a.doctor_id = d.doctor_id
        ORDER BY a.date DESC, a.time DESC LIMIT 5
    """)
    stats['recent_appointments'] = cur.fetchall()
    conn.close()
    return stats

# ─── Doctors ──────────────────────────────────────────────────────────────────

def get_all_doctors():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM doctor ORDER BY doctor_id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_doctor(name, specialization, available_time):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO doctor (doctor_name, specialization, available_time) VALUES (%s,%s,%s)",
                (name, specialization, available_time))
    conn.commit()
    conn.close()

def delete_doctor(doctor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM doctor WHERE doctor_id=%s", (doctor_id,))
    conn.commit()
    conn.close()

# ─── Patients ─────────────────────────────────────────────────────────────────

def get_all_patients():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patient ORDER BY patient_id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_patient(name, age, gender, contact_no):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO patient (name, age, gender, contact_no) VALUES (%s,%s,%s,%s)",
                (name, age, gender, contact_no))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM patient WHERE patient_id=%s", (patient_id,))
    conn.commit()
    conn.close()

# ─── Appointments ─────────────────────────────────────────────────────────────

def get_all_appointments():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.appointment_id, p.name AS patient_name, d.doctor_name,
               d.specialization, a.date, a.time
        FROM appointment a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN doctor d ON a.doctor_id = d.doctor_id
        ORDER BY a.date DESC, a.time DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def book_appointment(patient_id, doctor_id, date, time):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO appointment (patient_id, doctor_id, date, time) VALUES (%s,%s,%s,%s)",
                (patient_id, doctor_id, date, time))
    conn.commit()
    conn.close()

def delete_appointment(appt_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointment WHERE appointment_id=%s", (appt_id,))
    conn.commit()
    conn.close()

# ─── Medicine & Stock ─────────────────────────────────────────────────────────

def get_all_medicines_with_stock():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT m.medicine_id, m.medicine_name, m.price, m.expiry_date,
               COALESCE(s.quantity_available, 0) AS quantity_available
        FROM medicine m
        LEFT JOIN stock s ON m.medicine_id = s.medicine_id
        ORDER BY m.medicine_id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def add_medicine_with_stock(name, price, expiry_date, quantity):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO medicine (medicine_name, price, expiry_date) VALUES (%s,%s,%s)",
                (name, price, expiry_date))
    med_id = cur.lastrowid
    cur.execute("INSERT INTO stock (medicine_id, quantity_available) VALUES (%s,%s)",
                (med_id, quantity))
    conn.commit()
    conn.close()

def delete_medicine(med_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM stock WHERE medicine_id=%s", (med_id,))
    cur.execute("DELETE FROM medicine WHERE medicine_id=%s", (med_id,))
    conn.commit()
    conn.close()
