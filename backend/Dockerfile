

stage-1
RUN apt-get update && apt-get install -y --no-install-recommends supervisor libpq5 && rm -rf /var/lib/apt/lists/*
8s
Processing triggers for libc-bin (2.41-12) ...

builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git
12s
Processing triggers for libc-bin (2.41-12) ...

stage-1
RUN addgroup --system app && adduser --system --group app
227ms

builder
COPY requirements.txt .
60ms

builder
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels     --index-url https://download.pytorch.org/whl/cpu     torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0
10s
Saved ./wheels/urllib3-1.26.13-py2.py3-none-any.whl

builder
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt
1m 20s
Saved ./wheels/wcwidth-0.2.14-py2.py3-none-any.whl

stage-1
COPY --from=builder /usr/src/app/wheels /wheels
5s

stage-1
RUN pip install --no-cache --no-index --find-links=/wheels /wheels/*
15s
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
Dockerfile:46
-------------------
44 |     # Install the wheels. Using --no-index ensures we ONLY install from our local wheels,
45 |     # preventing any accidental re-downloads.
46 | >>> RUN pip install --no-cache --no-index --find-links=/wheels /wheels/*
47 |
48 |     # Copy the application source code
-------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c pip install --no-cache --no-index --find-links=/wheels /wheels/*" did not complete successfully: exit code: 1
