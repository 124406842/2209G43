### Toolchain Critique

## Overview
This project used a simple but effective toolchain.
The toolchain consisted of Flask, Supabase and the Official Joke API.
We also used PyCharm and GitHub.
Each tool had its own role in the integration process and its own strengths and limitations.


## Flask

Flask handled merging joke data, images, and Supabase statistics into a single response.

# Strengths
- Very lightweight and easy to set up
- Perfect for small integration projects
- Simple routing model
- Easy to return JSON responses

# Limitations
- No built‑in structure for larger applications
- Requires manual setup for logging, error handling and configuration

## Supabase
Supabase made it straightforward to compute statistics such as the most popular joke and per‑session joke counts.

# Strengths
- Very easy to create tables and manage data
- Dashboard UI is clean and beginner‑friendly
- UUID generation and timestamps handled automatically

# Limitations
- RLS policies can be confusing at first
- Occasional slow response times
- Documentation sometimes assumes SQL knowledge
- Requires environment variables which can cause issues if misconfigured

## External Joke API
Returned the jokes, including a setup and a punchline

# Strengths
- Simple JSON responses
- No authentication required
- Supports categories (general, programming, knock‑knock)
- Fast and reliable for most requests

# Limitations
- No guarantee of long‑term stability
- Limited documentation
- Some categories return fewer jokes


## PyCharm

# Strengths
- Excellent Python support
- Built‑in debugger
- Easy environment management
- Integrated terminal

# Limitations
- Some features locked behind the Professional edition


## GitHub

# Strengths
- Makes collaboration easier
- Tracks changes and prevents overwriting
- Allows branching and merging

# Limitations
- Requires team discipline to use properly
- Merge conflicts can be confusing


## Overall Reflection
The toolchain was effective for our application.
Flask handled routing, Supabase handled persistent storage and the Joke API supplied external data.
PyCharm supported development and GitHub helped collaboration.
The main challenges were configuring Supabase policies and handling external API failures, which we addressed with proper error handling.
