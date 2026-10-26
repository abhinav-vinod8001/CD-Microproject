# Dockerfile for Malayalam Educational Compiler Web IDE
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5050

EXPOSE 5050

# Run with Gunicorn production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--timeout", "60", "app:app"]
