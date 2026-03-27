"""
QuantBack Pro - Main Streamlit Application
Interactive backtesting dashboard with AI insights
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Optional

# Import our modules
from quantback_core import BacktestEngine, OrderType, OrderSide
from strategies import (
    MovingAverageCrossover, 
    RSIMomentum, 
    MACDCrossover, 
    MeanReversion,
    CombinedRSIMACD
)
from data_engine import DataFetcher, DataProcessor, DataValidator
from walk_forward import WalkForwardAnalyzer
from visualizations import VisualizationEngine
from llm_integration import LLMAnalyzer


# Page configuration
st.set_page_config(
    page_title="QuantBack Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
        :root {
            --qb-bg: #07111f;
            --qb-panel: rgba(10, 20, 38, 0.88);
            --qb-border: rgba(95, 214, 255, 0.24);
            --qb-accent: #8bf3ff;
            --qb-accent-2: #18c8c1;
            --qb-text: #f5fbff;
            --qb-muted: #96abc2;
        }
        .main {
            background:
                radial-gradient(circle at top left, rgba(24, 200, 193, 0.14), transparent 28%),
                radial-gradient(circle at top right, rgba(139, 243, 255, 0.12), transparent 24%),
                linear-gradient(180deg, #06101c 0%, #091728 42%, #07111f 100%);
            color: var(--qb-text);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 999px;
            padding: 10px 18px;
        }
        .metric-box {
            background-color: rgba(0, 255, 65, 0.1);
            border: 1px solid #00FF41;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }
        .metric-box.loss {
            background-color: rgba(255, 0, 110, 0.1);
            border-color: #FF006E;
        }
        .metric-box.neutral {
            background-color: rgba(0, 217, 255, 0.1);
            border-color: #00D9FF;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
            border: 1px solid rgba(139, 243, 255, 0.12);
            border-radius: 18px;
            padding: 14px 12px;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }
        .qb-hero {
            position: relative;
            overflow: hidden;
            margin: 0 0 22px 0;
            padding: 34px 34px 28px;
            border-radius: 28px;
            border: 1px solid var(--qb-border);
            background:
                radial-gradient(circle at 12% 18%, rgba(139, 243, 255, 0.18), transparent 18%),
                linear-gradient(135deg, rgba(9, 24, 41, 0.96), rgba(9, 19, 34, 0.90));
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
        }
        .qb-hero:before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.04), transparent);
            transform: translateX(-100%);
            animation: qb-sheen 7s linear infinite;
        }
        .qb-kicker {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(139, 243, 255, 0.08);
            border: 1px solid rgba(139, 243, 255, 0.18);
            color: var(--qb-accent);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .qb-title {
            margin: 16px 0 10px;
            color: var(--qb-text);
            font-size: 3rem;
            line-height: 1.02;
            font-weight: 800;
            letter-spacing: -0.04em;
        }
        .qb-subtitle {
            max-width: 820px;
            color: var(--qb-muted);
            font-size: 1.04rem;
            line-height: 1.7;
            margin: 0 0 18px;
        }
        .qb-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }
        .qb-pill {
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--qb-text);
            font-size: 0.85rem;
        }
        .qb-link {
            color: var(--qb-accent);
            text-decoration: none;
            font-weight: 600;
        }
        .qb-link:hover {
            color: #ffffff;
        }
        .qb-strategy-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }
        .qb-strategy-card {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.02));
            border: 1px solid rgba(139, 243, 255, 0.12);
            border-radius: 20px;
            padding: 18px 18px 16px;
            min-height: 220px;
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.16);
        }
        .qb-strategy-title {
            color: var(--qb-text);
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .qb-strategy-desc {
            color: var(--qb-muted);
            font-size: 0.92rem;
            line-height: 1.65;
            margin-bottom: 12px;
        }
        .qb-strategy-line {
            color: var(--qb-text);
            font-size: 0.9rem;
            line-height: 1.65;
            margin: 4px 0;
        }
        .qb-strategy-label {
            color: var(--qb-accent);
            font-weight: 700;
        }
        @keyframes qb-sheen {
            from { transform: translateX(-100%); }
            to { transform: translateX(100%); }
        }
        footer {
            visibility: hidden;
        }
        footer:after {
            content: "Made By Sourish Dey";
            visibility: visible;
            display: block;
            position: relative;
            text-align: center;
            color: #ffffff;
            padding: 12px 0 18px;
        }
    </style>
""", unsafe_allow_html=True)



