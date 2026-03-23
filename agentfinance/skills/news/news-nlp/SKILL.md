---
name: news-nlp
description: >
  NLP-based news analysis for trading. Use when analyzing news headlines and articles
  for sentiment, market impact prediction, and breaking news response.
---

# News NLP Skill

NLP processes financial news to extract sentiment and predict market impact.

## NLP Pipeline

```
Raw News → Text Cleaning → Tokenization → Sentiment Analysis → Impact Scoring → Trade Signal
```

## Key NLP Components

### Sentiment Scoring
- **Positive/Negative/Neutral**: Overall sentiment direction
- **Score Range**: -1.0 (very negative) to +1.0 (very positive)
- **Confidence**: How certain the model is (0-100%)

### Named Entity Recognition (NER)
- Companies, people, places, organizations
- Central banks, institutions
- Countries, currencies

### Impact Prediction
| Impact | Score | Example |
|--------|-------|---------|
| Very High | > 8 | Fed emergency cut |
| High | 6-8 | NFP big miss/beat |
| Medium | 4-6 | Company earnings |
| Low | 2-4 | Routine release |
| Very Low | < 2 | Minor data |

## Trading Rules

### High-Impact News
1. **Breaking news**: React immediately to direction
2. **Expected news**: Trade the surprise (actual vs forecast)
3. **Market already positioned**: Fade the move if overdone

### News Sentiment Trades
1. **Bullish headline + positive price reaction** → Confirm buy
2. **Bearish headline + price not falling** → Watch for breakout
3. **Headlines improving + price falling** → Divergence, potential reversal
4. **Headlines worsening + price rising** → Divergence, potential reversal

### Time-Based Rules
- **Pre-market**: React to overnight news
- **Intraday**: React to breaking news
- **Post-market**: Position for next day

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Multiple sources confirm | +30% |
| Major outlets/reuters | +20% |
| Named entity clarity | +15% |
| Sentiment score extreme | +20% |
| Historical pattern match | +15% |

## Data Sources
- Reuters, Bloomberg (paid)
- NewsAPI (free tier)
- Alpha Vantage News
- TradingEconomics
- FRED/ederal Reserve news
