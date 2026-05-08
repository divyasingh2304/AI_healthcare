import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import jsonify
from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import mysql.connector
import razorpay

razorpay_client = razorpay.Client(auth=("rzp_test_SXiqm0ONCrlnZY", "aUQqzbnjlBXQtsuw5U84bXCg"))

app = Flask(__name__)
app.secret_key = "secretkey"

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'amansingh64862@gmail.com'
app.config['MAIL_PASSWORD'] = 'wisn qviz pmvr fapj'

mail = Mail(app)

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="healthcare",
    autocommit=True
)

def send_email(receiver_email, patient, doctor, date, appointment_id):

    sender_email = "amansingh64862@gmail.com"
    sender_password = "gdvw tjvd nkch ahfp"

    subject = "Appointment Confirmation - Healthcare+"

    body = f"""
Hello {patient},

Your appointment has been successfully booked.

Appointment ID : {appointment_id}

Doctor : {doctor}
Date : {date}

Hospital Address :
Healthcare+ Medical Center
MG Road, Pune, Maharashtra

Please arrive 10 minutes before your appointment.

Thank you for using Healthcare+.
Stay Healthy!
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email Error:", e)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Email already registered"

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        db.commit()
        
        cursor.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    role = request.args.get("role")

    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        cursor = db.cursor(dictionary=True)

        if role == "user":
            cursor.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, password)
            )

            user = cursor.fetchone()

            if user:
                session["user"] = user["name"]   # fixed here
                return redirect("/dashboard")
            else:
                return "Invalid Login"

        elif role == "admin":
            cursor.execute(
                "SELECT * FROM admins WHERE email=%s AND password=%s",
                (email, password)
            )

            admin = cursor.fetchone()

            if admin:
                session["admin"] = admin["name"]
                return redirect("/admin_dashboard")
            else:
                return "Invalid Login"

    return render_template("login.html", role=role)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login?role=user")

    return render_template("dashboard.html", user=session["user"])

@app.route("/book", methods=["GET", "POST"])
def book():

    if "user" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    today = datetime.today().strftime("%Y-%m-%d")

    if request.method == "POST":

        doctor_id = request.form.get("doctor")
        date = request.form.get("date")
        time = request.form.get("time")
        patient_name = request.form.get("patient_name")

        # ❗ Slot validation
        if not time:
            return render_template(
                "book.html",
                doctors=doctors,
                today=today,
                error="Please select a time slot"
            )

        # Get doctor details
        cursor.execute("SELECT * FROM doctors WHERE id=%s", (doctor_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return redirect("/book")

        # ✅ Date validation
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        today_date = datetime.today().date()

        if selected_date < today_date:
            return "Past date appointment not allowed"

        # ✅ Time validation
        selected_time = datetime.strptime(time, "%H:%M").time()

        doctor_from = (datetime.min + doctor["available_from"]).time()
        doctor_to = (datetime.min + doctor["available_to"]).time()

        if selected_time < doctor_from or selected_time > doctor_to:
            return "Doctor not available at this time"

        # ✅ Slot already booked check
        cursor.execute("""
            SELECT * FROM appointments
            WHERE doctor_name=%s
            AND appointment_date=%s
            AND appointment_time=%s
        """, (doctor["name"], date, time))

        existing = cursor.fetchone()

        if existing:
            return render_template(
                "book.html",
                doctors=doctors,
                today=today,
                error="This slot is already booked"
            )

        # ✅ STORE IN SESSION (IMPORTANT)
        session["booking"] = {
            "patient": patient_name,
            "doctor": doctor["name"],
            "specialization": doctor["specialization"],
            "fees": doctor["fees"],
            "date": date,
            "time": time
        }

        # ✅ CREATE RAZORPAY ORDER
        amount = int(doctor["fees"]) * 100  # convert to paisa

        order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        cursor.close()

        # ✅ SEND TO PAYMENT PAGE
        return render_template(
    "payment.html",
    booking=session["booking"],   # 🔥 ADD THIS
    order=order,
            key="rzp_test_SXiqm0ONCrlnZY"  # 🔥 put your real test key here
        )

    cursor.close()

    return render_template(
        "book.html",
        doctors=doctors,
        today=today
    )
@app.route("/payment")
def payment():

    if "booking" not in session:
        return redirect("/book")

    booking = session["booking"]

    amount = int(booking["fees"]) * 100

    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template("payment.html", order=order, key="rzp_test_SXiqm0ONCrlnZY")
@app.route("/payment-success")
def payment_success():

    if "booking" not in session:
        return redirect("/book")

    booking = session["booking"]

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO appointments 
        (patient_name, doctor_name, specialization, doctor_fees,
         appointment_date, appointment_time, status, meet_link, login_user)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        booking["patient"],
        booking["doctor"],
        booking["specialization"],
        booking["fees"],
        booking["date"],
        booking["time"],
        "Confirmed",
        "https://meet.google.com/xyz-abc",
        session["user"]
    ))

    db.commit()
    cursor.close()

    session.pop("booking", None)

    return redirect("/history")
    
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT * FROM appointments WHERE login_user=%s",
        (session["user"],)
    )
    data = cursor.fetchall()
    cursor.close()

    return render_template("history.html", data=data)
from flask import jsonify

@app.route("/get-slots")
def get_slots():
    try:
        doctor_id = request.args.get("doctor")
        date = request.args.get("date")

        print("API HIT:", doctor_id, date)

        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT name FROM doctors WHERE id=%s", (doctor_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return jsonify([])

        cursor.execute("""
            SELECT appointment_time FROM appointments
            WHERE doctor_name=%s AND appointment_date=%s
        """, (doctor["name"], date))

        data = cursor.fetchall()

        booked_slots = []

        for row in data:
            time_val = row["appointment_time"]

            # 🔥 SAFE HANDLING (NO CRASH)
            if isinstance(time_val, str):
                booked_slots.append(time_val[:5])
            elif time_val is not None:
                booked_slots.append(str(time_val)[:5])

        cursor.close()

        return jsonify(booked_slots)

    except Exception as e:
        print("ERROR IN /get-slots:", e)
        return jsonify([])


@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    cursor = db.cursor(dictionary=True)

    # Appointment list
    cursor.execute("""
        SELECT 
            appointments.id,
            appointments.patient_name,
            appointments.status,
            doctors.name AS doctor_name,
            doctors.specialization
        FROM appointments
        JOIN doctors 
        ON appointments.doctor_name = doctors.name
    """)

    data = cursor.fetchall()

    # Pending notifications
    cursor.execute("SELECT COUNT(*) AS total FROM appointments WHERE status='Pending'")
    pending = cursor.fetchone()["total"]

    # Today's appointments
    cursor.execute("SELECT COUNT(*) AS total FROM appointments WHERE appointment_date=CURDATE()")
    today_count = cursor.fetchone()["total"]

    # Contact messages count
    cursor.execute("SELECT COUNT(*) AS total FROM contact_messages")
    message_count = cursor.fetchone()["total"]

    cursor.close()

    return render_template(
        "admin_dashboard.html",
        data=data,
        pending=pending,
        today_count=today_count,
        message_count=message_count
    )
    
@app.route("/approve/<int:id>")
def approve(id):
    cursor = db.cursor()
    cursor.execute("UPDATE appointments SET status='Approved' WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect("/admin_dashboard")


@app.route("/reject/<int:id>")
def reject(id):
    cursor = db.cursor()
    cursor.execute("UPDATE appointments SET status='Rejected' WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect("/admin_dashboard")

@app.route("/cancel/<int:id>")
def cancel(id):

    cursor = db.cursor()

    cursor.execute(
        "UPDATE appointments SET status='Cancelled' WHERE id=%s",
        (id,)
    )

    db.commit()
    cursor.close()

    return redirect("/history")

@app.route("/ai", methods=["GET", "POST"])
def ai():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        fever = int(request.form["fever"])
        cough = int(request.form["cough"])
        headache = int(request.form["headache"])

        if fever == 1 and cough == 1:
            result = "You may have Flu"
        elif fever == 1 and headache == 1:
            result = "You may have Dengue"
        else:
            result = "Common Cold"

        return render_template("ai.html", prediction=result)

    return render_template("ai.html")

from flask import request, jsonify

@app.route("/chatbot", methods=["POST"])
def chatbot():

    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"reply": "Please type a message."})

        message = data["message"].lower()

        if "flu" in message:
            reply = "Take rest, drink warm fluids, and take paracetamol if needed."

        elif "dengue" in message:
            reply = "Drink plenty of fluids, avoid painkillers like ibuprofen, and consult a doctor."

        elif "cold" in message:
            reply = "Stay warm, drink hot liquids, and rest."

        elif "fever" in message:
            reply = "Monitor your temperature, stay hydrated, and take proper rest."

        elif "cough" in message:
            reply = "Drink warm water, take steam inhalation, and avoid cold food."

        elif "headache" in message:
            reply = "Take rest, stay hydrated, and reduce screen time."

        else:
            reply = "Please tell me your symptoms like fever, cough, headache."

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": "Something went wrong. Please try again."})

@app.route("/manage_doctors")
def manage_doctors():
    if "admin" not in session:
        return redirect("/admin_login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()

    return render_template("manage_doctors.html", doctors=doctors)

@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":
        name = request.form["name"]
        specialization = request.form["specialization"]
        fees = request.form["fees"]
        available_from = request.form["available_from"]
        available_to = request.form["available_to"]

        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO doctors (name, specialization, fees, available_from, available_to)
            VALUES (%s,%s,%s,%s,%s)
        """, (name, specialization, fees, available_from, available_to))
        db.commit()
        cursor.close()

        return redirect("/manage_doctors")

    return render_template("add_doctor.html")

