from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import time
import base64
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

HF_API_URL = "https://router.huggingface.co/hf-inference/models/openai-community/roberta-base-openai-detector"
HF_API_KEY = os.environ.get("HF_API_KEY", "").strip()

LEMONSQUEEZY_URL = os.environ.get("LEMONSQUEEZY_URL", "https://yourusername.lemonsqueezy.com/checkout/buy/YOUR-PRODUCT-ID")

# Rate limiting: 10 free checks per IP per day
rate_limit = defaultdict(list)
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = timedelta(days=1)

def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()

def check_rate_limit(ip):
    now = datetime.utcnow()
    rate_limit[ip] = [ts for ts in rate_limit[ip] if now - ts < RATE_LIMIT_WINDOW]
    return RATE_LIMIT_MAX - len(rate_limit[ip])

def record_use(ip):
    rate_limit[ip].append(datetime.utcnow())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify({"status": "ok", "version": "1.0"})

@app.route("/upgrade")
def upgrade():
    return redirect(LEMONSQUEEZY_URL, code=302)

@app.route("/detect", methods=["POST"])
def detect():
    ip = get_client_ip()
    remaining = check_rate_limit(ip)

    if remaining <= 0:
        return jsonify({
            "error": "Daily limit reached",
            "upgraded": False,
            "upgrade_url": "/upgrade",
            "message": "You've used all 10 free checks today. Upgrade for unlimited access."
        }), 429

    text = request.json.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 50:
        return jsonify({"error": "Text must be at least 50 characters"}), 400

    record_use(ip)

    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

    try:
        payload = {"inputs": text}
        resp = requests.post(HF_API_URL, json=payload, headers=headers, timeout=30)

        if resp.status_code == 503:
            time.sleep(2)
            resp = requests.post(HF_API_URL, json=payload, headers=headers, timeout=30)

        if resp.ok:
            result = resp.json()
            if isinstance(result, list) and len(result) > 0:
                data = result[0] if isinstance(result[0], list) else result
                human_score = 0
                ai_score = 0
                for item in data:
                    label = item.get("label", "").lower()
                    score = item.get("score", 0)
                    if "real" in label or "human" in label:
                        human_score = score
                    elif "fake" in label or "ai" in label or "gpt" in label:
                        ai_score = score

                ai_pct = round(ai_score * 100, 1)
                human_pct = round(human_score * 100, 1)

                verdict = "🤖 AI-Generated" if ai_score > human_score else "✅ Human-Written"
                confidence = max(ai_score, human_score) * 100
                remaining = check_rate_limit(ip)

                return jsonify({
                    "ai_pct": ai_pct,
                    "human_pct": human_pct,
                    "verdict": verdict,
                    "confidence": round(confidence, 1),
                    "status": "success",
                    "remaining": remaining
                })
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Unknown error"}), 500

@app.route("/detect/image", methods=["POST"])
def detect_image():
    """AI-generated image detection via Hugging Face.
    Uses_imagenette-if-you-know-me) or similar.
    Falls back to error if no image model configured. """
    ip = get_client_ip()
    remaining = check_rate_limit(ip)

    if remaining <= 0:
        return jsonify({
            "error": "Daily limit reached",
            "upgraded": False,
            "upgrade_url": "/upgrade",
            "message": "You've used all 10 free checks today. Upgrade for unlimited access."
        }), 429

    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    if not file.filename.lower().match(r'.*\.(jpg|jpeg|png|gif|webp)$'):
        return jsonify({"error": "Unsupported file type. Use JPG, PNG, GIF, or WEBP."}), 400

    record_use(ip)

    HF_IMAGE_API_URL = os.environ.get("HF_IMAGE_API_URL", "").strip()
    if not HF_IMAGE_API_URL:
        return jsonify({
            "error": "Image detection not yet configured",
            "message": "Image detection API not set up. Please use text mode or contact support."
        }), 501

    try:
        img_bytes = file.read()
        b64 = base64.b64encode(img_bytes).decode()
        payload = {"inputs": {"image": b64}}

        headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
        resp = requests.post(HF_IMAGE_API_URL, json=payload, headers=headers, timeout=30)

        if resp.ok:
            result = resp.json()
            # Expected: {ai_pct, human_pct, verdict, confidence...}
            if isinstance(result, dict):
                result["remaining"] = check_rate_limit(ip)
                return jsonify(result)
            return jsonify({"error": "Unexpected response format", "details": str(result)}), 502
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
