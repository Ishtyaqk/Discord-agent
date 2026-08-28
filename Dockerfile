FROM python:3.11-slim

# Install system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ripgrep \
    ffmpeg \
    ca-certificates \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Clone Hermes Agent
RUN git clone --depth 1 https://github.com/NousResearch/hermes-agent.git /app

# Install Hermes Agent dependencies into virtualenv
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache -e "."

# Create config directory and copy custom configs
RUN mkdir -p /root/.hermes
COPY SOUL.md /root/.hermes/SOUL.md
COPY config.yaml /root/.hermes/config.yaml

ENV HERMES_HOME=/root/.hermes
ENV PYTHONUNBUFFERED=1

# Run the Hermes Gateway daemon
CMD ["hermes", "gateway", "run"]
