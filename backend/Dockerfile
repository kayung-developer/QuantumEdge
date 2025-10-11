# --- Stage 1: Build Stage ---
# Use a full Python image to build wheels, including packages that need compilation.
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Set env vars for a clean build environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build-essential for C extensions and libpq-dev for PostgreSQL adapter
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

# Copy requirements and build wheels for faster installation in the next stage
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Stage 2: Final Production Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install supervisord, the process manager that will run our services.
# Also install netcat, a useful utility for waiting for the database to be ready.
RUN apt-get update && apt-get install -y --no-install-recommends supervisor netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Create a non-root user for enhanced security
RUN addgroup --system app && adduser --system --group app

# Copy installed Python packages (wheels) from the build stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy the entire application source code
COPY . /app

# Copy the supervisord configuration file into the correct location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Change ownership of the entire /app directory to our non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# --- RAILWAY SPECIFIC CONFIGURATION ---
# Railway dynamically assigns a port and provides it via the PORT environment variable.
# We don't need to EXPOSE it, but we need to use it in our start command.
# The default port for web services on Railway is 8080 if not specified.

# The final command: Start supervisord. It will take care of starting all our processes.
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]