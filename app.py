from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import fitz
import os

# Load environment variables
load_dotenv()

# OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)  # may be None if not provided

# Flag to use mock summaries instead of calling OpenAI
USE_MOCK = os.getenv("MOCK_SUMMARY", "false").lower() in ("1","true","yes")

app = Flask(__name__)
CORS(app)

# -------------------------------
# Common Summary Function
# -------------------------------
def get_summary(prompt):
    # if mock mode enabled or no API key available, return placeholder text
    if USE_MOCK or not api_key:
        return "[MOCK SUMMARY] This is a fake summary used for testing."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes content clearly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        # bubble up a readable error
        raise RuntimeError(f"Summarization failed: {e}")


# -------------------------------
# TEXT SUMMARIZATION
# -------------------------------
@app.route("/summarize/text", methods=["POST"])
def summarize_text():
    try:
        data = request.get_json(silent=True)
        # also accept form-encoded or multipart data
        if not data:
            data = request.form

        text = data.get("text") if data else None
        if not text:
            return jsonify({"error": "No text provided"}), 400

        prompt = f"Summarize the following text:\n{text}"
        summary = get_summary(prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# PDF SUMMARIZATION
# -------------------------------
@app.route("/summarize/pdf", methods=["POST"])
def summarize_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        doc = fitz.open(stream=file.read(), filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()

        if not text.strip():
            return jsonify({"error": "PDF contains no extractable text"}), 400

        prompt = f"Summarize the following PDF content:\n{text}"
        summary = get_summary(prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# YOUTUBE SUMMARIZATION
# -------------------------------
@app.route("/summarize/youtube", methods=["POST"])
def summarize_youtube():
    try:
        data = request.get_json(silent=True)
        if not data:
            data = request.form

        url = None
        if data:
            url = data.get("url") or data.get("youtubeURL")

        if not url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        # try to extract video id robustly
        if "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        else:
            # handle youtu.be short links
            parts = url.rstrip("/").split("/")
            video_id = parts[-1]

        # Use instance API: fetch returns a FetchedTranscript with snippet objects
        fetched = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join([snippet.text for snippet in fetched])

        if not text.strip():
            return jsonify({"error": "No transcript available for this video"}), 400

        prompt = f"Summarize this YouTube transcript:\n{text}"
        summary = get_summary(prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
