#!/usr/bin/env python3
"""
cTrader REST API Server — Docker Container
Bridges HTTP REST endpoints → cTrader OpenAPI Protobuf TCP protocol.

Run inside Docker:
    docker run -p 9009:9009 ctrader-api-server

Endpoints:
    GET  /health                    - Health check
    GET  /status                    - Connection + account status
    GET  /symbols                   - List all symbols
    GET  /positions                 - List open positions
    GET  /orders                    - List pending orders
    GET  /account                   - Account summary
    POST /orders/market             - Place market order
    POST /orders/limit              - Place limit order
    POST /orders/stop              - Place stop order
    POST /orders/close              - Close position
    POST /orders/cancel             - Cancel pending order
    POST /orders/amend              - Amend position SL/TP
    POST /orders/close-all          - Close all positions
    GET  /history                   - Get historical bars
    POST /trendbars                 - Get trendbars (candles)
"""

import os
import sys
import time
import logging
import threading
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from functools import partial

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from dotenv import load_dotenv

logger = logging.getLogger("ctrader-rest-server")

# ============================================================================
# AUTHENTICATION
# ============================================================================
# API key auth: /orders/*, /trendbars POST require X-API-Key header.
# GET /health, /status, /symbols, /positions, /orders, /account remain open.

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verify the X-API-Key header against REST_API_KEY in the environment.
    Returns the key on success. Raises 403 on failure.
    """
    required_key = os.getenv("REST_API_KEY", "")
    if not required_key:
        # Auth disabled if no key is configured — log warning
        logger.warning(
            "REST_API_KEY not set in environment — API authentication is DISABLED"
        )
        return "DISABLED"
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header. Pass: curl -H 'X-API-Key: YOUR_KEY' ...",
        )
    if api_key != required_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

load_dotenv()

# ============================================================================
# CTRADER OPENAPI (Twisted/Protobuf)
# ============================================================================

HAS_CTRADER = False
try:
    from twisted.internet import reactor
    from twisted.internet.task import deferLater
    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq,
        ProtoOAAccountAuthReq,
        ProtoOASymbolsListReq,
        ProtoOAGetPositionsReq,
        ProtoOAReconcileReq,
        ProtoOANewOrderReq,
        ProtoOAClosePositionReq,
        ProtoOAAmendPositionSLTPReq,
        ProtoOACancelOrderReq,
        ProtoOAGetTrendbarsReq,
        ProtoOAGetAccountInfoReq,
        ProtoOASubscribeSpotsReq,
        ProtoOAUnsubscribeSpotsReq,
        ProtoOAOrderType,
        ProtoOATradeSide,
        ProtoOAAccountAuthRes,
        ProtoOASymbolsListRes,
        ProtoOAExecutionEvent,
        ProtoOAOrderErrorEvent,
        ProtoOAReconcileRes,
        ProtoOASpotEvent,
        ProtoOAGetTrendbarsRes,
        ProtoOAMassCloseReq,
    )
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import (
        ProtoOAExecutionType,
        ProtoOATrendbarPeriod,
    )

    HAS_CTRADER = True
    logger.info("ctrader-open-api loaded successfully")
except ImportError:
    logger.warning(
        "ctrader-open-api not installed — REST API will run in SIMULATION mode"
    )
    HAS_CTRADER = False


# ============================================================================
# CTRADER BOT (Twisted TCP client with callbacks)
# ============================================================================


class CTraderBot:
    """
    Twisted-based cTrader OpenAPI client with callback-driven state.
    Runs inside the Docker container. Thread-safe interface for FastAPI.
    """

    def __init__(self):
        self.client_id = os.getenv("CTRADER_CLIENT_ID", "")
        self.client_secret = os.getenv("CTRADER_CLIENT_SECRET", "")
        self.access_token = os.getenv("CTRADER_ACCESS_TOKEN", "")
        self.account_id = int(os.getenv("CTRADER_ACCOUNT_ID", "46729678"))
        self.host = os.getenv("CTRADER_HOST", "demo").lower()

        self._client = None
        self._connected = False
        self._app_auth = False
        self._account_auth = False

        self.symbols: Dict[str, int] = {}
        self.symbols_by_id: Dict[int, str] = {}
        self.positions: List[Dict] = []
        self.pending_orders: List[Dict] = []
        self.account: Dict = {}

        self._pending_deferreds: Dict[int, Any] = {}
        self._order_results: Dict[str, Dict] = {}
        self._lock = threading.Lock()

        self._reconnect_delay = 5
        self._max_reconnect = 5
        self._reconnect_count = 0

    @property
    def is_connected(self) -> bool:
        return self._connected and self._app_auth and self._account_auth

    def connect(self):
        if not HAS_CTRADER:
            logger.warning(
                "ctrader-open-api not available — running in SIMULATION mode"
            )
            self._load_simulation()
            return

        if not all([self.client_id, self.client_secret, self.access_token]):
            logger.warning("Missing credentials — running in SIMULATION mode")
            self._load_simulation()
            return

        host = (
            EndPoints.PROTOBUF_LIVE_HOST
            if self.host == "live"
            else EndPoints.PROTOBUF_DEMO_HOST
        )
        logger.info(f"Connecting to {host}:{EndPoints.PROTOBUF_PORT}...")

        self._client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
        self._client.setConnectedCallback(self._on_connected)
        self._client.setDisconnectedCallback(self._on_disconnected)
        self._client.setMessageReceivedCallback(self._on_message)
        self._client.startService()

    def _load_simulation(self):
        self._connected = True
        self._app_auth = True
        self._account_auth = True
        symbols = [
            ("EURUSD", 1),
            ("GBPUSD", 2),
            ("USDJPY", 3),
            ("XAUUSD", 4),
            ("AUDUSD", 5),
            ("USDCAD", 6),
            ("NZDUSD", 7),
            ("EURGBP", 8),
            ("EURJPY", 9),
            ("GBPJPY", 10),
            ("XAGUSD", 11),
            ("USDCHF", 12),
            ("NAS100", 13),
            ("USOIL", 14),
        ]
        for name, sid in symbols:
            self.symbols[name] = sid
            self.symbols_by_id[sid] = name
        self.account = {
            "balance": 10500.00,
            "equity": 10427.50,
            "margin": 1248.30,
            "freeMargin": 9179.20,
            "marginLevel": 834.8,
            "openPositions": 0,
        }
        logger.info(f"Simulation mode: {len(self.symbols)} symbols loaded")

    def _on_connected(self, client):
        logger.info("TCP connected to cTrader")
        self._connected = True
        req = ProtoOAApplicationAuthReq()
        req.clientId = self.client_id
        req.clientSecret = self.client_secret
        client.send(req)

    def _on_disconnected(self, client, reason):
        logger.warning(f"Disconnected: {reason}")
        self._connected = False
        self._app_auth = False
        self._account_auth = False
        self._schedule_reconnect()

    def _schedule_reconnect(self):
        if self._reconnect_count < self._max_reconnect:
            self._reconnect_count += 1
            logger.info(
                f"Scheduling reconnect in {self._reconnect_delay}s (attempt {self._reconnect_count})"
            )
            reactor.callLater(self._reconnect_delay, self.connect)

    def _on_message(self, client, message):
        try:
            payload = message.payloadType

            if payload == ProtoOAApplicationAuthReq().payloadType:
                logger.info("Application authenticated")
                self._app_auth = True
                self._authenticate_account()

            elif payload == ProtoOAAccountAuthRes().payloadType:
                logger.info("Account authenticated")
                self._account_auth = True
                self._reconnect_count = 0
                self._request_symbols()

            elif payload == ProtoOASymbolsListRes().payloadType:
                self._handle_symbols(message)

            elif payload == ProtoOAReconcileRes().payloadType:
                self._handle_reconcile(message)

            elif payload == ProtoOAExecutionEvent().payloadType:
                self._handle_execution(message)

            elif payload == ProtoOAOrderErrorEvent().payloadType:
                self._handle_order_error(message)

            elif payload == ProtoOAGetTrendbarsRes().payloadType:
                self._handle_trendbars(message)

            elif payload == ProtoOAGetAccountInfoReq().payloadType:
                self._handle_account_info(message)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _authenticate_account(self):
        req = ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = self.account_id
        req.accessToken = self.access_token
        self._client.send(req)

    def _request_symbols(self):
        req = ProtoOASymbolsListReq()
        req.ctidTraderAccountId = self.account_id
        self._client.send(req)

    def _handle_symbols(self, message):
        response = Protobuf.extract(message)
        with self._lock:
            for sym in response.symbol:
                self.symbols[sym.symbolName] = sym.symbolId
                self.symbols_by_id[sym.symbolId] = sym.symbolName
        logger.info(f"Loaded {len(self.symbols)} symbols")
        self.refresh_positions()

    def _handle_reconcile(self, message):
        response = Protobuf.extract(message)
        with self._lock:
            self.positions = []
            for pos in response.position:
                self.positions.append(
                    {
                        "positionId": pos.positionId,
                        "symbolId": pos.symbolId,
                        "symbol": self.symbols_by_id.get(
                            pos.symbolId, str(pos.symbolId)
                        ),
                        "side": "BUY"
                        if pos.tradeSide == ProtoOATradeSide.Value("BUY")
                        else "SELL",
                        "volume": pos.volume / 100000.0,
                        "entryPrice": pos.entryPrice / 100000.0,
                        "currentPrice": pos.closePrice / 100000.0,
                        "pnl": pos.profit / 100.0,
                        "pnlPct": 0.0,
                        "stopLoss": pos.stopLoss / 100000.0 if pos.stopLoss else None,
                        "takeProfit": pos.takeProfit / 100000.0
                        if pos.takeProfit
                        else None,
                    }
                )
            self.pending_orders = []
            for order in response.order:
                self.pending_orders.append(
                    {
                        "orderId": order.orderId,
                        "symbolId": order.symbolId,
                        "symbol": self.symbols_by_id.get(
                            order.symbolId, str(order.symbolId)
                        ),
                        "side": "BUY"
                        if order.tradeSide == ProtoOATradeSide.Value("BUY")
                        else "SELL",
                        "orderType": ProtoOAOrderType.Name(order.orderType),
                        "volume": order.volume / 100000.0,
                        "price": order.limitPrice / 100000.0,
                        "stopPrice": order.stopPrice / 100000.0,
                        "stopLoss": order.stopLoss / 100000.0
                        if order.stopLoss
                        else None,
                        "takeProfit": order.takeProfit / 100000.0
                        if order.takeProfit
                        else None,
                    }
                )
        logger.info(
            f"Reconcile: {len(self.positions)} positions, {len(self.pending_orders)} orders"
        )

    def _handle_execution(self, message):
        response = Protobuf.extract(message)
        for exec_event in response.execution:
            order_id = exec_event.orderId or exec_event.positionId
            status = ProtoOAExecutionType.Name(exec_event.executionType)
            logger.info(f"Execution: {status} — Order/Position ID: {order_id}")
            with self._lock:
                self._order_results[str(order_id)] = {
                    "status": status,
                    "orderId": order_id,
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
        self.refresh_positions()

    def _handle_order_error(self, message):
        response = Protobuf.extract(message)
        for err in response.error:
            logger.error(f"Order error {err.errorCode}: {err.message}")

    def _handle_trendbars(self, message):
        response = Protobuf.extract(message)
        bars = []
        for bar in response.trendbar:
            bars.append(
                {
                    "timestamp": datetime.fromtimestamp(bar.from_, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "open": bar.open / 100000.0,
                    "high": bar.high / 100000.0,
                    "low": bar.low / 100000.0,
                    "close": bar.close / 100000.0,
                    "volume": bar.tickVolume,
                }
            )

    def _handle_account_info(self, message):
        response = Protobuf.extract(message)
        if hasattr(response, "account"):
            acc = response.account[0]
            with self._lock:
                self.account = {
                    "balance": acc.balance / 100.0,
                    "equity": acc.equity / 100.0,
                    "margin": acc.margin / 100.0,
                    "freeMargin": acc.freeMargin / 100.0,
                    "marginLevel": acc.marginLevel / 100.0,
                    "openPositions": acc.positionsCount,
                }

    def refresh_positions(self):
        if not self.is_connected:
            return
        req = ProtoOAReconcileReq()
        req.ctidTraderAccountId = self.account_id
        self._client.send(req)

    def _send_order(
        self,
        order_type: int,
        side: str,
        symbol_id: int,
        volume: float,
        price: float,
        sl: float = 0,
        tp: float = 0,
        order_id: int = 0,
        close_volume: float = 0,
    ) -> Dict:
        """
        Send order via Twisted. Returns immediately with order_id.
        Final status comes via _handle_execution callback.
        """
        trade_side = ProtoOATradeSide.Value(side.upper())
        vol_cl = int(volume * 100000)
        price_cl = int(price * 100000)
        sl_cl = int(sl * 100000) if sl else 0
        tp_cl = int(tp * 100000) if tp else 0

        if order_type == ProtoOAOrderType.Value("MARKET"):
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = symbol_id
            req.orderType = order_type
            req.tradeSide = trade_side
            req.volume = vol_cl
            req.stopLoss = sl_cl
            req.takeProfit = tp_cl
            req.comment = "AgentFinance"
            result = self._client.send(req)
            logger.info(
                f"Market order sent: {side} {volume}lots @ {price} SL={sl} TP={tp}"
            )
            return {"status": "PENDING", "symbolId": symbol_id, "volume": volume}

        elif order_type == ProtoOAOrderType.Value("LIMIT"):
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = symbol_id
            req.orderType = order_type
            req.tradeSide = trade_side
            req.volume = vol_cl
            req.limitPrice = price_cl
            req.stopLoss = sl_cl
            req.takeProfit = tp_cl
            req.comment = "AgentFinance"
            self._client.send(req)
            logger.info(
                f"Limit order sent: {side} {volume}lots @ {price} SL={sl} TP={tp}"
            )
            return {
                "status": "PENDING",
                "symbolId": symbol_id,
                "price": price,
                "volume": volume,
            }

        elif order_type == ProtoOAOrderType.Value("STOP"):
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = symbol_id
            req.orderType = order_type
            req.tradeSide = trade_side
            req.volume = vol_cl
            req.stopPrice = price_cl
            req.stopLoss = sl_cl
            req.takeProfit = tp_cl
            req.comment = "AgentFinance"
            self._client.send(req)
            logger.info(
                f"Stop order sent: {side} {volume}lots @ {price} SL={sl} TP={tp}"
            )
            return {
                "status": "PENDING",
                "symbolId": symbol_id,
                "price": price,
                "volume": volume,
            }

        elif close_volume > 0:
            req = ProtoOAClosePositionReq()
            req.ctidTraderAccountId = self.account_id
            req.positionId = order_id
            req.volume = int(close_volume * 100000)
            self._client.send(req)
            logger.info(f"Close request: position #{order_id} volume={close_volume}")
            return {"status": "CLOSING", "positionId": order_id, "volume": close_volume}

        elif order_id > 0 and close_volume == 0:
            # Amend SL/TP
            req = ProtoOAAmendPositionSLTPReq()
            req.ctidTraderAccountId = self.account_id
            req.positionId = order_id
            req.stopLoss = sl_cl
            req.takeProfit = tp_cl
            self._client.send(req)
            logger.info(f"Amend SL/TP: position #{order_id} SL={sl} TP={tp}")
            return {"status": "AMENDING", "positionId": order_id}

        return {"status": "ERROR", "message": "Unknown order type"}

    def close_all_positions(self) -> Dict:
        if not self.is_connected:
            return {"status": "ERROR", "message": "Not connected"}
        with self._lock:
            pos_ids = [p["positionId"] for p in self.positions]
        for pos_id in pos_ids:
            req = ProtoOAClosePositionReq()
            req.ctidTraderAccountId = self.account_id
            req.positionId = pos_id
            req.volume = 0  # Full close
            self._client.send(req)
        return {"status": "CLOSING_ALL", "count": len(pos_ids)}

    def cancel_order(self, order_id: int) -> Dict:
        if not self.is_connected:
            return {"status": "ERROR", "message": "Not connected"}
        req = ProtoOACancelOrderReq()
        req.ctidTraderAccountId = self.account_id
        req.orderId = order_id
        self._client.send(req)
        logger.info(f"Cancel order: #{order_id}")
        return {"status": "CANCELING", "orderId": order_id}

    def get_trendbars(
        self, symbol_id: int, period: str = "H1", count: int = 100
    ) -> List[Dict]:
        period_map = {
            "M1": ProtoOATrendbarPeriod.Value("MINUTE1"),
            "M5": ProtoOATrendbarPeriod.Value("MINUTE5"),
            "M15": ProtoOATrendbarPeriod.Value("MINUTE15"),
            "M30": ProtoOATrendbarPeriod.Value("MINUTE30"),
            "H1": ProtoOATrendbarPeriod.Value("HOUR1"),
            "H4": ProtoOATrendbarPeriod.Value("HOUR4"),
            "D1": ProtoOATrendbarPeriod.Value("DAY1"),
        }
        p = period_map.get(period.upper(), ProtoOATrendbarPeriod.Value("HOUR1"))
        req = ProtoOAGetTrendbarsReq()
        req.ctidTraderAccountId = self.account_id
        req.symbolId = symbol_id
        req.period = p
        req.style = 1
        self._client.send(req)
        return []  # Returned via callback

    def disconnect(self):
        if self._client:
            try:
                self._client.stopService()
            except Exception:
                pass


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Global bot instance (shared across requests)
_bot: Optional[CTraderBot] = None


def get_bot() -> CTraderBot:
    if _bot is None:
        raise HTTPException(503, "cTrader bot not initialized")
    return _bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bot
    logger.info("Starting cTrader REST API Server...")

    _bot = CTraderBot()

    if HAS_CTRADER:
        # Run Twisted reactor in a separate thread
        def run_reactor():
            reactor.run(installSignalHandlers=0)

        _reactor_thread = threading.Thread(target=run_reactor, daemon=True)
        _reactor_thread.start()
        logger.info("Twisted reactor started in background thread")

        # Give the bot time to connect
        for _ in range(30):
            await asyncio.sleep(0.5)
            if _bot.is_connected:
                logger.info("cTrader connected and authenticated!")
                break
        else:
            logger.warning("cTrader connection timeout — running in SIMULATION mode")

    else:
        _bot._load_simulation()

    logger.info(f"REST API ready at http://0.0.0.0:9009")
    logger.info(f"  Mode: {'LIVE' if _bot.host == 'live' else 'DEMO'}")
    logger.info(f"  Account: {_bot.account_id}")
    logger.info(f"  Symbols: {len(_bot.symbols)}")

    yield

    logger.info("Shutting down...")
    if _bot:
        _bot.disconnect()


app = FastAPI(
    title="cTrader REST API",
    description="REST bridge to cTrader OpenAPI for AgentFinance v3",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST / RESPONSE MODELS
# ============================================================================


class MarketOrderRequest(BaseModel):
    symbol: str = Field(..., example="EURUSD")
    side: str = Field(..., example="BUY", pattern="^(BUY|SELL)$")
    volume: float = Field(..., gt=0, le=100, example=0.10)
    stopLoss: Optional[float] = Field(None, example=1.0750)
    takeProfit: Optional[float] = Field(None, example=1.0890)
    orderType: str = Field("MARKET", example="MARKET")


class LimitOrderRequest(BaseModel):
    symbol: str = Field(..., example="EURUSD")
    side: str = Field(..., example="BUY", pattern="^(BUY|SELL)$")
    volume: float = Field(..., gt=0, le=100, example=0.10)
    price: float = Field(..., example=1.0800)
    stopLoss: Optional[float] = Field(None, example=1.0750)
    takeProfit: Optional[float] = Field(None, example=1.0890)


class StopOrderRequest(BaseModel):
    symbol: str = Field(..., example="EURUSD")
    side: str = Field(..., example="BUY", pattern="^(BUY|SELL)$")
    volume: float = Field(..., gt=0, le=100, example=0.10)
    price: float = Field(..., example=1.0850)
    stopLoss: Optional[float] = Field(None, example=1.0750)
    takeProfit: Optional[float] = Field(None, example=1.0890)


class CloseOrderRequest(BaseModel):
    positionId: int = Field(..., example=12345)
    volume: Optional[float] = Field(None, gt=0, example=0.10)


class CancelOrderRequest(BaseModel):
    orderId: int = Field(..., example=12345)


class AmendPositionRequest(BaseModel):
    positionId: int = Field(..., example=12345)
    stopLoss: Optional[float] = Field(None, example=1.0750)
    takeProfit: Optional[float] = Field(None, example=1.0890)


class TrendbarRequest(BaseModel):
    symbol: str = Field(..., example="EURUSD")
    period: str = Field("H1", example="H1")
    count: int = Field(100, ge=1, le=1000, example=100)


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
def health():
    """Health check endpoint."""
    bot = get_bot()
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "live" if bot.host == "live" else "demo",
    }


@app.get("/status")
def status():
    """Full connection and account status."""
    bot = get_bot()
    return {
        "connected": bot.is_connected,
        "app_authenticated": bot._app_auth,
        "account_authenticated": bot._account_auth,
        "host": bot.host,
        "account_id": bot.account_id,
        "symbols_count": len(bot.symbols),
        "positions_count": len(bot.positions),
        "pending_orders_count": len(bot.pending_orders),
        "mode": "SIMULATION" if not HAS_CTRADER or not bot._connected else "LIVE",
    }


@app.get("/symbols")
def list_symbols():
    """List all available trading symbols."""
    bot = get_bot()
    with bot._lock:
        return {"symbols": [{"name": k, "id": v} for k, v in bot.symbols.items()]}


@app.get("/positions")
def list_positions():
    """List all open positions."""
    bot = get_bot()
    bot.refresh_positions()
    time.sleep(0.2)  # Brief pause for Twisted callback to populate data
    with bot._lock:
        return {"positions": list(bot.positions), "count": len(bot.positions)}


@app.get("/orders")
def list_orders():
    """List all pending orders."""
    bot = get_bot()
    bot.refresh_positions()
    time.sleep(0.2)  # Brief pause for Twisted callback to populate data
    with bot._lock:
        return {"orders": list(bot.pending_orders), "count": len(bot.pending_orders)}


@app.get("/account")
def account():
    """Get account summary."""
    bot = get_bot()
    return {"account": bot.account, "account_id": bot.account_id}


@app.post("/orders/market", dependencies=[Depends(verify_api_key)])
def place_market_order(req: MarketOrderRequest):
    """Place a market order."""
    bot = get_bot()
    if req.symbol not in bot.symbols:
        raise HTTPException(404, f"Symbol '{req.symbol}' not found")
    symbol_id = bot.symbols[req.symbol]

    order_type = {"MARKET": "MARKET", "STOP_ENTRY": "STOP", "LIMIT_ENTRY": "LIMIT"}.get(
        req.orderType.upper(), "MARKET"
    )
    proto_type = ProtoOAOrderType.Value(order_type)

    result = bot._send_order(
        order_type=proto_type,
        side=req.side.upper(),
        symbol_id=symbol_id,
        volume=req.volume,
        price=0,
        sl=req.stopLoss or 0,
        tp=req.takeProfit or 0,
    )
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/limit", dependencies=[Depends(verify_api_key)])
def place_limit_order(req: LimitOrderRequest):
    """Place a limit order."""
    bot = get_bot()
    if req.symbol not in bot.symbols:
        raise HTTPException(404, f"Symbol '{req.symbol}' not found")
    symbol_id = bot.symbols[req.symbol]

    result = bot._send_order(
        order_type=ProtoOAOrderType.Value("LIMIT"),
        side=req.side.upper(),
        symbol_id=symbol_id,
        volume=req.volume,
        price=req.price,
        sl=req.stopLoss or 0,
        tp=req.takeProfit or 0,
    )
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/stop", dependencies=[Depends(verify_api_key)])
def place_stop_order(req: StopOrderRequest):
    """Place a stop order."""
    bot = get_bot()
    if req.symbol not in bot.symbols:
        raise HTTPException(404, f"Symbol '{req.symbol}' not found")
    symbol_id = bot.symbols[req.symbol]

    result = bot._send_order(
        order_type=ProtoOAOrderType.Value("STOP"),
        side=req.side.upper(),
        symbol_id=symbol_id,
        volume=req.volume,
        price=req.price,
        sl=req.stopLoss or 0,
        tp=req.takeProfit or 0,
    )
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/close", dependencies=[Depends(verify_api_key)])
def close_order(req: CloseOrderRequest):
    """Close a position (full or partial)."""
    bot = get_bot()
    volume = req.volume or 0
    result = bot._send_order(
        order_type=0,
        side="",
        symbol_id=0,
        volume=0,
        price=0,
        order_id=req.positionId,
        close_volume=volume,
    )
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/cancel", dependencies=[Depends(verify_api_key)])
def cancel_order(req: CancelOrderRequest):
    """Cancel a pending order."""
    bot = get_bot()
    result = bot.cancel_order(req.orderId)
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/amend", dependencies=[Depends(verify_api_key)])
def amend_position(req: AmendPositionRequest):
    """Amend stop loss and take profit on a position."""
    bot = get_bot()
    result = bot._send_order(
        order_type=0,
        side="",
        symbol_id=0,
        volume=0,
        price=0,
        sl=req.stopLoss or 0,
        tp=req.takeProfit or 0,
        order_id=req.positionId,
        close_volume=0,
    )
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/orders/close-all", dependencies=[Depends(verify_api_key)])
def close_all():
    """Close all open positions."""
    bot = get_bot()
    result = bot.close_all_positions()
    return {
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/trendbars", dependencies=[Depends(verify_api_key)])
def get_trendbars(req: TrendbarRequest):
    """Get historical candlestick data."""
    bot = get_bot()
    if req.symbol not in bot.symbols:
        raise HTTPException(404, f"Symbol '{req.symbol}' not found")
    symbol_id = bot.symbols[req.symbol]
    bars = bot.get_trendbars(symbol_id, req.period, req.count)
    return {"symbol": req.symbol, "period": req.period, "bars": bars}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "ctrader_api_server:app",
        host="0.0.0.0",
        port=9009,
        log_level="info",
    )
