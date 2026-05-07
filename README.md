# Bourse360 — Ghana Markets Terminal

**Real-time Ghana Stock Exchange analytics terminal built with Python & Streamlit.**

Developed by **Bismark N. G. Ababio** · BismarkDataLab Inc

---

## Features
- Live GSE stock prices with auto-refresh
- Market heatmap — colour-coded by performance
- AI signal panel — BUY/SELL/HOLD for all equities
- Portfolio simulator — historical return calculator
- Advanced charts — Robinhood-style with RSI, MACD, Bollinger Bands
- Daily market review report
- Sector analysis & bubble map
- Multi-stock comparison with correlation matrix
- Portfolio tracker with P&L
- Company profiles, directors, office addresses
- Finance news (Ghana, Reuters, BBC)
- Real-time ticker tape

## Run locally
```bash
cd GSE_Analytics
streamlit run app.py
```

## Deploy
See [share.streamlit.io](https://share.streamlit.io) — connect GitHub repo, point to `app.py`.

## Data
- Primary: [dev.kwayisi.org/apis/gse](https://dev.kwayisi.org/apis/gse)
- Fallback: african-markets.com
- History: `gse_history.csv` (auto-built daily)

## License
© 2026 BismarkDataLab Inc. All rights reserved.
