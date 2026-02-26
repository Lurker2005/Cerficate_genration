# # # from flask import Flask, request, jsonify, send_file, render_template_string
# # # from PIL import Image, ImageDraw, ImageFont
# # # import qrcode
# # # import hashlib
# # # import uuid
# # # import json
# # # from datetime import datetime
# # # import os
# # # import textwrap
# # # import cv2
# # # from pyzbar.pyzbar import decode
# # # import mysql.connector

# # # app = Flask(__name__)

# # # # -----------------------------------
# # # # CONSTANTS
# # # # -----------------------------------
# # # DB_PATH = "database.json" 
# # # BG_PATH = "certificate_bg.jpg"
# # # FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# # # BASE_URL = "http://cerficate.bharatwipe.online"

# # # os.makedirs("certificates", exist_ok=True)
# # # os.makedirs("uploads", exist_ok=True)

# # # # -----------------------------------
# # # # JSON DB FUNCTIONS
# # # # -----------------------------------
# # # if not os.path.exists(DB_PATH):
# # #     with open(DB_PATH, "w") as f:
# # #         json.dump({}, f)

# # # def load_db():
# # #     with open(DB_PATH, "r") as f:
# # #         return json.load(f)

# # # def save_db(data):
# # #     with open(DB_PATH, "w") as f:
# # #         json.dump(data, f, indent=4)

# # # # -----------------------------------
# # # # MYSQL CONNECTION
# # # # -----------------------------------
# # # def get_db():
# # #     return mysql.connector.connect(
# # #         host="localhost",
# # #         user="bw_user",
# # #         password="StrongPassword123",
# # #         database="certificates"
# # #     )

# # # # -----------------------------------
# # # # STORE VERIFICATION LOG IN MYSQL
# # # # -----------------------------------
# # # def log_verification(username, certificate_id):
# # #     conn = get_db()
# # #     cur = conn.cursor()

# # #     cur.execute("""
# # #         INSERT INTO verified_logs (username, certificate_id)
# # #         VALUES (%s, %s)
# # #     """, (username, certificate_id))

# # #     conn.commit()
# # #     cur.close()
# # #     conn.close()

# # # # -----------------------------------
# # # # GET TOTAL VERIFICATION COUNT
# # # # -----------------------------------
# # # def get_verification_count(username):
# # #     conn = get_db()
# # #     cur = conn.cursor()

# # #     cur.execute("""
# # #         SELECT COUNT(*) FROM verified_logs WHERE username = %s
# # #     """, (username,))

# # #     count = cur.fetchone()[0]

# # #     cur.close()
# # #     conn.close()

# # #     return count

# # # # -----------------------------------
# # # # GET CERTIFICATE FROM JSON DB
# # # # -----------------------------------
# # # def get_certificate_from_db(cert_id):
# # #     db = load_db()
# # #     return db.get(cert_id)

# # # # -----------------------------------
# # # # CERTIFICATE GENERATOR
# # # # -----------------------------------
# # # def generate_certificate(device_name, username):
# # #     timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# # #     cert_id = str(uuid.uuid4())

# # #     raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
# # #     hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

# # #     qr_data = f"{BASE_URL}/verify/{cert_id}"
# # #     qr = qrcode.make(qr_data).resize((230, 230))

# # #     bg = Image.open(BG_PATH).convert("RGBA")
# # #     draw = ImageDraw.Draw(bg)

# # #     try:
# # #         title_font = ImageFont.truetype(FONT_PATH, 52)
# # #         label_font = ImageFont.truetype(FONT_PATH, 28)
# # #         value_font = ImageFont.truetype(FONT_PATH, 28)
# # #     except:
# # #         title_font = label_font = value_font = ImageFont.load_default()

