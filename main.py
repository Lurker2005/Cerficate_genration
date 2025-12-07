
# from flask import Flask, request, jsonify, send_file, render_template_string
# from PIL import Image, ImageDraw, ImageFont
# import qrcode
# import hashlib
# import uuid
# import json
# from datetime import datetime
# import os
# import textwrap

# app = Flask(__name__)

# DB_PATH = "database.json"
# BG_PATH = "certificate_bg.jpg"
# FONT_PATH = "arial.ttf"

# # ✅ YOUR CURRENT NGROK URL (UPDATE IF NGROK CHANGES)
# NGROK_URL = "https://postdevelopmental-gertrudis-pindling.ngrok-free.dev"

# os.makedirs("certificates", exist_ok=True)

# # =========================
# # ✅ CREATE EMPTY DB
# # =========================
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

#     # Unique Certificate ID
#     cert_id = str(uuid.uuid4())

#     # Create hash
#     raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
#     hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

#     # ✅ QR WITH NGROK LINK
#     qr_data = f"{NGROK_URL}/verify/{cert_id}"
#     qr = qrcode.make(qr_data).resize((230, 230))

#     # Load certificate background
#     bg = Image.open(BG_PATH).convert("RGBA")
#     draw = ImageDraw.Draw(bg)

#     # Fonts
#     title_font = ImageFont.truetype(FONT_PATH, 52)
#     label_font = ImageFont.truetype(FONT_PATH, 28)
#     value_font = ImageFont.truetype(FONT_PATH, 28)

#     # =========================
#     # ✅ CENTER TITLE
#     # =========================
#     title_text = "CERTIFICATE"
#     w, h = draw.textbbox((0, 0), title_text, font=title_font)[2:]
#     draw.text(((bg.width - w) / 2, 350), title_text, fill="black", font=title_font)

#     # =========================
#     # ✅ LEFT ALIGNED DATA
#     # =========================
#     start_x = 160
#     start_y = 460
#     gap = 50

#     draw.text((start_x, start_y), "Device Name:", fill="black", font=label_font)
#     draw.text((start_x + 230, start_y), device_name, fill="black", font=value_font)

#     draw.text((start_x, start_y + gap), "Username:", fill="black", font=label_font)
#     draw.text((start_x + 230, start_y + gap), username, fill="black", font=value_font)

#     draw.text((start_x, start_y + gap * 2), "Timestamp:", fill="black", font=label_font)
#     draw.text((start_x + 230, start_y + gap * 2), timestamp, fill="black", font=value_font)

#     draw.text((start_x, start_y + gap * 3), "Hash:", fill="black", font=label_font)

#     wrapped_hash = textwrap.fill(hash_id, width=42)
#     draw.text((start_x + 230, start_y + gap * 3),
#               wrapped_hash, fill="black", font=value_font)

#     # =========================
#     # ✅ STATUS + DATE
#     # =========================
#     draw.text((start_x, start_y + gap * 6), "Status:", fill="black", font=label_font)
#     draw.text((start_x + 230, start_y + gap * 6), "Verified",
#               fill="green", font=value_font)

#     draw.text((start_x, start_y + gap * 7), "Date:", fill="black", font=label_font)
#     draw.text((start_x + 230, start_y + gap * 7),
#               datetime.now().strftime("%d %b %Y"),
#               fill="black", font=value_font)

#     # =========================
#     # ✅ PASTE QR (BOTTOM RIGHT)
#     # =========================
#     qr_x = bg.width - 300
#     qr_y = bg.height - 300
#     bg.paste(qr, (qr_x, qr_y))

#     # =========================
#     # ✅ SAVE CERTIFICATE
#     # =========================
#     output_path = f"certificates/{cert_id}.png"
#     bg.save(output_path)

#     # =========================
#     # ✅ SAVE TO DATABASE
#     # =========================
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
# # ✅ API: GENERATE CERTIFICATE
# # =========================
# @app.route("/generate", methods=["POST"])
# def generate_api():
#     data = request.json
#     device = data["device"]
#     user = data["username"]

