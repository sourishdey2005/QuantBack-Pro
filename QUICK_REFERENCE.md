# ⚡ QuantBack Pro - Quick Reference Guide

## 🚀 Launch in 30 Seconds

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_key"
streamlit run app.py
```

Visit: `http://localhost:8501`

---

## 📋 Common Tasks

### 1. Run a Quick Backtest

```python
from data_engine import DataFetcher, DataProcessor
from strategies import MovingAverageCrossover
from quantback_core import BacktestEngine, OrderType, OrderSide

# Fetch data
data = DataFetcher.fetch_ohlcv('AAPL', '2023-01-01', '2024-01-01')
data = DataProcessor.prepare_for_backtest(data)

# Create strategy
strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
signals = strategy.generate_signals(data)

# Run backtest
engine = BacktestEngine(initial_cash=100000)
for idx in range(1, len(signals)):
    # Your trading logic here
    pass

stats = engine.get_portfolio_stats()
print(f"Sharpe: {stats['sharpe_ratio']:.2f}")
```

### 2. Test Multiple Strategies

```python
from strategies import (
    MovingAverageCrossover, RSIMomentum, MACDCrossover,
    MeanReversion, CombinedRSIMACD
)

strategies = {
    'MA': MovingAverageCrossover(20, 50),
    'RSI': RSIMomentum(14, 30, 70),
    'MACD': MACDCrossover(12, 26, 9),
    'MR': MeanReversion(20, 2.0),
    'Combo': CombinedRSIMACD(14, 12, 26),
}

for name, strategy in strategies.items():
    signals = strategy.generate_signals(data)
    # Run backtest...
```

### 3. Perform Walk-Forward Analysis

```python
from walk_forward import WalkForwardAnalyzer

windows = WalkForwardAnalyzer.create_windows(
    data,
    train_period_days=252,
    test_period_days=63,
    step_days=63,
)

for window in windows:
    train_stats, test_stats = WalkForwardAnalyzer.analyze_window(window)
    print(f"Train Sharpe: {train_stats['sharpe_ratio']:.2f}")
    print(f"Test Sharpe: {test_stats['sharpe_ratio']:.2f}")

overfitting = WalkForwardAnalyzer.detect_overfitting(windows)
print(f"Overfit: {overfitting['is_overfit']}")
```

### 4. Get AI Analysis

```python
from llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer()
analysis = analyzer.analyze_strategy(
    strategy_name="Moving Average Crossover",
    ticker="AAPL",
    stats=stats,
    overfitting_analysis=overfitting,
    trade_count=150,
)
print(analysis)
```

### 5. Create Custom Visualizations

```python
from visualizations import VisualizationEngine

# Equity curve
fig = VisualizationEngine.create_equity_curve(
    engine.portfolio.equity_curve,
    engine.portfolio.timestamps
)
fig.show()

# Price with signals
fig = VisualizationEngine.create_price_with_signals(
    data,
    signal_column='signal',
    ma_columns=['sma_20', 'sma_50']
)
fig.show()

# Metrics table
fig = VisualizationEngine.create_performance_metrics_table(stats)
fig.show()
```

### 6. Optimize Parameters

```python
results = []

for fast in range(10, 50, 5):
    for slow in range(50, 200, 10):
        strategy = MovingAverageCrossover(fast, slow)
        signals = strategy.generate_signals(data)
        engine = BacktestEngine(initial_cash=100000)
        
        # Run backtest...
        stats = engine.get_portfolio_stats()
        
        results.append({
            'fast': fast,
            'slow': slow,
            'sharpe': stats['sharpe_ratio'],
            'return': stats['total_return'],
        })

# Find best
best = max(results, key=lambda x: x['sharpe'])
print(f"Best: Fast={best['fast']}, Slow={best['slow']}")
```

### 7. Add Technical Indicators

```python
from data_engine import DataProcessor

# Add individual indicators
data = DataProcessor.add_sma(data, periods=[20, 50, 200])
data = DataProcessor.add_ema(data, periods=[12, 26])
data = DataProcessor.add_rsi(data, period=14)
data = DataProcessor.add_macd(data)
data = DataProcessor.add_bollinger_bands(data)
data = DataProcessor.add_atr(data)

# Or use prepare_for_backtest (includes all)
data = DataProcessor.prepare_for_backtest(data)
```

### 8. Custom Strategy

```python
from strategies import Strategy

class MyStrategy(Strategy):
    def generate_signals(self, data):
        data = data.copy()
        
        # Entry: Price crosses above 20-day SMA
        # Exit: Price crosses below 50-day SMA
        
        data['signal'] = 0
        above_20 = data['close'] > data['sma_20']
        above_50 = data['close'] > data['sma_50']
        
        data.loc[above_20 & above_50, 'signal'] = 1  # Buy
        data.loc[~above_20 | ~above_50, 'signal'] = -1  # Sell
        
        data['position'] = data['signal'].diff()
        return data

# Use it
strategy = MyStrategy()
signals = strategy.generate_signals(data)
```

---

## 📊 Key Metrics Explained

```
Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
              Higher is better
              > 1.0 is good
              > 2.0 is excellent

Sortino Ratio = Return / Downside Volatility
               Like Sharpe but only penalizes losses
               > 1.5 is good

Max Drawdown = Maximum peak-to-trough decline
              < -20% is acceptable
              < -10% is excellent

Win Rate = Winning Trades / Total Trades
          > 50% means more wins than losses
          > 60% is very good

Profit Factor = Gross Profit / Gross Loss
               > 1.5 means 1.5x more profit than loss
               > 2.0 is excellent
```