@app.route("/edit_doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        specialization = request.form["specialization"]
        fees = request.form["fees"]
        available_from = request.form["available_from"]
        available_to = request.form["available_to"]

        cursor.execute("""
            UPDATE doctors
            SET name=%s, specialization=%s, fees=%s,
                available_from=%s, available_to=%s
            WHERE id=%s
        """, (name, specialization, fees, available_from, available_to, id))

        db.commit()
        cursor.close()
        return redirect("/manage_doctors")

    cursor.execute("SELECT * FROM doctors WHERE id=%s", (id,))
    doctor = cursor.fetchone()
    cursor.close()

    return render_template("edit_doctor.html", doctor=doctor)

@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cursor = db.cursor()
    cursor.execute("DELETE FROM doctors WHERE id=%s", (id,))
    db.commit()
    cursor.close()

    return redirect("/manage_doctors")

@app.route("/analytics")
def analytics():
    if "admin" not in session:
        return redirect("/admin_login")

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    cursor.close()

    return render_template("analytics.html",
                           total=total,
                           approved=approved,
                           pending=pending,
                           rejected=rejected)

@app.route("/emergency")
def emergency():

    if "user" not in session:
        return redirect("/login")

    services = [
        {"name": "Ambulance Service", "number": "102"},
        {"name": "Emergency Helpline", "number": "108"},
        {"name": "Women Helpline", "number": "1091"},
        {"name": "Police Emergency", "number": "100"}
    ]

    hospitals = [
        "City Hospital",
        "Apollo Hospital",
        "Government Medical Hospital",
        "Lifeline Trauma Center"
    ]

    return render_template("emergency.html",
                           services=services,
                           hospitals=hospitals)
    
@app.route("/review/<int:doctor_id>", methods=["GET", "POST"])
def review(doctor_id):
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        rating = request.form["rating"]
        review = request.form["review"]

        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO reviews (doctor_id, user_name, rating, review)
            VALUES (%s,%s,%s,%s)
        """, (doctor_id, session["user"], rating, review))
        db.commit()
        cursor.close()

        return redirect("/dashboard")

    return render_template("review.html", doctor_id=doctor_id)

@app.route("/chat/<doctor_name>", methods=["GET", "POST"])
def chat(doctor_name):
    if "user" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        message = request.form["message"]

        cursor.execute("""
            INSERT INTO chat_messages (sender, receiver, message)
            VALUES (%s, %s, %s)
        """, (session["user"], doctor_name, message))

        db.commit()

    cursor.execute("""
        SELECT * FROM chat_messages
        WHERE (sender=%s AND receiver=%s)
        OR (sender=%s AND receiver=%s)
        ORDER BY timestamp
    """, (session["user"], doctor_name, doctor_name, session["user"]))

    messages = cursor.fetchall()
    cursor.close()

    return render_template("chat.html",
                           doctor=doctor_name,
                           messages=messages)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)   
    return redirect("/login?role=admin")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Save to database
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (%s,%s,%s)",
            (name, email, message)
        )
        db.commit()

        # Send email to admin
        msg = Message(
            "New Contact Message",
            sender="yourgmail@gmail.com",
            recipients=["adminemail@gmail.com"]
        )

        msg.body = f"""
        New message from user:

        Name: {name}
        Email: {email}
        Message: {message}
        """

        mail.send(msg)

    return render_template("contact.html")

@app.route("/admin/messages")
def admin_messages():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_messages ORDER BY id DESC")
    messages = cursor.fetchall()

    return render_template("admin_messages.html", messages=messages)

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            send_email(email, "User", "Password Reset", "Use temporary password", 0)
            return "Reset email sent"

    return render_template("forgot_password.html")

@app.route("/reply/<int:id>", methods=["POST"])
def reply_message(id):
    reply = request.form["reply"]

    cursor = db.cursor()
    cursor.execute(
        "UPDATE contact_messages SET reply=%s WHERE id=%s",
        (reply, id)
    )
    db.commit()
    cursor.close()

    return redirect("/admin/messages")

@app.route("/top_doctors")
def top_doctors():

    cursor = db.cursor()

    cursor.execute("""
        SELECT doctor_id, AVG(rating)
        FROM reviews
        GROUP BY doctor_id
        ORDER BY AVG(rating) DESC
    """)

    data = cursor.fetchall()

    return render_template("top_doctors.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)