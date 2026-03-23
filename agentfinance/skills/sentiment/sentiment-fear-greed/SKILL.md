---
name: sentiment-fear-greed
description: >
  Fear and greed sentiment index analysis. Use when identifying market extremes, contrarian
  entry points, and crowd sentiment as a reversal indicator.
---

# Sentiment Fear-Greed Skill

Fear-Greed indices measure overall market sentiment and identify extremes.

## Fear-Greed Scale

| Value | Sentiment | Market State | Trading Implication |
|-------|-----------|-------------|-------------------|
| 0-25 | Extreme Fear | Capitulation, panic selling | **BUY ZONE** - Contrarian |
| 25-45 | Fear | Weakness, pessimism | Cautious, accumulate on dips |
| 45-55 | Neutral | Balanced, uncertainty | Wait for clear signal |
| 55-75 | Greed | Optimism, accumulation | Take profits, reduce risk |
| 75-100 | Extreme Greed | Euphoria, FOMO | **SELL ZONE** - Contrarian |

## Components

| Component | Weight | What It Measures |
|-----------|--------|----------------|
| Stock Price Momentum | 25% | S&P 500 vs 125-day MA |
| Stock Price Breadth | 25% | Advancing vs declining |
| Put/Call Ratio | 10% | Put buying pressure |
| Junk Bond Demand | 10% | Risk appetite |
| Market Volatility | 25% | VIX levels |
| Safe Haven Demand | 5% | Stocks vs bonds |

## Trading Rules

### Extreme Fear (0-25)
1. Market in oversold condition
2. Often coincides with panic/capitulation
3. **High probability reversal zone**
4. Start building long positions gradually
5. Set stops below panic lows

### Extreme Greed (75-100)
1. Market in overbought condition
2. Often coincides with FOMO/in euphoria
3. **High probability reversal zone**
4. Take profits, reduce exposure
5. Prepare for shorting opportunities

### Mid-Range (25-75)
1. Sentiment not extreme
2. Follow trend (don't fight it)
3. Normal risk management applies
4. Use other indicators for timing

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| At extreme (0-25 or 75-100) | +30% |
| Multiple consecutive days at extreme | +25% |
| Price diverging from sentiment | +20% |
| Supporting technical signals | +15% |
| Volume confirmation | +10% |

## Limitations
- Fear-greed can stay extreme for extended periods
- Use as contrarian indicator, not timing tool
- Combine with technical/fundamental analysis
- Best for multi-week to multi-month views
