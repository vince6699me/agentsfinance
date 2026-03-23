# cTrader Docker REST API Server

**Architecture:** HTTP REST Bridge → cTrader OpenAPI Protobuf TCP

```
AgentFinance (Python)
       ↓ HTTP REST
ctrader-api Docker container  ←  ctrader-open-api (Twisted/Protobuf)
       ↓ TCP/Protobuf                     
  demo.ctraderapi.com:5035  or  live.ctraderapi.com:5035
```

## Why Docker?

cTrader's OpenAPI uses a proprietary **Protobuf over TCP** protocol. The official `ctrader-open-api` Python package requires Twisted's async reactor. Running it in Docker provides:

- **Isolation**: The Twisted reactor runs in its own container/process
- **Simplicity**: REST/HTTP from your code instead of Twisted callbacks
- **Portability**: Works on any platform with Docker (Linux, macOS, Windows/WSL)
- **Swagger UI**: Built-in API documentation at `/docs`
- **Health checks**: Docker monitors the API server health

## Quick Start

### 1. Get cTrader API Credentials

1. Go to [Spotware Connect](https://connect.spotware.com/apps)
2. Create a new application
3. Get your **Client ID** and **Client Secret**
4. Get your **Access Token** from the cTrader platform (Pepperstone)
   - Pepperstone Demo: https://pepperstone.com/en/trading-platforms/ctrader
   - Demo Account: **#46729678**

### 2. Configure Credentials

```bash
# From the ctrader/ directory
cd /home/greywolf/Documents/AgentFinance/agentfinance/ctrader

# Copy the template
cp .env.example ../.env

# Edit with your credentials
nano ../.env
```

### 3. Start the Container

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up --build -d

# Check logs
docker compose logs -f ctrader-api

# Stop
docker compose down
```

### 4. Verify

```bash
# Health check
curl http://localhost:9009/health

# Get account status
curl http://localhost:9009/status

# List positions
curl http://localhost:9009/positions

# Swagger docs
open http://localhost:9009/docs
```

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/status` | Connection + account status |
| `GET` | `/symbols` | List all symbols |
| `GET` | `/positions` | List open positions |
| `GET` | `/orders` | List pending orders |
| `GET` | `/account` | Account summary |
| `POST` | `/orders/market` | Place market order |
| `POST` | `/orders/limit` | Place limit order |
| `POST` | `/orders/stop` | Place stop order |
| `POST` | `/orders/close` | Close position |
| `POST` | `/orders/cancel` | Cancel pending order |
| `POST` | `/orders/amend` | Amend position SL/TP |
| `POST` | `/orders/close-all` | Close all positions |
| `POST` | `/trendbars` | Get historical candles |

### Example: Place a Market Order

```bash
curl -X POST http://localhost:9009/orders/market \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "side": "BUY",
    "volume": 0.10,
    "stopLoss": 1.0756,
    "takeProfit": 1.0890
  }'
```

## Using the REST Client in AgentFinance

### Option 1: Direct HTTP (any Python code)

```python
import requests

resp = requests.post("http://localhost:9009/orders/market", json={
    "symbol": "EURUSD",
    "side": "BUY",
    "volume": 0.10,
    "stopLoss": 1.0756,
    "takeProfit": 1.0890,
})
print(resp.json())
```

### Option 2: REST Client Module

```python
import sys
sys.path.insert(0, "ctrader/rest_client")
from rest_client import CTraderRESTClient

client = CTraderRESTClient(base_url="http://localhost:9009")
client.connect()
positions = client.get_positions()
result = client.place_market_order("EURUSD", "BUY", 0.10, sl=1.0756, tp=1.0890)
```

## Switching Between Direct TCP and REST

`live_executor.py` and `smc_pipeline.py` automatically use:
- **Direct TCP** if `CTRADER_CLIENT_ID` etc. are set and `ctrader-open-api` is installed
- **REST** if `CTRADER_REST_URL` is set
- **Simulation** if neither is available

Set in `.env`:
```bash
# For direct TCP (no Docker):
CTRADER_CLIENT_ID=your_client_id
CTRADER_CLIENT_SECRET=your_client_secret
CTRADER_ACCESS_TOKEN=your_access_token

# For REST via Docker:
CTRADER_REST_URL=http://localhost:9009
```

## Volumes

The docker-compose mounts `../.env` to `/app/.env` so credentials are loaded automatically.

## Troubleshooting

### "Connection refused" on port 9009
```bash
# Check if container is running
docker ps | grep ctrader

# Check logs for errors
docker compose logs ctrader-api

# Restart the container
docker compose restart ctrader-api
```

### "SIMULATION mode" even with credentials
The REST API falls back to simulation if the cTrader credentials are missing or invalid. Make sure:
```bash
# Verify credentials in .env
grep -E "CTRADER_CLIENT_ID|CTRADER_ACCESS_TOKEN" ../.env
```

### Container won't start
```bash
# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up
```

## Architecture Details

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Container                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ctrader_api_server.py (FastAPI + Uvicorn)          │   │
│  │  - REST endpoints                                    │   │
│  │  - Swagger UI (/docs)                                │   │
│  └──────────────────┬────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼────────────────────────────────────┐   │
│  │  CTraderBot (Twisted Client)                         │   │
│  │  - TCP/Protobuf connection                            │   │
│  │  - Callback-driven events                             │   │
│  │  - Auto-reconnect                                    │   │
│  └──────────────────┬────────────────────────────────────┘   │
│                     │ Protobuf/TCP                          │
│  demo.ctraderapi.com:5035  (or live)                       │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │ HTTP REST
┌────────────────────┴──────────────────────────────────────┐
│  AgentFinance (Python)                                     │
│  - live_executor.py (Agent 28)                            │
│  - smc_pipeline.py (SMC → Execution)                     │
│  - REST client (no Twisted needed!)                       │
└───────────────────────────────────────────────────────────┘
```
