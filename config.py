"""
QuantBack Pro - Configuration Settings
Customize behavior, parameters, and defaults
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BacktestConfig:
    """Backtesting parameters"""
    initial_cash: float = 100000.0
    slippage_pct: float = 0.001  # 0.1%
    commission_pct: float = 0.001  # 0.1%
    max_position_size_pct: float = 0.95  # Use max 95% of cash per position
    margin_multiplier: float = 1.0  # No margin by default


@dataclass
class DataConfig:
    """Data source and processing settings"""
    # API sources
    use_yfinance: bool = True
    yfinance_retry_attempts: int = 3
    yfinance_retry_delay: int = 1  # seconds
    
    # Data validation
    min_data_points: int = 20  # Minimum bars for analysis
    max_gap_days: int = 5  # Maximum days between trades
    fill_missing_data: bool = True
    fill_method: str = 'forward'  # 'forward', 'interpolate'
    
    # Indicators
    compute_sma_periods: List[int] = None  # Default [20, 50, 200]
    compute_ema_periods: List[int] = None  # Default [12, 26]
    compute_rsi_period: int = 14
    compute_macd: bool = True
    compute_bollinger_bands: bool = True
    compute_atr: bool = True


@dataclass
class StrategyConfig:
    """Strategy-specific parameters"""
    # Moving Average Crossover
    ma_crossover_fast_period: int = 20
    ma_crossover_slow_period: int = 50
    
    # RSI Momentum
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    
    # MACD
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Bollinger Bands
    bb_period: int = 20
    bb_std_dev: float = 2.0


@dataclass
class WalkForwardConfig:
    """Walk-forward analysis settings"""
    enabled: bool = True
    train_period_days: int = 252  # 1 year
    test_period_days: int = 63  # ~3 months
    step_days: int = 63  # Quarterly rebalancing
    overfitting_threshold: float = 0.30  # 30% degradation
    min_windows: int = 3


@dataclass
class RiskConfig:
    """Risk management settings"""
    # Position sizing
    position_sizing_method: str = 'fixed'  # 'fixed', 'kelly', 'volatility'
    position_size_pct: float = 0.95  # % of capital per trade
    
    # Risk limits
    max_position_loss: float = 0.02  # -2% stop loss
    profit_target: float = 0.05  # +5% target
    max_portfolio_drawdown: float = 0.20  # Stop trading if -20% drawdown
    
    # Risk metrics
    var_percentile: float = 0.95  # 95% VaR
    cvar_percentile: float = 0.95  # 95% CVaR


@dataclass
class VisualizationConfig:
    """Visualization settings"""
    # Theme
    color_profit: str = "#00FF41"  # Neon green
    color_loss: str = "#FF006E"    # Hot pink
    color_neutral: str = "#00D9FF"  # Cyan
    color_background: str = "#0a0e27"
    color_text: str = "#ffffff"
    
    # Chart settings
    chart_height: int = 600
    chart_template: str = 'plotly_dark'
    show_grid: bool = True
    
    # Advanced
    plot_rolling_metrics: bool = True
    rolling_window_days: int = 20
    heatmap_cmap: str = 'RdYlGn'


@dataclass
class LLMConfig:
    """LLM integration settings"""
    enabled: bool = True
    api_key: Optional[str] = None
    model: str = "gemini-2.5-flash"
    max_tokens: int = 2000
    
    # Analysis features
    enable_strategy_analysis: bool = True
    enable_improvement_suggestions: bool = True
    enable_trade_explanation: bool = True
    enable_report_generation: bool = True
    
    # Temperature (creativity)
    temperature: float = 0.7  # 0-1, lower = more deterministic


@dataclass
class StreamlitConfig:
    """Streamlit UI settings"""
    page_title: str = "QuantBack Pro"
    page_icon: str = "📈"
    layout: str = "wide"
    
    # Default values
    default_ticker: str = "AAPL"
    default_initial_cash: float = 100000
    default_strategy: str = "Moving Average Crossover"
    
    # Data date ranges
    default_start_offset_days: int = 365
    
    # UI refresh
    auto_refresh: bool = False
    refresh_interval: int = 300  # seconds


class Config:
    """Master configuration class"""
    
    # Load from environment or use defaults
    backtest = BacktestConfig()
    data = DataConfig(
        compute_sma_periods=[20, 50, 200],
        compute_ema_periods=[12, 26],
    )
    strategy = StrategyConfig()
    walk_forward = WalkForwardConfig()
    risk = RiskConfig()
    visualization = VisualizationConfig()
    llm = LLMConfig(
        api_key=os.environ.get("GEMINI_API_KEY")
    )
    streamlit = StreamlitConfig()
    
    @classmethod
    def from_dict(cls, config_dict: Dict):
        """Load configuration from dictionary"""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(getattr(cls, key), '__dict__', value)
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Export configuration as dictionary"""
        return {
            'backtest': cls.backtest.__dict__,
            'data': cls.data.__dict__,
            'strategy': cls.strategy.__dict__,
            'walk_forward': cls.walk_forward.__dict__,
            'risk': cls.risk.__dict__,
            'visualization': cls.visualization.__dict__,
            'llm': cls.llm.__dict__,
            'streamlit': cls.streamlit.__dict__,
        }


# Preset configurations for different use cases

AGGRESSIVE_CONFIG = Config()
AGGRESSIVE_CONFIG.backtest.commission_pct = 0.002
AGGRESSIVE_CONFIG.backtest.max_position_size_pct = 1.0
AGGRESSIVE_CONFIG.risk.max_position_loss = 0.05  # -5% stop
AGGRESSIVE_CONFIG.risk.profit_target = 0.10  # +10% target

CONSERVATIVE_CONFIG = Config()
CONSERVATIVE_CONFIG.backtest.commission_pct = 0.001
CONSERVATIVE_CONFIG.backtest.max_position_size_pct = 0.5
CONSERVATIVE_CONFIG.risk.max_position_loss = 0.01  # -1% stop
CONSERVATIVE_CONFIG.risk.profit_target = 0.02  # +2% target

RESEARCH_CONFIG = Config()
RESEARCH_CONFIG.backtest.slippage_pct = 0.0005
RESEARCH_CONFIG.backtest.commission_pct = 0.0005
RESEARCH_CONFIG.walk_forward.enabled = True
RESEARCH_CONFIG.walk_forward.min_windows = 5


# Example usage:
if __name__ == "__main__":
    # Use default config
    print("Default Configuration:")
    print(f"  Initial Cash: ${Config.backtest.initial_cash:,.0f}")
    print(f"  Commission: {Config.backtest.commission_pct*100:.2f}%")
    print(f"  Slippage: {Config.backtest.slippage_pct*100:.2f}%")
    print(f"  LLM Enabled: {Config.llm.enabled}")
    
    # Use aggressive preset
    print("\nAggressive Configuration:")
    print(f"  Max Position: {AGGRESSIVE_CONFIG.backtest.max_position_size_pct*100:.0f}%")
    print(f"  Stop Loss: {AGGRESSIVE_CONFIG.risk.max_position_loss*100:.1f}%")
    print(f"  Profit Target: {AGGRESSIVE_CONFIG.risk.profit_target*100:.1f}%")
    
    # Use conservative preset
    print("\nConservative Configuration:")
    print(f"  Max Position: {CONSERVATIVE_CONFIG.backtest.max_position_size_pct*100:.0f}%")
    print(f"  Stop Loss: {CONSERVATIVE_CONFIG.risk.max_position_loss*100:.1f}%")
    print(f"  Profit Target: {CONSERVATIVE_CONFIG.risk.profit_target*100:.1f}%")
