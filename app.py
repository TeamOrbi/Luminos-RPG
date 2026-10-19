# Handler for Email Sending
from __future__ import annotations
import hashlib
import hmac
import os
import re
import time
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from database import connect, initialise
from game_engine import handle_email

load_dotenv()
app = Flask(__name__)

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
MAILGUN_BASE_URL = os.getenv("MAILGUN_BASE_URL", "https://api.mailgun.net")
MAILGUN_FROM = os.getenv("MAILGUN_FROM", "")
MAILGUN_WEBHOOK_SIGNING_KEY = os.getenv("MAILGUN_WEBHOOK_SIGNING_KEY", "")
INBOUND_ADDRESS = os.getenv("INBOUND_ADDRESS", "").strip().lower()
TIMEZONE = os.getenv("LUMINOS_TIMEZONE", "Australia/Adelaide")

def verify_mailgun_signature(timestamp: str, token: str, signature: str) -> bool:
    if not MAILGUN_WEBHOOK_SIGNING_KEY or not timestamp or not token or not signature:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 15 * 60:
            return False
    except (TypeError, ValueError):
        return False
    digest = hmac.new(MAILGUN_WEBHOOK_SIGNING_KEY.encode(), (timestamp + token).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)

def send_email(to_address: str, subject: str, body: str) -> None:
    if not all((MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_FROM)):
        raise RuntimeError("Mailgun sending is not configured. Check MAILGUN_API_KEY, MAILGUN_DOMAIN and MAILGUN_FROM.")
    base = MAILGUN_BASE_URL.rstrip("/")
    response = requests.post(
        f"{base}/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": MAILGUN_FROM, "to": to_address, "subject": subject, "text": body},
        timeout=20,
    )
    response.raise_for_status()

def valid_email(address: str) -> bool:
    return bool(re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", address or ""))

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "luminos-email-rpg"})

@app.post("/mailgun/inbound")
def inbound():
    fields = request.form
    signature = fields.get("signature", "")
    if not verify_mailgun_signature(fields.get("timestamp", ""), fields.get("token", ""), signature):
        return jsonify({"error": "invalid webhook signature"}), 403
    sender = (fields.get("sender") or fields.get("from") or "").strip().lower()
    recipient = (fields.get("recipient") or "").strip().lower()
    subject = fields.get("subject", "")
    body = fields.get("body-plain", "")
    message_id = (fields.get("Message-Id") or fields.get("message-id") or "").strip()
    if not valid_email(sender):
        return jsonify({"error": "missing or invalid sender"}), 400
    if INBOUND_ADDRESS and recipient != INBOUND_ADDRESS:
        return jsonify({"error": "unexpected recipient"}), 400
    if not message_id:
        # Stable ID is required for safe retries
        return jsonify({"error": "missing Message-Id"}), 400
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        exists = conn.execute("SELECT 1 FROM processed_messages WHERE message_id=?", (message_id,)).fetchone()
        if exists:
            conn.rollback()
            return jsonify({"status": "duplicate ignored"}), 200
        reply = handle_email(conn, sender, subject, body, TIMEZONE)
        conn.execute("INSERT INTO processed_messages(message_id) VALUES (?)", (message_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        app.logger.exception("Failed to process inbound email")
        return jsonify({"error": "processing failed"}), 500
    finally:
        conn.close()

    # Consumed state before sending to Mailgun, so does not consume second turn on retry.
    try:
        send_email(sender, "Luminos - Emailed Adventure", reply)
    except Exception:
        app.logger.exception("Game action saved, but reply email could not be sent")
        # 200 avoids processing same action on provider retry.
        return jsonify({"status": "processed", "reply": "send_failed_check_logs"}), 200
    return jsonify({"status": "processed"}), 200

if __name__ == "__main__":
    initialise()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))