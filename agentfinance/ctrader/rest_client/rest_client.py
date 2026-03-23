#!/usr/bin/env python3
"""
cTrader REST Client
===================
HTTP REST client for the cTrader REST API Docker container.
Use this when running cTrader via Docker (ctrader_api_server.py in a container).

Environment variables:
    CTRADER_REST_URL  - Base URL of the REST API server (default: http://localhost:9009)
    CTRADER_CLIENT_ID - API application client ID
    CTRADER_CLIENT_SECRET - API application client secret
    CTRADER_ACCESS_TOKEN - Trading account access token
    CTRADER_ACCOUNT_ID   - Trading account ID (default: 46729678)
    CTRADER_HOST         - "demo" or "live" (default: demo)

Usage:
    from rest_client import CTraderRESTClient
    client = CTraderRESTClient()
    client.connect()
    positions = client.get_positions()
    result = client.place_market_order("EURUSD", "BUY", 0.10, sl=1.0756, tp=1.0890)

Docker setup:
    cd ctrader/
    docker compose up --build
    # API available at http://localhost:9009
    # Swagger docs at http://localhost:9009/docs
"""

import os
import time
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger("ctrader-rest-client")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class CTraderRESTClient:
    """
    HTTP REST client for the cTrader REST API Docker container.
    Provides the same interface as CTraderClient for drop-in replacement.
    """

    def __init__(
        self,
        base_url: str = None,
        client_id: str = None,
        client_secret: str = None,
        access_token: str = None,
        account_id: int = None,
        host: str = None,
        timeout: int = 30,
    ):
        self.base_url = (
            base_url or os.environ.get("CTRADER_REST_URL", "http://localhost:9009")
        ).rstrip("/")

        # Credentials (stored but used by the Docker container, not this client)
        self.client_id = client_id or os.environ.get("CTRADER_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get(
            "CTRADER_CLIENT_SECRET", ""
        )
        self.access_token = access_token or os.environ.get("CTRADER_ACCESS_TOKEN", "")
        self.account_id = int(
            account_id or os.environ.get("CTRADER_ACCOUNT_ID", "46729678")
        )
        self.host_type = (host or os.environ.get("CTRADER_HOST", "demo")).lower()
        self.timeout = timeout

        self._connected = False
        self._simulation = False
        self.symbols: Dict[str, int] = {}
        self.positions: List[Dict] = []
        self.orders: List[Dict] = []
        self.account_info: Dict = {}

        logger.info(
            f"CTraderRESTClient init — URL: {self.base_url}, Account: {self.account_id}"
        )

    def _request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Make HTTP request to the REST API server."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            logger.error(f"HTTP {e.code} on {method} {path}: {body}")
            return {"error": f"HTTP {e.code}", "detail": body}
        except urllib.error.URLError as e:
            logger.error(f"Connection error on {method} {path}: {e}")
            return {"error": "CONNECTION_FAILED", "detail": str(e)}
        except Exception as e:
            logger.error(f"Request error on {method} {path}: {e}")
            return {"error": str(e)}

    def connect(self, timeout: int = 30) -> bool:
        """Connect to the cTrader REST API Docker container."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                health = self._request("GET", "/health")
                if "error" not in health:
                    status = self._request("GET", "/status")
                    self._connected = True
                    self._simulation = status.get("mode") == "SIMULATION"

                    if self._simulation:
                        logger.warning(
                            "REST API running in SIMULATION mode (missing credentials)"
                        )

                    # Load symbols
                    sym_resp = self._request("GET", "/symbols")
                    self.symbols = {
                        s["Name"]: s["id"] for s in sym_resp.get("symbols", [])
                    }

                    logger.info(
                        f"Connected to REST API — {len(self.symbols)} symbols, "
                        f"mode={status.get('mode', 'unknown')}"
                    )
                    return True

            except Exception as e:
                logger.debug(f"Waiting for REST API... ({e})")
                time.sleep(1)

        logger.warning(
            f"Could not connect to REST API at {self.base_url} — "
            f"running in SIMULATION mode"
        )
        self._load_demo_data()
        return True

    def _load_demo_data(self):
        """Load demo data when REST API is unreachable."""
        self._connected = True
        self._simulation = True
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
        self.account_info = {
            "balance": 10500.00,
            "equity": 10427.50,
            "margin": 1248.30,
            "freeMargin": 9179.20,
            "marginLevel": 834.8,
        }
        self.positions = []
        self.orders = []
        logger.info(f"Simulation mode: {len(self.symbols)} symbols loaded")

    def disconnect(self):
        """Disconnect from the REST API (no-op for HTTP)."""
        self._connected = False
        logger.info("Disconnected from REST API")

    def place_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: float = None,
        tp: float = None,
        order_type: str = "MARKET",
    ) -> Dict:
        """Place a market order."""
        if not self._connected or symbol not in self.symbols:
            if not self._simulation:
                return {
                    "status": "ERROR",
                    "message": "Not connected or symbol not found",
                }
            symbol_id = self.symbols.get(symbol, 1)
        else:
            symbol_id = self.symbols[symbol]

        data = {
            "symbol": symbol,
            "side": side.upper(),
            "volume": volume,
            "stopLoss": sl,
            "takeProfit": tp,
            "orderType": order_type,
        }
        result = self._request("POST", "/orders/market", data)
        logger.info(
            f"Market order: {side} {volume} {symbol} SL={sl} TP={tp} → {result}"
        )
        return result

    def create_limit_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: float,
        sl: float = None,
        tp: float = None,
    ) -> Dict:
        """Place a limit order."""
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "volume": volume,
            "price": price,
            "stopLoss": sl,
            "takeProfit": tp,
        }
        result = self._request("POST", "/orders/limit", data)
        logger.info(f"Limit order: {side} {volume} {symbol} @{price} → {result}")
        return result

    def create_stop_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: float,
        sl: float = None,
        tp: float = None,
    ) -> Dict:
        """Place a stop order."""
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "volume": volume,
            "price": price,
            "stopLoss": sl,
            "takeProfit": tp,
        }
        result = self._request("POST", "/orders/stop", data)
        logger.info(f"Stop order: {side} {volume} {symbol} @{price} → {result}")
        return result

    def close_position(self, position_id: int, volume: float = None) -> Dict:
        """Close a position (full close if volume is None)."""
        data = {"positionId": position_id, "volume": volume}
        result = self._request("POST", "/orders/close", data)
        logger.info(f"Close position #{position_id} vol={volume} → {result}")
        return result

    def close_all_positions(self) -> Dict:
        """Close all open positions."""
        result = self._request("POST", "/orders/close-all")
        logger.info(f"Close all positions → {result}")
        return result

    def amend_position(
        self, position_id: int, sl: float = None, tp: float = None
    ) -> Dict:
        """Amend stop loss and take profit on a position."""
        data = {"positionId": position_id, "stopLoss": sl, "takeProfit": tp}
        result = self._request("POST", "/orders/amend", data)
        logger.info(f"Amend position #{position_id} SL={sl} TP={tp} → {result}")
        return result

    def cancel_order(self, order_id: int) -> Dict:
        """Cancel a pending order."""
        data = {"orderId": order_id}
        result = self._request("POST", "/orders/cancel", data)
        logger.info(f"Cancel order #{order_id} → {result}")
        return result

    def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        if not self._connected:
            return []
        result = self._request("GET", "/positions")
        self.positions = result.get("positions", [])
        return self.positions

    def get_pending_orders(self) -> List[Dict]:
        """Get all pending orders."""
        if not self._connected:
            return []
        result = self._request("GET", "/orders")
        self.orders = result.get("orders", [])
        return self.orders

    def get_account_summary(self) -> Dict:
        """Get account summary."""
        if not self._connected:
            return self.account_info
        result = self._request("GET", "/account")
        self.account_info = result.get("account", {})
        return self.account_info

    def get_historical_data(
        self, symbol: str, period: str = "H1", count: int = 100
    ) -> List[Dict]:
        """Get historical candlestick data."""
        data = {"symbol": symbol, "period": period, "count": count}
        result = self._request("POST", "/trendbars", data)
        return result.get("bars", [])

    def get_symbol_id(self, symbol: str) -> Optional[int]:
        """Get cTrader symbol ID for a symbol name."""
        return self.symbols.get(symbol)

    # Alias for compatibility
    place_market_order_ = place_market_order


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="cTrader REST Client")
    parser.add_argument("command", choices=["positions", "orders", "account", "status"])
    parser.add_argument(
        "--url", default=os.environ.get("CTRADER_REST_URL", "http://localhost:9009")
    )
    args = parser.parse_args()

    client = CTraderRESTClient(base_url=args.url)
    client.connect(timeout=10)

    if args.command == "positions":
        positions = client.get_positions()
        print(
            json.dumps(
                {"positions": positions, "count": len(positions)}, indent=2, default=str
            )
        )
    elif args.command == "orders":
        orders = client.get_pending_orders()
        print(
            json.dumps({"orders": orders, "count": len(orders)}, indent=2, default=str)
        )
    elif args.command == "account":
        acc = client.get_account_summary()
        print(json.dumps({"account": acc}, indent=2, default=str))
    elif args.command == "status":
        status = client._request("GET", "/status")
        print(json.dumps(status, indent=2, default=str))
