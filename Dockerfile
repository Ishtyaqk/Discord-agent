FROM ghcr.io/nousresearch/hermes-agent:latest

# Copy customized prompt and configuration into the container
COPY SOUL.md /opt/data/SOUL.md
COPY config.yaml /opt/data/config.yaml

# Run Hermes gateway continuously
CMD ["gateway", "run"]
