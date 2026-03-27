"""
QuantBack Pro - Complete Example Workflow
Demonstrates how to use all components end-to-end
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import our modules
from quantback_core import BacktestEngine, OrderType, OrderSide
from strategies import MovingAverageCrossover, RSIMomentum
from data_engine import DataFetcher, DataProcessor, DataValidator
from walk_forward import WalkForwardAnalyzer
from visualizations import VisualizationEngine
from llm_integration import LLMAnalyzer


def example_basic_backtest():
    """Example 1: Basic backtest workflow"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Moving Average Crossover Backtest")
    print("=" * 60)
    
    # Step 1: Fetch data
    print("\n📡 Fetching AAPL data...")
    ticker = "AAPL"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    
    data = DataFetcher.fetch_ohlcv(ticker, start_date, end_date)
    print(f"✅ Fetched {len(data)} days of data")
    print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    # Step 2: Validate data
    print("\n🔍 Validating data...")
    is_valid = DataValidator.validate_data(data)
    print(f"✅ Data validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Step 3: Prepare data
    print("\n📊 Preparing data with indicators...")
    data = DataProcessor.prepare_for_backtest(data, add_indicators=True)
    print(f"✅ Added technical indicators")
    print(f"   Columns: {', '.join(data.columns.tolist()[:10])}")
    
    # Step 4: Create strategy
    print("\n🎯 Creating Moving Average Crossover strategy...")
    strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
    signals = strategy.generate_signals(data)
    print(f"✅ Generated signals")
    print(f"   Buy signals: {(signals['signal'] == 1).sum()}")
    print(f"   Sell signals: {(signals['signal'] == -1).sum()}")
    
    # Step 5: Run backtest
    print("\n⚙️ Running backtest engine...")
    engine = BacktestEngine(
        initial_cash=100000,
        slippage_pct=0.001,  # 0.1%
        commission_pct=0.001,  # 0.1%
    )
    
    for idx in range(1, len(signals)):
        row = signals.iloc[idx]
        prev_row = signals.iloc[idx - 1]
        timestamp = signals.index[idx]
        
        # Process orders
        engine.process_orders(row, ticker, timestamp)
        
        # Generate new orders
        if prev_row.get('position', 0) == 1:  # Buy signal
            quantity = int(engine.portfolio.cash / row['close'] * 0.95)
            if quantity > 0:
                engine.place_order(
                    timestamp=timestamp,
                    asset=ticker,
                    side=OrderSide.BUY,
                    quantity=quantity,
                    order_type=OrderType.MARKET,
                )
        
        elif prev_row.get('position', 0) == -1:  # Sell signal
            position = engine.portfolio.get_position(ticker)
            if position.quantity > 0:
                engine.place_order(
                    timestamp=timestamp,
                    asset=ticker,
                    side=OrderSide.SELL,
                    quantity=position.quantity,
                    order_type=OrderType.MARKET,
                )
        
        # Update portfolio
        current_prices = {ticker: row['close']}
        engine.portfolio.update_unrealized(current_prices)
        engine.portfolio.get_total_equity(current_prices, timestamp)
    
    print(f"✅ Backtest completed")
    
    # Step 6: Get statistics
    print("\n📈 Performance Statistics:")
    stats = engine.get_portfolio_stats()
    print(f"   Total Return: {stats.get('total_return', 0)*100:.2f}%")
    print(f"   CAGR: {stats.get('cagr', 0)*100:.2f}%")
    print(f"   Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}")
    print(f"   Sortino Ratio: {stats.get('sortino_ratio', 0):.2f}")
    print(f"   Max Drawdown: {stats.get('max_drawdown', 0)*100:.2f}%")
    print(f"   Win Rate: {stats.get('win_rate', 0)*100:.2f}%")
    print(f"   Total Trades: {stats.get('total_trades', 0)}")
    
    return engine, signals, stats


def example_walk_forward_analysis():
    """Example 2: Walk-forward validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Walk-Forward Analysis")
    print("=" * 60)
    
    # Fetch data
    data = DataFetcher.fetch_ohlcv("MSFT", "2021-01-01", "2024-01-01")
    data = DataProcessor.prepare_for_backtest(data)
    
    # Create windows
    print("\n📅 Creating walk-forward windows...")
    windows = WalkForwardAnalyzer.create_windows(
        data,
        train_period_days=252,  # 1 year training
        test_period_days=63,    # 3 months testing
        step_days=63,           # Quarterly rebalance
    )
    print(f"✅ Created {len(windows)} rolling windows")
    
    # Analyze each window
    print("\n🔍 Analyzing each window...")
    window_stats = []
    for i, window in enumerate(windows):
        train_stats, test_stats = WalkForwardAnalyzer.analyze_window(window)
        window_stats.append({
            'window': i,
            'train_sharpe': train_stats.get('sharpe_ratio', 0),
            'test_sharpe': test_stats.get('sharpe_ratio', 0),
            'train_return': train_stats.get('total_return', 0),
            'test_return': test_stats.get('total_return', 0),
        })
        print(f"   Window {i}: Train Sharpe={train_stats.get('sharpe_ratio', 0):.2f}, "
              f"Test Sharpe={test_stats.get('sharpe_ratio', 0):.2f}")
    
    # Detect overfitting
    print("\n⚠️ Overfitting Detection:")
    overfitting = WalkForwardAnalyzer.detect_overfitting(windows)
    print(f"   Is Overfit: {overfitting.get('is_overfit', False)}")
    print(f"   Sharpe Degradation: {overfitting.get('sharpe_degradation', 0)*100:.2f}%")
    print(f"   Train Sharpe Stability: {overfitting.get('train_sharpe_stability', 0):.2f}")
    print(f"   Test Sharpe Stability: {overfitting.get('test_sharpe_stability', 0):.2f}")
    
    return windows, overfitting


def example_multiple_strategies():
    """Example 3: Compare multiple strategies"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Comparing Multiple Strategies")
    print("=" * 60)
    
    # Fetch data
    data = DataFetcher.fetch_ohlcv("GOOGL", "2023-01-01", "2024-01-01")
    data = DataProcessor.prepare_for_backtest(data)
    
    strategies = {
        "MA Crossover (20/50)": MovingAverageCrossover(20, 50),
        "MA Crossover (10/30)": MovingAverageCrossover(10, 30),
        "RSI Momentum": RSIMomentum(rsi_period=14, oversold=30, overbought=70),
    }
    
    results = {}
    
    for strategy_name, strategy in strategies.items():
        print(f"\n🎯 Testing {strategy_name}...")
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Run backtest (simplified)
        engine = BacktestEngine(initial_cash=100000)
        
        # ... execution loop (simplified for example) ...
        
        stats = engine.get_portfolio_stats()
        results[strategy_name] = stats
        
        print(f"   Sharpe: {stats.get('sharpe_ratio', 0):.2f}")
        print(f"   Return: {stats.get('total_return', 0)*100:.2f}%")
        print(f"   Win Rate: {stats.get('win_rate', 0)*100:.2f}%")
    
    # Compare
    print("\n📊 Strategy Comparison:")
    print("-" * 60)
    for name, stats in results.items():
        print(f"{name:30s} | Sharpe: {stats.get('sharpe_ratio', 0):6.2f} | "
              f"Return: {stats.get('total_return', 0)*100:7.2f}% | "
              f"Win Rate: {stats.get('win_rate', 0)*100:6.2f}%")
    
    return results


