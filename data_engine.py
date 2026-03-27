"""
QuantBack Pro - Data Engine
Free API data sourcing and validation
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import time
import yfinance as yf
import warnings

warnings.filterwarnings('ignore')


class DataFetcher:
    """Fetch market data from free APIs"""

    last_error: Optional[str] = None

    @staticmethod
    def _normalize_ohlcv_columns(data: pd.DataFrame) -> pd.DataFrame:
        """Normalize yfinance output to lowercase OHLCV columns."""
        required_cols = ['open', 'high', 'low', 'close', 'volume']

        if isinstance(data.columns, pd.MultiIndex):
            # yfinance can return columns like ('Close', 'AAPL') or ('AAPL', 'Close').
            normalized_data = pd.DataFrame(index=data.index)
            for col in data.columns:
                parts = [str(part).strip().lower() for part in col]
                for part in parts:
                    if part in required_cols and part not in normalized_data.columns:
                        normalized_data[part] = data[col]
                        break
            data = normalized_data
        else:
            normalized_map = {}
            for col in data.columns:
                col_norm = str(col).strip().lower()
                if col_norm in required_cols and col_norm not in normalized_map:
                    normalized_map[col_norm] = col
            data = data.rename(columns={v: k for k, v in normalized_map.items()})

        return data

    @staticmethod
    def _fetch_stooq_ohlcv(
        ticker: str,
        start_ts: pd.Timestamp,
        end_ts: pd.Timestamp,
    ) -> pd.DataFrame:
        """Fallback provider via Stooq daily CSV endpoint."""
        symbol_candidates = [f"{ticker.lower()}.us", ticker.lower()]

        for symbol in symbol_candidates:
            try:
                url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
                data = pd.read_csv(url)
                if data is None or data.empty or "Date" not in data.columns:
                    continue

                data = data.rename(
                    columns={
                        "Date": "date",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Volume": "volume",
                    }
                )
                required_cols = ["date", "open", "high", "low", "close", "volume"]
                if not all(col in data.columns for col in required_cols):
                    continue

                data["date"] = pd.to_datetime(data["date"], errors="coerce")
                data = data.dropna(subset=["date"]).set_index("date").sort_index()
                data = data[(data.index >= start_ts) & (data.index <= end_ts)]
                if data.empty:
                    continue

                return data[["open", "high", "low", "close", "volume"]]
            except Exception:
                continue

        return pd.DataFrame()
    
    @staticmethod
    def fetch_ohlcv(
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data using yfinance
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: '1d', '1wk', '1mo'
        
        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        DataFetcher.last_error = None
        try:
            ticker = str(ticker).strip().upper()
            start_ts = pd.to_datetime(start_date)
            end_ts = pd.to_datetime(end_date)

            # yfinance `end` is exclusive; keep a valid window in all cases.
            if end_ts <= start_ts:
                end_ts = start_ts + pd.Timedelta(days=1)

            start_str = start_ts.strftime("%Y-%m-%d")
            end_str = end_ts.strftime("%Y-%m-%d")
            data = pd.DataFrame()

            # For standard daily backtests, prefer Stooq first because Yahoo often
            # fails in restricted environments with timezone/delisted errors.
            if interval == "1d":
                data = DataFetcher._fetch_stooq_ohlcv(ticker, start_ts, end_ts)

            # Yahoo remains as fallback for non-daily intervals or when Stooq has no data.
            if data is None or data.empty:
                for _ in range(3):
                    try:
                        data = yf.download(
                            ticker,
                            start=start_str,
                            end=end_str,
                            interval=interval,
                            progress=False,
                            auto_adjust=False,
                            group_by="column",
                            actions=False,
                            threads=False,
                        )
                    except Exception:
                        data = pd.DataFrame()
                    if data is not None and not data.empty:
                        break
                    time.sleep(0.6)

            if data is None or data.empty:
                try:
                    history = yf.Ticker(ticker).history(
                        start=start_str,
                        end=end_str,
                        interval=interval,
                        auto_adjust=False,
                        actions=False,
                    )
                    if history is not None and not history.empty:
                        data = history
                except Exception:
                    data = pd.DataFrame()

            if data is None or data.empty:
                try:
                    history = yf.Ticker(ticker).history(
                        period="2y",
                        interval=interval,
                        auto_adjust=False,
                        actions=False,
                    )
                    if history is not None and not history.empty:
                        history.index = pd.to_datetime(history.index)
                        data = history[(history.index >= start_ts) & (history.index <= end_ts)]
                except Exception:
                    data = pd.DataFrame()

            if data is None or data.empty:
                DataFetcher.last_error = (
                    f"No market data returned for ticker '{ticker}'. "
                    "Tried Yahoo and Stooq providers. Check internet/firewall settings."
                )
                return pd.DataFrame()

            # Normalize yfinance outputs across versions.
            data = DataFetcher._normalize_ohlcv_columns(data)
            data.index.name = 'date'

            # Ensure required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                DataFetcher.last_error = (
                    f"Downloaded data is missing required columns: {', '.join(missing_cols)}."
                )
                return pd.DataFrame()

            data = data[required_cols]

            # Fill any missing data
            data = data.ffill().bfill()

            if data.empty:
                DataFetcher.last_error = f"Data was empty after preprocessing for '{ticker}'."
                return pd.DataFrame()
            
            return data
        
        except Exception as e:
            DataFetcher.last_error = f"Error fetching data for {ticker}: {str(e)}"
            print(DataFetcher.last_error)
            return pd.DataFrame()
    
    @staticmethod
    def fetch_multiple_tickers(
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple tickers"""
        data = {}
        for ticker in tickers:
            data[ticker] = DataFetcher.fetch_ohlcv(ticker, start_date, end_date)
        return data
    
    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        """Validate data integrity"""
        if data.empty:
            return False
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_cols):
            return False
        
        # Check for NaN values
        if data[required_cols].isna().any().any():
            print("Warning: Data contains NaN values")
            return False
        
        return True


