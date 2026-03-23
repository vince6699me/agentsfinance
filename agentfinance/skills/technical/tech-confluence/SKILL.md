---
name: tech-confluence
description: >
  Multi-indicator confluence trading strategy. Use when combining multiple technical
  indicators for high-probability trade setups with weighted scoring.
---

# Tech Confluence Skill

Confluence = multiple indicators agreeing = high probability trade setup.

## Confluence Components

### Trend Indicators
- EMA crossover (9/21 or 20/50)
- MACD histogram direction
- ADX strength level
- Price vs EMAs

### Momentum Indicators
- RSI position (OB/OS/mid)
- Stochastic position
- CCI position
- ROC direction

### Volatility Indicators
- Bollinger Band touch/position
- ATR relative level
- VWAP relationship

### Volume Indicators
- Volume vs average
- OBV direction
- CMF position

## Scoring System

```
Score = Sum(Indicator Signals × Weight)
Grade:
  80-100%: A+ (High conviction)
  60-79%:  A  (Strong)
  40-59%:  B  (Moderate - watch only)
  20-39%:  C  (Weak - skip)
  0-19%:   F  (No trade)
```

## Trading Rules

### Entry Requirements
- Grade A+ or A required for execution
- Minimum 4 indicators agreeing
- SMC structure confirming
- Kill zone timing (bonus)

### Position Management
- Higher score = larger position (max 2x base)
- Lower score = smaller position or skip
- Exit on score dropping below threshold

## Example Confluence Matrix

```
EURUSD BUY Setup:
EMA 9 > EMA 21        → +20% ✓
MACD > Signal          → +20% ✓
RSI = 55 (bullish zone) → +15% ✓
ADX = 28 (strengthening) → +15% ✓
Volume = 1.5x avg      → +10% ✓
Bollinger mid band     → +10% ✓
VWAP > price           → +10% ✓
Total: 100% → A+ GRADE
```
