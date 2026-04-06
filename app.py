from flask import Flask, render_template, request, jsonify
import requests
import os
import time

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/roberta-base-openai-detector"
HF_API_KEY = os.environ.get("HF_API_KEY", "").strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    text = request.json.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 50:
        return jsonify({"error": "Text must be at least 50 characters"}), 400

    # Query Hugging Face API
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

    try:
        payload = {"inputs": text}
        resp = requests.post(HF_API_URL, json=payload, headers=headers, timeout=30)

        if resp.status_code == 503:
            # Model loading - try again
            time.sleep(2)
            resp = requests.post(HF_API_URL, json=payload, headers=headers, timeout=30)

        if resp.ok:
            result = resp.json()
            # Format: [[{label, score}, ...]]
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

                return jsonify({
                    "ai_pct": ai_pct,
                    "human_pct": human_pct,
                    "verdict": verdict,
                    "confidence": round(confidence, 1),
                    "status": "success"
                })
        else:
            return jsonify({"error": f"API error: {resp.status_code}"}), 500

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Unknown error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
