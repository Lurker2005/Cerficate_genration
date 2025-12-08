
# from flask import Flask, request, jsonify, send_file, render_template_string
# from PIL import Image, ImageDraw, ImageFont
# import qrcode
# import hashlib
# import uuid
# import json
# from datetime import datetime
# import os
# import textwrap
# import cv2
# from pyzbar.pyzbar import decode

# app = Flask(__name__)

# DB_PATH = "database.json"
# BG_PATH = "certificate_bg.jpg"
# FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# BASE_URL = "http://cerficate.bharatwipe.online"

# os.makedirs("certificates", exist_ok=True)
# os.makedirs("uploads", exist_ok=True)

# if not os.path.exists(DB_PATH):
#     with open(DB_PATH, "w") as f:
#         json.dump({}, f)

# def save_db(data):
#     with open(DB_PATH, "w") as f:
#         json.dump(data, f, indent=4)

# def load_db():
#     with open(DB_PATH, "r") as f:
#         return json.load(f)

# # =========================
# # ✅ CERTIFICATE GENERATOR
# # =========================
# def generate_certificate(device_name, username):
#     timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#     cert_id = str(uuid.uuid4())

#     raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
#     hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

#     qr_data = f"{BASE_URL}/verify/{cert_id}"
#     qr = qrcode.make(qr_data).resize((230, 230))

#     bg = Image.open(BG_PATH).convert("RGBA")
#     draw = ImageDraw.Draw(bg)

#     try:
#         title_font = ImageFont.truetype(FONT_PATH, 52)
#         label_font = ImageFont.truetype(FONT_PATH, 28)
#         value_font = ImageFont.truetype(FONT_PATH, 28)
#     except:
#         title_font = ImageFont.load_default()
#         label_font = ImageFont.load_default()
#         value_font = ImageFont.load_default()

#     draw.text((400, 350), "CERTIFICATE", fill="black", font=title_font)

#     draw.text((160, 460), "Device Name:", fill="black", font=label_font)
#     draw.text((390, 460), device_name, fill="black", font=value_font)

#     draw.text((160, 510), "Username:", fill="black", font=label_font)
#     draw.text((390, 510), username, fill="black", font=value_font)

#     draw.text((160, 560), "Timestamp:", fill="black", font=label_font)
#     draw.text((390, 560), timestamp, fill="black", font=value_font)

#     draw.text((160, 610), "Hash:", fill="black", font=label_font)
#     draw.text((390, 610), textwrap.fill(hash_id, width=42), fill="black", font=value_font)

#     draw.text((160, 760), "Status:", fill="black", font=label_font)
#     draw.text((390, 760), "Verified", fill="green", font=value_font)

#     qr_x = bg.width - 300
#     qr_y = bg.height - 300
#     bg.paste(qr, (qr_x, qr_y))

#     output_path = f"certificates/{cert_id}.png"
#     bg.save(output_path)

#     db = load_db()
#     db[cert_id] = {
#         "device_name": device_name,
#         "username": username,
#         "timestamp": timestamp,
#         "hash": hash_id
#     }
#     save_db(db)

#     return cert_id, output_path

# # =========================
# # ✅ GENERATE API
# # =========================
# @app.route("/generate", methods=["POST"])
# def generate_api():
#     data = request.json
#     cert_id, path = generate_certificate(data["device"], data["username"])
#     return jsonify({"certificate_id": cert_id, "certificate_image": path})

# # =========================
# # ✅ QR VERIFY (WEB)
# # =========================
# @app.route("/verify/<cert_id>")
# def verify(cert_id):
#     db = load_db()
#     if cert_id not in db:
#         return "<h1 style='color:red;'>❌ Certificate Not Found</h1>"

#     data = db[cert_id]
#     raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
#     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

#     if verify_hash != data["hash"]:
#         return "<h1 style='color:red;'>❌ Certificate Tampered</h1>"

#     return render_template_string(
#         f"<h1 style='color:green;'>✅ CERTIFICATE VERIFIED</h1><img src='/certificate/{cert_id}' width='70%'>"
#     )

