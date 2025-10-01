# syntax=docker/dockerfile:1

FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# OS deps kept minimal (add build-essential only if you compile native code)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps (CPU torch via extra index)
# Put only requirements first to leverage Docker layer cache
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r /app/requirements.txt

# Copy the app code
COPY app /app/app

# (Optional) create non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

EXPOSE 9999
ENV HOST=0.0.0.0 PORT=9999

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999"]
