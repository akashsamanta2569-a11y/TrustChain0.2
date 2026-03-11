# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import qrcode
import os
import time
from database import init_db

app = Flask(__name__)
app.secret_key = "xibit_2026_secret_key"

# This creates the NEW blockchain database format
init_db()

# ------------------------------
# NEW BLOCKCHAIN LOGIC
# ------------------------------
def get_previous_hash():
    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT certificate_hash FROM certificates ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "GENESIS_BLOCK"

def generate_block_hash(student, course, issuer, previous_hash, current_time):
    data = student + course + issuer + previous_hash + current_time
    return hashlib.sha256(data.encode()).hexdigest()

def generate_qr(cert_hash, host_url):
    # HARDCODED IP FOR THE XIBIT WI-FI
    verify_url = f"http://10.10.10.251:5000/verify?hash={cert_hash}"
    qr = qrcode.make(verify_url)
    filename = f"{cert_hash}.png"
    path = os.path.join("static", "qr", filename)
    os.makedirs(os.path.join("static", "qr"), exist_ok=True)
    qr.save(path)
    return filename

# ------------------------------
# ROUTES
# ------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    if password == "admin123":
        session["logged_in"] = True
        return redirect(url_for("issue"))
    else:
        return redirect(url_for("home"))

@app.route("/issue", methods=["GET", "POST"])
def issue():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    if request.method == "POST":
        student = request.form["student"]
        course = request.form["course"]
        issuer = request.form["issuer"]
        
        # BLOCKCHAIN CREATION
        current_time = str(time.time())
        previous_hash = get_previous_hash()
        cert_hash = generate_block_hash(student, course, issuer, previous_hash, current_time)
        qr_filename = generate_qr(cert_hash, request.host_url)

        conn = sqlite3.connect("certificates.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO certificates(student_name, course_name, issuer, certificate_hash, previous_hash, timestamp)
        VALUES(?,?,?,?,?,?)
        """, (student, course, issuer, cert_hash, previous_hash, time.ctime()))
        conn.commit()
        conn.close()

        # Update the result array to match the new database columns
        return render_template("verify.html", result=[0, student, course, issuer, cert_hash], newly_issued=True, qr_filename=qr_filename)

    return render_template("issue.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", certificates=data)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    result = None
    hash_value = request.args.get("hash") or (request.form.get("hash") if request.method == "POST" else None)

    if hash_value:
        conn = sqlite3.connect("certificates.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM certificates WHERE certificate_hash=?", (hash_value,))
        result = cursor.fetchone()
        conn.close()

    return render_template("verify.html", result=result, hash_value=hash_value)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)