---

## 🔧 Configuration Presets

### Aggressive (High Risk, High Reward)
```python
from config import AGGRESSIVE_CONFIG
# Larger positions, wider stops, bigger targets
```

### Conservative (Low Risk, Low Reward)
```python
from config import CONSERVATIVE_CONFIG
# Smaller positions, tight stops, modest targets
```

### Research (Optimal for testing)
```python
from config import RESEARCH_CONFIG
# Low fees, extensive walk-forward analysis
```

---

## 🎯 Strategy Comparison

| Strategy | Best For | Entry | Exit |
|----------|----------|-------|------|
| **MA Crossover** | Trending | Fast > Slow | Fast < Slow |
| **RSI** | Reversals | RSI < 30 | RSI > 70 |
| **MACD** | Momentum | Hist > 0 | Hist < 0 |
| **Mean Rev** | Extremes | Price < Lower | Price > Upper |
| **RSI+MACD** | Confirmation | Both bullish | Both bearish |

---

## 📈 Performance Targets

```
Minimum acceptable:
- Sharpe Ratio: 1.0
- Win Rate: 50%
- Max Drawdown: -25%
- Profit Factor: 1.2

Good performance:
- Sharpe Ratio: 1.5+
- Win Rate: 55%+
- Max Drawdown: -15%
- Profit Factor: 1.8+

Excellent performance:
- Sharpe Ratio: 2.0+
- Win Rate: 60%+
- Max Drawdown: -10%
- Profit Factor: 2.5+
```

---

## 🐛 Debugging Tips

### Check data quality
```python
from data_engine import DataValidator

stats = DataValidator.get_data_stats(data)
print(f"Days: {stats['total_days']}")
print(f"Missing: {stats['missing_values']}")
print(f"Price range: {stats['price_range']}")
```

### Check for overfitting
```python
degradation = overfitting['sharpe_degradation']
if degradation > 0.30:
    print("⚠️ WARNING: Strategy may be overfitted")
else:
    print("✅ Good robustness")
```

### Validate signals
```python
print(f"Buy signals: {(signals['signal'] == 1).sum()}")
print(f"Sell signals: {(signals['signal'] == -1).sum()}")
print(f"Hold days: {(signals['signal'] == 0).sum()}")
```

### Check execution
```python
print(f"Total trades: {len(engine.portfolio.trade_history)}")
print(f"Avg trade duration: {np.mean([t.days_held for t in engine.portfolio.trade_history])}")
print(f"Largest win: {max([t.pnl for t in engine.portfolio.trade_history])}")
print(f"Largest loss: {min([t.pnl for t in engine.portfolio.trade_history])}")
```

---

## ⚠️ Common Mistakes to Avoid

1. **Look-ahead bias**
   - ❌ Using future data in signals
   - ✅ Only use data up to current bar

2. **Overfitting**
   - ❌ Optimizing on entire dataset
   - ✅ Use walk-forward validation

3. **Ignoring costs**
   - ❌ Backtesting with 0% slippage
   - ✅ Use realistic 0.05-0.1% slippage

4. **Insufficient data**
   - ❌ Backtesting with 50 data points
   - ✅ Use at least 1-2 years of data

5. **Curve fitting**
   - ❌ Too many parameters
   - ✅ Keep strategies simple

6. **Market regime changes**
   - ❌ Testing only bull markets
   - ✅ Test across multiple market conditions

---

## 📱 Streamlit Tips

### Run multiple apps
```bash
streamlit run app.py --logger.level=error
```

### Clear cache
```bash
streamlit cache clear
```

### Remote deployment
```bash
# Streamlit Cloud
streamlit run app.py --client.showErrorDetails=false
```

---

## 🔗 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python
- **Pandas Docs**: https://pandas.pydata.org/docs
- **NumPy Docs**: https://numpy.org/doc
- **yfinance Docs**: https://github.com/ranaroussi/yfinance
- **Anthropic API**: https://docs.anthropic.com

---

## 💡 Pro Tips

1. **Start simple** - Test basic strategies first
2. **Document everything** - Comments help future you
3. **Version control** - Use git to track changes
4. **Keep logs** - Record all backtest results
5. **Validate thoroughly** - Don't skip walk-forward
6. **Test edge cases** - What about crashes/gaps?
7. **Paper trade first** - Before real money
8. **Monitor live** - Markets change, strategies may not

---

## 🚨 When to Reject a Strategy

Stop developing if you see:
- ❌ Sharpe ratio < 0.5
- ❌ Win rate < 40%
- ❌ Max drawdown > -40%
- ❌ Profit factor < 1.0
- ❌ Overfitting degradation > 50%
- ❌ Few trades (less than 20)
- ❌ Clustering (all trades in specific period)

---

## ✅ Checklist Before Live Trading

- [ ] Tested on multiple years of data
- [ ] Walk-forward validation passed
- [ ] Sharpe ratio > 1.5
- [ ] Max drawdown acceptable (-15% or less)
- [ ] Win rate > 55%
- [ ] Profit factor > 1.8
- [ ] Zero look-ahead bias
- [ ] Realistic slippage/commission
- [ ] Paper traded for 2+ weeks
- [ ] Risk per trade acceptable
- [ ] Stop loss in place
- [ ] Position size appropriate
- [ ] Market conditions favorable
- [ ] Backup plan if market crashes

---

**Last updated**: March 27, 2026  
**Version**: 1.0.0