def example_parameter_optimization():
    """Example 4: Test different parameters"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Parameter Optimization")
    print("=" * 60)
    
    # Fetch data
    data = DataFetcher.fetch_ohlcv("TSLA", "2023-01-01", "2024-01-01")
    data = DataProcessor.prepare_for_backtest(data)
    
    print("\n🔧 Testing Moving Average Crossover with different parameters...")
    
    best_sharpe = -np.inf
    best_params = None
    results = []
    
    for fast in [10, 15, 20, 25, 30]:
        for slow in [40, 50, 60, 70, 80]:
            if fast >= slow:
                continue
            
            strategy = MovingAverageCrossover(fast, slow)
            signals = strategy.generate_signals(data)
            
            # Run backtest (simplified)
            engine = BacktestEngine(initial_cash=100000)
            stats = engine.get_portfolio_stats()
            
            sharpe = stats.get('sharpe_ratio', 0)
            results.append({
                'fast': fast,
                'slow': slow,
                'sharpe': sharpe,
                'return': stats.get('total_return', 0),
            })
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = (fast, slow)
    
    # Sort and display top 5
    results.sort(key=lambda x: x['sharpe'], reverse=True)
    
    print("\n📈 Top 5 Parameter Combinations:")
    for i, result in enumerate(results[:5]):
        print(f"   {i+1}. Fast={result['fast']}, Slow={result['slow']} | "
              f"Sharpe={result['sharpe']:.2f} | Return={result['return']*100:.2f}%")
    
    return results


def example_with_ai_analysis():
    """Example 5: Get AI insights"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: AI-Powered Analysis")
    print("=" * 60)
    
    # Example stats from a backtest
    stats = {
        'total_return': 0.45,
        'cagr': 0.35,
        'sharpe_ratio': 2.1,
        'sortino_ratio': 3.2,
        'max_drawdown': -0.15,
        'win_rate': 0.65,
        'profit_factor': 2.5,
    }
    
    overfitting = {
        'avg_train_sharpe': 2.5,
        'avg_test_sharpe': 1.8,
        'sharpe_degradation': 0.28,
        'is_overfit': False,
    }
    
    print("\n🧠 Requesting AI analysis...")
    print("   (Note: Requires ANTHROPIC_API_KEY environment variable)")
    
    try:
        analyzer = LLMAnalyzer()
        analysis = analyzer.analyze_strategy(
            strategy_name="Moving Average Crossover",
            ticker="AAPL",
            stats=stats,
            overfitting_analysis=overfitting,
            trade_count=150,
        )
        
        print("\n📋 AI Analysis Results:")
        print("-" * 60)
        print(analysis)
    
    except Exception as e:
        print(f"❌ AI analysis failed: {str(e)}")
        print("   Make sure ANTHROPIC_API_KEY is set")


def main():
    """Run all examples"""
    print("\n" + "🚀 " * 20)
    print("QuantBack Pro - Complete Workflow Examples")
    print("🚀 " * 20 + "\n")
    
    # Example 1: Basic backtest
    try:
        engine, signals, stats = example_basic_backtest()
    except Exception as e:
        print(f"❌ Example 1 failed: {str(e)}")
    
    # Example 2: Walk-forward
    try:
        windows, overfitting = example_walk_forward_analysis()
    except Exception as e:
        print(f"❌ Example 2 failed: {str(e)}")
    
    # Example 3: Multiple strategies
    try:
        results = example_multiple_strategies()
    except Exception as e:
        print(f"❌ Example 3 failed: {str(e)}")
    
    # Example 4: Parameter optimization
    try:
        param_results = example_parameter_optimization()
    except Exception as e:
        print(f"❌ Example 4 failed: {str(e)}")
    
    # Example 5: AI analysis
    try:
        example_with_ai_analysis()
    except Exception as e:
        print(f"❌ Example 5 failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Launch the web UI: streamlit run app.py")
    print("  2. Explore different strategies and parameters")
    print("  3. Review the visualizations and AI insights")
    print("  4. Build your own custom strategies!")
    print("\n")


if __name__ == "__main__":
    main()