#     cert_id, path = generate_certificate(device, user)

#     return jsonify({
#         "certificate_id": cert_id,
#         "certificate_image": path
#     })

# # =========================
# # ✅ BEAUTIFUL VERIFY PAGE
# # =========================
# @app.route("/verify/<cert_id>")
# def verify(cert_id):
#     db = load_db()

#     if cert_id not in db:
#         return "<h1 style='color:red;text-align:center;'>❌ Certificate Not Found</h1>"

#     data = db[cert_id]
#     raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
#     verify_hash = hashlib.sha256(raw.encode()).hexdigest()

#     if verify_hash != data["hash"]:
#         return "<h1 style='color:red;text-align:center;'>❌ Certificate Tampered</h1>"

#     cert_img = f"/certificate/{cert_id}"

#     return render_template_string(f"""
#     <html>
#     <head>
#         <title>Certificate Verification</title>
#         <style>
#             body {{ font-family: Arial; background: #f4f6f8; text-align: center; }}
#             .box {{ background: white; padding: 30px; width: 85%; margin: auto; margin-top: 40px; border-radius: 12px; box-shadow: 0 0 10px #aaa; }}
#             h1 {{ color: green; }}
#             img {{ margin-top: 20px; width: 90%; max-width: 800px; border: 2px solid #ccc; border-radius: 10px; }}
#         </style>
#     </head>
#     <body>
#         <div class="box">
#             <h1>✅ CERTIFICATE VERIFIED</h1>
#             <p><b>Device:</b> {data["device_name"]}</p>
#             <p><b>User:</b> {data["username"]}</p>
#             <p><b>Timestamp:</b> {data["timestamp"]}</p>
#             <p><b>Status:</b> AUTHENTIC ✅</p>

#             <img src="{cert_img}">
#         </div>
#     </body>
#     </html>
#     """)

# # =========================
# # ✅ API: DOWNLOAD IMAGE
# # =========================
# @app.route("/certificate/<cert_id>")
# def get_certificate_file(cert_id):
#     return send_file(f"certificates/{cert_id}.png")

# # =========================
# # ✅ RUN APP (PUBLIC ACCESS ENABLED)
# # =========================
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import qrcode
import hashlib
import uuid
import json
from datetime import datetime
import os
import textwrap

app = Flask(__name__)

# =========================
# ✅ PATH CONFIG
# =========================
DB_PATH = "database.json"
BG_PATH = "certificate_bg.jpg"
FONT_PATH = "arial.ttf"

# ✅ LIVE DOMAIN (YOUR SUBDOMAIN)
BASE_URL = "https://cerficate.bharatwipe.online"

# =========================
# ✅ FOLDERS
# =========================
os.makedirs("certificates", exist_ok=True)

