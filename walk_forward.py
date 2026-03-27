"""
QuantBack Pro - Walk-Forward Analysis
Rolling window validation to detect overfitting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WalkForwardWindow:
    """Single window in walk-forward analysis"""
    window_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train_data: pd.DataFrame
    test_data: pd.DataFrame
    train_stats: Optional[Dict] = None
    test_stats: Optional[Dict] = None


class WalkForwardAnalyzer:
    """Perform walk-forward analysis"""
    
    @staticmethod
    def create_windows(
        data: pd.DataFrame,
        train_period_days: int = 252,  # 1 year
        test_period_days: int = 63,    # 3 months
        step_days: int = 63,            # Quarterly rebalance
    ) -> List[WalkForwardWindow]:
        """
        Create rolling train/test windows
        
        Args:
            data: Full historical data
            train_period_days: Training window size
            test_period_days: Testing window size
            step_days: How much to roll forward
        
        Returns:
            List of WalkForwardWindow objects
        """
        windows = []
        start_date = data.index[0]
        end_date = data.index[-1]
        
        current_train_start = start_date
        window_id = 0
        
        while True:
            train_end = current_train_start + timedelta(days=train_period_days)
            test_start = train_end + timedelta(days=1)
            test_end = test_start + timedelta(days=test_period_days)
            
            # Ensure test_end doesn't exceed data
            if test_end > end_date:
                test_end = end_date
            
            # Check if we have enough data
            if test_start >= end_date:
                break
            
            # Filter data for this window
            train_data = data[(data.index >= current_train_start) & (data.index <= train_end)]
            test_data = data[(data.index >= test_start) & (data.index <= test_end)]
            
            if len(train_data) > 0 and len(test_data) > 0:
                window = WalkForwardWindow(
                    window_id=window_id,
                    train_start=current_train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                    train_data=train_data,
                    test_data=test_data,
                )
                windows.append(window)
                window_id += 1
            
            # Move forward
            current_train_start += timedelta(days=step_days)
        
        return windows
    
    @staticmethod
    def analyze_window(window: WalkForwardWindow) -> Tuple[Dict, Dict]:
        """
        Analyze train vs test performance
        Returns: (train_stats, test_stats)
        """
        def calculate_stats(data: pd.DataFrame) -> Dict:
            if 'returns' not in data.columns or len(data) < 2:
                return {}
            
            returns = data['returns'].dropna()
            
            if len(returns) == 0:
                return {}
            
            total_return = (1 + returns).prod() - 1
            annual_return = (1 + total_return) ** (252 / len(returns)) - 1
            
            annual_returns = returns * 252
            sharpe = annual_return / returns.std() if returns.std() > 0 else 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std()
            sortino = (annual_return / downside_std) if downside_std > 0 else 0
            
            # Max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_dd = drawdown.min()
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe_ratio': sharpe,
                'sortino_ratio': sortino,
                'max_drawdown': max_dd,
                'volatility': returns.std(),
                'annual_volatility': returns.std() * np.sqrt(252),
                'num_periods': len(returns),
                'win_rate': (returns > 0).sum() / len(returns) if len(returns) > 0 else 0,
            }
        
        train_stats = calculate_stats(window.train_data)
        test_stats = calculate_stats(window.test_data)
        
        window.train_stats = train_stats
        window.test_stats = test_stats
        
        return train_stats, test_stats
    
    @staticmethod
    def detect_overfitting(windows: List[WalkForwardWindow]) -> Dict:
        """
        Analyze degradation from train to test
        Returns overfitting metrics
        """
        if len(windows) == 0:
            return {
                'num_windows': 0,
                'avg_train_sharpe': None,
                'avg_test_sharpe': None,
                'sharpe_degradation': None,
                'avg_train_return': None,
                'avg_test_return': None,
                'return_degradation': None,
                'train_sharpe_stability': None,
                'test_sharpe_stability': None,
                'is_overfit': None,
                'overfitting_score': None,
                'status': 'insufficient_data',
                'message': 'Not enough history for walk-forward windows. Increase the date range.',
            }
        
        # Extract metrics
        train_sharpes = [w.train_stats.get('sharpe_ratio', 0) for w in windows if w.train_stats]
        test_sharpes = [w.test_stats.get('sharpe_ratio', 0) for w in windows if w.test_stats]
        
        train_returns = [w.train_stats.get('total_return', 0) for w in windows if w.train_stats]
        test_returns = [w.test_stats.get('total_return', 0) for w in windows if w.test_stats]
        
        train_max_dd = [w.train_stats.get('max_drawdown', 0) for w in windows if w.train_stats]
        test_max_dd = [w.test_stats.get('max_drawdown', 0) for w in windows if w.test_stats]
        
        # Calculate degradation
        avg_train_sharpe = np.mean(train_sharpes) if train_sharpes else 0
        avg_test_sharpe = np.mean(test_sharpes) if test_sharpes else 0
        sharpe_degradation = (avg_train_sharpe - avg_test_sharpe) / abs(avg_train_sharpe) if avg_train_sharpe != 0 else 0
        
        avg_train_return = np.mean(train_returns) if train_returns else 0
        avg_test_return = np.mean(test_returns) if test_returns else 0
        return_degradation = (avg_train_return - avg_test_return) / abs(avg_train_return) if avg_train_return != 0 else 0
        
        # Stability metrics
        train_sharpe_std = np.std(train_sharpes) if len(train_sharpes) > 1 else 0
        test_sharpe_std = np.std(test_sharpes) if len(test_sharpes) > 1 else 0
        
        return {
            'num_windows': len(windows),
            'avg_train_sharpe': avg_train_sharpe,
            'avg_test_sharpe': avg_test_sharpe,
            'sharpe_degradation': sharpe_degradation,
            'avg_train_return': avg_train_return,
            'avg_test_return': avg_test_return,
            'return_degradation': return_degradation,
            'train_sharpe_stability': train_sharpe_std,
            'test_sharpe_stability': test_sharpe_std,
            'is_overfit': sharpe_degradation > 0.3,  # 30% degradation threshold
            'overfitting_score': sharpe_degradation,
            'status': 'ok',
            'message': '',
        }
    
    @staticmethod
    def get_parameter_stability(windows: List[WalkForwardWindow]) -> Dict:
        """
        Analyze parameter stability across windows
        Useful if you're optimizing parameters in each window
        """
        if len(windows) == 0:
            return {}
        
        # Check sharpe consistency
        sharpes = [w.test_stats.get('sharpe_ratio', 0) for w in windows if w.test_stats]
        
        return {
            'mean_sharpe': np.mean(sharpes),
            'std_sharpe': np.std(sharpes),
            'min_sharpe': np.min(sharpes),
            'max_sharpe': np.max(sharpes),
            'sharpe_cv': np.std(sharpes) / np.mean(sharpes) if np.mean(sharpes) != 0 else 0,  # Coefficient of variation
        }


class RollingOptimizer:
    """Optimize parameters in each window (advanced feature)"""
    
    @staticmethod
    def optimize_window_parameters(
        window: WalkForwardWindow,
        parameter_ranges: Dict,
        objective_metric: str = 'sharpe_ratio',
    ) -> Dict:
        """
        Optimize strategy parameters for a single window
        This is a template - you'd implement your own optimization
        """
        # This would involve:
        # 1. Grid search or Bayesian optimization over parameter_ranges
        # 2. Running strategy on train_data for each parameter combo
        # 3. Selecting parameters that maximize objective_metric
        # 4. Returning optimal parameters
        
        return {
            'optimal_params': {},
            'best_score': 0,
        }