# # =========================
# # ✅ ✅ ✅ PNG + QR UPLOAD VERIFY API ✅ ✅ ✅
# # =========================
# @app.route("/verify/image", methods=["POST"])
# def verify_image():
#     file = request.files.get("file")

#     if not file:
#         return jsonify({"valid": False, "reason": "No image uploaded"}), 400

#     path = os.path.join("uploads", file.filename)
#     file.save(path)

#     img = cv2.imread(path)
#     decoded = decode(img)

#     if not decoded:
#         os.remove(path)
#         return jsonify({"valid": False, "reason": "QR not detected"}), 400

#     qr_data = decoded[0].data.decode("utf-8")
#     cert_id = qr_data.split("/")[-1]

#     db = load_db()
#     if cert_id not in db:
#         os.remove(path)
#         return jsonify({"valid": False, "reason": "Certificate not found"}), 404

#     data = db[cert_id]
#     raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
#     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

#     if verify_hash != data["hash"]:
#         os.remove(path)
#         return jsonify({"valid": False, "reason": "Certificate tampered"}), 400

#     os.remove(path)

#     return jsonify({
#         "valid": True,
#         "certificate_id": cert_id,
#         "device_name": data["device_name"],
#         "username": data["username"],
#         "timestamp": data["timestamp"],
#         "message": "✅ Certificate Verified Successfully"
#     })

# # =========================
# # ✅ IMAGE DOWNLOAD
# # =========================
# @app.route("/certificate/<cert_id>")
# def get_certificate_file(cert_id):
#     return send_file(f"certificates/{cert_id}.png")

# # =========================
# # ✅ RUN
# # =========================
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=False)

from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import qrcode
import hashlib
import uuid
import json
from datetime import datetime
import os
import textwrap
import cv2
from pyzbar.pyzbar import decode
import mysql.connector

app = Flask(__name__)

# -----------------------------------
# CONSTANTS
# -----------------------------------
DB_PATH = "database.json"                     # JSON DB storing certificate metadata
BG_PATH = "certificate_bg.jpg"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BASE_URL = "http://cerficate.bharatwipe.online"

os.makedirs("certificates", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# -----------------------------------
# CHECK JSON DB EXISTS
# -----------------------------------
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------------
# MYSQL CONNECTION
# -----------------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="bw_user",
        password="StrongPassword123",
        database="bharatwipe"
    )

