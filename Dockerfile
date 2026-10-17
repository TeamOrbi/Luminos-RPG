FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /add
copy requirements.txt .
run pip install --no-cache-dir -r requirements.txt
copy . .
run mkdir -p /app/data/ && useradd --create-home -uid 10001 luminos && chown -R luminos:luminos /app
USER luminos
EXPOSE 8000
CMD ["sh", "-c", "python -c 'from database import initialise; initialise()' && gunicorn --workers 2 --bind 0.0.0.0:${PORT:-8000} app:app"]