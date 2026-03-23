---
name: indices-smc
description: >
  Index-specific SMC trading strategies. Use when applying Smart Money Concepts to equity
  indices (S&P 500, NASDAQ, DAX, FTSE) with focus on institutional flow patterns.
---

# Indices SMC Skill

SMC analysis for equity index trading.

## Major Indices

### US Indices
| Index | Symbol | Session (UTC) | Volatility |
|-------|--------|--------------|-----------|
| S&P 500 | SPX500 | 14:30-21:00 | Medium |
| NASDAQ | US100 | 14:30-21:00 | High |
| Dow Jones | US30 | 14:30-21:00 | Low |

### European Indices
| Index | Symbol | Session (UTC) | Volatility |
|-------|--------|--------------|-----------|
| DAX | Germany40 | 07:00-21:00 | High |
| FTSE | UK100 | 07:00-15:30 | Medium |
| Euro Stoxx | EUREX50 | 07:00-21:00 | Medium |

## Index-Specific SMC

### S&P 500 Characteristics
- Strong trending behavior
- Higher timeframe structure dominant
- News-driven moves
- Overnight sessions create gaps

### Index Kill Zones (ET → UTC+5)
| Zone | ET | UTC | Quality |
|------|----|----|---------|
| NY Open | 09:30 | 14:30 | High |
| Pre-Open | 09:15 | 14:15 | Medium |
| Lunch | 12:00 | 17:00 | Low |
| NY Close | 16:00 | 21:00 | Medium |

## Gap Analysis
| Gap Type | Frequency | Direction Bias |
|----------|----------|----------------|
| Overnight | Daily | Up (bull bias) |
| Weekend | Weekly | Down (risk-off) |
| Breakaway | Rare | Follows momentum |

## Index Trading Parameters
| Index | Typical SL | TP1 | TP2 |
|-------|-----------|-----|------|
| SPX500 | 15-30 pts | 30 | 60 |
| US100 | 40-80 pts | 80 | 160 |
| Germany40 | 30-60 pts | 60 | 120 |

## Confidence Scoring
| Factor | Weight |
|--------|--------|
| Pre/Post market analysis | +25% |
| Gap direction aligned | +20% |
| Sector rotation confirms | +20% |
| VIX at extremes | +15% |
| Institutional flow | +20% |
