from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import time
import base64
import re
import io
from collections import defaultdict
from datetime import datetime, timedelta

# Document parsing
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

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

def extract_text_from_pdf(file_stream) -> str:
    if PdfReader is None:
        raise ValueError("PDF parsing not available")
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Could not parse PDF: {e}")

def extract_text_from_docx(file_stream) -> str:
    if docx is None:
        raise ValueError("DOCX parsing not available")
    try:
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        raise ValueError(f"Could not parse DOCX: {e}")

def extract_text_from_file(file, filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return extract_text_from_pdf(file)
    elif ext in ('docx', 'doc'):
        return extract_text_from_docx(file)
    elif ext in ('txt', 'text'):
        return file.read().decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

def analyze_sentences(text: str, hf_headers: dict) -> list:
    """Analyze each sentence for AI probability. Returns list of {sentence, ai_pct, human_pct, is_ai}."""
    import requests
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    results = []

    for sent in sentences:
        if len(sent) < 15:
            results.append({"sentence": sent, "ai_pct": 0, "human_pct": 0, "is_ai": False, "short": True})
            continue
        try:
            payload = {"inputs": sent}
            resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=20)
            if resp.ok:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    items = data[0] if isinstance(data[0], list) else data
                    human_score = next((i.get("score", 0) for i in items if "real" in i.get("label", "").lower() or "human" in i.get("label", "").lower()), 0)
                    ai_score = next((i.get("score", 0) for i in items if "fake" in i.get("label", "").lower() or "ai" in i.get("label", "").lower()), 0)
                    results.append({
                        "sentence": sent,
                        "ai_pct": round(ai_score * 100, 1),
                        "human_pct": round(human_score * 100, 1),
                        "is_ai": ai_score > human_score,
                        "short": False
                    })
                else:
                    results.append({"sentence": sent, "ai_pct": 0, "human_pct": 0, "is_ai": False, "short": False})
            else:
                results.append({"sentence": sent, "ai_pct": 0, "human_pct": 0, "is_ai": False, "short": False})
        except:
            results.append({"sentence": sent, "ai_pct": 0, "human_pct": 0, "is_ai": False, "short": False})

    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify({"status": "ok", "version": "1.1"})

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
    hf_headers = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "application/json"} if HF_API_KEY else {"Accept": "application/json"}

    try:
        payload = {"inputs": text}
        resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)
        if resp.status_code == 503:
            time.sleep(2)
            resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)

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
                    "remaining": remaining,
                    "text_length": len(text)
                })
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Unknown error"}), 500

@app.route("/detect/file", methods=["POST"])
def detect_file():
    """Handle document upload: PDF, DOCX, TXT. Runs sentence-level analysis."""
    ip = get_client_ip()
    remaining = check_rate_limit(ip)

    if remaining <= 0:
        return jsonify({
            "error": "Daily limit reached",
            "upgraded": False,
            "upgrade_url": "/upgrade",
            "message": "You've used all 10 free checks today."
        }), 429

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = file.filename or ""
    ext = filename.lower().split('.')[-1]

    if ext not in ('pdf', 'docx', 'doc', 'txt', 'text'):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

    try:
        text = extract_text_from_file(file, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if len(text) < 50:
        return jsonify({"error": "File content too short (minimum 50 characters)"}), 400

    if len(text) > 10000:
        text = text[:10000]

    record_use(ip)
    hf_headers = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "application/json"} if HF_API_KEY else {"Accept": "application/json"}

    # Overall score
    try:
        payload = {"inputs": text[:2000]}  # Cap for API
        resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)
        if resp.status_code == 503:
            time.sleep(2)
            resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)

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

                # Sentence-level analysis (limited for speed)
                sentence_results = analyze_sentences(text[:1500], hf_headers) if len(text) > 50 else []

                return jsonify({
                    "ai_pct": ai_pct,
                    "human_pct": human_pct,
                    "verdict": verdict,
                    "confidence": round(confidence, 1),
                    "status": "success",
                    "remaining": remaining,
                    "text_length": len(text),
                    "file_name": filename,
                    "sentences": sentence_results
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
    ip = get_client_ip()
    remaining = check_rate_limit(ip)

    if remaining <= 0:
        return jsonify({
            "error": "Daily limit reached",
            "upgraded": False,
            "upgrade_url": "/upgrade",
            "message": "You've used all 10 free checks today."
        }), 429

    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    if not re.match(r'.*\.(jpg|jpeg|png|gif|webp)$', file.filename.lower()):
        return jsonify({"error": "Unsupported file type. Use JPG, PNG, GIF, or WEBP."}), 400

    record_use(ip)

    HF_IMAGE_API_URL = os.environ.get("HF_IMAGE_API_URL", "").strip()
    if not HF_IMAGE_API_URL:
        return jsonify({
            "error": "Image detection not yet configured",
            "message": "Image detection API not set up. Please use text or document mode."
        }), 501

    try:
        img_bytes = file.read()
        b64 = base64.b64encode(img_bytes).decode()
        payload = {"inputs": {"image": b64}}
        headers = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "application/json"} if HF_API_KEY else {"Accept": "application/json"}
        resp = requests.post(HF_IMAGE_API_URL, json=payload, headers=headers, timeout=30)

        if resp.ok:
            result = resp.json()
            if isinstance(result, dict):
                result["remaining"] = check_rate_limit(ip)
                return jsonify(result)
            return jsonify({"error": "Unexpected response format"}), 502
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
