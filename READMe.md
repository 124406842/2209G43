# Random Joke Generator , A flask / Supabase integrated project
    Sean Daly - 124406842
    Darragh Higgins - 12450620
    Alan Neville - 124440282

## GitHub Repository Link
https://github.com/124406842/2209G43

# A WebApp generating random jokes
    supports category based jokes
    stores history using Supabase
    user statistics, popular category insights
- Built using Flask, Supabase, HTML/CSS/JS. Also supported by docker and github
# The goal:
- of our project is to show API integration, error handling and basic UI interaction
through a simple web interface. The homepage has minimal UI which allows the user to select a
joke from a list of categories. All other endpoints return JSON responses.

# Key Aspects:
Random joke generation
fetches jokes from the Official Joke API.
- Category‑Based Jokes such as:
general , programming , knock‑knock
- User Joke History:
every user is given a unique session_id cookie.
history is stored in Supabase → joke_history table.
- User Statistics consisting of:
total jokes generated
jokes per category
Top Category (global)
Shows the most frequently generated joke category across all users.
- 
# Health / Status Endpoints
- /status — environment variable check
- /health — Supabase + External API + Joke API health

- Combined API Endpoint  
Fetches:
Supabase data
External API data
A random joke
all in one response.
Clean UI
Category dropdown
Stats/history dropdown
Dynamic joke display
Simple, responsive card layout

# PROJECT STRUCTURE
2209G43/
│
├── .github/workflows/ci.yml
├── .venv/
├── docs/
│   ├── architecture-note.md
│   ├── collaboration-log.md
│   ├── error-handling.md
│   ├── toolchain-critique.md
│   └── user-stories.md
├── static/
├── icons
│   └─.keep 
|   |-default.png
|   |-general.png
|   |-knockknock.png
|   |-programming.png
├── .env
├── .env.example
├── .gitignore
├── app.py
├── Dockerfile
├── README.md
└── requirements.txt


# Setup
Prerequisites
Python 3.11+
PostgreSQL DB (Supabase)
Jokes API
GitHub account (CI/CD)
Docker (optional)


## How to run the application
   - Install dependencies:
pip install -r requirements.txt 
   - Create a .env file in the project folder:
SUPABASE_URL=<your-url>
SUPABASE_KEY=<your-key>
EXTERNAL_API_URL=https://jsonplaceholder.typicode.com/todos/1
   - Run the flask app:
python app.py
   - Open the app in your browser:
http://127.0.0.1:5000/
# Environment variables
   - Create a .env file in the project root with:
Variable	|   Description	   |          Example
SUPABASE_URL	Supabase project URL	     https://xyzcompany.supabase.co
SUPABASE_KEY	Supabase service role or anon key	
EXTERNAL_API_URL	Secondary external API endpoint	  https://jsonplaceholder.typicode.com/todos/1
A .env.example file is included to show the required structure.
Copy it and rename it to `.env` before running the project.
# Deployment
 - The application is deployed at:
Production URL: https://<your-app-host>.com
 - To deploy a new version:
1. Push changes to main
2. GitHub Actions builds and publishes the Docker image
3. The hosting platform pulls the latest image and restarts the service


Endpoints
# Homepage  
Displays a simple UI with a button to select a type of joke, which then fetches a random joke under
that category. Uses JavaScript to call /joke.
# /joke  
Returns a random joke from the Official Joke API.
# /combined  
Returns a combined JSON response which includes:
Data from Supabase
Data from the external API
A random joke
Shows multi‑source integration.
# /health  
Health check endpoint reporting status of:
Supabase connection
External API
Joke API
Returns “ok” or “degraded”.
# /status  
Shows if the environment variables are loaded correctly and displays URLs being used.
Example requests and responses
# GET /joke
 - Request:
Code
GET /joke HTTP/1.1
Host: localhost:5000
Accept: application/json 
 - Response:
{
  "setup": "Why do programmers prefer dark mode?",
  "punchline": "Because light attracts bugs.",
  "category": "programming"
}

 
# Supabase table used:
The project uses a Supabase table called joke_history which stores every joke fetched by the user.
Column |	Type |	Notes
id	   |    uuid | Primary key — default: uuid_generate_v4()
session_id| text |	Identifies the user/session
setup  |    text |	Joke setup text
punchline|  text |	Joke punchline text
category|   text |	Joke category (e.g., general, programming)
created_at| timestamp |	Default: now()


# Technologies used
Flask – backend
Supabase – database + REST API
Official Joke API – external API
Requests – HTTP client
JavaScript Fetch API – frontend interaction
Docker – container
GitHub Actions – CI/CD
HTML / CSS – basic UI

# Error handling
The app includes:
Retry logic for the external API should it fail
Fallback to cached data
Valid JSON error messages
Timeout handling
Logging with request IDs

# Observability
Each request logged contains a:
Unique request ID
Status code
Path
Duration (ms)
 - Helps support tracing and debugging.

# Limitations
UI is minimal
No authentication
External API availability might affect /combined

## CI/CD pipeline
This project uses GitHub Actions for continuous integration and delivery:
On every pull request and push to main:
Lints the code (flake8 / ruff)
Runs tests with pytest
Generates a coverage report
Builds the Docker image

 - On successful builds from main:
The Docker image is published to GitHub Container Registry (GHCR)
The latest image is deployed to the hosting environment (Render / Railway / VM)
Status checks must pass before merging PRs into main.





