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
        <head><title>Random Joke Generator</title></head>
        <body style='font-family: Arial; padding: 20px;'>
            <h1>Random Joke Generator</h1>
            <button onclick="loadJoke()">Get Joke</button>
            <p id="joke" style="margin-top:20px; font-size:18px;"></p>

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