# # #     draw.text((400, 350), "CERTIFICATE", fill="black", font=title_font)
# # #     draw.text((160, 460), "Device Name:", fill="black", font=label_font)
# # #     draw.text((390, 460), device_name, fill="black", font=value_font)
# # #     draw.text((160, 510), "Username:", fill="black", font=label_font)
# # #     draw.text((390, 510), username, fill="black", font=value_font)
# # #     draw.text((160, 560), "Timestamp:", fill="black", font=label_font)
# # #     draw.text((390, 560), timestamp, fill="black", font=value_font)
# # #     draw.text((160, 610), "Hash:", fill="black", font=label_font)
# # #     draw.text((390, 610), textwrap.fill(hash_id, width=42), fill="black", font=value_font)
# # #     draw.text((160, 760), "Status:", fill="black", font=label_font)
# # #     draw.text((390, 760), "Verified", fill="green", font=value_font)

# # #     bg.paste(qr, (bg.width - 300, bg.height - 300))

# # #     output_path = f"certificates/{cert_id}.png"
# # #     bg.save(output_path)

# # #     db = load_db()
# # #     db[cert_id] = {
# # #         "device_name": device_name,
# # #         "username": username,
# # #         "timestamp": timestamp,
# # #         "hash": hash_id
# # #     }
# # #     save_db(db)

# # #     return cert_id, output_path

# # # # -----------------------------------
# # # # GENERATE API
# # # # -----------------------------------
# # # @app.route("/generate", methods=["POST"])
# # # def generate_api():
# # #     data = request.json
# # #     cert_id, path = generate_certificate(data["device"], data["username"])
# # #     return jsonify({"certificate_id": cert_id, "certificate_image": path})

# # # # -----------------------------------
# # # # VERIFY PNG IMAGE WITH QR CODE (MAIN API)
# # # # -----------------------------------
# # # @app.route("/verify/image", methods=["POST"])
# # # def verify_image():
# # #     file = request.files.get("file")
# # #     verifier_username = request.form.get("verifier_username")

# # #     if not file or not verifier_username:
# # #         return jsonify({"valid": False, "reason": "Missing data"}), 400

# # #     filename = f"{uuid.uuid4().hex}.jpg"
# # #     path = os.path.join("uploads", filename)
# # #     file.save(path)

# # #     img = cv2.imread(path)
# # #     if img is None:
# # #         os.remove(path)
# # #         return jsonify({"valid": False, "reason": "Invalid image file"}), 400

# # #     decoded = decode(img)
# # #     if not decoded:
# # #         os.remove(path)
# # #         return jsonify({"valid": False, "reason": "QR not detected"}), 400

# # #     qr_data = decoded[0].data.decode("utf-8")
# # #     cert_id = qr_data.split("/")[-1]

# # #     certificate = get_certificate_from_db(cert_id)
# # #     if not certificate:
# # #         os.remove(path)
# # #         return jsonify({"valid": False, "reason": "Certificate not found"}), 404

# # #     raw = f"{certificate['device_name']}|{certificate['username']}|{certificate['timestamp']}|{cert_id}"
# # #     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

# # #     if verify_hash != certificate["hash"]:
# # #         os.remove(path)
# # #         return jsonify({"valid": False, "reason": "Certificate tampered"}), 400

# # #     os.remove(path)

# # #     # Store verification log
# # #     log_verification(verifier_username, cert_id)

# # #     return jsonify({
# # #         "valid": True,
# # #         "certificate_id": cert_id,
# # #         "certificate_owner": certificate["username"],
# # #         "verified_by": verifier_username,
# # #         "timestamp": certificate["timestamp"],
# # #         "verified_count": get_verification_count(verifier_username),
# # #         "message": "✅ Certificate Verified Successfully"
# # #     })

# # # # -----------------------------------
# # # # DOWNLOAD CERTIFICATE IMAGE
# # # # -----------------------------------
# # # @app.route("/certificate/<cert_id>")
# # # def get_certificate_file(cert_id):
# # #     return send_file(f"certificates/{cert_id}.png")

# # # # -----------------------------------
# # # # GET VERIFICATION COUNT
# # # # -----------------------------------
# # # @app.route("/verify/count/<username>")
# # # def count_api(username):
# # #     return jsonify({
# # #         "username": username,
# # #         "verified_count": get_verification_count(username)
# # #     })

