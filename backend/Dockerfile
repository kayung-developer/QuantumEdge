# --- Stage 1: Build Stage ---
# This stage's only purpose is to compile dependencies and create wheels.
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# Install build dependencies, including git
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git

# Copy only the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# --- CRITICAL OPTIMIZATION ---
# Install a specific, CPU-only version of PyTorch to drastically reduce size.
# We also pre-install it before the main requirements.txt to have more control.
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0

# Now, install the rest of the requirements
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Stage 2: Final Production Stage ---
# This stage will be as minimal as possible.
FROM python:3.11-slim

WORKDIR /app

# Install only the necessary runtime dependencies.
# 'supervisor' for process management and 'libpq5' for the PostgreSQL client.
RUN apt-get update && apt-get install -y --no-install-recommends supervisor libpq5 && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy the pre-built Python packages (wheels) from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels
# Install the wheels. Using --no-index ensures we ONLY install from our local wheels,
# preventing any accidental re-downloads.
RUN pip install --no-cache --no-index --find-links=/wheels /wheels/*

# Copy the application source code
COPY . /app

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Change ownership of the app directory
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to start supervisord, which runs our app
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
