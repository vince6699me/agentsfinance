FROM python:3.11-bookworm

LABEL maintainer="AgentFinance v3"
LABEL description="cTrader REST API Server — bridges HTTP REST to cTrader OpenAPI Protobuf TCP"

WORKDIR /app

# Python dependencies (bookworm has gcc + libffi + openssl pre-installed)
COPY requirements.docker.txt /tmp/requirements.docker.txt
RUN pip install --no-cache-dir -r /tmp/requirements.docker.txt

# Copy application
COPY ctrader_api_server.py /app/
COPY .env.example /app/.env.template

EXPOSE 9009

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9009/health')" || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "ctrader_api_server:app", "--host", "0.0.0.0", "--port", "9009"]
