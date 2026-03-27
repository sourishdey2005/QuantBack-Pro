"""
QuantBack Pro - Backtesting Engine
Core event-driven backtesting system with realistic execution
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Represents a trading order"""
    timestamp: pd.Timestamp
    asset: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    limit_price: Optional[float] = None
    filled: bool = False
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0


@dataclass
class Trade:
    """Represents a closed trade"""
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    asset: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    days_held: int


@dataclass
class Position:
    """Current position tracking"""
    asset: str
    quantity: float = 0.0
    avg_entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    
    def update(self, quantity: float, price: float):
        if self.quantity == 0:
            self.avg_entry_price = price
            self.quantity = quantity
        else:
            total_cost = (self.avg_entry_price * self.quantity) + (price * quantity)
            self.quantity += quantity
            if self.quantity != 0:
                self.avg_entry_price = total_cost / self.quantity
    
    def get_value(self, current_price: float) -> float:
        return self.quantity * current_price


class Portfolio:
    """Portfolio state management"""
    
    def __init__(self, initial_cash: float = 100000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Trade] = []
        self.equity_curve: List[float] = [initial_cash]
        self.timestamps: List[pd.Timestamp] = []
        self.daily_returns: List[float] = []
        self.trades_by_asset: Dict[str, List[Trade]] = defaultdict(list)
    
    def get_position(self, asset: str) -> Position:
        if asset not in self.positions:
            self.positions[asset] = Position(asset)
        return self.positions[asset]
    
    def get_total_equity(self, current_prices: Dict[str, float], current_time: pd.Timestamp) -> float:
        """Calculate total portfolio value"""
        equity = self.cash
        for asset, position in self.positions.items():
            if asset in current_prices:
                equity += position.quantity * current_prices[asset]
        
        self.equity_curve.append(equity)
        self.timestamps.append(current_time)
        
        if len(self.equity_curve) > 1:
            daily_ret = (self.equity_curve[-1] - self.equity_curve[-2]) / self.equity_curve[-2]
            self.daily_returns.append(daily_ret)
        
        return equity
    
    def record_trade(self, trade: Trade):
        """Record a closed trade"""
        self.trade_history.append(trade)
        self.trades_by_asset[trade.asset].append(trade)
    
    def update_unrealized(self, current_prices: Dict[str, float]):
        """Update unrealized PnL for all positions"""
        for asset, position in self.positions.items():
            if asset in current_prices:
                position.current_price = current_prices[asset]
                position.unrealized_pnl = position.quantity * (current_prices[asset] - position.avg_entry_price)


class BacktestEngine:
    """Event-driven backtesting engine"""
    
    def __init__(
        self,
        initial_cash: float = 100000,
        slippage_pct: float = 0.001,  # 0.1% slippage
        commission_pct: float = 0.001,  # 0.1% commission
    ):
        self.portfolio = Portfolio(initial_cash)
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct
        self.open_orders: List[Order] = []
        self.order_history: List[Order] = []
    
    def place_order(
        self,
        timestamp: pd.Timestamp,
        asset: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
    ) -> Order:
        """Place a new order"""
        order = Order(
            timestamp=timestamp,
            asset=asset,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
        )
        self.open_orders.append(order)
        return order
    
    def process_orders(self, bar: pd.Series, asset: str, timestamp: pd.Timestamp):
        """Process pending orders at current bar"""
        filled_orders = []
        
        for order in self.open_orders:
            if order.asset != asset:
                continue
            
            # Market order execution
            if order.order_type == OrderType.MARKET:
                fill_price = bar['open']  # Execute at open price
                commission = fill_price * order.quantity * self.commission_pct
                slippage = fill_price * order.quantity * self.slippage_pct
                
                actual_price = fill_price
                if order.side == OrderSide.BUY:
                    actual_price += slippage
                    cost = (fill_price * order.quantity) + commission
                    self.portfolio.cash -= cost
                else:  # SELL
                    actual_price -= slippage
                    proceeds = (fill_price * order.quantity) - commission
                    self.portfolio.cash += proceeds
                
                order.filled = True
                order.filled_price = actual_price
                order.filled_quantity = order.quantity
                filled_orders.append(order)
                
                # Update position
                position = self.portfolio.get_position(asset)
                if order.side == OrderSide.BUY:
                    position.update(order.quantity, actual_price)
                else:
                    # Record trade if closing position
                    if position.quantity > 0:
                        pnl = (actual_price - position.avg_entry_price) * order.quantity
                        pnl_pct = (actual_price - position.avg_entry_price) / position.avg_entry_price
                        days_held = (timestamp - order.timestamp).days
                        
                        trade = Trade(
                            entry_time=order.timestamp,
                            exit_time=timestamp,
                            asset=asset,
                            entry_price=position.avg_entry_price,
                            exit_price=actual_price,
                            quantity=order.quantity,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            days_held=max(1, days_held),
                        )
                        self.portfolio.record_trade(trade)
                    
                    position.quantity -= order.quantity
            
            # Limit order execution
            elif order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and bar['low'] <= order.limit_price:
                    fill_price = order.limit_price
                    commission = fill_price * order.quantity * self.commission_pct
                    self.portfolio.cash -= (fill_price * order.quantity + commission)
                    
                    position = self.portfolio.get_position(asset)
                    position.update(order.quantity, fill_price)
                    
                    order.filled = True
                    order.filled_price = fill_price
                    order.filled_quantity = order.quantity
                    filled_orders.append(order)
                
                elif order.side == OrderSide.SELL and bar['high'] >= order.limit_price:
                    fill_price = order.limit_price
                    commission = fill_price * order.quantity * self.commission_pct
                    self.portfolio.cash += (fill_price * order.quantity - commission)
                    
                    position = self.portfolio.get_position(asset)
                    position.quantity -= order.quantity
                    
                    order.filled = True
                    order.filled_price = fill_price
                    order.filled_quantity = order.quantity
                    filled_orders.append(order)
        
        # Remove filled orders
        for order in filled_orders:
            self.open_orders.remove(order)
            self.order_history.append(order)
    
    def get_portfolio_stats(self) -> Dict:
        """Calculate comprehensive portfolio statistics"""
        equity = self.portfolio.equity_curve
        returns = self.portfolio.daily_returns
        trades = self.portfolio.trade_history
        
        if len(equity) < 2 or len(returns) == 0:
            return {}
        
        total_return = (equity[-1] - equity[0]) / equity[0]
        cagr = (equity[-1] / equity[0]) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
        
        annual_returns = np.array(returns) * 252
        sharpe = np.mean(annual_returns) / np.std(annual_returns) if np.std(returns) > 0 else 0
        
        sortino_returns = np.array([r for r in returns if r < 0]) * 252
        downside_std = np.std(sortino_returns) if len(sortino_returns) > 0 else np.std(returns)
        sortino = (np.mean(annual_returns) / downside_std) if downside_std > 0 else 0
        
        # Drawdown
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Win rate
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        win_rate = winning_trades / len(trades) if trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': len(trades) - winning_trades,
            'avg_trade_return': np.mean([t.pnl_pct for t in trades]) if trades else 0,
            'final_equity': equity[-1],
            'final_cash': self.portfolio.cash,
        }
