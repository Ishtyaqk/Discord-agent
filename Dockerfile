FROM python:3.11-slim

# 1. Install system utilities and build tools
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

# 2. Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# 3. Clone and pre-install Hermes Agent at build time
RUN git clone --depth 1 https://github.com/NousResearch/hermes-agent.git /app
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache -e "." yt-dlp

# 4. Hugging Face non-root user (UID 1000) setup
RUN useradd -m -u 1000 user
ENV HOME=/home/user
ENV HERMES_HOME=/home/user/.hermes
RUN mkdir -p /home/user/.hermes /home/user/app && chown -R user:user /home/user /app

USER user
WORKDIR /home/user/app

# 5. Copy configuration and start script
COPY --chown=user:user SOUL.md /home/user/.hermes/SOUL.md
COPY --chown=user:user config.yaml /home/user/.hermes/config.yaml
COPY --chown=user:user skills /home/user/.hermes/skills
COPY --chown=user:user start.py /home/user/app/start.py

ENV PYTHONUNBUFFERED=1
EXPOSE 7860

# 6. Launch pre-built application
CMD ["python", "start.py"]
