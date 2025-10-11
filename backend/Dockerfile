# --- Stage 1: Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- CRITICAL FIX: Install 'git' alongside other build tools ---
# This makes the 'git' command available for pip to install packages from GitHub.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git

# Copy requirements and build wheels for faster installation in the next stage
COPY requirements.txt .
# We will run the standard install here to see if the PyPI version works with the git fix
RUN pip install --no-cache-dir -r requirements.txt --target=/usr/src/app/packages

# --- Stage 2: Final Production Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install supervisord and netcat
RUN apt-get update && apt-get install -y --no-install-recommends supervisor netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy the installed Python packages from the build stage
COPY --from=builder /usr/src/app/packages /usr/local/lib/python3.11/site-packages

# Copy the application source code
COPY . /app

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Change ownership
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