class DataProcessor:
    """Process and augment market data"""
    
    @staticmethod
    def add_returns(data: pd.DataFrame) -> pd.DataFrame:
        """Add returns columns"""
        data = data.copy()
        data['returns'] = data['close'].pct_change()
        data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        return data
    
    @staticmethod
    def add_volatility(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Add rolling volatility"""
        data = data.copy()
        data['volatility'] = data['returns'].rolling(window=window).std()
        data['volatility_annual'] = data['volatility'] * np.sqrt(252)
        return data
    
    @staticmethod
    def add_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average True Range"""
        data = data.copy()
        
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        data['atr'] = atr
        data['atr_pct'] = atr / data['close']
        
        return data
    
    @staticmethod
    def add_sma(data: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
        """Add Simple Moving Averages"""
        data = data.copy()
        for period in periods:
            data[f'sma_{period}'] = data['close'].rolling(window=period).mean()
        return data
    
    @staticmethod
    def add_ema(data: pd.DataFrame, periods: List[int] = [12, 26]) -> pd.DataFrame:
        """Add Exponential Moving Averages"""
        data = data.copy()
        for period in periods:
            data[f'ema_{period}'] = data['close'].ewm(span=period, adjust=False).mean()
        return data
    
    @staticmethod
    def add_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add RSI indicator"""
        data = data.copy()
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        data['rsi'] = rsi
        return data
    
    @staticmethod
    def add_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Add MACD indicator"""
        data = data.copy()
        
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        data['macd'] = macd_line
        data['macd_signal'] = signal_line
        data['macd_histogram'] = histogram
        
        return data
    
    @staticmethod
    def add_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Add Bollinger Bands"""
        data = data.copy()
        
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        data['bb_upper'] = upper
        data['bb_middle'] = sma
        data['bb_lower'] = lower
        data['bb_position'] = (data['close'] - lower) / (upper - lower)
        
        return data
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with NaN indicator values"""
        return data.dropna()
    
    @staticmethod
    def prepare_for_backtest(
        data: pd.DataFrame,
        add_indicators: bool = True
    ) -> pd.DataFrame:
        """Full data preparation pipeline"""
        data = data.copy()
        
        if add_indicators:
            data = DataProcessor.add_returns(data)
            data = DataProcessor.add_volatility(data)
            data = DataProcessor.add_atr(data)
            data = DataProcessor.add_sma(data)
            data = DataProcessor.add_ema(data)
            data = DataProcessor.add_rsi(data)
            data = DataProcessor.add_macd(data)
            data = DataProcessor.add_bollinger_bands(data)
        
        data = DataProcessor.clean_data(data)
        
        return data


class DataValidator:
    """Validate data quality"""
    
    @staticmethod
    def check_gaps(data: pd.DataFrame, max_gap_days: int = 5) -> bool:
        """Check for large gaps in data"""
        if len(data) < 2:
            return False
        
        gaps = data.index.to_series().diff().dt.days
        return (gaps <= max_gap_days).all()
    
    @staticmethod
    def check_outliers(data: pd.DataFrame, column: str = 'returns', std_threshold: float = 5) -> pd.DataFrame:
        """Flag outliers using z-score"""
        mean = data[column].mean()
        std = data[column].std()
        z_score = np.abs((data[column] - mean) / std)
        return data[z_score > std_threshold]
    
    @staticmethod
    def get_data_stats(data: pd.DataFrame) -> Dict:
        """Get data quality statistics"""
        return {
            'start_date': data.index[0],
            'end_date': data.index[-1],
            'total_days': len(data),
            'missing_values': data.isnull().sum().sum(),
            'price_range': (data['close'].min(), data['close'].max()),
            'avg_volume': data['volume'].mean(),
        }
