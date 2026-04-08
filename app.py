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
# Rate limiting: effectively unlimited (99999/day)
rate_limit = defaultdict(list)
RATE_LIMIT_MAX = 99999
RATE_LIMIT_WINDOW = timedelta(days=1)

def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()

def check_rate_limit(ip):
    return RATE_LIMIT_MAX

def record_use(ip):
    pass

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

@app.route("/detect", methods=["POST"])
def detect():
    ip = get_client_ip()
    remaining = check_rate_limit(ip)

    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 50:
        return jsonify({"error": "Text must be at least 50 characters"}), 400

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

@app.route("/paraphrase", methods=["POST"])
def paraphrase():
    """Paraphrase text to sound more naturally human-written."""
    data = request.json or {})
    text = data.get("text", "").strip()
    level = data.get("level", "medium")  # light, medium, strong

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 20:
        return jsonify({"error": "Text too short (minimum 20 characters)"}), 400

    if len(text) > 5000:
        text = text[:5000]

    if level not in ('light', 'medium', 'strong'):
        level = 'medium'

    try:
        from paraphrase import paraphrase, paraphrase_multiple
        # Generate 3 variants at the requested level
        variants = paraphrase_multiple(text, n_variants=3, level=level)
        # Also provide one at each level
        light = paraphrase(text, 'light')
        strong = paraphrase(text, 'strong')

        return jsonify({
            "original": text,
            "level": level,
            "variants": variants,
            "light": light,
            "medium": variants[0] if variants else paraphrase(text, 'medium'),
            "strong": strong,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": f"Paraphrasing failed: {str(e)}"}), 500


@app.route("/detect/image", methods=["POST"])
def detect_image():
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    if not re.match(r'.*\.(jpg|jpeg|png|gif|webp)$', file.filename.lower()):
        return jsonify({"error": "Unsupported file type. Use JPG, PNG, GIF, or WEBP."}), 400

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
                return jsonify(result)
            return jsonify({"error": "Unexpected response format"}), 502
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/vocabulary", methods=["POST"])
def vocabulary_scan():
    """Scan text for AI vocabulary patterns."""
    ip = get_client_ip()
    text = request.json.get("text", "").strip()
    if not text or len(text) < 30:
        return jsonify({"error": "Text too short (minimum 30 characters)"}), 400
    try:
        from ai_vocabulary import scan_text_for_ai_vocabulary
        result = scan_text_for_ai_vocabulary(text)
        result["status"] = "success"
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/writing-stats", methods=["POST"])
def writing_stats():
    """Analyze writing: readability, tone, stats."""
    ip = get_client_ip()
    text = request.json.get("text", "").strip()
    if not text or len(text) < 30:
        return jsonify({"error": "Text too short (minimum 30 characters)"}), 400
    try:
        from writing_analyzer import analyze_writing
        result = analyze_writing(text)
        if not result:
            return jsonify({"error": "Could not analyze text"}), 400
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/grammar-check", methods=["POST"])
def grammar_check():
    """Check grammar using LanguageTool public API."""
    ip = get_client_ip()
    text = request.json.get("text", "").strip()
    if not text or len(text) < 10:
        return jsonify({"error": "Text too short"}), 400
    if len(text) > 50000:
        text = text[:50000]
    try:
        resp = requests.post(
            "https://api.languagetool.org/v2/check",
            data={
                "text": text,
                "language": "en-US",
                "level": "default"
            },
            timeout=15
        )
        if resp.ok:
            data = resp.json()
            matches = []
            for m in data.get("matches", []):
                issues = []
                for r in m.get("rule", {}).get("annotations", []):
                    issues.append(r.get("value", m.get("message", "")))
                matches.append({
                    "message": m.get("message", ""),
                    "short_message": m.get("shortMessage", ""),
                    "offset": m.get("offset", {}).get("value", 0),
                    "length": m.get("length", 0),
                    "context": m.get("context", {}).get("text", ""),
                    "type": m.get("type", {}).get("typeName", "Unknown"),
                    "rule": m.get("rule", {}).get("id", ""),
                    "replacements": [r.get("value", "") for r in m.get("replacements", [])[:3]],
                })
            return jsonify({
                "status": "success",
                "matches": matches,
                "total_issues": len(matches),
                "text_length": len(text)
            })
        else:
            return jsonify({"error": f"Grammar API error: {resp.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summarize", methods=["POST"])
def summarize():
    """Summarize text using HuggingFace summarization model."""
    ip = get_client_ip()
    text = request.json.get("text", "").strip()
    length = request.json.get("length", "medium")
    if not text or len(text) < 50:
        return jsonify({"error": "Text too short (minimum 50 characters)"}), 400
    if len(text) > 3000:
        text = text[:3000]
    try:
        from summarizer import summarize
        result = summarize(text, length)
        if not result:
            return jsonify({"error": "Summarization failed"}), 500
        return jsonify({"status": "success", "summary": result, "original_length": len(text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/batch-detect", methods=["POST"])
def batch_detect():
    """Process multiple text files at once."""
    results = []
    files = request.files.getlist("files")
    if not files or len(files) == 0:
        return jsonify({"error": "No files provided"}), 400
    if len(files) > 10:
        return jsonify({"error": "Maximum 10 files at a time"}), 400

    hf_headers = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "application/json"} if HF_API_KEY else {"Accept": "application/json"}

    for file in files:
        filename = file.filename or "unknown"
        ext = filename.lower().split('.')[-1]

        try:
            if ext == 'pdf':
                text = extract_text_from_pdf(file.stream)
            elif ext in ('docx', 'doc'):
                text = extract_text_from_docx(file.stream)
            elif ext in ('txt', 'text'):
                text = file.read().decode('utf-8', errors='ignore')
            else:
                results.append({"filename": filename, "error": "Unsupported file type"})
                continue

            text = text.strip()
            if len(text) < 50:
                results.append({"filename": filename, "error": "File content too short (min 50 chars)"})
                continue
            if len(text) > 3000:
                text = text[:3000]

            payload = {"inputs": text}
            resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)
            if resp.status_code == 503:
                time.sleep(2)
                resp = requests.post(HF_API_URL, json=payload, headers=hf_headers, timeout=30)

            if resp.ok:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    items = data[0] if isinstance(data[0], list) else data
                    human_score = next((i.get("score", 0) for i in items if "real" in i.get("label", "").lower() or "human" in i.get("label", "").lower()), 0)
                    ai_score = next((i.get("score", 0) for i in items if "fake" in i.get("label", "").lower() or "ai" in i.get("label", "").lower()), 0)
                    results.append({
                        "filename": filename,
                        "ai_pct": round(ai_score * 100, 1),
                        "human_pct": round(human_score * 100, 1),
                        "verdict": "AI-Generated" if ai_score > human_score else "Human-Written",
                        "confidence": round(max(ai_score, human_score) * 100, 1),
                        "word_count": len(text.split()),
                    })
            else:
                results.append({"filename": filename, "error": f"API error: {resp.status_code}"})
        except Exception as e:
            results.append({"filename": filename, "error": str(e)})

    return jsonify({"status": "success", "results": results})


@app.route("/readability", methods=["POST"])
def readability():
    """Enhanced readability analysis with multiple metrics."""
    text = request.json.get("text", "").strip()
    if not text or len(text) < 30:
        return jsonify({"error": "Text too short (minimum 30 characters)"}), 400
    try:
        from readability import analyze_writing_v2
        result = analyze_writing_v2(text)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/humanize", methods=["POST"])
def humanize_route():
    """Rewrite AI text to sound more human."""
    ip = get_client_ip()
    text = request.json.get("text", "").strip()
    level = request.json.get("level", "medium")
    if not text or len(text) < 20:
        return jsonify({"error": "Text too short"}), 400
    if level not in ('light', 'medium', 'strong'):
        level = 'medium'
    try:
        from humanizer import humanize, humanize_multiple
        variants = humanize_multiple(text, n_variants=3, level=level)
        return jsonify({
            "status": "success",
            "original": text,
            "variants": variants,
            "level": level,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cite", methods=["POST"])
def cite():
    """Generate citations from URL or DOI."""
    ip = get_client_ip()
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        from citation_generator import generate_citations
        citations = generate_citations(url)
        return jsonify({"status": "success", **citations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