TOP_STOCK_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "BRK-B", "UNH",
    "XOM", "JPM", "V", "JNJ", "WMT", "MA", "PG", "HD", "CVX", "MRK",
    "ABBV", "KO", "PEP", "COST", "AVGO", "BAC", "LLY", "ORCL", "CSCO", "ACN",
    "MCD", "DIS", "NFLX", "AMD", "ADBE", "CRM", "TMO", "ABT", "DHR", "WFC",
    "CMCSA", "TXN", "LIN", "NKE", "PM", "BMY", "QCOM", "HON", "UPS", "AMGN",
    "RTX", "LOW", "UNP", "IBM", "INTC", "SPGI", "MS", "CAT", "GS", "BLK",
    "BA", "MDT", "PLD", "DE", "GE", "ISRG", "NOW", "SYK", "ADP", "BKNG",
    "C", "LMT", "GILD", "AXP", "AMAT", "SBUX", "MMM", "T", "VZ", "PGR",
    "ETN", "CB", "ELV", "SCHW", "TJX", "MO", "USB", "FI", "PANW", "MU",
    "ZTS", "CCI", "SO", "DUK", "COP", "EOG", "ADI", "KLAC", "ANET", "CRWD",
    "SNPS", "CDNS", "MAR", "APD", "ICE", "CME", "AON", "MMC", "CI", "HUM",
    "AEP", "D", "F", "GM", "HCA", "CVS", "SLB", "MCK", "PNC", "KMI",
    "NEM", "SHW", "EMR", "GD", "EW", "PSX", "MPC", "OXY", "ROP", "RSG",
    "NSC", "FCX", "ITW", "FDX", "REGN", "ADSK", "AIG", "NOC", "KMB", "CL",
    "DG", "ROST", "ORLY", "O", "SPG", "MCO", "WM", "AFL", "MET", "TRV",
    "PRU", "ALL", "COF", "BK", "STT", "TFC", "FITB", "RF", "KEY", "HBAN",
    "CFG", "PYPL", "SHOP", "NXPI", "MCHP", "MRVL", "ON", "QRVO", "SWKS", "TER",
    "MPWR", "LRCX", "PFE", "BIIB", "VRTX", "MRNA", "ILMN", "IDXX", "CMG", "YUM",
    "DPZ", "SYY", "KR", "GIS", "KHC", "CAG", "HSY", "MNST", "UAL", "DAL",
    "AAL", "LUV", "EXPE", "ABNB", "RIVN", "PH", "CARR", "OTIS", "TT", "JCI",
    "PCAR", "PAYX", "INTU", "TEAM", "DOCU", "ZM", "DDOG", "NET", "DVN", "APA",
    "FANG", "HAL", "BKR", "NEE", "EXC", "XEL", "SRE", "PEG", "EIX", "ED",
    "WEC", "AMT", "EQIX", "PSA", "DLR", "WELL", "VICI", "EQR", "AVB", "UBER",
    "LYFT", "SNAP", "PINS", "RBLX", "WDAY", "SNOW", "PLTR", "ARM", "SMCI", "DELL",
    "HPQ", "EA", "TTWO", "ROKU", "SONY", "BABA", "PDD", "NIO", "LI", "XPEV",
    "JD", "BIDU", "ASML", "TSM", "SQ", "BILL", "AFRM", "SOFI", "HOOD",
]

def initialize_session():
    """Initialize Streamlit session state"""
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'ai_analysis' not in st.session_state:
        st.session_state.ai_analysis = None


