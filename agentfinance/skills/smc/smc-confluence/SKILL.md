---
name: smc-confluence
description: >
  SMC confluence scoring and multi-factor trade validation. Use when combining multiple
  SMC elements, scoring trade setups, and filtering low-probability trades.
---

# SMC Confluence Skill

Confluence = multiple SMC elements pointing to the same direction = higher probability trade.

## Confluence Categories

### Level 1 - Structural (Highest Weight)
- Order block (untouched)
- Fair value gap
- Break of structure
- Liquidity grab

### Level 2 - Positional (Medium Weight)
- Premium/discount zone
- Higher timeframe structure
- Session bias

### Level 3 - Confirmatory (Lower Weight)
- Kill zone timing
- Momentum divergence
- Volume confirmation

## Confluence Scoring Formula

```
Total Score = Sum(Component Scores × Weight)
Grade:
  80-100%: A+ (High conviction)
  60-79%:  A  (Strong)
  40-59%:  B  (Moderate)
  20-39%:  C  (Weak - avoid)
  0-19%:   F  (Skip)
```

## Minimum Requirements

| Requirement | Threshold |
|-------------|-----------|
| Structural elements | 2+ required |
| Positional alignment | 1+ recommended |
| Score grade | B+ (65%) minimum |
| Confidence | 75% minimum for execution |

## Trade Setup Examples

### A+ Setup (80%+)
```
EURUSD H4 Bullish:
- Bullish OB at 1.0820 (Level 1)     → 25%
- Bullish FVG at 1.0815 (Level 1)    → 25%
- HH/HL forming (Level 1)           → 20%
- Discount zone (Level 2)           → 15%
- London kill zone (Level 3)         → 10%
Total: 95% → EXECUTE
```

### B Setup (40-59%)
```
GBPUSD H1:
- Bearish FVG at 1.2680 (Level 1)    → 25%
- Premium zone (Level 2)             → 15%
- Kill zone (Level 3)               → 10%
Total: 50% → WATCH only (no execute)
```

## Workflow

1. Identify all structural elements (OB, FVG, BOS)
2. Check positional context (premium/discount, HT bias)
3. Validate timing (kill zone, news)
4. Calculate total score
5. Grade the setup
6. Execute if B+ (65%) and 2+ structural elements

## Example Decision Tree

```
OB detected → Check if in discount zone? → Kill zone timing?
Yes → Score = 25+15+10 = 50% (B grade)
↓
Add FVG confluence = +25% → Score = 75% (A grade)
↓
Confidence check: 75% >= 75%? → YES → EXECUTE
```
