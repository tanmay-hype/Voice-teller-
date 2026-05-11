Keep-alive / Keepalive Notes
=============================

Purpose
-------
This document explains the optional keep-alive (self-ping) feature implemented in `backend/main.py` and provides recommendations for deploying on Render.

Quick summary
-------------
- A background self-pinger is available in `backend/main.py`. It periodically sends GET requests to the configured health endpoint to keep the process warm.
- The feature is configurable via environment variables (recommended to set these in your Render service settings or `.env`).

Environment variables
---------------------
- `KEEPALIVE_ENABLE` (bool) — set to `true` to enable the in-process keep-alive loop. Default: `false`.
- `KEEPALIVE_INTERVAL_SECONDS` (int) — ping interval in seconds. Default: `300` (5 minutes).
- `KEEPALIVE_URL` (string) — full URL to ping. Default: `http://127.0.0.1:8000/health` (change to your public URL when deployed).

Example `.env` entries
----------------------
KEEPALIVE_ENABLE=true
KEEPALIVE_INTERVAL_SECONDS=300
KEEPALIVE_URL=https://your-app.onrender.com/health

Render deployment notes
-----------------------
- Preferred approach: use Render's Cron Job or an external uptime service to ping your `/health` endpoint regularly. This is more reliable and keeps concerns outside your application process.
  - Create a Render Cron Job that performs an HTTP GET on `https://your-app.onrender.com/health` every 5 minutes.
- Alternative (in-app): enable `KEEPALIVE_ENABLE=true` and set `KEEPALIVE_URL` to the public health endpoint. Note: when the process is idled by the platform, an in-process keep-alive may not help — external pings are more reliable.

Sample Render Cron request
---------------------------
Use a Render Cron Job with:

- Schedule: `*/5 * * * *`
- Command:

```bash
curl -fsS https://your-app.onrender.com/health >/dev/null
```

If you prefer `wget`, this works too:

```bash
wget -qO- https://your-app.onrender.com/health >/dev/null
```

How it works in this repo
-------------------------
- `backend/main.py` starts a background `asyncio` task on startup when `KEEPALIVE_ENABLE` is true. It issues GET requests to `KEEPALIVE_URL` at the configured interval.
- On shutdown the task is cancelled cleanly.

Security & costs
----------------
- Keep payloads minimal (GET `/health`). Avoid sending secrets to the keep-alive endpoint.
- If using an external uptime service, be mindful of rate limits and costs for very frequent pings.

Recommendation
--------------
Use Render Cron Job (or external uptime-monitor) to call `/health` every 5 minutes and keep the service warm. Enable the in-app keep-alive only if you want a fallback or cannot use an external ping.

Files changed
-------------
- `backend/core/config.py` — added keep-alive config variables.
- `backend/main.py` — added optional background keep-alive loop and shutdown cleanup.

Contact
-------
If you want, I can add a `.env.example` at the project root and a sample Render Cron configuration snippet.