def run_backtest(
    ticker: str,
    strategy_name: str,
    start_date: str,
    end_date: str,
    initial_cash: float,
    strategy_params: dict,
) -> dict:
    """Run complete backtest with all analysis"""
    
    with st.spinner("🔄 Fetching market data..."):
        # Fetch data
        data = DataFetcher.fetch_ohlcv(ticker, start_date, end_date)
        
        if data.empty:
            details = DataFetcher.last_error or "Check ticker symbol and internet connection."
            st.error(f"❌ Failed to fetch data. {details}")
            return None
        
        # Prepare data
        data = DataProcessor.prepare_for_backtest(data, add_indicators=True)
        st.session_state.data = data
    
    with st.spinner("📊 Selecting strategy..."):
        # Create strategy
        strategy_map = {
            'Moving Average Crossover': MovingAverageCrossover(
                fast_period=strategy_params.get('fast_period', 20),
                slow_period=strategy_params.get('slow_period', 50),
            ),
            'RSI Momentum': RSIMomentum(
                rsi_period=strategy_params.get('rsi_period', 14),
                oversold=strategy_params.get('oversold', 30),
                overbought=strategy_params.get('overbought', 70),
            ),
            'MACD Crossover': MACDCrossover(
                fast=strategy_params.get('fast', 12),
                slow=strategy_params.get('slow', 26),
                signal=strategy_params.get('signal', 9),
            ),
            'Mean Reversion': MeanReversion(
                period=strategy_params.get('period', 20),
                std_dev=strategy_params.get('std_dev', 2.0),
            ),
            'RSI + MACD': CombinedRSIMACD(
                rsi_period=strategy_params.get('rsi_period', 14),
                macd_fast=strategy_params.get('macd_fast', 12),
                macd_slow=strategy_params.get('macd_slow', 26),
            ),
        }
        
        strategy = strategy_map[strategy_name]
    
    with st.spinner("🎯 Generating trading signals..."):
        # Generate signals
        signals = strategy.generate_signals(data)
    
    with st.spinner("⚙️ Running backtest engine..."):
        # Run backtest
        engine = BacktestEngine(
            initial_cash=initial_cash,
            slippage_pct=0.001,
            commission_pct=0.001,
        )
        
        for idx in range(1, len(signals)):
            row = signals.iloc[idx]
            prev_row = signals.iloc[idx - 1]
            timestamp = signals.index[idx]
            
            # Process existing orders
            engine.process_orders(row, ticker, timestamp)
            
            # Generate new orders based on signals
            position_change = prev_row.get('position', 0)

            if position_change > 0:  # Buy signal or bullish flip
                quantity = int(engine.portfolio.cash / row['close'] * 0.95)  # Use 95% of cash
                if quantity > 0:
                    engine.place_order(
                        timestamp=timestamp,
                        asset=ticker,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        order_type=OrderType.MARKET,
                    )
            
            elif position_change < 0:  # Sell signal or bearish flip
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
        
        stats = engine.get_portfolio_stats()
    
    with st.spinner("🔍 Performing walk-forward analysis..."):
        # Walk-forward analysis
        windows = WalkForwardAnalyzer.create_windows(
            data,
            train_period_days=252,
            test_period_days=63,
            step_days=63,
        )
        
        window_stats_list = []
        for window in windows:
            train_stats, test_stats = WalkForwardAnalyzer.analyze_window(window)
            window_stats_list.append({
                'train_sharpe': train_stats.get('sharpe_ratio', 0),
                'test_sharpe': test_stats.get('sharpe_ratio', 0),
                'train_return': train_stats.get('total_return', 0),
                'test_return': test_stats.get('total_return', 0),
            })
        
        overfitting_analysis = WalkForwardAnalyzer.detect_overfitting(windows)
    
    return {
        'engine': engine,
        'signals': signals,
        'stats': stats,
        'window_stats': window_stats_list,
        'overfitting': overfitting_analysis,
        'ticker': ticker,
        'strategy_name': strategy_name,
    }


