# AgentFinance Trading Engine

Python-based trading engine with SMC analysis, technical indicators, and cTrader execution.

## Installation

```bash
pip install pandas numpy scipy ta requests aiohttp websockets
```

## Usage

### SMC Analysis

```python
from trading.engines.smc_engine import run_full_smc_analysis, get_active_kill_zones

# Run full SMC analysis
analysis = run_full_smc_analysis("EURUSD", ohlcv_df)
print(f"Bias: {analysis.bias}")
print(f"Confluence: {analysis.confluence_score}")
print(f"Setups: {len(analysis.setups)}")
```

### Technical Indicators

```python
from trading.engines.technical_engine import IndicatorEngine

engine = IndicatorEngine()
indicators = engine.run_all(ohlcv_df)
signal = engine.get_confluence_signal(indicators)
print(f"Direction: {signal.direction}")
print(f"Confidence: {signal.confidence}")
```

### Kill Zones

```python
from trading.engines.session_engine import get_active_sessions

sessions = get_active_sessions()
for session in sessions:
    print(f"{session.session_type.value}: {session.description}")
```

### cTrader Execution

```python
from trading.execution.ctrader_client import CTraderClient

client = CTraderClient()
client.connect_tcp()

# Place order
result = client.place_order(
    symbol="EURUSD",
    side="BUY",
    volume=0.10,
    stop_loss=1.0800,
    take_profit=1.0900
)
```

### Risk Management

```python
from trading.execution.risk_manager import RiskManager, TradeSignal
from datetime import datetime

risk_mgr = RiskManager()

signal = TradeSignal(
    signal_id="TEST-001",
    symbol="EURUSD",
    direction="BUY",
    entry_price=1.0850,
    stop_loss=1.0800,
    take_profit=1.0900,
    confidence=0.85,
    risk_reward=2.0,
    created_at=datetime.now()
)

result = risk_mgr.check_signal(signal)
print(f"Allowed: {result.allowed}")
print(f"Risk Level: {result.risk_level}")
```

## Structure

```
trading/
├── engines/
│   ├── smc_engine.py       # Smart Money Concepts
│   ├── technical_engine.py # 80+ indicators
│   └── session_engine.py   # Kill zones & COT
├── execution/
│   ├── ctrader_client.py  # cTrader API
│   └── risk_manager.py     # Risk controls
└── backtest/
    └── backtest_engine.py  # Strategy backtesting
```

## Risk Rules

| Rule | Value |
|------|-------|
| Max risk/trade | 1% |
| Max daily loss | 3% |
| Max positions | 5 |
| Min R:R | 1.5 |
| Min confidence | 75% |
| Max spread | 3x avg |