# # # # -----------------------------------
# # # # RUN SERVER
# # # # -----------------------------------
# # # if __name__ == "__main__":
# # #     app.run(host="0.0.0.0", port=5001, debug=False)
# # from flask import Flask, request, jsonify, send_file
# # from PIL import Image, ImageDraw, ImageFont
# # import qrcode
# # import hashlib
# # import uuid
# # from datetime import datetime
# # import os
# # import textwrap
# # import cv2
# # from pyzbar.pyzbar import decode
# # import psycopg2
# # import base64
# # import io

# # app = Flask(__name__)

# # # -----------------------------
# # # CONFIG
# # # -----------------------------
# # BG_PATH = "certificate_bg.jpg"
# # FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# # BASE_URL = "https://your-render-url.onrender.com"

# # # -----------------------------
# # # DATABASE CONNECTION (RENDER STYLE)
# # # -----------------------------
# # def get_db():
# #     return psycopg2.connect(
# #         os.getenv("DATABASE_URL"),
# #         sslmode="require"
# #     )

# # # -----------------------------
# # # AUTO CREATE TABLES
# # # -----------------------------
# # def init_db():
# #     conn = get_db()
# #     cur = conn.cursor()

# #     cur.execute("""
# #         CREATE TABLE IF NOT EXISTS certificates (
# #             certificate_id VARCHAR(255) PRIMARY KEY,
# #             device_name TEXT,
# #             username TEXT,
# #             timestamp TEXT,
# #             hash TEXT,
# #             image_data TEXT
# #         );
# #     """)

# #     cur.execute("""
# #         CREATE TABLE IF NOT EXISTS verified_logs (
# #             id SERIAL PRIMARY KEY,
# #             username TEXT,
# #             certificate_id TEXT,
# #             verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #         );
# #     """)

# #     conn.commit()
# #     cur.close()
# #     conn.close()

# # # Call table creation at startup
# # init_db()

# # # -----------------------------
# # # STORE VERIFICATION LOG
# # # -----------------------------
# # def log_verification(username, certificate_id):
# #     conn = get_db()
# #     cur = conn.cursor()

# #     cur.execute("""
# #         INSERT INTO verified_logs (username, certificate_id)
# #         VALUES (%s, %s)
# #     """, (username, certificate_id))

# #     conn.commit()
# #     cur.close()
# #     conn.close()

# # # -----------------------------
# # # GET VERIFICATION COUNT
# # # -----------------------------
# # def get_verification_count(username):
# #     conn = get_db()
# #     cur = conn.cursor()

# #     cur.execute("""
# #         SELECT COUNT(*) FROM verified_logs WHERE username = %s
# #     """, (username,))

# #     count = cur.fetchone()[0]

# #     cur.close()
# #     conn.close()

# #     return count

# # # -----------------------------
# # # GET CERTIFICATE FROM DB
# # # -----------------------------
# # def get_certificate_from_db(cert_id):
# #     conn = get_db()
# #     cur = conn.cursor()

# #     cur.execute("""
# #         SELECT device_name, username, timestamp, hash, image_data
# #         FROM certificates
# #         WHERE certificate_id = %s
# #     """, (cert_id,))

# #     row = cur.fetchone()

# #     cur.close()
# #     conn.close()

# #     if not row:
# #         return None

# #     return {
# #         "device_name": row[0],
# #         "username": row[1],
# #         "timestamp": row[2],
# #         "hash": row[3],
# #         "image_data": row[4]
# #     }

# # # -----------------------------
# # # GENERATE CERTIFICATE
# # # -----------------------------
# # def generate_certificate(device_name, username):
# #     timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# #     cert_id = str(uuid.uuid4())

# #     raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
# #     hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

# #     qr_data = f"{BASE_URL}/certificate/{cert_id}"
# #     qr = qrcode.make(qr_data).resize((230, 230))

# #     bg = Image.open(BG_PATH).convert("RGBA")
# #     draw = ImageDraw.Draw(bg)

# #     try:
# #         title_font = ImageFont.truetype(FONT_PATH, 52)
# #         label_font = ImageFont.truetype(FONT_PATH, 28)
# #         value_font = ImageFont.truetype(FONT_PATH, 28)
# #     except:
# #         title_font = label_font = value_font = ImageFont.load_default()

