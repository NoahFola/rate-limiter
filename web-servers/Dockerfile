# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (this layer gets cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the app code
COPY app.py .
COPY src/ src/

# Default port; Render overrides this with its own PORT variable
ENV PORT=5000
EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:${PORT} --workers 2 app:app