def main():
    initialize_session()
    
    st.markdown(
        """
        <section class="qb-hero">
            <div class="qb-kicker">Quantitative Research Workspace</div>
            <h1 class="qb-title">QuantBack Pro</h1>
            <p class="qb-subtitle">
                Institutional-grade algorithmic trading backtesting, signal diagnostics, walk-forward validation,
                and AI-assisted strategy review in one high-conviction research terminal.
            </p>
            <div class="qb-meta">
                <span class="qb-pill">Professional Strategy Lab</span>
                <span class="qb-pill">Advanced Visual Analytics</span>
                <span class="qb-pill">Walk-Forward Robustness Checks</span>
                <span class="qb-pill">
                    Built by
                    <a class="qb-link" href="https://sourishdeyportfolio.vercel.app/" target="_blank">
                        Sourish Dey
                    </a>
                </span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    
    # Sidebar controls
    st.sidebar.header("⚙️ Configuration")
    
    # Input section
    col1, col2 = st.sidebar.columns(2)
    with col1:
        ticker = st.selectbox(
            "Ticker Symbol",
            options=TOP_STOCK_TICKERS,
            index=TOP_STOCK_TICKERS.index("AAPL"),
            key="ticker",
            help="Search by typing to quickly find one of 200+ top stocks.",
        )
    with col2:
        initial_cash = st.number_input("💰 Initial Capital ($)", value=100000, step=10000)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("📅 End Date", value=datetime.now())
    
    # Strategy selection
    strategy_name = st.sidebar.selectbox(
        "🎯 Strategy",
        [
            'Moving Average Crossover',
            'RSI Momentum',
            'MACD Crossover',
            'Mean Reversion',
            'RSI + MACD',
        ]
    )
    
    # Strategy parameters
    st.sidebar.subheader("🔧 Strategy Parameters")
    
    strategy_params = {}
    
    if strategy_name == 'Moving Average Crossover':
        strategy_params['fast_period'] = st.sidebar.slider("Fast MA Period", 5, 50, 20)
        strategy_params['slow_period'] = st.sidebar.slider("Slow MA Period", 50, 200, 50)
    
    elif strategy_name == 'RSI Momentum':
        strategy_params['rsi_period'] = st.sidebar.slider("RSI Period", 5, 30, 14)
        strategy_params['oversold'] = st.sidebar.slider("Oversold Level", 10, 40, 30)
        strategy_params['overbought'] = st.sidebar.slider("Overbought Level", 60, 90, 70)
    
    elif strategy_name == 'MACD Crossover':
        strategy_params['fast'] = st.sidebar.slider("Fast EMA", 5, 20, 12)
        strategy_params['slow'] = st.sidebar.slider("Slow EMA", 20, 50, 26)
        strategy_params['signal'] = st.sidebar.slider("Signal EMA", 5, 20, 9)
    
    elif strategy_name == 'Mean Reversion':
        strategy_params['period'] = st.sidebar.slider("BB Period", 10, 50, 20)
        strategy_params['std_dev'] = st.sidebar.slider("Std Dev", 1.0, 4.0, 2.0)
    
    elif strategy_name == 'RSI + MACD':
        strategy_params['rsi_period'] = st.sidebar.slider("RSI Period", 5, 30, 14)
        strategy_params['macd_fast'] = st.sidebar.slider("MACD Fast", 5, 20, 12)
        strategy_params['macd_slow'] = st.sidebar.slider("MACD Slow", 20, 50, 26)
    
    # Run backtest button
    if st.sidebar.button("🚀 Run Backtest", use_container_width=True):
        results = run_backtest(
            ticker=ticker.upper(),
            strategy_name=strategy_name,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_cash=initial_cash,
            strategy_params=strategy_params,
        )
        
        if results:
            st.session_state.backtest_results = results
            st.session_state.ai_analysis = None
            st.success("✅ Backtest completed successfully!")
    
    # Main content area
    if st.session_state.backtest_results:
        results = st.session_state.backtest_results
        engine = results['engine']
        stats = results['stats']
        
        # Key metrics
        st.header("📊 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_return = stats.get('total_return', 0)
            color = "green" if total_return > 0 else "red"
            st.metric("Total Return", f"{total_return*100:.2f}%", delta_color="off")
        
        with col2:
            sharpe = stats.get('sharpe_ratio', 0)
            st.metric("Sharpe Ratio", f"{sharpe:.2f}", delta_color="off")
        
        with col3:
            max_dd = stats.get('max_drawdown', 0)
            st.metric("Max Drawdown", f"{max_dd*100:.2f}%", delta_color="off")
        
        with col4:
            win_rate = stats.get('win_rate', 0)
            st.metric("Win Rate", f"{win_rate*100:.2f}%", delta_color="off")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📊 Metrics", "🔍 Walk-Forward", "🤖 AI Analysis"])
        
        with tab1:
            st.subheader("📈 Visualizations")
            
            # Equity curve
            col1, col2 = st.columns(2)
            with col1:
                equity_fig = VisualizationEngine.create_equity_curve(
                    engine.portfolio.equity_curve,
                    engine.portfolio.timestamps,
                )
                st.plotly_chart(equity_fig, use_container_width=True)
            
            with col2:
                drawdown_fig = VisualizationEngine.create_drawdown_chart(
                    engine.portfolio.equity_curve,
                    engine.portfolio.timestamps,
                )
                st.plotly_chart(drawdown_fig, use_container_width=True)
            
            # Price with signals
            price_fig = VisualizationEngine.create_price_with_signals(
                results['signals'],
                signal_column='position',
                ma_columns=['fast_ma', 'slow_ma'] if 'fast_ma' in results['signals'].columns else None,
            )
            st.plotly_chart(price_fig, use_container_width=True)
            
            # Returns distribution
            col1, col2 = st.columns(2)
            with col1:
                dist_fig = VisualizationEngine.create_return_distribution(
                    [r * 100 for r in engine.portfolio.daily_returns]
                )
                st.plotly_chart(dist_fig, use_container_width=True)
            
            with col2:
                if engine.portfolio.trade_history:
                    pnl_fig = VisualizationEngine.create_trade_pnl_histogram(
                        [t.pnl for t in engine.portfolio.trade_history]
                    )
                    st.plotly_chart(pnl_fig, use_container_width=True)
            
            # Rolling metrics
            col1, col2 = st.columns(2)
            with col1:
                sharpe_fig = VisualizationEngine.create_rolling_sharpe(
                    engine.portfolio.equity_curve,
                    window=20,
                )
                st.plotly_chart(sharpe_fig, use_container_width=True)
            
            with col2:
                vol_fig = VisualizationEngine.create_volatility_curve(
                    engine.portfolio.daily_returns,
                    window=20,
                )
                st.plotly_chart(vol_fig, use_container_width=True)

            st.subheader(f"Strategy Visualization Pack: {results['strategy_name']}")
            strategy_pack = VisualizationEngine.create_strategy_visualization_pack(
                results['signals'],
                results['strategy_name'],
                engine.portfolio.trade_history,
            )

            for idx in range(0, len(strategy_pack), 2):
                pack_col1, pack_col2 = st.columns(2)
                with pack_col1:
                    st.plotly_chart(strategy_pack[idx]['figure'], use_container_width=True)
                if idx + 1 < len(strategy_pack):
                    with pack_col2:
                        st.plotly_chart(strategy_pack[idx + 1]['figure'], use_container_width=True)
        
        with tab2:
            st.subheader("📊 Performance Metrics")
            
            metrics_fig = VisualizationEngine.create_performance_metrics_table(stats)
            st.plotly_chart(metrics_fig, use_container_width=True)

            st.subheader("Candlestick Metrics Gallery")
            candlestick_pack = VisualizationEngine.create_metrics_candlestick_pack(
                results['signals'],
                results['strategy_name'],
            )
            for idx in range(0, len(candlestick_pack), 2):
                candle_col1, candle_col2 = st.columns(2)
                with candle_col1:
                    st.plotly_chart(candlestick_pack[idx]['figure'], use_container_width=True)
                if idx + 1 < len(candlestick_pack):
                    with candle_col2:
                        st.plotly_chart(candlestick_pack[idx + 1]['figure'], use_container_width=True)
            
            # Trade analysis
            st.subheader("📋 Trade Analysis")
            if engine.portfolio.trade_history:
                trades_df = pd.DataFrame([
                    {
                        'Entry Time': t.entry_time.strftime('%Y-%m-%d'),
                        'Exit Time': t.exit_time.strftime('%Y-%m-%d'),
                        'Entry Price': f"${t.entry_price:.2f}",
                        'Exit Price': f"${t.exit_price:.2f}",
                        'Quantity': int(t.quantity),
                        'P&L': f"${t.pnl:.2f}",
                        'P&L %': f"{t.pnl_pct*100:.2f}%",
                        'Days Held': t.days_held,
                    }
                    for t in engine.portfolio.trade_history
                ])
                st.dataframe(trades_df, use_container_width=True, hide_index=True)
            else:
                st.info("No closed trades")
        
        with tab3:
            st.subheader("🔍 Walk-Forward Analysis")
            
            if results['window_stats']:
                wf_fig = VisualizationEngine.create_walk_forward_comparison(results['window_stats'])
                st.plotly_chart(wf_fig, use_container_width=True)
            else:
                st.warning("Not enough historical data to build walk-forward windows. Try a longer date range such as 3-5 years.")
            
            # Overfitting metrics
            ov = results['overfitting']
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_train_sharpe = ov.get('avg_train_sharpe')
                st.metric("Avg Train Sharpe", "N/A" if avg_train_sharpe is None else f"{avg_train_sharpe:.2f}")
            with col2:
                avg_test_sharpe = ov.get('avg_test_sharpe')
                st.metric("Avg Test Sharpe", "N/A" if avg_test_sharpe is None else f"{avg_test_sharpe:.2f}")
            with col3:
                is_overfit_value = ov.get('is_overfit')
                if is_overfit_value is None:
                    is_overfit = "N/A"
                else:
                    is_overfit = "⚠️ YES" if is_overfit_value else "✅ NO"
                st.metric("Overfitting?", is_overfit)
            
            if ov.get('message'):
                st.caption(ov['message'])
        
        with tab4:
            st.subheader("🤖 AI-Powered Analysis")
            
            if st.button("🔮 Analyze Strategy with AI"):
                with st.spinner("🧠 Analyzing..."):
                    llm = LLMAnalyzer()
                    analysis = llm.analyze_strategy(
                        strategy_name=results['strategy_name'],
                        ticker=results['ticker'],
                        stats=stats,
                        overfitting_analysis=results['overfitting'],
                        trade_count=len(engine.portfolio.trade_history),
                    )
                    st.session_state.ai_analysis = analysis or "AI analysis did not return any text."
            
            if st.session_state.ai_analysis:
                st.markdown(st.session_state.ai_analysis)
    
    else:
        st.info("👈 Configure your backtest in the sidebar and click 'Run Backtest' to begin")
        
        # Show strategy frameworks
        st.header("Strategy Frameworks")
        st.caption("A concise overview of the research models currently available in QuantBack Pro.")
        st.markdown(
            """
            <div class="qb-strategy-grid">
                <div class="qb-strategy-card">
                    <div class="qb-strategy-title">Moving Average Crossover</div>
                    <div class="qb-strategy-desc">A trend-following framework designed to capture sustained directional movement by comparing fast and slow moving averages.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Entry:</span> Long exposure is initiated when the fast moving average overtakes the slow moving average.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Exit:</span> The position is reduced when the fast average loses trend leadership and crosses back below the slow line.</div>
                </div>
                <div class="qb-strategy-card">
                    <div class="qb-strategy-title">RSI Momentum</div>
                    <div class="qb-strategy-desc">A momentum exhaustion model built for identifying short-term dislocations where price may be primed for reversal.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Entry:</span> Buy conditions appear when RSI falls beneath the configured oversold threshold.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Exit:</span> The signal exits when RSI recovers into overbought territory.</div>
                </div>
                <div class="qb-strategy-card">
                    <div class="qb-strategy-title">MACD Crossover</div>
                    <div class="qb-strategy-desc">A momentum continuation framework that monitors directional strength through MACD and signal-line interaction.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Entry:</span> Participation begins when the MACD structure turns constructive and momentum moves positive.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Exit:</span> Exposure is cut back when momentum weakens and the MACD histogram shifts negative.</div>
                </div>
                <div class="qb-strategy-card">
                    <div class="qb-strategy-title">Mean Reversion</div>
                    <div class="qb-strategy-desc">A Bollinger Band framework aimed at capturing reversion from statistically stretched price extremes back toward equilibrium.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Entry:</span> Long setups emerge when price extends below the lower volatility band.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Exit:</span> Risk is taken off when price reverts toward or through the upper band region.</div>
                </div>
                <div class="qb-strategy-card">
                    <div class="qb-strategy-title">RSI + MACD</div>
                    <div class="qb-strategy-desc">A confirmation-driven hybrid model that combines momentum positioning with directional validation for higher-conviction entries.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Entry:</span> Long bias is activated when RSI remains below its centerline while MACD reasserts positive direction.</div>
                    <div class="qb-strategy-line"><span class="qb-strategy-label">Exit:</span> The framework turns defensive when RSI strengthens above the centerline while MACD deteriorates.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
