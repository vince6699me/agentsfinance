#!/usr/bin/env python3
"""
AgentFinance cTrader Client
Direct cTrader OpenAPI integration for live trading execution.
Based on ctrader-open-api (TCP + Protobuf protocol).
Pepperstone Demo Account ID: 46729678

Usage:
    from ctrader_client import CTraderClient
    client = CTraderClient()
    client.connect()
    client.get_positions()
    client.create_market_order("EURUSD", "BUY", 0.01, 1.0750, 1.0950)
"""

import os
import sys
import time
import logging
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ctrader_client")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Try to import cTrader API at module level (graceful failure)
HAS_CTRADER = False
try:
    from twisted.internet import reactor
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
    )
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import (
        ProtoOAExecutionType,
        ProtoOATradeSide as ProtoOATradeSide2,
        ProtoOATrendbarPeriod,
    )

    HAS_CTRADER = True
except ImportError:
    logger.warning("ctrader-open-api not installed — will run in simulation mode")
    HAS_CTRADER = False


# ============================================================================
# CTRADER CLIENT
# ============================================================================


class CTraderClient:
    """
    Direct cTrader OpenAPI client for live trading.
    Uses TCP/Protobuf protocol via ctrader-open-api package.

    Environment variables (.env):
        CTRADER_CLIENT_ID       - API application client ID
        CTRADER_CLIENT_SECRET   - API application client secret
        CTRADER_ACCESS_TOKEN    - Trading account access token
        CTRADER_ACCOUNT_ID      - Trading account ID (default: 46729678)
        CTRADER_HOST            - "demo" or "live" (default: demo)
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        access_token: str = None,
        account_id: int = None,
        host: str = None,
    ):
        self.client_id = client_id or os.environ.get("CTRADER_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get(
            "CTRADER_CLIENT_SECRET", ""
        )
        self.access_token = access_token or os.environ.get("CTRADER_ACCESS_TOKEN", "")
        self.account_id = int(
            account_id or os.environ.get("CTRADER_ACCOUNT_ID", "46729678")
        )
        self.host_type = (host or os.environ.get("CTRADER_HOST", "demo")).lower()

        self._client = None
        self._connected = False
        self._app_authenticated = False
        self._account_authenticated = False

        self.symbols: Dict[str, Dict] = {}
        self.positions: List[Dict] = []
        self.orders: List[Dict] = []
        self.account_info: Dict = {}
        self._historical_data: Dict[str, pd.DataFrame] = {}

        logger.info(
            f"CTraderClient init — Account: {self.account_id}, Host: {self.host_type}"
        )

    # --------------------------------------------------------------------------
    # CONNECTION
    # --------------------------------------------------------------------------

    def connect(self, timeout: int = 30) -> bool:
        """Connect to cTrader API and authenticate."""
        if not all([self.client_id, self.client_secret, self.access_token]):
            logger.warning(
                "Missing credentials — running in SIMULATION mode. "
                "Set CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, "
                "CTRADER_ACCESS_TOKEN in .env for live trading."
            )
            self._load_demo_data()
            return True

        if not HAS_CTRADER:
            logger.warning("ctrader-open-api not installed — SIMULATION mode")
            self._load_demo_data()
            return True

        try:
            host = (
                EndPoints.PROTOBUF_LIVE_HOST
                if self.host_type == "live"
                else EndPoints.PROTOBUF_DEMO_HOST
            )

            self._client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
            self._client.setConnectedCallback(self._on_connected)
            self._client.setDisconnectedCallback(self._on_disconnected)
            self._client.setMessageReceivedCallback(self._on_message)
            self._client.startService()
            logger.info(f"Connecting to {host}:{EndPoints.PROTOBUF_PORT}...")

            start = time.time()
            while time.time() - start < timeout:
                if (
                    self._connected
                    and self._app_authenticated
                    and self._account_authenticated
                    and len(self.symbols) > 0
                ):
                    logger.info(f"Connected! Loaded {len(self.symbols)} symbols")
                    return True
                time.sleep(0.5)

            logger.error("Connection timeout")
            self._load_demo_data()
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._load_demo_data()
            return True

    def _load_demo_data(self):
        """Load demo/fallback data when not connected."""
        self._connected = True
        self._app_authenticated = True
        self._account_authenticated = True
        self.account_info = {
            "balance": 10500.00,
            "equity": 10427.50,
            "margin": 1248.30,
            "free_margin": 9179.20,
            "margin_level": 834.8,
        }
        self.positions = []
        self.orders = []
        for i, sym in enumerate(
            [
                "EURUSD",
                "GBPUSD",
                "USDJPY",
                "XAUUSD",
                "AUDUSD",
                "USDCAD",
                "NZDUSD",
                "EURGBP",
                "EURJPY",
                "GBPJPY",
                "XAGUSD",
                "USDCHF",
                "NAS100",
                "USOIL",
            ]
        ):
            self.symbols[sym] = {"id": i + 1, "name": sym, "digits": 5}

    def disconnect(self):
        """Disconnect from cTrader API."""
        if self._client:
            try:
                self._client.stopService()
            except Exception:
                pass
        self._connected = False
        self._app_authenticated = False
        self._account_authenticated = False
        logger.info("Disconnected")

    # --------------------------------------------------------------------------
    # TWISTED CALLBACKS
    # --------------------------------------------------------------------------

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
        self._app_authenticated = False
        self._account_authenticated = False

    def _on_message(self, client, message):
        try:
            payload = message.payloadType

            if payload == ProtoOAApplicationAuthReq().payloadType:
                logger.info("Application authenticated")
                self._app_authenticated = True
                self._authenticate_account()

            elif payload == ProtoOAAccountAuthRes().payloadType:
                logger.info("Account authenticated")
                self._account_authenticated = True
                self._request_symbols()

            elif payload == ProtoOASymbolsListRes().payloadType:
                self._handle_symbols(message)

            elif payload == ProtoOAExecutionEvent().payloadType:
                self._handle_execution_event(message)

            elif payload == ProtoOAOrderErrorEvent().payloadType:
                self._handle_order_error(message)

            elif payload == ProtoOAReconcileRes().payloadType:
                self._handle_reconcile(message)

            elif payload == ProtoOASpotEvent().payloadType:
                pass

            elif payload == ProtoOAGetTrendbarsRes().payloadType:
                self._handle_trendbars(message)

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
        for sym in response.symbol:
            self.symbols[sym.symbolName] = {
                "id": sym.symbolId,
                "name": sym.symbolName,
                "digits": getattr(sym, "digits", 5),
            }
        logger.info(f"Loaded {len(self.symbols)} symbols")
        self.refresh_positions()

    def _handle_execution_event(self, message):
        event = Protobuf.extract(message)
        et = event.executionType
        if et == ProtoOAExecutionType.ORDER_ACCEPTED:
            logger.info(f"Order accepted: {event.order.orderId}")
        elif et == ProtoOAExecutionType.ORDER_FILLED:
            logger.info(f"Order filled: {event.order.orderId}")
        elif et == ProtoOAExecutionType.ORDER_CANCELLED:
            logger.info(f"Order cancelled: {event.order.orderId}")
        elif et == ProtoOAExecutionType.ORDER_REJECTED:
            logger.error(f"Order rejected: {event.order.orderId}")
        self.refresh_positions()

    def _handle_order_error(self, message):
        err = Protobuf.extract(message)
        logger.error(f"Order error {err.errorCode}: {err.description}")

    def _handle_reconcile(self, message):
        resp = Protobuf.extract(message)
        if hasattr(resp, "balance"):
            self.account_info["balance"] = resp.balance / 100
        if hasattr(resp, "equity"):
            self.account_info["equity"] = resp.equity / 100
        if hasattr(resp, "margin"):
            self.account_info["margin"] = resp.margin / 100
        if hasattr(resp, "freeMargin"):
            self.account_info["free_margin"] = resp.freeMargin / 100

        self.positions = []
        for pos in resp.position:
            sym_info = next(
                (s for s in self.symbols.values() if s["id"] == pos.tradeData.symbolId),
                None,
            )
            self.positions.append(
                {
                    "id": pos.positionId,
                    "symbol_id": pos.tradeData.symbolId,
                    "symbol_name": sym_info["name"] if sym_info else "Unknown",
                    "side": "BUY"
                    if pos.tradeData.tradeSide == ProtoOATradeSide2.BUY
                    else "SELL",
                    "volume": pos.tradeData.volume / 100,
                    "entry_price": pos.price,
                    "pnl": getattr(pos, "grossProfit", 0) / 100,
                    "swap": getattr(pos, "swap", 0) / 100,
                    "commission": getattr(pos, "commission", 0) / 100,
                }
            )

        self.orders = []
        for order in resp.order:
            sym_info = next(
                (
                    s
                    for s in self.symbols.values()
                    if s["id"] == order.tradeData.symbolId
                ),
                None,
            )
            self.orders.append(
                {
                    "id": order.orderId,
                    "symbol_id": order.tradeData.symbolId,
                    "symbol_name": sym_info["name"] if sym_info else "Unknown",
                    "side": "BUY"
                    if order.tradeData.tradeSide == ProtoOATradeSide2.BUY
                    else "SELL",
                    "volume": order.tradeData.volume / 100,
                }
            )

        logger.info(f"Positions: {len(self.positions)}, Orders: {len(self.orders)}")

    def _handle_trendbars(self, message):
        resp = Protobuf.extract(message)
        if not hasattr(resp, "trendbar") or len(resp.trendbar) == 0:
            return
        sym_name = next(
            (s["name"] for s in self.symbols.values() if s["id"] == resp.symbolId),
            "Unknown",
        )
        sym_info = self.symbols.get(sym_name, {})
        digits = sym_info.get("digits", 5)
        divisor = 10**digits
        data = []
        for bar in resp.trendbar:
            low = bar.low / divisor
            data.append(
                {
                    "timestamp": pd.to_datetime(
                        bar.utcTimestampInMinutes * 60, unit="s"
                    ),
                    "open": low
                    + (bar.deltaOpen / divisor if hasattr(bar, "deltaOpen") else 0),
                    "high": low
                    + (bar.deltaHigh / divisor if hasattr(bar, "deltaHigh") else 0),
                    "low": low,
                    "close": low
                    + (bar.deltaClose / divisor if hasattr(bar, "deltaClose") else 0),
                    "volume": getattr(bar, "volume", 0),
                }
            )
        df = pd.DataFrame(data).set_index("timestamp")
        period_map = {
            1: "M1",
            5: "M5",
            15: "M15",
            30: "M30",
            60: "H1",
            240: "H4",
            1440: "D1",
            10080: "W1",
            43200: "MN1",
        }
        period_name = period_map.get(resp.period, "H1")
        self._historical_data[f"{sym_name}_{period_name}"] = df

    # --------------------------------------------------------------------------
    # POSITIONS & ORDERS
    # --------------------------------------------------------------------------

    def refresh_positions(self):
        """Refresh positions and orders from server."""
        if not self._account_authenticated:
            return
        req = ProtoOAReconcileReq()
        req.ctidTraderAccountId = self.account_id
        self._client.send(req)

    def get_positions(self) -> List[Dict]:
        """Return current open positions."""
        return self.positions

    def get_pending_orders(self) -> List[Dict]:
        """Return current pending orders."""
        return self.orders

    # --------------------------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------------------------

    def get_account_summary(self) -> Dict:
        """Return account summary."""
        return {
            "account_id": self.account_id,
            "balance": self.account_info.get("balance", 10500.0),
            "equity": self.account_info.get("equity", 10427.50),
            "margin": self.account_info.get("margin", 1248.30),
            "free_margin": self.account_info.get("free_margin", 9179.20),
            "margin_level": self.account_info.get("margin_level", 834.8),
            "open_positions": len(self.positions),
            "pending_orders": len(self.orders),
        }

    def get_daily_pnl(self) -> Dict:
        """Return daily P&L breakdown."""
        total_pnl = sum(p.get("pnl", 0) for p in self.positions)
        return {
            "daily_pnl": total_pnl,
            "daily_pnl_pct": round(
                total_pnl / max(self.account_info.get("balance", 10500.0), 1) * 100, 2
            ),
            "open_pnl": total_pnl,
            "closed_pnl": 0.0,
        }

    # --------------------------------------------------------------------------
    # TRADING ORDERS
    # --------------------------------------------------------------------------

    def _get_symbol_id(self, symbol_name: str) -> Optional[int]:
        sym = self.symbols.get(symbol_name.upper())
        return sym["id"] if sym else None

    def _price_to_int(self, price: float, symbol_name: str) -> int:
        digits = self.symbols.get(symbol_name.upper(), {}).get("digits", 5)
        return int(price * (10**digits))

    def create_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        stop_loss: float = None,
        take_profit: float = None,
    ) -> Dict:
        """Place a market order."""
        if not self._account_authenticated and not self._connected:
            return {"success": False, "error": "Not connected"}

        sym_id = self._get_symbol_id(symbol)
        if not sym_id:
            return {"success": False, "error": f"Unknown symbol: {symbol}"}

        if not HAS_CTRADER or not self._client:
            return self._simulate_order(symbol, side, volume, stop_loss, take_profit)

        try:
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = sym_id
            req.orderType = ProtoOAOrderType.MARKET
            req.tradeSide = (
                ProtoOATradeSide.BUY if side.upper() == "BUY" else ProtoOATradeSide.SELL
            )
            req.volume = int(volume * 100)

            if stop_loss:
                req.stopLoss = self._price_to_int(stop_loss, symbol)
            if take_profit:
                req.takeProfit = self._price_to_int(take_profit, symbol)

            self._client.send(req)
            logger.info(
                f"Market order sent: {side} {volume} lots {symbol} "
                f"SL={stop_loss} TP={take_profit}"
            )
            self.refresh_positions()
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "volume": volume,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "ACCEPTED",
            }
        except Exception as e:
            logger.error(f"create_market_order error: {e}")
            return {"success": False, "error": str(e)}

    def create_limit_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: float,
        stop_loss: float = None,
        take_profit: float = None,
    ) -> Dict:
        """Place a limit (pending) order."""
        if not self._account_authenticated and not self._connected:
            return {"success": False, "error": "Not connected"}

        sym_id = self._get_symbol_id(symbol)
        if not sym_id:
            return {"success": False, "error": f"Unknown symbol: {symbol}"}

        if not HAS_CTRADER or not self._client:
            return self._simulate_order(symbol, side, volume, stop_loss, take_profit)

        try:
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = sym_id
            req.orderType = ProtoOAOrderType.LIMIT
            req.tradeSide = (
                ProtoOATradeSide.BUY if side.upper() == "BUY" else ProtoOATradeSide.SELL
            )
            req.volume = int(volume * 100)
            req.limitPrice = self._price_to_int(price, symbol)

            if stop_loss:
                req.stopLoss = self._price_to_int(stop_loss, symbol)
            if take_profit:
                req.takeProfit = self._price_to_int(take_profit, symbol)

            self._client.send(req)
            logger.info(f"Limit order sent: {side} {volume} lots {symbol} @ {price}")
            self.refresh_positions()
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "volume": volume,
                "price": price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "PENDING",
            }
        except Exception as e:
            logger.error(f"create_limit_order error: {e}")
            return {"success": False, "error": str(e)}

    def create_stop_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: float,
        stop_loss: float = None,
        take_profit: float = None,
    ) -> Dict:
        """Place a stop order."""
        if not self._account_authenticated and not self._connected:
            return {"success": False, "error": "Not connected"}

        sym_id = self._get_symbol_id(symbol)
        if not sym_id:
            return {"success": False, "error": f"Unknown symbol: {symbol}"}

        if not HAS_CTRADER or not self._client:
            return self._simulate_order(symbol, side, volume, stop_loss, take_profit)

        try:
            req = ProtoOANewOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = sym_id
            req.orderType = ProtoOAOrderType.STOP
            req.tradeSide = (
                ProtoOATradeSide.BUY if side.upper() == "BUY" else ProtoOATradeSide.SELL
            )
            req.volume = int(volume * 100)
            req.stopPrice = self._price_to_int(price, symbol)

            if stop_loss:
                req.stopLoss = self._price_to_int(stop_loss, symbol)
            if take_profit:
                req.takeProfit = self._price_to_int(take_profit, symbol)

            self._client.send(req)
            logger.info(f"Stop order sent: {side} {volume} lots {symbol} @ {price}")
            self.refresh_positions()
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "volume": volume,
                "stop_price": price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "PENDING",
            }
        except Exception as e:
            logger.error(f"create_stop_order error: {e}")
            return {"success": False, "error": str(e)}

    def close_position(self, position_id: int, volume: float = None) -> Dict:
        """Close an open position (full or partial)."""
        if not self._account_authenticated and not self._connected:
            return {"success": False, "error": "Not connected"}

        pos = next((p for p in self.positions if p["id"] == position_id), None)
        if not pos:
            return {"success": False, "error": f"Position {position_id} not found"}

        if not HAS_CTRADER or not self._client:
            return {"success": True, "position_id": position_id, "status": "SIMULATED"}

        try:
            req = ProtoOAClosePositionReq()
            req.ctidTraderAccountId = self.account_id
            req.positionId = position_id
            req.volume = int((volume or pos["volume"]) * 100)
            self._client.send(req)
            logger.info(f"Close position sent: #{position_id}")
            self.refresh_positions()
            return {"success": True, "position_id": position_id, "status": "CLOSING"}
        except Exception as e:
            logger.error(f"close_position error: {e}")
            return {"success": False, "error": str(e)}

    def close_all_positions(self) -> Dict:
        """Close all open positions."""
        closed = 0
        for pos in self.positions:
            result = self.close_position(pos["id"])
            if result.get("success"):
                closed += 1
        return {"success": True, "closed_count": closed}

    def cancel_order(self, order_id: int) -> Dict:
        """Cancel a pending order."""
        if not self._account_authenticated and not self._connected:
            return {"success": False, "error": "Not connected"}

        if not HAS_CTRADER or not self._client:
            return {"success": True, "order_id": order_id, "status": "SIMULATED"}

        try:
            req = ProtoOACancelOrderReq()
            req.ctidTraderAccountId = self.account_id
            req.orderId = order_id
            self._client.send(req)
            logger.info(f"Cancel order sent: #{order_id}")
            self.refresh_positions()
            return {"success": True, "order_id": order_id, "status": "CANCELLED"}
        except Exception as e:
            logger.error(f"cancel_order error: {e}")
            return {"success": False, "error": str(e)}

    # --------------------------------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------------------------------

    def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "H1",
        count: int = 100,
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV candlestick data."""
        cache_key = f"{symbol.upper()}_{timeframe}"
        if cache_key in self._historical_data:
            return self._historical_data[cache_key]

        sym_id = self._get_symbol_id(symbol)
        if not sym_id:
            return None

        timeframe_map = {
            "M1": 1,
            "M5": 5,
            "M15": 15,
            "M30": 30,
            "H1": 60,
            "H4": 240,
            "D1": 1440,
            "W1": 10080,
            "MN1": 43200,
        }
        period = timeframe_map.get(timeframe, 60)

        if not HAS_CTRADER or not self._client:
            return None

        try:
            period_enum = getattr(
                ProtoOATrendbarPeriod, timeframe, ProtoOATrendbarPeriod.H1
            )
            now_ms = int(time.time() * 1000)
            req = ProtoOAGetTrendbarsReq()
            req.ctidTraderAccountId = self.account_id
            req.symbolId = sym_id
            req.period = period_enum
            req.fromTimestamp = now_ms - (count * period * 60 * 1000)
            req.toTimestamp = now_ms
            req.count = count
            self._client.send(req)
            time.sleep(1)
            return self._historical_data.get(cache_key)
        except Exception as e:
            logger.error(f"get_historical_data error: {e}")
            return None

    # --------------------------------------------------------------------------
    # SIMULATION HELPERS
    # --------------------------------------------------------------------------

    def _simulate_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        stop_loss: float,
        take_profit: float,
    ) -> Dict:
        """Return simulated order response when API unavailable."""
        order_id = f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"[SIMULATED] Order: {side} {volume} lots {symbol}")
        return {
            "success": True,
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "volume": volume,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "SIMULATED",
            "simulation": True,
        }

    # --------------------------------------------------------------------------
    # CONVENIENCE METHODS
    # --------------------------------------------------------------------------

    def place_market_order(
        self,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        take_profit: float,
        volume: float = 0.01,
        label: str = "",
    ) -> Dict:
        """Alias for create_market_order (backward compat)."""
        return self.create_market_order(
            symbol, direction, volume, stop_loss, take_profit
        )

    def get_trade_history(self, trade_id: str) -> Dict:
        """Return trade history entry (simulated)."""
        return {
            "trade_id": trade_id,
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry": 1.0823,
            "exit": 1.0890,
            "pnl_pips": 67,
            "result": "WIN",
        }


# ============================================================================
# CLI
# ============================================================================


def main():
    """CLI for testing the client."""
    client = CTraderClient()
    connected = client.connect(timeout=10)

    if connected:
        print("\n=== Account Summary ===")
        summary = client.get_account_summary()
        for k, v in summary.items():
            print(f"  {k}: {v}")

        print("\n=== Open Positions ===")
        positions = client.get_positions()
        for p in positions:
            print(
                f"  {p['symbol_name']} {p['side']} {p['volume']} lots — P&L: ${p.get('pnl', 0):.2f}"
            )
        if not positions:
            print("  (none)")

        print("\n=== Pending Orders ===")
        orders = client.get_pending_orders()
        for o in orders:
            print(f"  {o['symbol_name']} {o['side']} {o['volume']} lots")
        if not orders:
            print("  (none)")

        print(f"\n=== Symbol Count ===")
        print(f"  {len(client.symbols)} symbols loaded")
    else:
        print("Not connected — check credentials in .env")


if __name__ == "__main__":
    main()
