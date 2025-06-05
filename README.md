# Judexia Application

This project requires **Python 3.10+**.

Install dependencies with:

```bash
pip install -r requirements.txt
```

Set the following environment variables before running:

- `DATABASE_URL` – PostgreSQL connection string
- `OPENAI_API_KEY` – API key for OpenAI services

Run locally with:

```bash
python app.py
```

For production, you can use Gunicorn:

```bash
gunicorn app:app
```
