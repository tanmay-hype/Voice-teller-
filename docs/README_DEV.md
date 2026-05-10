Development Docker workflow

Recommended approach to avoid uvicorn scanning host virtualenvs (prevents OOM when using --reload):

Option A (recommended): keep your local Python virtualenv outside the project folder.
- Create venv in your home or a sibling folder, e.g. `python -m venv ~/.venvs/aivoice`.
- Activate that venv for local development.
- Use the default `docker-compose.yml` which does not mount your local source.
- For iterative development, use the dev override below.

Option B (if you want in-container reload): use the dev compose override but ensure your host venv is NOT inside `backend/`.
- Start the stack in dev mode (this will mount your local backend into the container):

```bash
# from repo root
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Notes & rationale
- The base `docker-compose.yml` no longer bind-mounts `./backend` to avoid accidentally mounting a local virtualenv into `/app` inside the container (this caused uvicorn's file-watcher to traverse many site-packages files and exhaust memory).
- The `docker-compose.dev.yml` override provides an opt-in mount and `--reload` for fast feedback during development. Use it only when your host venv is outside the repo.
- We include a `.dockerignore` that excludes common venv folders from image build context and avoids leaking secrets.

Production / Hosting (Render, Netlify)
- For Render / production, build images without dev mounts and run the API with a production server (gunicorn + uvicorn workers) or plain `uvicorn` without `--reload`.
- Netlify is for frontend hosting; deploy the frontend build there and point `VITE_API_URL` to your deployed API.

If you want, I can:
- add a `Makefile` with common commands, or
- update `backend/Dockerfile` to create a venv in `/opt/venv` and use it, or
- add a small preflight script that warns when starting dev compose if a venv folder is detected inside `backend/`.
