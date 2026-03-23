# cTrader OpenAPI Implementation Guide

> **Project:** AgentFinance  
> **Purpose:** Enable automated trading actions via cTrader OpenAPI  
> **Account:** Pepperstone Demo (Account #5249494) | cTrader ID: vince6699me  
> **Last Updated:** 2026-03-20

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Authentication](#3-authentication)
4. [Account Management](#4-account-management)
5. [Market Data](#5-market-data)
6. [Trading Operations](#6-trading-operations)
7. [Real-time Streaming](#7-real-time-streaming)
8. [Implementation Examples](#8-implementation-examples)
9. [Error Handling](#9-error-handling)
10. [Rate Limits & Best Practices](#10-rate-limits--best-practices)

---

## 1. Overview

### What is cTrader OpenAPI?

cTrader OpenAPI provides programmatic access to:
- **Account Management** — View balances, positions, orders
- **Market Data** — Real-time prices, historical candles
- **Trading Operations** — Place, modify, close orders
- **Webhooks** — Trade confirmations, margin alerts

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  AgentFinance   │────▶│  cTrader API    │────▶│  Pepperstone    │
│    Agents       │     │  (OAuth + TCP)   │     │    Broker       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Intelligence          ProtoOA Messages         Demo/Live
   & Strategy            (Protobuf/JSON)          Account
```

### Environment Endpoints

| Environment | Host | Port | Protocol |
|-------------|------|------|----------|
| **Demo** | demo.ctraderapi.com | 5035 | TCP/Protobuf |
| **Demo** | demo.ctraderapi.com | 5036 | TCP/JSON |
| **Demo** | wss://demo.ctraderapi.com | 5035 | WebSocket |
| **Live** | live.ctraderapi.com | 5035 | TCP/Protobuf |
| **Live** | live.ctraderapi.com | 5036 | TCP/JSON |
| **Live** | wss://live.ctraderapi.com | 5035 | WebSocket |

### Your Account Details

| Field | Value |
|-------|-------|
| **Account Number** | 5249494 |
| **Broker** | Pepperstone |
| **Server** | cTrader DEMO |
| **Account ID** | 46729678 |
| **Leverage** | 1:400 |
| **Currency** | USD |
| **Balance** | $10,000.00 |

---

## 2. Prerequisites

### Required Components

1. **cTrader ID** — Registered at [ctid.novaglobal.io](https://ctid.novaglobal.io)
2. **Application Registration** — App created at [connect.spotware.com/apps](https://connect.spotware.com/apps)
3. **Client ID** — From your registered application
4. **Client Secret** — From your registered application
5. **Access Token** — Obtained via OAuth flow

### Application Setup

1. Go to [connect.spotware.com/apps](https://connect.spotware.com/apps)
2. Click **"Add New Application"**
3. Configure:
   - **Name**: AgentFinance Trading
   - **Redirect URI**: `http://localhost:8080/callback`
   - **Application Usages**: ✅ Access own account information | ✅ Trading for own purpose
   - **Allowed Grant Types**: Check all options
   - **Scope**: `trading` (full access)
4. Wait for approval (typically 24-48 hours)
5. Copy **Client ID** and **Client Secret**

### Docker CLI (Alternative to SDK)

The `ghcr.io/spotware/ctrader-console` Docker image provides CLI access:

```bash
# List accounts
docker run --rm -v /tmp/ctrader-pwd.txt:/pwd.txt:ro \
  ghcr.io/spotware/ctrader-console:latest \
  accounts --ctid vince6699me --pwd-file /pwd.txt

# Get symbols for account
docker run --rm -v /tmp/ctrader-pwd.txt:/pwd.txt:ro \
  ghcr.io/spotware/ctrader-console:latest \
  symbols --ctid vince6699me --pwd-file /pwd.txt --account 5249494
```

---

## 3. Authentication

### OAuth 2.0 Flow

#### Step 1: Authorization Request

Redirect user to authorization URL:

```
https://id.ctrader.com/my/settings/openapi/grantingaccess/
?client_id=YOUR_CLIENT_ID
&redirect_uri=YOUR_REDIRECT_URI
&scope=trading
&product=web
```

#### Step 2: Exchange Code for Token

After user grants permission, exchange the `code` for tokens:

```bash
curl -X GET 'https://openapi.ctrader.com/apps/token
?grant_type=authorization_code
&code=AUTH_CODE
&redirect_uri=YOUR_REDIRECT_URI
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET'
-H 'Accept: application/json'
```

#### Response

```json
{
  "accessToken": "eyJhbGci...",
  "refreshToken": "rt_abc123...",
  "expiresIn": 2592000,
  "tokenType": "bearer"
}
```

#### Step 3: Refresh Token

```bash
curl -X GET 'https://openapi.ctrader.com/apps/token
?grant_type=refresh_token
&refresh_token=REFRESH_TOKEN
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET'
```

### TCP Protocol Authentication

After establishing TCP connection, send authentication messages:

#### 1. Application Authentication

```protobuf
ProtoOAApplicationAuthReq {
  clientId: "YOUR_CLIENT_ID"
  clientSecret: "YOUR_CLIENT_SECRET"
}
```

#### 2. Get Account List

```protobuf
ProtoOAGetAccountListByAccessTokenReq {
  accessToken: "ACCESS_TOKEN"
}
```

Response contains `ctidTraderAccountId` values.

#### 3. Account Authentication

```protobuf
ProtoOAAccountAuthReq {
  ctidTraderAccountId: 46729678
  accessToken: "ACCESS_TOKEN"
}
```

---

## 4. Account Management

### Get Account Information

```protobuf
ProtoOAGetAccountInfoReq {
  ctidTraderAccountId: 46729678
}
```

**Response Fields:**
| Field | Description |
|-------|-------------|
| `balance` | Account balance |
| `equity` | Current equity |
| `usedMargin` | Margin in use |
| `freeMargin` | Available margin |
| `marginLevel` | Margin level percentage |
| `unrealizedPL` | Floating P/L |

### Get Account Summary

```protobuf
ProtoOAGetAccountSummaryReq {
  ctidTraderAccountId: 46729678
}
```

### Get All Positions

```protobuf
ProtoOAGetPositionsReq {
  ctidTraderAccountId: 46729678
}
```

**Position Response:**
```json
{
  "positionId": 123456789,
  "symbolId": 1,
  "symbolName": "EURUSD",
  "tradeSide": "BUY",
  "volume": 100000,
  "priceOpen": 1.0850,
  "priceCurrent": 1.0860,
  "profitLoss": 100.00,
  "commission": -2.00,
  "swap": -0.50
}
```

### Get Pending Orders

```protobuf
ProtoOAGetOrdersReq {
  ctidTraderAccountId: 46729678
}
```

### Get Historical Trades

```protobuf
ProtoOAGetTradesHistoryReq {
  ctidTraderAccountId: 46729678
  fromTimestamp: 1700000000000
  toTimestamp: 1700100000000
}
```

---

## 5. Market Data

### Get Symbols List

```protobuf
ProtoOASymbolsListReq {
  ctidTraderAccountId: 46729678
}
```

**Common Symbol IDs:**
| Symbol | SymbolId | Category |
|--------|----------|----------|
| EURUSD | 1 | Forex Major |
| GBPUSD | 2 | Forex Major |
| USDJPY | 3 | Forex Major |
| XAUUSD | 4 | Metals |
| BTCUSD | 5 | Crypto |

### Get Symbol Details

```protobuf
ProtoOASymbolReq {
  ctidTraderAccountId: 46729678
  symbolId: 1
}
```

**Response:**
```json
{
  "symbolId": 1,
  "symbolName": "EURUSD",
  "description": "Euro vs US Dollar",
  "category": "Forex",
  "digits": 5,
  "pipSize": 0.0001,
  "tradeEnabled": true,
  "maxVolume": 100000000,
  "minVolume": 1000,
  "volumeStep": 1000
}
```

### Get Price History (OHLC)

```protobuf
ProtoOAGetTrendbarsReq {
  ctidTraderAccountId: 46729678
  symbolId: 1
  period: "m1"  // m1, m5, h1, h4, d1
  fromTimestamp: 1700000000000
  toTimestamp: 1700100000000
}
```

**Period Codes:**
| Code | Timeframe |
|------|-----------|
| t1-t10000 | Tick intervals |
| m1-m45 | Minute candles |
| h1-h12 | Hour candles |
| D1-D3 | Daily candles |
| W1 | Weekly |
| Month1 | Monthly |

### Subscribe to Price Updates

```protobuf
ProtoOASubscribeSpotsReq {
  ctidTraderAccountId: 46729678
  symbolId: [1, 2, 3]  // Array of symbol IDs
}
```

**Price Update Event:**
```json
{
  "type": "ProtoOASpotEvent",
  "symbolId": 1,
  "bid": 1.08520,
  "ask": 1.08523,
  "timestamp": 1700000000000
}
```

---

## 6. Trading Operations

### Order Types

| Type | Code | Description |
|------|------|-------------|
| Market | `MARKET` | Execute immediately at current price |
| Limit | `LIMIT` | Execute at specified price or better |
| Stop | `STOP` | Execute when price reaches level |
| Stop Loss | `STOP_LOSS` | Close position at loss limit |
| Take Profit | `TAKE_PROFIT` | Close position at profit target |

### Trade Sides

| Side | Code | Description |
|------|------|-------------|
| Buy | `BUY` | Long position |
| Sell | `SELL` | Short position |

### Place New Order

```protobuf
ProtoOANewOrderReq {
  ctidTraderAccountId: 46729678
  symbolId: 1                    // EURUSD
  orderType: MARKET
  tradeSide: BUY
  volume: 10000                  // 0.10 lots (volume × 100000)
  clientOrderId: "order_001"
  // Optional:
  // stopLoss: 1.0800
  // takeProfit: 1.0900
  // price: 1.0850              // For limit orders
}
```

**Volume Calculation:**
- `1000` = 0.01 lots (1,000 units)
- `10000` = 0.10 lots (10,000 units)
- `100000` = 1.00 lots (100,000 units)

**Response:**
```json
{
  "clientOrderId": "order_001",
  "orderId": 987654321,
  "status": "ACCEPTED",
  "fillPrice": 1.08523,
  "fillVolume": 10000
}
```

### Place Limit Order

```protobuf
ProtoOANewOrderReq {
  ctidTraderAccountId: 46729678
  symbolId: 1
  orderType: LIMIT
  tradeSide: BUY
  volume: 10000
  price: 1.0800                 // Buy limit
  clientOrderId: "limit_001"
}
```

### Modify Order

```protobuf
ProtoOAAmendOrderReq {
  ctidTraderAccountId: 46729678
  orderId: 987654321
  price: 1.0810                 // New price
  volume: 15000                 // New volume
  // or for SL/TP:
  // stopLoss: 1.0750
  // takeProfit: 1.0900
}
```

### Modify Position SL/TP

```protobuf
ProtoOAAmendPositionSLTPReq {
  ctidTraderAccountId: 46729678
  positionId: 123456789
  stopLoss: 1.0800
  takeProfit: 1.0900
}
```

### Close Position

**Full Close:**
```protobuf
ProtoOAClosePositionReq {
  ctidTraderAccountId: 46729678
  positionId: 123456789
  volume: 10000                 // Full volume
}
```

**Partial Close:**
```protobuf
ProtoOAClosePositionReq {
  ctidTraderAccountId: 46729678
  positionId: 123456789
  volume: 5000                  // Half position
}
```

### Cancel Pending Order

```protobuf
ProtoOACancelOrderReq {
  ctidTraderAccountId: 46729678
  orderId: 987654321
}
```

### Close by Hedge

```protobuf
ProtoOAClosePositionReq {
  ctidTraderAccountId: 46729678
  positionId: 123456789
  volume: 10000
  closeByAccountId: 46729678     // Same account = hedge
}
```

---

## 7. Real-time Streaming

### WebSocket Connection

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('wss://demo.ctraderapi.com:5035', {
  headers: {
    'Authorization': 'Bearer ACCESS_TOKEN'
  }
});

ws.on('open', () => {
  console.log('Connected to cTrader WebSocket');
  
  // Application auth
  ws.send(JSON.stringify({
    type: 'ProtoOAApplicationAuthReq',
    clientId: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET'
  }));
});

ws.on('message', (data) => {
  const message = JSON.parse(data);
  handleMessage(message);
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
});
```

### Subscribe to Updates

```javascript
// After account authentication, subscribe to:

// 1. Account updates
ws.send(JSON.stringify({
  type: 'ProtoOAGetAccountInfoReq',
  ctidTraderAccountId: 46729678
}));

// 2. Positions updates
ws.send(JSON.stringify({
  type: 'ProtoOAGetPositionsReq',
  ctidTraderAccountId: 46729678
}));

// 3. Price updates
ws.send(JSON.stringify({
  type: 'ProtoOASubscribeSpotsReq',
  ctidTraderAccountId: 46729678,
  symbolId: [1, 2, 3]
}));
```

### Event Types

| Event | Description |
|-------|-------------|
| `ProtoOASpotEvent` | Price tick update |
| `ProtoOAExecutionEvent` | Order filled/executed |
| `ProtoOAPositionUpdateEvent` | Position modified |
| `ProtoOAMarginChangedEvent` | Margin level changed |
| `ProtoOAOrderExecutedEvent` | Pending order triggered |
| `ProtoOAOrderDeletedEvent` | Order cancelled |

---

## 8. Implementation Examples

### Python — Full Trading Client

```python
import asyncio
from ctrader_open_api import Client, TcpProtocol, EndPoints
from ctrader_open_api.messages import (
    ProtoOAApplicationAuthReq,
    ProtoOAAccountAuthReq,
    ProtoOANewOrderReq,
    ProtoOAGetAccountInfoReq,
    ProtoOAGetPositionsReq
)

class cTraderClient:
    def __init__(self, client_id, client_secret, access_token, account_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.account_id = account_id
        self.client = None
        
    def connect(self):
        host = EndPoints.PROTOBUF_DEMO_HOST
        port = EndPoints.PROTOBUF_PORT
        self.client = Client(host, port, TcpProtocol)
        
        self.client.startService()
        
        # Authenticate application
        app_auth = ProtoOAApplicationAuthReq()
        app_auth.clientId = self.client_id
        app_auth.clientSecret = self.client_secret
        self.client.send(app_auth)
        
    def on_message(self, client, message):
        msg_type = type(message).__name__
        
        if msg_type == 'ProtoOAApplicationAuthRes':
            # Now authenticate account
            acc_auth = ProtoOAAccountAuthReq()
            acc_auth.ctidTraderAccountId = self.account_id
            acc_auth.accessToken = self.access_token
            self.client.send(acc_auth)
            
        elif msg_type == 'ProtoOAAccountAuthRes':
            print("Authenticated successfully!")
            self.get_account_info()
            
        elif msg_type == 'ProtoOAGetAccountInfoRes':
            print(f"Balance: {message.balance}")
            print(f"Equity: {message.equity}")
            print(f"Margin Level: {message.marginLevel}")
            
        elif msg_type == 'ProtoOANewOrderRes':
            print(f"Order placed: {message.orderId}")
            
    def place_order(self, symbol_id, side, volume, order_type='MARKET',
                    stop_loss=None, take_profit=None):
        order = ProtoOANewOrderReq()
        order.ctidTraderAccountId = self.account_id
        order.symbolId = symbol_id
        order.tradeSide = side
        order.volume = volume
        order.orderType = order_type
        
        if stop_loss:
            order.stopLoss = stop_loss
        if take_profit:
            order.takeProfit = take_profit
            
        self.client.send(order)
        
    def get_account_info(self):
        req = ProtoOAGetAccountInfoReq()
        req.ctidTraderAccountId = self.account_id
        self.client.send(req)
        
    def get_positions(self):
        req = ProtoOAGetPositionsReq()
        req.ctidTraderAccountId = self.account_id
        self.client.send(req)

# Usage
client = cTraderClient(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    access_token='ACCESS_TOKEN',
    account_id=46729678
)
client.connect()

# Place a BUY order on EURUSD
client.place_order(
    symbol_id=1,
    side='BUY',
    volume=10000,
    stop_loss=1.0800,
    take_profit=1.0900
)
```

### Node.js — WebSocket Trading

```javascript
const WebSocket = require('ws');

class cTraderWS {
    constructor(config) {
        this.clientId = config.clientId;
        this.clientSecret = config.clientSecret;
        this.accessToken = config.accessToken;
        this.accountId = config.accountId;
        this.ws = null;
        this.authenticated = false;
    }

    connect() {
        this.ws = new WebSocket('wss://demo.ctraderapi.com:5035', {
            perMessageDeflate: false
        });

        this.ws.on('open', () => this.onOpen());
        this.ws.on('message', (data) => this.onMessage(data));
        this.ws.on('error', (err) => this.onError(err));
        this.ws.on('close', () => this.onClose());
    }

    onOpen() {
        console.log('Connected');
        // Application auth
        this.send({
            type: 'ProtoOAApplicationAuthReq',
            clientId: this.clientId,
            clientSecret: this.clientSecret
        });
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    onMessage(data) {
        const msg = JSON.parse(data);
        const type = msg.type;

        switch (type) {
            case 'ProtoOAApplicationAuthRes':
                console.log('App authenticated');
                // Account auth
                this.send({
                    type: 'ProtoOAAccountAuthReq',
                    ctidTraderAccountId: this.accountId,
                    accessToken: this.accessToken
                });
                break;

            case 'ProtoOAAccountAuthRes':
                this.authenticated = true;
                console.log('Account authenticated');
                this.subscribe();
                break;

            case 'ProtoOASpotEvent':
                console.log(`Price: ${msg.bid}/${msg.ask}`);
                break;

            case 'ProtoOAExecutionEvent':
                console.log(`Order filled: ${msg.orderId}`);
                break;
        }
    }

    subscribe() {
        // Subscribe to positions
        this.send({
            type: 'ProtoOAGetPositionsReq',
            ctidTraderAccountId: this.accountId
        });

        // Subscribe to prices
        this.send({
            type: 'ProtoOASubscribeSpotsReq',
            ctidTraderAccountId: this.accountId,
            symbolId: [1, 2, 3]  // EURUSD, GBPUSD, USDJPY
        });
    }

    placeOrder(order) {
        this.send({
            type: 'ProtoOANewOrderReq',
            ctidTraderAccountId: this.accountId,
            symbolId: order.symbolId,
            orderType: order.orderType || 'MARKET',
            tradeSide: order.side,
            volume: order.volume,
            stopLoss: order.stopLoss,
            takeProfit: order.takeProfit,
            clientOrderId: `order_${Date.now()}`
        });
    }

    closePosition(positionId, volume) {
        this.send({
            type: 'ProtoOAClosePositionReq',
            ctidTraderAccountId: this.accountId,
            positionId: positionId,
            volume: volume
        });
    }
}

// Usage
const trader = new cTraderWS({
    clientId: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET',
    accessToken: 'ACCESS_TOKEN',
    accountId: 46729678
});

trader.connect();

// Place order after connection
setTimeout(() => {
    trader.placeOrder({
        symbolId: 1,  // EURUSD
        side: 'BUY',
        volume: 10000,
        stopLoss: 1.0800,
        takeProfit: 1.0900
    });
}, 2000);
```

### cTrader CLI Docker (Quick Commands)

```bash
# Create password file
echo -n 'YOUR_PASSWORD' > /tmp/ctrader-pwd.txt
chmod 600 /tmp/ctrader-pwd.txt

# List accounts
docker run --rm -v /tmp/ctrader-pwd.txt:/pwd.txt:ro \
  ghcr.io/spotware/ctrader-console:latest \
  accounts --ctid vince6699me --pwd-file /pwd.txt

# List symbols
docker run --rm -v /tmp/ctrader-pwd.txt:/pwd.txt:ro \
  ghcr.io/spotware/ctrader-console:latest \
  symbols --ctid vince6699me --pwd-file /pwd.txt --account 5249494

# Run backtest
docker run --rm -v /tmp/ctrader-pwd.txt:/pwd.txt:ro \
  ghcr.io/spotware/ctrader-console:latest \
  backtest mybot.algo --start="01/01/2025 00:00" --end="01/03/2025 00:00" \
  --ctid vince6699me --pwd-file /pwd.txt --account 5249494 \
  --symbol EURUSD --period h1 --data-mode m1
```

---

## 9. Error Handling

### Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| `INVALID_CREDENTIALS` | Invalid ctid or password | Verify credentials, disable 2FA |
| `AUTH_FAILED` | Authentication failed | Check tokens, re-authenticate |
| `INSUFFICIENT_MARGIN` | Not enough margin | Reduce position size |
| `INVALID_VOLUME` | Volume too small/large | Check min/max limits |
| `MARKET_CLOSED` | Market is closed | Check trading hours |
| `INVALID_SYMBOL` | Symbol not found | Verify symbol ID |
| `CONNECTION_LOST` | Connection dropped | Implement reconnection logic |

### Error Handling Example (Python)

```python
import time
from ctrader_open_api.errors import (
    AuthenticationError,
    MarginError,
    OrderError
)

def safe_place_order(client, order_params, max_retries=3):
    for attempt in range(max_retries):
        try:
            client.place_order(**order_params)
            return {"success": True}
            
        except AuthenticationError as e:
            print(f"Auth error: {e}")
            client.reauthenticate()
            
        except MarginError as e:
            print(f"Margin error: {e}")
            return {"success": False, "error": "INSUFFICIENT_MARGIN"}
            
        except OrderError as e:
            print(f"Order error: {e}")
            return {"success": False, "error": str(e)}
            
        except ConnectionError as e:
            print(f"Connection lost: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
            client.reconnect()
            
    return {"success": False, "error": "MAX_RETRIES_EXCEEDED"}
```

### Reconnection Logic

```python
import asyncio

class ReconnectingClient:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
        
    async def connect(self):
        while True:
            try:
                self.client = await create_client(self.config)
                await self.client.connect()
                self.reconnect_delay = 1  # Reset on success
                
            except ConnectionError:
                print(f"Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_reconnect_delay
                )
```

---

## 10. Rate Limits & Best Practices

### Rate Limits

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Non-historical data | 50 requests | 1 second |
| Historical data | 5 requests | 1 second |
| Order operations | 10 requests | 1 second |

### Best Practices

1. **Reuse Connections**
   - Maintain persistent WebSocket/TCP connections
   - Don't reconnect for every request

2. **Batch Requests**
   - Subscribe to multiple symbols in single request
   - Use list endpoints vs individual lookups

3. **Handle Disconnections**
   ```python
   # Implement heartbeat
   async def heartbeat(ws, interval=30):
       while True:
           await asyncio.sleep(interval)
           if ws.connected:
               ws.send_ping()
   ```

4. **Secure Storage**
   ```python
   # Never hardcode credentials
   import os
   CLIENT_ID = os.environ['CTRADER_CLIENT_ID']
   CLIENT_SECRET = os.environ['CTRADER_CLIENT_SECRET']
   ```

5. **Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger('ctrader')
   
   logger.info(f"Order placed: {order_id}")
   logger.error(f"Trade failed: {error}")
   ```

6. **Test Thoroughly**
   - Always test with demo account first
   - Verify order fills before live trading
   - Implement paper trading mode

---

## Quick Reference Card

### Common Symbol IDs

| Symbol | ID |
|--------|-----|
| EURUSD | 1 |
| GBPUSD | 2 |
| USDJPY | 3 |
| XAUUSD | 4 |
| BTCUSD | 5 |

### Order Types

| Type | Use Case |
|------|----------|
| `MARKET` | Immediate execution |
| `LIMIT` | Buy/sell at better price |
| `STOP` | Enter on breakout |

### Message Flow

```
1. Connect to endpoint
2. Send ProtoOAApplicationAuthReq
3. Send ProtoOAAccountAuthReq
4. Receive ProtoOAAccountAuthRes
5. Send trading/market data requests
6. Receive streaming updates
```

---

## Next Steps

1. **Register Application** at [connect.spotware.com/apps](https://connect.spotware.com/apps)
2. **Obtain OAuth Token** via authorization flow
3. **Test with Docker CLI** — `docker run ghcr.io/spotware/ctrader-console:latest`
4. **Implement Trading Client** — Use Python or Node.js examples above
5. **Connect to AgentFinance** — Integrate with n8n workflows for automation

---

*Document Version: 1.0*  
*Compatible with: cTrader OpenAPI v2*
