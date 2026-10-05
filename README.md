# ZTNA-SDP

Identity-centric Zero Trust Network Access broker using an SDP-inspired architecture.
Academic prototype by Jatin and Komal. This is a ZTNA/SDP-inspired prototype, not a production system.

## Setup (Windows PowerShell)
```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the printed key into `.env` after `SECRET_KEY=`. Never commit `.env`.

## Run the tests
```
cd backend
python -m pytest -q
```

## Team workflow
- Branches: `main` (releases only), `develop` (integration), `feature/<name>-<topic>`.
- Never commit directly to `develop` or `main`. Open a PR; the other person reviews and merges.
- Commit style: `feat`, `fix`, `test`, `docs`, `chore`.