from flask import Flask, render_template, request, redirect, url_for, session, flash
import db

app = Flask(__name__)
app.secret_key = 'clinic_secret_key_2024'

# ─── Auth ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get_user(username, password)
        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Try admin / admin123')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

# ─── Doctors ─────────────────────────────────────────────────────────────────

@app.route('/doctors')
@login_required
def doctors():
    all_doctors = db.get_all_doctors()
    return render_template('doctors.html', doctors=all_doctors)

@app.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        name = request.form['doctor_name']
        spec = request.form['specialization']
        avail = request.form['available_time']
        db.add_doctor(name, spec, avail)
        flash('Doctor added successfully!')
        return redirect(url_for('doctors'))
    return render_template('add_doctor.html')

@app.route('/delete_doctor/<int:doctor_id>')
@login_required
def delete_doctor(doctor_id):
    db.delete_doctor(doctor_id)
    flash('Doctor removed.')
    return redirect(url_for('doctors'))

# ─── Patients ────────────────────────────────────────────────────────────────

@app.route('/patients')
@login_required
def patients():
    all_patients = db.get_all_patients()
    return render_template('patients.html', patients=all_patients)

@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact_no']
        db.add_patient(name, age, gender, contact)
        flash('Patient registered successfully!')
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

@app.route('/delete_patient/<int:patient_id>')
@login_required
def delete_patient(patient_id):
    db.delete_patient(patient_id)
    flash('Patient removed.')
    return redirect(url_for('patients'))

# ─── Appointments ────────────────────────────────────────────────────────────

@app.route('/appointments')
@login_required
def appointments():
    all_appts = db.get_all_appointments()
    return render_template('book_appointment.html', appointments=all_appts,
                           patients=db.get_all_patients(), doctors=db.get_all_doctors())

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    date = request.form['date']
    time = request.form['time']
    db.book_appointment(patient_id, doctor_id, date, time)
    flash('Appointment booked successfully!')
    return redirect(url_for('appointments'))

@app.route('/delete_appointment/<int:appt_id>')
@login_required
def delete_appointment(appt_id):
    db.delete_appointment(appt_id)
    flash('Appointment cancelled.')
    return redirect(url_for('appointments'))

# ─── Medicine & Stock ────────────────────────────────────────────────────────

@app.route('/medicines')
@login_required
def medicines():
    all_meds = db.get_all_medicines_with_stock()
    return render_template('medicines.html', medicines=all_meds)

@app.route('/add_medicine', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        name = request.form['medicine_name']
        price = request.form['price']
        expiry = request.form['expiry_date']
        qty = request.form['quantity']
        db.add_medicine_with_stock(name, price, expiry, qty)
        flash('Medicine & stock added!')
        return redirect(url_for('medicines'))
    return render_template('add_medicine.html')

@app.route('/delete_medicine/<int:med_id>')
@login_required
def delete_medicine(med_id):
    db.delete_medicine(med_id)
    flash('Medicine removed.')
    return redirect(url_for('medicines'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

