import os
import time
import uuid
import logging
import requests
from flask import Flask, jsonify, g, request
from dotenv import load_dotenv

load_dotenv()

cache = {"external_api": None, "timestamp": 0}

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://jsonplaceholder.typicode.com/todos/1")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    g.path = request.path

@app.after_request
def after_request(response):
    duration = round((time.time() - g.start_time) * 1000, 2)
    app.logger.info(
        f"request_id={g.request_id} status={response.status_code} path={g.path} duration_ms={duration}"
    )
    response.headers["X-Request-ID"] = g.request_id
    return response

@app.route("/")
def home():
    return "Flask app is running"

@app.route("/status")
def status():
    return {
        "supabase_url_loaded": bool(SUPABASE_URL),
        "supabase_key_loaded": bool(SUPABASE_KEY),
        "external_api_url": EXTERNAL_API_URL
    }

@app.route("/health")
def health():
    db_ok = check_supabase_connection()
    api_ok = check_external_api()

    status_code = 200 if db_ok["status"] == "ok" and api_ok["status"] == "ok" else 503

    return jsonify({
        "status": "ok" if status_code == 200 else "degraded",
        "database": db_ok,
        "external_api": api_ok
    }), status_code

@app.route("/combined")
def combined():
    db_data = get_data_from_supabase()
    api_data = get_data_from_external_api()

    return jsonify({
        "database": db_data,
        "external_api": api_data
    }), 200

def check_supabase_connection():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "error", "message": "Supabase env vars missing"}

    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers,
            timeout=5
        )

        if response.status_code in [200, 404]:
            return {"status": "ok", "message": "Supabase reachable"}

        return {"status": "error", "message": f"Supabase returned {response.status_code}"}

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

def get_data_from_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"error": "Supabase not configured"}

    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/cities?select=*",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return {
            "error": "Failed to fetch from Supabase",
            "status_code": response.status_code,
            "response": response.text
        }

    except requests.RequestException as e:
        return {"error": str(e)}

def check_external_api():
    try:
        response = requests.get(EXTERNAL_API_URL, timeout=5)
        response.raise_for_status()
        return {"status": "ok", "message": "External API reachable"}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

def get_data_from_external_api():
    attempts = 3
    delay = 1

    for _ in range(attempts):
        try:
            response = requests.get(EXTERNAL_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            cache["external_api"] = data
            cache["timestamp"] = time.time()
            return data
        except requests.RequestException:
            time.sleep(delay)
            delay *= 2

    if cache["external_api"] is not None:
        return {"cached": True, "data": cache["external_api"]}

    return {"error": "external API unreachable after retries"}

if __name__ == "__main__":
    app.run(debug=True)
