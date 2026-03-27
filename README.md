# QuantBack Pro

QuantBack Pro is a professional Streamlit-based research terminal for designing, testing, and reviewing algorithmic trading strategies with institutional-style analytics, strategy diagnostics, and AI-assisted commentary.

Built by Sourish Dey  
Portfolio: https://sourishdeyportfolio.vercel.app/

## Overview

QuantBack Pro is designed for fast iterative strategy research. It combines market data ingestion, technical signal generation, portfolio simulation, walk-forward validation, AI interpretation, and rich interactive visualization in a single workflow.

The app is built for traders, students, quant researchers, and portfolio experimenters who want a practical backtesting environment that is easy to run locally and still feels polished enough for serious review sessions.

## Highlights

- Professional backtesting dashboard built with Streamlit and Plotly
- Five built-in trading strategies with configurable parameters
- Detailed performance metrics including Sharpe, Sortino, CAGR, drawdown, win rate, and profit factor
- Walk-forward analysis to assess robustness and reduce overfitting risk
- AI-powered strategy review using Gemini
- Large visualization library with strategy-specific chart packs
- Candlestick-driven metrics gallery for technical review
- Searchable ticker menu with 200+ large-cap symbols
- Multi-provider market data fallback workflow

## Built-In Strategies

- Moving Average Crossover
- RSI Momentum
- MACD Crossover
- Mean Reversion
- RSI + MACD

Each strategy is configurable from the sidebar and produces signal-aware charts tailored to its indicator logic.

## Feature Set

### Research Workflow

- Select a stock from the curated ticker universe
- Configure time range, capital, and strategy parameters
- Run a backtest with realistic position handling, commission, and slippage
- Review equity curve, drawdown, trade history, and indicator-specific visuals
- Inspect walk-forward stability and overfitting signals
- Generate AI commentary for strengths, weaknesses, and improvement ideas

### Analytics

- Portfolio equity curve
- Drawdown and underwater analysis
- Rolling volatility and rolling Sharpe
- Trade P&L distributions
- Walk-forward comparison charts
- Strategy-specific visualization packs
- Metrics candlestick gallery

### AI Analysis

Gemini is used for:

- strategy assessment
- risk review
- improvement suggestions
- report-style commentary

The app reads `GEMINI_API_KEY` and `GEMINI_MODEL` from the local `.env` file.

## Tech Stack

- Python
- Streamlit
- Plotly
- Pandas
- NumPy
- yfinance
- Google GenAI SDK

## Project Structure

```text
Quantback Pro/
|-- app.py
|-- quantback_core.py
|-- strategies.py
|-- data_engine.py
|-- walk_forward.py
|-- visualizations.py
|-- llm_integration.py
|-- config.py
|-- requirements.txt
|-- .env
|-- README.md
```

## Installation

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -U -r requirements.txt
```

### 3. Configure environment variables

Add the following to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Run the app

```powershell
streamlit run app.py
```

## Usage

### Quick Start

1. Launch the Streamlit app.
2. Choose a ticker from the dropdown.
3. Select a strategy.
4. Adjust the capital, date range, and indicator parameters.
5. Run the backtest.
6. Review charts, metrics, walk-forward output, and AI analysis.

### Interpreting Results

- `Total Return` shows cumulative strategy return over the selected period.
- `Sharpe Ratio` reflects return relative to volatility.
- `Max Drawdown` shows worst peak-to-trough loss.
- `Win Rate` shows the share of profitable closed trades.
- `Walk-Forward Analysis` helps judge robustness rather than raw performance.

If walk-forward metrics show `N/A`, the selected period likely does not provide enough data to form valid train/test windows. A longer range such as 3 to 5 years is recommended.

## Data Notes

The application uses a fallback-oriented market data workflow so common symbols can still load when one provider is unavailable. Daily backtests prefer a more resilient route before falling back to Yahoo-style fetches.

If data still fails to load, the app will display a direct error message describing the provider failure.

## Visualization Experience

QuantBack Pro includes both core performance analytics and strategy-native chart packs.

Examples include:

- candlestick price action charts
- buy and sell signal overlays
- moving average spread diagnostics
- RSI signal maps
- MACD structure charts
- Bollinger Band positioning
- signal transition views
- monthly return heatmaps
- trade-level P&L analysis
- candlestick metrics gallery

## Professional Positioning

This project is suitable for:

- personal quant research portfolios
- interview demos
- strategy prototyping
- student quant labs
- trading dashboard case studies

## Roadmap Ideas

- benchmark comparison support
- exportable PDF research reports
- parameter sweep dashboards
- multi-asset portfolio testing
- broker integration for paper trading
- regime classification overlays

## Disclaimer

This project is for educational and research purposes only. Backtest results do not guarantee future performance. Always validate on out-of-sample data and apply proper risk management before using any strategy in live trading.

## Contact

Sourish Dey  
Portfolio: https://sourishdeyportfolio.vercel.app/