# #     draw.text((400, 350), "CERTIFICATE", fill="black", font=title_font)
# #     draw.text((160, 460), "Device Name:", fill="black", font=label_font)
# #     draw.text((390, 460), device_name, fill="black", font=value_font)
# #     draw.text((160, 510), "Username:", fill="black", font=label_font)
# #     draw.text((390, 510), username, fill="black", font=value_font)
# #     draw.text((160, 560), "Timestamp:", fill="black", font=label_font)
# #     draw.text((390, 560), timestamp, fill="black", font=value_font)
# #     draw.text((160, 610), "Hash:", fill="black", font=label_font)
# #     draw.text((390, 610), textwrap.fill(hash_id, width=42), fill="black", font=value_font)
# #     draw.text((160, 760), "Status:", fill="black", font=label_font)
# #     draw.text((390, 760), "Verified", fill="green", font=value_font)

# #     bg.paste(qr, (bg.width - 300, bg.height - 300))

# #     buffer = io.BytesIO()
# #     bg.save(buffer, format="PNG")
# #     img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

# #     conn = get_db()
# #     cur = conn.cursor()

# #     cur.execute("""
# #         INSERT INTO certificates
# #         (certificate_id, device_name, username, timestamp, hash, image_data)
# #         VALUES (%s, %s, %s, %s, %s, %s)
# #     """, (cert_id, device_name, username, timestamp, hash_id, img_data))

# #     conn.commit()
# #     cur.close()
# #     conn.close()

# #     return cert_id

# # # -----------------------------
# # # GENERATE API
# # # -----------------------------
# # @app.route("/generate", methods=["POST"])
# # def generate_api():
# #     data = request.json
# #     cert_id = generate_certificate(data["device"], data["username"])
# #     return jsonify({"certificate_id": cert_id})

# # # -----------------------------
# # # VERIFY IMAGE
# # # -----------------------------
# # @app.route("/verify/image", methods=["POST"])
# # def verify_image():
# #     file = request.files.get("file")
# #     verifier_username = request.form.get("verifier_username")

# #     if not file or not verifier_username:
# #         return jsonify({"valid": False, "reason": "Missing data"}), 400

# #     temp_path = "temp.jpg"
# #     file.save(temp_path)

# #     img = cv2.imread(temp_path)
# #     decoded = decode(img)
# #     os.remove(temp_path)

# #     if not decoded:
# #         return jsonify({"valid": False, "reason": "QR not detected"}), 400

# #     qr_data = decoded[0].data.decode("utf-8")
# #     cert_id = qr_data.split("/")[-1]

# #     certificate = get_certificate_from_db(cert_id)
# #     if not certificate:
# #         return jsonify({"valid": False, "reason": "Certificate not found"}), 404

# #     raw = f"{certificate['device_name']}|{certificate['username']}|{certificate['timestamp']}|{cert_id}"
# #     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

# #     if verify_hash != certificate["hash"]:
# #         return jsonify({"valid": False, "reason": "Certificate tampered"}), 400

# #     log_verification(verifier_username, cert_id)

# #     return jsonify({
# #         "valid": True,
# #         "certificate_id": cert_id,
# #         "certificate_owner": certificate["username"],
# #         "verified_by": verifier_username,
# #         "timestamp": certificate["timestamp"],
# #         "verified_count": get_verification_count(verifier_username),
# #         "message": "✅ Certificate Verified Successfully"
# #     })

# # # -----------------------------
# # # DOWNLOAD CERTIFICATE
# # # -----------------------------
# # @app.route("/certificate/<cert_id>")
# # def download_certificate(cert_id):
# #     certificate = get_certificate_from_db(cert_id)
# #     if not certificate:
# #         return jsonify({"error": "Not found"}), 404

# #     img_bytes = base64.b64decode(certificate["image_data"])
# #     return send_file(io.BytesIO(img_bytes), mimetype="image/png")

# # # -----------------------------
# # # RUN
# # # -----------------------------
# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5000)