# -----------------------------------
# LOG VERIFICATION IN MYSQL
# -----------------------------------
def log_verification(username, certificate_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO verification_logs (username, certificate_id)
        VALUES (%s, %s)
    """, (username, certificate_id))

    conn.commit()
    cur.close()
    conn.close()

# -----------------------------------
# GET USER VERIFICATION COUNT
# -----------------------------------
def get_verification_count(username):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM verification_logs WHERE username = %s", (username,))
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count

# -----------------------------------
# CERTIFICATE GENERATOR
# -----------------------------------
def generate_certificate(device_name, username):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cert_id = str(uuid.uuid4())

    raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
    hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

    # QR CODE
    qr_data = f"{BASE_URL}/verify/{cert_id}"
    qr = qrcode.make(qr_data).resize((230, 230))

    # LOAD BACKGROUND
    bg = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # FONTS
    try:
        title_font = ImageFont.truetype(FONT_PATH, 52)
        label_font = ImageFont.truetype(FONT_PATH, 28)
        value_font = ImageFont.truetype(FONT_PATH, 28)
    except:
        title_font = label_font = value_font = ImageFont.load_default()

    # WRITE TEXT
    draw.text((400, 350), "CERTIFICATE", fill="black", font=title_font)

    draw.text((160, 460), "Device Name:", fill="black", font=label_font)
    draw.text((390, 460), device_name, fill="black", font=value_font)

    draw.text((160, 510), "Username:", fill="black", font=label_font)
    draw.text((390, 510), username, fill="black", font=value_font)

    draw.text((160, 560), "Timestamp:", fill="black", font=label_font)
    draw.text((390, 560), timestamp, fill="black", font=value_font)

    draw.text((160, 610), "Hash:", fill="black", font=label_font)
    draw.text((390, 610), textwrap.fill(hash_id, width=42), fill="black", font=value_font)

    draw.text((160, 760), "Status:", fill="black", font=label_font)
    draw.text((390, 760), "Verified", fill="green", font=value_font)

    # PASTE QR
    qr_x = bg.width - 300
    qr_y = bg.height - 300
    bg.paste(qr, (qr_x, qr_y))

    output_path = f"certificates/{cert_id}.png"
    bg.save(output_path)

    # SAVE TO JSON DB
    db = load_db()
    db[cert_id] = {
        "device_name": device_name,
        "username": username,
        "timestamp": timestamp,
        "hash": hash_id
    }
    save_db(db)

    return cert_id, output_path

# -----------------------------------
# API: GENERATE CERTIFICATE
# -----------------------------------
@app.route("/generate", methods=["POST"])
def generate_api():
    data = request.json
    cert_id, path = generate_certificate(data["device"], data["username"])
    return jsonify({"certificate_id": cert_id, "certificate_image": path})

# -----------------------------------
# WEB VERIFY (for QR page)
# -----------------------------------
@app.route("/verify/<cert_id>")
def verify(cert_id):
    db = load_db()

    if cert_id not in db:
        return "<h1 style='color:red;'>❌ Certificate Not Found</h1>"

    data = db[cert_id]

    raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
    verify_hash = hashlib.sha256(raw.encode()).hexdigest()

    # CHECK HASH
    if verify_hash != data["hash"]:
        return "<h1 style='color:red;'>❌ Certificate Tampered</h1>"

    # 🔥 INCREMENT USER COUNTER HERE ALSO
    log_verification(data["username"], cert_id)

    # SHOW USER COUNT IN WEB PAGE
    count = get_verification_count(data["username"])

    return render_template_string(f"""
        <h1 style='color:green;'>✅ CERTIFICATE VERIFIED</h1>
        <p>User: {data['username']}</p>
        <p>Total verifications: {count}</p>
        <img src='/certificate/{cert_id}' width='70%'>
    """)

# -----------------------------------
# PNG VERIFICATION API (Flutter)
# -----------------------------------
@app.route("/verify/image", methods=["POST"])
def verify_image():
    file = request.files.get("file")
    if not file:
        return jsonify({"valid": False, "reason": "No image uploaded"}), 400

    path = os.path.join("uploads", file.filename)
    file.save(path)

    img = cv2.imread(path)
    decoded = decode(img)

    if not decoded:
        os.remove(path)
        return jsonify({"valid": False, "reason": "QR not detected"}), 400

    qr_data = decoded[0].data.decode("utf-8")
    cert_id = qr_data.split("/")[-1]

    db = load_db()

    if cert_id not in db:
        os.remove(path)
        return jsonify({"valid": False, "reason": "Certificate not found"}), 404

    data = db[cert_id]

    raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
    verify_hash = hashlib.sha256(raw.encode()).hexdigest()

    if verify_hash != data["hash"]:
        os.remove(path)
        return jsonify({"valid": False, "reason": "Certificate tampered"}), 400

    os.remove(path)

    # 🔥 INCREMENT USER VERIFICATION COUNT
    log_verification(data["username"], cert_id)

    return jsonify({
        "valid": True,
        "certificate_id": cert_id,
        "device_name": data["device_name"],
        "username": data["username"],
        "timestamp": data["timestamp"],
        "verified_count": get_verification_count(data["username"]),
        "message": "✅ Certificate Verified Successfully"
    })

# -----------------------------------
# DOWNLOAD CERTIFICATE IMAGE
# -----------------------------------
@app.route("/certificate/<cert_id>")
def get_certificate_file(cert_id):
    return send_file(f"certificates/{cert_id}.png")

# -----------------------------------
# API: GET USER VERIFICATION COUNT
# -----------------------------------
@app.route("/verify/count/<username>")
def count_api(username):
    return jsonify({
        "username": username,
        "verified_count": get_verification_count(username)
    })

# -----------------------------------
# RUN SERVER
# -----------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
