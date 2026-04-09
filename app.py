import os
import time
import uuid
import logging
import requests
from flask import Flask, jsonify, g, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

cache = {"external_api": None, "timestamp": 0}

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://jsonplaceholder.typicode.com/todos/1")
JOKES_API_URL = "https://official-joke-api.appspot.com/random_joke"

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
    return """
    <html>
        <head>
            <title>Random Joke Generator</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f4f6f9;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .card {
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    width: 400px;
                    text-align: center;
                }
                h1 {
                    font-size: 24px;
                    margin-bottom: 20px;
                    color: #333;
                }
                button {
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 16px;
                    cursor: pointer;
                }
                button:hover {
                    background: #0056b3;
                }
                #joke {
                    margin-top: 20px;
                    font-size: 18px;
                    color: #444;
                    min-height: 40px;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Random Joke Generator</h1>
                <button onclick="loadJoke()">Get Joke</button>
                <p id="joke"></p>
            </div>

            <script>
                async function loadJoke() {
                    const res = await fetch('/joke');
                    const data = await res.json();
                    if (data.error) {
                        document.getElementById('joke').innerText = "Error: " + data.error;
                    } else {
                        document.getElementById('joke').innerText =
                            data.setup + " — " + data.punchline;
                    }
                }
            </script>
        </body>
    </html>
    """

@app.route("/status")
def status():
    return {
        "supabase_url_loaded": bool(SUPABASE_URL),
        "supabase_key_loaded": bool(SUPABASE_KEY),
        "external_api_url": EXTERNAL_API_URL,
        "jokes_api_url": JOKES_API_URL
    }

@app.route("/health")
def health():
    db_ok = check_supabase_connection()
    api_ok = check_external_api()
    jokes_ok = check_jokes_api()

    status_code = 200 if (
        db_ok["status"] == "ok" and
        api_ok["status"] == "ok" and
        jokes_ok["status"] == "ok"
    ) else 503

    return jsonify({
        "status": "ok" if status_code == 200 else "degraded",
        "database": db_ok,
        "external_api": api_ok,
        "jokes_api": jokes_ok
    }), status_code

@app.route("/combined")
def combined():
    db_data = get_data_from_supabase()
    api_data = get_data_from_external_api()

    try:
        joke_res = requests.get(JOKES_API_URL, timeout=5)
        joke_res.raise_for_status()
        joke_data = joke_res.json()
    except requests.RequestException:
        joke_data = {"error": "Jokes API unavailable"}

    return jsonify({
        "database": db_data,
        "external_api": api_data,
        "joke": joke_data
    }), 200

@app.route("/joke")
def joke():
    try:
        response = requests.get(JOKES_API_URL, timeout=5)
        response.raise_for_status()
        joke_data = response.json()
        return jsonify({
            "setup": joke_data.get("setup"),
            "punchline": joke_data.get("punchline")
        }), 200
    except requests.RequestException as e:
        return jsonify({
            "error": "Jokes API unavailable",
            "message": str(e)
        }), 503

def check_supabase_connection():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "error", "message": "Supabase env vars missing"}

    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers, timeout=5)

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

def check_jokes_api():
    try:
        response = requests.get(JOKES_API_URL, timeout=5)
        response.raise_for_status()
        return {"status": "ok", "message": "Jokes API reachable"}
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
            cache["timestamp"] = int(time.time())
            return data
        except requests.RequestException:
            time.sleep(delay)
            delay *= 2

    if cache["external_api"] is not None:
        return {"cached": True, "data": cache["external_api"]}

    return {"error": "external API unreachable after retries"}

if __name__ == "__main__":
    app.run(debug=True)