# from flask import Flask, request, jsonify, send_file
# from PIL import Image, ImageDraw, ImageFont
# import qrcode
# import hashlib
# import uuid
# from datetime import datetime
# import os
# import textwrap
# import cv2
# import psycopg2
# import base64
# import io

# app = Flask(__name__)

# # -----------------------------
# # CONFIG
# # -----------------------------
# BG_PATH = "certificate_bg.jpg"
# FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# BASE_URL = "https://certificate-generation-1.onrender.com"  # CHANGE to your real URL

# # -----------------------------
# # DATABASE CONNECTION
# # -----------------------------
# def get_db():
#     return psycopg2.connect(
#         os.getenv("DATABASE_URL"),
#         sslmode="require"
#     )

# # -----------------------------
# # AUTO CREATE TABLES
# # -----------------------------
# def init_db():
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS certificates (
#             certificate_id VARCHAR(255) PRIMARY KEY,
#             device_name TEXT,
#             username TEXT,
#             timestamp TEXT,
#             hash TEXT,
#             image_data TEXT
#         );
#     """)

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS verified_logs (
#             id SERIAL PRIMARY KEY,
#             username TEXT,
#             certificate_id TEXT,
#             verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#     """)

#     conn.commit()
#     cur.close()
#     conn.close()

# init_db()

# # -----------------------------
# # STORE VERIFICATION LOG
# # -----------------------------
# def log_verification(username, certificate_id):
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute("""
#         INSERT INTO verified_logs (username, certificate_id)
#         VALUES (%s, %s)
#     """, (username, certificate_id))

#     conn.commit()
#     cur.close()
#     conn.close()

# # -----------------------------
# # GET VERIFICATION COUNT
# # -----------------------------
# def get_verification_count(username):
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT COUNT(*) FROM verified_logs WHERE username = %s
#     """, (username,))

#     count = cur.fetchone()[0]

#     cur.close()
#     conn.close()

#     return count

# # -----------------------------
# # GET CERTIFICATE FROM DB
# # -----------------------------
# def get_certificate_from_db(cert_id):
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT device_name, username, timestamp, hash, image_data
#         FROM certificates
#         WHERE certificate_id = %s
#     """, (cert_id,))

#     row = cur.fetchone()

#     cur.close()
#     conn.close()

#     if not row:
#         return None

#     return {
#         "device_name": row[0],
#         "username": row[1],
#         "timestamp": row[2],
#         "hash": row[3],
#         "image_data": row[4]
#     }

# # -----------------------------
# # GENERATE CERTIFICATE
# # -----------------------------
# def generate_certificate(device_name, username):
#     timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#     cert_id = str(uuid.uuid4())

#     raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
#     hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

#     qr_data = f"{BASE_URL}/certificate/{cert_id}"
#     qr = qrcode.make(qr_data).resize((230, 230))

#     bg = Image.open(BG_PATH).convert("RGBA")
#     draw = ImageDraw.Draw(bg)

#     try:
#         title_font = ImageFont.truetype(FONT_PATH, 52)
#         label_font = ImageFont.truetype(FONT_PATH, 28)
#         value_font = ImageFont.truetype(FONT_PATH, 28)
#     except:
#         title_font = label_font = value_font = ImageFont.load_default()

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

#     bg.paste(qr, (bg.width - 300, bg.height - 300))

#     buffer = io.BytesIO()
#     bg.save(buffer, format="PNG")
#     img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute("""
#         INSERT INTO certificates
#         (certificate_id, device_name, username, timestamp, hash, image_data)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     """, (cert_id, device_name, username, timestamp, hash_id, img_data))

#     conn.commit()
#     cur.close()
#     conn.close()

#     return cert_id

# # -----------------------------
# # GENERATE API
# # -----------------------------
# @app.route("/generate", methods=["POST"])
# def generate_api():
#     data = request.json
#     cert_id = generate_certificate(data["device"], data["username"])
#     return jsonify({"certificate_id": cert_id})

# # -----------------------------
# # VERIFY IMAGE (USING OPENCV)
# # -----------------------------
# @app.route("/verify/image", methods=["POST"])
# def verify_image():
#     file = request.files.get("file")
#     verifier_username = request.form.get("verifier_username")

#     if not file or not verifier_username:
#         return jsonify({"valid": False, "reason": "Missing data"}), 400

#     temp_path = "temp.jpg"
#     file.save(temp_path)

#     img = cv2.imread(temp_path)
#     detector = cv2.QRCodeDetector()
#     qr_data, bbox, _ = detector.detectAndDecode(img)

#     os.remove(temp_path)

#     if not qr_data:
#         return jsonify({"valid": False, "reason": "QR not detected"}), 400

#     cert_id = qr_data.split("/")[-1]

#     certificate = get_certificate_from_db(cert_id)
#     if not certificate:
#         return jsonify({"valid": False, "reason": "Certificate not found"}), 404

#     raw = f"{certificate['device_name']}|{certificate['username']}|{certificate['timestamp']}|{cert_id}"
#     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

#     if verify_hash != certificate["hash"]:
#         return jsonify({"valid": False, "reason": "Certificate tampered"}), 400

#     log_verification(verifier_username, cert_id)

#     return jsonify({
#         "valid": True,
#         "certificate_id": cert_id,
#         "certificate_owner": certificate["username"],
#         "verified_by": verifier_username,
#         "timestamp": certificate["timestamp"],
#         "verified_count": get_verification_count(verifier_username),
#         "message": "✅ Certificate Verified Successfully"
#     })

# # -----------------------------
# # DOWNLOAD CERTIFICATE
# # -----------------------------
# @app.route("/certificate/<cert_id>")
# def download_certificate(cert_id):
#     certificate = get_certificate_from_db(cert_id)
#     if not certificate:
#         return jsonify({"error": "Not found"}), 404

#     img_bytes = base64.b64decode(certificate["image_data"])
#     return send_file(io.BytesIO(img_bytes), mimetype="image/png")

# # -----------------------------
# # RUN
# # -----------------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import hashlib
import uuid
from datetime import datetime
import os
import textwrap
import cv2
import mysql.connector
import base64
import io

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
BG_PATH = "certificate_bg.jpg"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BASE_URL = "https://certificate.bharatwipe.online"


# -----------------------------
# MYSQL CONNECTION
# -----------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="codewipe",
        password="Robotics26!",
        database="codewipe"
    )


# -----------------------------
# AUTO CREATE TABLES
# -----------------------------
def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS certificates (

        certificate_id VARCHAR(255) PRIMARY KEY,
        device_name TEXT,
        username TEXT,
        timestamp TEXT,
        hash TEXT,
        image_data LONGTEXT

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS verified_logs (

        id INT AUTO_INCREMENT PRIMARY KEY,
        username TEXT,
        certificate_id TEXT,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()


# -----------------------------
# STORE VERIFICATION LOG
# -----------------------------
def log_verification(username, certificate_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO verified_logs
    (username, certificate_id)

    VALUES (%s,%s)

    """, (username, certificate_id))

    conn.commit()
    cur.close()
    conn.close()


# -----------------------------
# GET VERIFICATION COUNT
# -----------------------------
def get_verification_count(username):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*)
    FROM verified_logs
    WHERE username=%s
    """, (username,))

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count


# -----------------------------
# GET CERTIFICATE FROM DB
# -----------------------------
def get_certificate_from_db(cert_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT device_name,username,timestamp,hash,image_data
    FROM certificates
    WHERE certificate_id=%s
    """, (cert_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return {

        "device_name":row[0],
        "username":row[1],
        "timestamp":row[2],
        "hash":row[3],
        "image_data":row[4]

    }


# -----------------------------
# GENERATE CERTIFICATE
# -----------------------------
def generate_certificate(device_name,username):

    timestamp=datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cert_id=str(uuid.uuid4())


    raw_data=f"{device_name}|{username}|{timestamp}|{cert_id}"

    hash_id=hashlib.sha256(raw_data.encode()).hexdigest()


    qr_data=f"{BASE_URL}/certificate/{cert_id}"

    qr=qrcode.make(qr_data).resize((230,230))


    bg=Image.open(BG_PATH).convert("RGBA")

    draw=ImageDraw.Draw(bg)


    try:

        title_font=ImageFont.truetype(FONT_PATH,52)
        label_font=ImageFont.truetype(FONT_PATH,28)
        value_font=ImageFont.truetype(FONT_PATH,28)

    except:

        title_font=label_font=value_font=ImageFont.load_default()


    draw.text((400,350),"CERTIFICATE",fill="black",font=title_font)

    draw.text((160,460),"Device Name:",fill="black",font=label_font)

    draw.text((390,460),device_name,fill="black",font=value_font)


    draw.text((160,510),"Username:",fill="black",font=label_font)

    draw.text((390,510),username,fill="black",font=value_font)


    draw.text((160,560),"Timestamp:",fill="black",font=label_font)

    draw.text((390,560),timestamp,fill="black",font=value_font)


    draw.text((160,610),"Hash:",fill="black",font=label_font)

    draw.text((390,610),
              textwrap.fill(hash_id,width=42),
              fill="black",
              font=value_font)


    draw.text((160,760),"Status:",fill="black",font=label_font)

    draw.text((390,760),"Verified",fill="green",font=value_font)


    bg.paste(qr,(bg.width-300,bg.height-300))


    buffer=io.BytesIO()

    bg.save(buffer,format="PNG")


    img_data=base64.b64encode(buffer.getvalue()).decode("utf-8")


    conn=get_db()

    cur=conn.cursor()


    cur.execute("""
    INSERT INTO certificates
    (certificate_id,device_name,username,timestamp,hash,image_data)

    VALUES (%s,%s,%s,%s,%s,%s)

    """,(cert_id,device_name,username,timestamp,hash_id,img_data))


    conn.commit()

    cur.close()

    conn.close()


    return cert_id



# -----------------------------
# GENERATE API
# -----------------------------
@app.route("/generate",methods=["POST"])
def generate_api():

    data=request.json

    cert_id=generate_certificate(

        data["device"],
        data["username"]

    )

    return jsonify({

        "certificate_id":cert_id

    })


# -----------------------------
# VERIFY IMAGE
# -----------------------------
@app.route("/verify/image",methods=["POST"])
def verify_image():

    file=request.files.get("file")

    verifier_username=request.form.get("verifier_username")


    if not file or not verifier_username:

        return jsonify({

            "valid":False,
            "reason":"Missing data"

        }),400


    temp_path="temp.jpg"

    file.save(temp_path)


    img=cv2.imread(temp_path)

    detector=cv2.QRCodeDetector()

    qr_data,bbox,_=detector.detectAndDecode(img)


    os.remove(temp_path)


    if not qr_data:

        return jsonify({

            "valid":False,
            "reason":"QR not detected"

        }),400


    cert_id=qr_data.split("/")[-1]


    certificate=get_certificate_from_db(cert_id)


    if not certificate:

        return jsonify({

            "valid":False,
            "reason":"Certificate not found"

        }),404


    raw=f"{certificate['device_name']}|{certificate['username']}|{certificate['timestamp']}|{cert_id}"


    verify_hash=hashlib.sha256(raw.encode()).hexdigest()


    if verify_hash!=certificate["hash"]:

        return jsonify({

            "valid":False,
            "reason":"Certificate tampered"

        }),400


    log_verification(verifier_username,cert_id)


    return jsonify({

        "valid":True,
        "certificate_id":cert_id,
        "certificate_owner":certificate["username"],
        "verified_by":verifier_username,
        "timestamp":certificate["timestamp"],
        "verified_count":get_verification_count(verifier_username),
        "message":"Certificate Verified Successfully"

    })


# -----------------------------
# DOWNLOAD CERTIFICATE
# -----------------------------
@app.route("/certificate/<cert_id>")
def download_certificate(cert_id):

    certificate=get_certificate_from_db(cert_id)


    if not certificate:

        return jsonify({

            "error":"Not found"

        }),404


    img_bytes=base64.b64decode(

        certificate["image_data"]

    )


    return send_file(

        io.BytesIO(img_bytes),

        mimetype="image/png"

    )


# -----------------------------
# RUN
# -----------------------------
if __name__=="__main__":

    app.run(host="0.0.0.0",port=5001)