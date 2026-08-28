FROM python:3.11-slim

# Install system tools, Node.js, and CLI utilities for Agent Reach
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ripgrep \
    ffmpeg \
    ca-certificates \
    gcc \
    g++ \
    make \
    nodejs \
    npm \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python packaging
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Clone Hermes Agent core
RUN git clone --depth 1 https://github.com/NousResearch/hermes-agent.git /app

# Install Hermes Agent dependencies and yt-dlp for video transcription
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache -e "." yt-dlp

# Create config directory and copy custom configs & Agent Reach skills
RUN mkdir -p /root/.hermes/skills
COPY SOUL.md /root/.hermes/SOUL.md
COPY config.yaml /root/.hermes/config.yaml
COPY skills /root/.hermes/skills
COPY start.py /app/start.py

ENV HERMES_HOME=/root/.hermes
ENV PYTHONUNBUFFERED=1

# Expose Render default port
EXPOSE 8080

# Start health check server & Hermes Gateway
CMD ["python", "start.py"]
