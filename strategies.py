"""
QuantBack Pro - Strategy Builder
Technical indicators and signal generation
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional


class Indicator(ABC):
    """Base indicator class"""
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pass


class SMA(Indicator):
    """Simple Moving Average"""
    
    def __init__(self, period: int = 20):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].rolling(window=self.period).mean()


class EMA(Indicator):
    """Exponential Moving Average"""
    
    def __init__(self, period: int = 20):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].ewm(span=self.period, adjust=False).mean()


class RSI(Indicator):
    """Relative Strength Index"""
    
    def __init__(self, period: int = 14):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class MACD(Indicator):
    """Moving Average Convergence Divergence"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def calculate(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        ema_fast = data['close'].ewm(span=self.fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram


class BollingerBands(Indicator):
    """Bollinger Bands"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
    
    def calculate(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        sma = data['close'].rolling(window=self.period).mean()
        std = data['close'].rolling(window=self.period).std()
        upper = sma + (std * self.std_dev)
        lower = sma - (std * self.std_dev)
        return upper, sma, lower


class ATR(Indicator):
    """Average True Range"""
    
    def __init__(self, period: int = 14):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(self.period).mean()
        return atr


class Strategy(ABC):
    """Base strategy class"""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return DataFrame with 'signal' column (1=BUY, -1=SELL, 0=HOLD)"""
        pass


class MovingAverageCrossover(Strategy):
    """MA Crossover Strategy"""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        fast_ma = data['close'].rolling(window=self.fast_period).mean()
        slow_ma = data['close'].rolling(window=self.slow_period).mean()
        
        data['fast_ma'] = fast_ma
        data['slow_ma'] = slow_ma
        
        # Generate signals
        data['signal'] = 0
        data.loc[fast_ma > slow_ma, 'signal'] = 1
        data.loc[fast_ma < slow_ma, 'signal'] = -1
        
        # Generate position (avoid redundant signals)
        data['position'] = data['signal'].diff()
        
        return data


class RSIMomentum(Strategy):
    """RSI-based momentum strategy"""
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70):
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        data['rsi'] = rsi
        
        # Generate signals
        data['signal'] = 0
        data.loc[rsi < self.oversold, 'signal'] = 1  # Oversold, BUY
        data.loc[rsi > self.overbought, 'signal'] = -1  # Overbought, SELL
        
        data['position'] = data['signal'].diff()
        
        return data


class MACDCrossover(Strategy):
    """MACD-based crossover strategy"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        ema_fast = data['close'].ewm(span=self.fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        data['macd'] = macd_line
        data['signal_line'] = signal_line
        data['histogram'] = histogram
        
        # Generate signals
        data['signal'] = 0
        data.loc[histogram > 0, 'signal'] = 1
        data.loc[histogram < 0, 'signal'] = -1
        
        data['position'] = data['signal'].diff()
        
        return data


class MeanReversion(Strategy):
    """Mean reversion strategy using Bollinger Bands"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        sma = data['close'].rolling(window=self.period).mean()
        std = data['close'].rolling(window=self.period).std()
        upper = sma + (std * self.std_dev)
        lower = sma - (std * self.std_dev)
        
        data['sma'] = sma
        data['upper_band'] = upper
        data['lower_band'] = lower
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['close'] < lower, 'signal'] = 1  # Oversold, BUY
        data.loc[data['close'] > upper, 'signal'] = -1  # Overbought, SELL
        
        data['position'] = data['signal'].diff()
        
        return data


class CombinedRSIMACD(Strategy):
    """Combined RSI + MACD strategy"""
    
    def __init__(self, rsi_period: int = 14, macd_fast: int = 12, macd_slow: int = 26):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_fast = data['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.macd_slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        
        data['rsi'] = rsi
        data['macd'] = macd_line
        
        # Combined signal
        data['signal'] = 0
        buy_condition = (rsi < 50) & (macd_line > 0)
        sell_condition = (rsi > 50) & (macd_line < 0)
        
        data.loc[buy_condition, 'signal'] = 1
        data.loc[sell_condition, 'signal'] = -1
        
        data['position'] = data['signal'].diff()
        
        return data
