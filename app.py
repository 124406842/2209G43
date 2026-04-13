import os
import time
import uuid
import logging
import requests
from collections import Counter
from flask import Flask, jsonify, g, request, make_response
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

cache = {"external_api": None, "timestamp": 0}

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://jsonplaceholder.typicode.com/todos/1")

JOKES_API_URL = "https://official-joke-api.appspot.com/random_joke"
JOKES_API_BASE = "https://official-joke-api.appspot.com/jokes"

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
    # simple session cookie for per-user history
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    html = """
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
                    width: 420px;
                    text-align: center;
                    border: 2px solid #007bff;

                }
                h1 {
                    font-size: 24px;
                    margin-bottom: 20px;
                    color: #333;
                }
                select, button {
                    padding: 10px 15px;
                    font-size: 16px;
                    border-radius: 6px;
                    border: 1px solid #ccc;
                    margin: 5px;
                }
                button {
                    background: #007bff;
                    color: white;
                    border: none;
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
                #history {
                    margin-top: 20px;
                    font-size: 14px;
                    color: #666;
                    text-align: left;
                    max-height: 150px;
                    overflow-y: auto;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Random Joke Generator</h1>

                <select id="category">
                    <option value="">Random</option>
                    <option value="general">General</option>
                    <option value="programming">Programming</option>
                    <option value="knock-knock">Knock‑Knock</option>
                </select>

                <button onclick="loadJoke()">Get Joke</button>

                <br/>

                <select id="info">
                    <option value="history">My History</option>
                    <option value="user_stats">My Stats</option>
                    <option value="popular_category">Most Popular Category</option>
                </select>
                <button onclick="loadInfo()">Show</button>

                <p id="joke"></p>
                <div id="history"></div>
            </div>

            <script>
                async function loadJoke() {
                    const cat = document.getElementById('category').value;
                    const endpoint = cat ? `/joke/${cat}` : '/joke';

                    const res = await fetch(endpoint);
                    const data = await res.json();

                    if (data.error) {
                        document.getElementById('joke').innerText = "Error: " + data.error;
                    } else {
                        document.getElementById('joke').innerText =
                            data.setup + " — " + data.punchline;
                    }
                }

                async function loadHistory() {
                    const res = await fetch('/jokes/history');
                    const data = await res.json();

                    const container = document.getElementById('history');
                    if (!Array.isArray(data) || data.length === 0) {
                        container.innerText = "No history yet.";
                        return;
                    }

                    container.innerHTML = "";
                    data.forEach(j => {
                        const p = document.createElement('p');
                        p.textContent = (j.category || 'unknown') + ": " + j.setup + " — " + j.punchline;
                        container.appendChild(p);
                    });
                }

                async function loadUserStats() {
                    const res = await fetch('/stats/user');
                    const data = await res.json();

                    const container = document.getElementById('history');

                    if (data.error) {
                        container.innerText = "Error loading stats: " + data.error;
                        return;
                    }

                    container.innerHTML = "";
                    const h = document.createElement('h3');
                    h.textContent = "My Stats";
                    container.appendChild(h);

                    const total = document.createElement('p');
                    total.textContent = "Total jokes generated: " + data.total_jokes;
                    container.appendChild(total);

                    const catsTitle = document.createElement('p');
                    catsTitle.textContent = "By category:";
                    container.appendChild(catsTitle);

                    const ul = document.createElement('ul');
                    for (const [cat, count] of Object.entries(data.categories || {})) {
                        const li = document.createElement('li');
                        li.textContent = cat + ": " + count;
                        ul.appendChild(li);
                    }
                    container.appendChild(ul);
                }

                async function loadPopularCategory() {
                    const res = await fetch('/stats/popular-category');
                    const data = await res.json();

                    const container = document.getElementById('history');

                    if (data.error) {
                        container.innerText = "Error loading popular category: " + data.error;
                        return;
                    }

                    container.innerHTML = "";
                    const h = document.createElement('h3');
                    h.textContent = "Most Popular Category (All Users)";
                    container.appendChild(h);

                    const p = document.createElement('p');
                    p.textContent = data.most_popular_category || "No data yet";
                    container.appendChild(p);
                }

                function loadInfo() {
                    const choice = document.getElementById('info').value;
                    if (choice === 'history') {
                        loadHistory();
                    } else if (choice === 'user_stats') {
                        loadUserStats();
                    } else if (choice === 'popular_category') {
                        loadPopularCategory();
                    }
                }
            </script>
        </body>
    </html>
    """

    resp = make_response(html)
    resp.set_cookie("session_id", session_id, max_age=60 * 60 * 24 * 30)  # 30 days
    return resp

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