# =========================
# ✅ CREATE EMPTY DB IF NOT EXISTS
# =========================
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({}, f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

# =========================
# ✅ CERTIFICATE GENERATOR
# =========================
def generate_certificate(device_name, username):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cert_id = str(uuid.uuid4())

    raw_data = f"{device_name}|{username}|{timestamp}|{cert_id}"
    hash_id = hashlib.sha256(raw_data.encode()).hexdigest()

    # ✅ LIVE QR VERIFICATION LINK
    qr_data = f"{BASE_URL}/verify/{cert_id}"
    qr = qrcode.make(qr_data).resize((230, 230))

    bg = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    title_font = ImageFont.truetype(FONT_PATH, 52)
    label_font = ImageFont.truetype(FONT_PATH, 28)
    value_font = ImageFont.truetype(FONT_PATH, 28)

    # ✅ TITLE
    title_text = "CERTIFICATE"
    w, h = draw.textbbox((0, 0), title_text, font=title_font)[2:]
    draw.text(((bg.width - w) / 2, 350), title_text, fill="black", font=title_font)

    # ✅ LEFT DATA
    start_x = 160
    start_y = 460
    gap = 50

    draw.text((start_x, start_y), "Device Name:", fill="black", font=label_font)
    draw.text((start_x + 230, start_y), device_name, fill="black", font=value_font)

    draw.text((start_x, start_y + gap), "Username:", fill="black", font=label_font)
    draw.text((start_x + 230, start_y + gap), username, fill="black", font=value_font)

    draw.text((start_x, start_y + gap * 2), "Timestamp:", fill="black", font=label_font)
    draw.text((start_x + 230, start_y + gap * 2), timestamp, fill="black", font=value_font)

    draw.text((start_x, start_y + gap * 3), "Hash:", fill="black", font=label_font)
    wrapped_hash = textwrap.fill(hash_id, width=42)
    draw.text((start_x + 230, start_y + gap * 3), wrapped_hash, fill="black", font=value_font)

    # ✅ STATUS & DATE
    draw.text((start_x, start_y + gap * 6), "Status:", fill="black", font=label_font)
    draw.text((start_x + 230, start_y + gap * 6), "Verified", fill="green", font=value_font)

    draw.text((start_x, start_y + gap * 7), "Date:", fill="black", font=label_font)
    draw.text((start_x + 230, start_y + gap * 7),
              datetime.now().strftime("%d %b %Y"),
              fill="black", font=value_font)

    # ✅ PASTE QR
    qr_x = bg.width - 300
    qr_y = bg.height - 300
    bg.paste(qr, (qr_x, qr_y))

    # ✅ SAVE IMAGE
    output_path = f"certificates/{cert_id}.png"
    bg.save(output_path)

    # ✅ SAVE DATABASE
    db = load_db()
    db[cert_id] = {
        "device_name": device_name,
        "username": username,
        "timestamp": timestamp,
        "hash": hash_id
    }
    save_db(db)

    return cert_id, output_path

# =========================
# ✅ API: GENERATE CERTIFICATE
# =========================
@app.route("/generate", methods=["POST"])
def generate_api():
    data = request.json
    device = data["device"]
    user = data["username"]

    cert_id, path = generate_certificate(device, user)

    return jsonify({
        "certificate_id": cert_id,
        "certificate_image": path
    })

# =========================
# ✅ BEAUTIFUL VERIFICATION PAGE
# =========================
@app.route("/verify/<cert_id>")
def verify(cert_id):
    db = load_db()

    if cert_id not in db:
        return "<h1 style='color:red;text-align:center;'>❌ Certificate Not Found</h1>"

    data = db[cert_id]
    raw = f"{data['device_name']}|{data['username']}|{data['timestamp']}|{cert_id}"
    verify_hash = hashlib.sha256(raw.encode()).hexdigest()

    if verify_hash != data["hash"]:
        return "<h1 style='color:red;text-align:center;'>❌ Certificate Tampered</h1>"

    cert_img = f"/certificate/{cert_id}"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Certificate Verified</title>
        <style>
            body {{
                font-family: Arial;
                background: #f4f6f8;
                text-align: center;
            }}
            .box {{
                background: white;
                padding: 30px;
                width: 85%;
                margin: auto;
                margin-top: 40px;
                border-radius: 12px;
                box-shadow: 0 0 10px #aaa;
            }}
            h1 {{ color: green; }}
            img {{
                margin-top: 20px;
                width: 90%;
                max-width: 800px;
                border: 2px solid #ccc;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>✅ CERTIFICATE VERIFIED</h1>
            <p><b>Device:</b> {data["device_name"]}</p>
            <p><b>User:</b> {data["username"]}</p>
            <p><b>Timestamp:</b> {data["timestamp"]}</p>
            <p><b>Status:</b> AUTHENTIC ✅</p>

            <img src="{cert_img}">
        </div>
    </body>
    </html>
    """)

# =========================
# ✅ IMAGE DOWNLOAD
# =========================
@app.route("/certificate/<cert_id>")
def get_certificate_file(cert_id):
    return send_file(f"certificates/{cert_id}.png")

# =========================
# ✅ PRODUCTION RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