def save_joke_to_history(joke_data):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return

    session_id = request.cookies.get("session_id")
    if not session_id:
        return

    payload = {
        "session_id": session_id,
        "setup": joke_data.get("setup"),
        "punchline": joke_data.get("punchline"),
        "category": joke_data.get("type")
    }

    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/joke_history",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=5
        )
    except requests.RequestException:
        # for assignment purposes, we can ignore failures here
        pass

@app.route("/joke")
def joke():
    try:
        response = requests.get(f"{JOKES_API_BASE}/random", timeout=5)
        response.raise_for_status()
        joke_data = response.json()

        if isinstance(joke_data, list) and joke_data:
            joke_data = joke_data[0]

        save_joke_to_history(joke_data)

        return jsonify({
            "setup": joke_data.get("setup"),
            "punchline": joke_data.get("punchline"),
            "type": joke_data.get("type")
        }), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Jokes API unavailable",
            "message": str(e)
        }), 503

@app.route("/joke/<category>")
def joke_by_category(category):
    allowed = {"general", "programming", "knock-knock"}

    if category not in allowed:
        return jsonify({
            "error": "Invalid category",
            "allowed": list(allowed)
        }), 400

    try:
        url = f"{JOKES_API_BASE}/{category}/random"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        joke_data = response.json()

        if isinstance(joke_data, list) and joke_data:
            joke_data = joke_data[0]

        # normalise type to the category we requested
        joke_data["type"] = category
        save_joke_to_history(joke_data)

        return jsonify({
            "setup": joke_data.get("setup"),
            "punchline": joke_data.get("punchline"),
            "type": joke_data.get("type")
        }), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Jokes API unavailable",
            "message": str(e)
        }), 503

@app.route("/jokes/history")
def jokes_history():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({"error": "Supabase not configured"}), 500

    session_id = request.cookies.get("session_id")
    if not session_id:
        return jsonify([]), 200

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/joke_history"
            f"?session_id=eq.{session_id}&order=created_at.desc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        resp.raise_for_status()
        return jsonify(resp.json()), 200
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch history", "message": str(e)}), 503

@app.route("/jokes/leaderboard")
def jokes_leaderboard():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/joke_history",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        resp.raise_for_status()
        rows = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch leaderboard data", "message": str(e)}), 503

    counter = Counter()
    for r in rows:
        key = (r.get("setup"), r.get("punchline"))
        counter[key] += 1

    top = []
    for (setup, punchline), count in counter.most_common(10):
        top.append({
            "setup": setup,
            "punchline": punchline,
            "count": count
        })

    return jsonify(top), 200

@app.route("/stats/user")
def stats_user():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({"error": "Supabase not configured"}), 500

    session_id = request.cookies.get("session_id")
    if not session_id:
        return jsonify({"total_jokes": 0, "categories": {} }), 200

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/joke_history?session_id=eq.{session_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        resp.raise_for_status()
        rows = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch user stats", "message": str(e)}), 503

    total = len(rows)
    cat_counter = Counter()
    for r in rows:
        cat = r.get("category") or "unknown"
        cat_counter[cat] += 1

    return jsonify({
        "total_jokes": total,
        "categories": dict(cat_counter)
    }), 200

@app.route("/stats/popular-category")
def stats_popular_category():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({"error": "Supabase not configured"}), 500

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/joke_history?select=category",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        resp.raise_for_status()
        rows = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch category stats", "message": str(e)}), 503

    if not rows:
        return jsonify({"most_popular_category": None}), 200

    counter = Counter([r["category"] for r in rows if r.get("category")])
    if not counter:
        return jsonify({"most_popular_category": None}), 200

    most_common = counter.most_common(1)[0][0]

    return jsonify({"most_popular_category": most_common}), 200

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
