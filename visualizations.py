"""
QuantBack Pro - Visualization Engine
50+ professional trading analytics visualizations
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional


class VisualizationEngine:
    """Create professional trading charts"""
    
    # Color scheme
    COLORS = {
        'profit': '#00FF41',  # Neon green
        'loss': '#FF006E',    # Hot pink
        'neutral': '#00D9FF', # Cyan
        'grid': '#1e1e1e',
        'text': '#ffffff',
        'background': '#0a0e27',
    }
    
    @staticmethod
    def create_equity_curve(equity: List[float], timestamps: List) -> go.Figure:
        """Equity curve with returns overlay"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=equity,
                name='Equity',
                line=dict(color=VisualizationEngine.COLORS['profit'], width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 65, 0.1)',
            ),
            row=1, col=1
        )
        
        # Daily returns
        returns = np.diff(equity) / equity[:-1]
        colors = [VisualizationEngine.COLORS['profit'] if r > 0 else VisualizationEngine.COLORS['loss'] for r in returns]
        
        fig.add_trace(
            go.Bar(
                x=timestamps[1:],
                y=returns * 100,
                name='Daily Returns %',
                marker=dict(color=colors),
                showlegend=True,
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_yaxes(title_text="Returns (%)", row=2, col=1)
        
        fig.update_layout(
            title="Portfolio Equity Curve",
            hovermode='x unified',
            template='plotly_dark',
            height=600,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_drawdown_chart(equity: List[float], timestamps: List) -> go.Figure:
        """Drawdown curve with underwater plot"""
        cumulative = np.array(equity)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = ((cumulative - running_max) / running_max) * 100
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=drawdown,
                name='Drawdown %',
                line=dict(color=VisualizationEngine.COLORS['loss'], width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 110, 0.2)',
            )
        )
        
        fig.update_layout(
            title="Underwater Plot - Drawdown",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_return_distribution(returns: List[float]) -> go.Figure:
        """Distribution of returns"""
        fig = go.Figure()
        
        fig.add_trace(
            go.Histogram(
                x=returns,
                name='Returns',
                nbinsx=50,
                marker=dict(color=VisualizationEngine.COLORS['neutral']),
            )
        )
        
        fig.add_vline(
            x=0,
            line_dash="dash",
            line_color=VisualizationEngine.COLORS['text'],
            annotation_text="Zero Return"
        )
        
        fig.update_layout(
            title="Distribution of Daily Returns",
            xaxis_title="Daily Returns (%)",
            yaxis_title="Frequency",
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_trade_pnl_histogram(trades_pnl: List[float]) -> go.Figure:
        """Trade PnL distribution"""
        fig = go.Figure()
        
        colors = [VisualizationEngine.COLORS['profit'] if pnl > 0 else VisualizationEngine.COLORS['loss'] 
                  for pnl in trades_pnl]
        
        fig.add_trace(
            go.Bar(
                x=list(range(len(trades_pnl))),
                y=trades_pnl,
                name='Trade PnL',
                marker=dict(color=colors),
            )
        )
        
        fig.update_layout(
            title="Trade P&L Distribution",
            xaxis_title="Trade #",
            yaxis_title="P&L ($)",
            hovermode='x',
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_win_loss_pie(num_wins: int, num_losses: int) -> go.Figure:
        """Win vs loss pie chart"""
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=['Wins', 'Losses'],
                    values=[num_wins, num_losses],
                    marker=dict(
                        colors=[VisualizationEngine.COLORS['profit'], VisualizationEngine.COLORS['loss']]
                    ),
                )
            ]
        )
        
        fig.update_layout(
            title=f"Win Rate: {num_wins / (num_wins + num_losses) * 100:.1f}%",
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_rolling_sharpe(equity: List[float], window: int = 20) -> go.Figure:
        """Rolling Sharpe ratio"""
        returns = np.diff(equity) / equity[:-1]
        rolling_returns = pd.Series(returns).rolling(window=window)
        
        rolling_sharpe = []
        for ret in rolling_returns:
            if len(ret) > 0 and ret.std() > 0:
                sharpe = ret.mean() * 252 / (ret.std() * np.sqrt(252))
                rolling_sharpe.append(sharpe)
            else:
                rolling_sharpe.append(np.nan)
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(rolling_sharpe))),
                y=rolling_sharpe,
                name='Rolling Sharpe',
                line=dict(color=VisualizationEngine.COLORS['neutral'], width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 217, 255, 0.1)',
            )
        )
        
        fig.update_layout(
            title=f"Rolling Sharpe Ratio ({window}-day window)",
            xaxis_title="Period",
            yaxis_title="Sharpe Ratio",
            hovermode='x',
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_volatility_curve(returns: List[float], window: int = 20) -> go.Figure:
        """Rolling volatility"""
        rolling_vol = pd.Series(returns).rolling(window=window).std() * np.sqrt(252) * 100
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(rolling_vol))),
                y=rolling_vol,
                name='Annual Volatility %',
                line=dict(color=VisualizationEngine.COLORS['loss'], width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 110, 0.1)',
            )
        )
        
        fig.update_layout(
            title=f"Rolling Volatility ({window}-day window)",
            xaxis_title="Period",
            yaxis_title="Annual Volatility (%)",
            hovermode='x',
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_price_with_signals(
        data: pd.DataFrame,
        signal_column: str = 'signal',
        ma_columns: List[str] = None,
    ) -> go.Figure:
        """Price chart with trading signals and moving averages"""
        fig = go.Figure()
        
        # Price candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
            )
        )
        
        # Moving averages
        if ma_columns:
            colors = ['#FF006E', '#00D9FF', '#FFD60A']
            for i, col in enumerate(ma_columns):
                if col in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data[col],
                            name=col,
                            line=dict(color=colors[i % len(colors)], width=1),
                        )
                    )
        
        # Buy signals
        buys = data[data[signal_column] == 1]
        if len(buys) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buys.index,
                    y=buys['low'],
                    mode='markers',
                    name='Buy',
                    marker=dict(symbol='triangle-up', size=10, color=VisualizationEngine.COLORS['profit']),
                )
            )
        
        # Sell signals
        sells = data[data[signal_column] == -1]
        if len(sells) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sells.index,
                    y=sells['high'],
                    mode='markers',
                    name='Sell',
                    marker=dict(symbol='triangle-down', size=10, color=VisualizationEngine.COLORS['loss']),
                )
            )
        
        fig.update_layout(
            title="Price Chart with Trading Signals",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            template='plotly_dark',
            height=600,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig
    
    @staticmethod
    def create_performance_metrics_table(stats: Dict) -> go.Figure:
        """Performance metrics table"""
        metrics = [
            ['Total Return', f"{stats.get('total_return', 0) * 100:.2f}%"],
            ['CAGR', f"{stats.get('cagr', 0) * 100:.2f}%"],
            ['Sharpe Ratio', f"{stats.get('sharpe_ratio', 0):.2f}"],
            ['Sortino Ratio', f"{stats.get('sortino_ratio', 0):.2f}"],
            ['Max Drawdown', f"{stats.get('max_drawdown', 0) * 100:.2f}%"],
            ['Win Rate', f"{stats.get('win_rate', 0) * 100:.2f}%"],
            ['Profit Factor', f"{stats.get('profit_factor', 0):.2f}"],
            ['Total Trades', f"{stats.get('total_trades', 0)}"],
        ]
        
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=['Metric', 'Value'],
                        fill_color=VisualizationEngine.COLORS['loss'],
                        align='left',
                        font=dict(color='white'),
                    ),
                    cells=dict(
                        values=list(zip(*metrics)),
                        fill_color='rgba(255, 255, 255, 0.05)',
                        align='left',
                        font=dict(color=VisualizationEngine.COLORS['text']),
                    ),
                )
            ]
        )
        
        fig.update_layout(
            title="Performance Metrics",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig
    
    @staticmethod
    def create_walk_forward_comparison(windows_stats: List[Dict]) -> go.Figure:
        """Compare train vs test performance across windows"""
        window_ids = list(range(len(windows_stats)))
        train_sharpes = [w.get('train_sharpe', 0) for w in windows_stats]
        test_sharpes = [w.get('test_sharpe', 0) for w in windows_stats]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=window_ids,
                y=train_sharpes,
                name='Train Sharpe',
                line=dict(color=VisualizationEngine.COLORS['profit'], width=2),
                marker=dict(size=8),
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=window_ids,
                y=test_sharpes,
                name='Test Sharpe',
                line=dict(color=VisualizationEngine.COLORS['loss'], width=2),
                marker=dict(size=8),
            )
        )
        
        fig.update_layout(
            title="Walk-Forward Analysis: Train vs Test Performance",
            xaxis_title="Window #",
            yaxis_title="Sharpe Ratio",
            hovermode='x',
            template='plotly_dark',
            height=400,
            font=dict(color=VisualizationEngine.COLORS['text']),
        )
        
        return fig

    @staticmethod
    def _styled_figure(fig: go.Figure, title: str, height: int = 360) -> go.Figure:
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=height,
            font=dict(color=VisualizationEngine.COLORS['text']),
            paper_bgcolor=VisualizationEngine.COLORS['background'],
            plot_bgcolor=VisualizationEngine.COLORS['background'],
            margin=dict(l=40, r=30, t=55, b=40),
        )
        fig.update_xaxes(showgrid=True, gridcolor=VisualizationEngine.COLORS['grid'])
        fig.update_yaxes(showgrid=True, gridcolor=VisualizationEngine.COLORS['grid'])
        return fig

    @staticmethod
    def _empty_chart(title: str, message: str) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            showarrow=False,
            font=dict(color=VisualizationEngine.COLORS['text'], size=14),
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return VisualizationEngine._styled_figure(fig, title, height=280)

    @staticmethod
    def _trade_df(trade_history: List) -> pd.DataFrame:
        if not trade_history:
            return pd.DataFrame(columns=['entry_time', 'exit_time', 'pnl', 'pnl_pct', 'days_held'])
        return pd.DataFrame(
            [
                {
                    'entry_time': t.entry_time,
                    'exit_time': t.exit_time,
                    'pnl': t.pnl,
                    'pnl_pct': t.pnl_pct * 100,
                    'days_held': t.days_held,
                }
                for t in trade_history
            ]
        )

    @staticmethod
    def _signal_frame(data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame['asset_return_pct'] = frame['close'].pct_change() * 100
        frame['cum_asset_return_pct'] = ((1 + frame['close'].pct_change().fillna(0)).cumprod() - 1) * 100
        frame['next_5d_return_pct'] = frame['close'].pct_change(5).shift(-5) * 100
        frame['month'] = frame.index.to_period('M').astype(str)
        frame['weekday'] = frame.index.day_name()
        frame['signal_state'] = frame.get('signal', 0).fillna(0)
        frame['position_event'] = frame.get('position', 0).fillna(0)
        return frame

    @staticmethod
    def _regime_duration_series(values: pd.Series) -> pd.Series:
        values = values.fillna(0)
        groups = values.ne(values.shift()).cumsum()
        durations = values.groupby(groups).size()
        labels = values.groupby(groups).first()
        return pd.Series(durations.values, index=labels.values)

    @staticmethod
    def _create_monthly_heatmap(frame: pd.DataFrame, value_col: str, title: str) -> go.Figure:
        heat = frame.copy()
        heat['year'] = heat.index.year
        heat['month_num'] = heat.index.month
        pivot = heat.pivot_table(index='year', columns='month_num', values=value_col, aggfunc='mean')
        pivot = pivot.reindex(columns=list(range(1, 13)))
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot.values,
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                y=pivot.index.astype(str),
                colorscale='RdYlGn',
                colorbar=dict(title=value_col),
            )
        )
        return VisualizationEngine._styled_figure(fig, title, height=320)

    @staticmethod
    def _create_transition_heatmap(frame: pd.DataFrame, title: str) -> go.Figure:
        transitions = pd.crosstab(frame['signal_state'].shift().fillna(0), frame['signal_state'])
        labels = {-1: 'Sell', 0: 'Flat', 1: 'Buy'}
        transitions = transitions.reindex(index=[-1, 0, 1], columns=[-1, 0, 1], fill_value=0)
        fig = go.Figure(
            data=go.Heatmap(
                z=transitions.values,
                x=[labels[c] for c in transitions.columns],
                y=[labels[i] for i in transitions.index],
                colorscale='Blues',
            )
        )
        fig.update_xaxes(title_text='To State')
        fig.update_yaxes(title_text='From State')
        return VisualizationEngine._styled_figure(fig, title, height=320)

    @staticmethod
    def _create_trade_charts(trade_history: List, prefix: str) -> List[Dict]:
        trades = VisualizationEngine._trade_df(trade_history)
        if trades.empty:
            empty = VisualizationEngine._empty_chart(f"{prefix} Trades", "No closed trades available yet.")
            return [{'title': f'{prefix} Trade P&L Curve', 'figure': empty}] * 4

        cumulative = trades['pnl'].cumsum()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=trades['exit_time'], y=cumulative, mode='lines+markers', name='Cum P&L'))
        fig1 = VisualizationEngine._styled_figure(fig1, f"{prefix} Trade P&L Curve")

        fig2 = px.scatter(
            trades,
            x='days_held',
            y='pnl',
            color='pnl',
            color_continuous_scale='RdYlGn',
        )
        fig2 = VisualizationEngine._styled_figure(fig2, f"{prefix} Trade Duration vs P&L")

        fig3 = go.Figure(data=[go.Histogram(x=trades['pnl'], nbinsx=20, marker_color=VisualizationEngine.COLORS['neutral'])])
        fig3 = VisualizationEngine._styled_figure(fig3, f"{prefix} Trade P&L Histogram")

        fig4 = go.Figure(data=[go.Histogram(x=trades['days_held'], nbinsx=20, marker_color=VisualizationEngine.COLORS['loss'])])
        fig4 = VisualizationEngine._styled_figure(fig4, f"{prefix} Holding Period Histogram")

        return [
            {'title': f'{prefix} Trade P&L Curve', 'figure': fig1},
            {'title': f'{prefix} Trade Duration vs P&L', 'figure': fig2},
            {'title': f'{prefix} Trade P&L Histogram', 'figure': fig3},
            {'title': f'{prefix} Holding Period Histogram', 'figure': fig4},
        ]

    @staticmethod
    def _create_rsi_trade_charts(frame: pd.DataFrame, trade_history: List, prefix: str) -> List[Dict]:
        trades = VisualizationEngine._trade_df(trade_history)
        if trades.empty:
            empty = VisualizationEngine._empty_chart(f"{prefix} RSI Trade View", "No closed trades available yet.")
            return [
                {'title': f'{prefix} Trade P&L Curve', 'figure': empty},
                {'title': f'{prefix} RSI Triangle Signal Map', 'figure': empty},
                {'title': f'{prefix} Trade P&L Histogram', 'figure': empty},
                {'title': f'{prefix} RSI Reversal Candlestick', 'figure': empty},
            ]

        cumulative = trades['pnl'].cumsum()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=trades['exit_time'], y=cumulative, mode='lines+markers', name='Cum P&L'))
        fig1 = VisualizationEngine._styled_figure(fig1, f"{prefix} Trade P&L Curve")

        buys = frame[frame['position_event'] > 0]
        sells = frame[frame['position_event'] < 0]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=buys.index, y=buys['rsi'], mode='markers', name='Buy',
            marker=dict(symbol='triangle-up', size=11, color=VisualizationEngine.COLORS['profit'])
        ))
        fig2.add_trace(go.Scatter(
            x=sells.index, y=sells['rsi'], mode='markers', name='Sell',
            marker=dict(symbol='triangle-down', size=11, color=VisualizationEngine.COLORS['loss'])
        ))
        fig2.add_hline(y=30, line_dash='dash', line_color=VisualizationEngine.COLORS['profit'])
        fig2.add_hline(y=70, line_dash='dash', line_color=VisualizationEngine.COLORS['loss'])
        fig2 = VisualizationEngine._styled_figure(fig2, f"{prefix} RSI Triangle Signal Map")

        fig3 = go.Figure(data=[go.Histogram(x=trades['pnl'], nbinsx=20, marker_color=VisualizationEngine.COLORS['neutral'])])
        fig3 = VisualizationEngine._styled_figure(fig3, f"{prefix} Trade P&L Histogram")

        fig4 = go.Figure()
        fig4.add_trace(go.Candlestick(
            x=frame.index,
            open=frame['open'],
            high=frame['high'],
            low=frame['low'],
            close=frame['close'],
            name='Price',
        ))
        fig4.add_trace(go.Scatter(
            x=buys.index, y=buys['low'], mode='markers', name='RSI Buy',
            marker=dict(symbol='triangle-up', size=10, color=VisualizationEngine.COLORS['profit'])
        ))
        fig4.add_trace(go.Scatter(
            x=sells.index, y=sells['high'], mode='markers', name='RSI Sell',
            marker=dict(symbol='triangle-down', size=10, color=VisualizationEngine.COLORS['loss'])
        ))
        fig4 = VisualizationEngine._styled_figure(fig4, f"{prefix} RSI Reversal Candlestick")

        return [
            {'title': f'{prefix} Trade P&L Curve', 'figure': fig1},
            {'title': f'{prefix} RSI Triangle Signal Map', 'figure': fig2},
            {'title': f'{prefix} Trade P&L Histogram', 'figure': fig3},
            {'title': f'{prefix} RSI Reversal Candlestick', 'figure': fig4},
        ]

    @staticmethod
    def _base_candlestick(frame: pd.DataFrame, title: str) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=frame.index,
            open=frame['open'],
            high=frame['high'],
            low=frame['low'],
            close=frame['close'],
            name='Price',
        ))
        return VisualizationEngine._styled_figure(fig, title, height=420)

    @staticmethod
    def create_metrics_candlestick_pack(data: pd.DataFrame, strategy_name: str) -> List[Dict]:
        frame = VisualizationEngine._signal_frame(data)
        buys = frame[frame['position_event'] > 0]
        sells = frame[frame['position_event'] < 0]
        charts: List[Dict] = []

        fig1 = VisualizationEngine._base_candlestick(frame, "Price Candlestick Overview")
        charts.append({'title': 'Price Candlestick Overview', 'figure': fig1})

        fig2 = VisualizationEngine._base_candlestick(frame, "Candlestick With Buy Sell Markers")
        fig2.add_trace(go.Scatter(x=buys.index, y=buys['low'], mode='markers', marker=dict(symbol='triangle-up', size=10, color=VisualizationEngine.COLORS['profit']), name='Buy'))
        fig2.add_trace(go.Scatter(x=sells.index, y=sells['high'], mode='markers', marker=dict(symbol='triangle-down', size=10, color=VisualizationEngine.COLORS['loss']), name='Sell'))
        charts.append({'title': 'Candlestick With Buy Sell Markers', 'figure': fig2})

        fig3 = VisualizationEngine._base_candlestick(frame, "Candlestick With Moving Averages")
        for col, color in [('fast_ma', VisualizationEngine.COLORS['profit']), ('slow_ma', VisualizationEngine.COLORS['loss']), ('sma', VisualizationEngine.COLORS['neutral'])]:
            if col in frame.columns:
                fig3.add_trace(go.Scatter(x=frame.index, y=frame[col], mode='lines', name=col, line=dict(color=color, width=1.5)))
        charts.append({'title': 'Candlestick With Moving Averages', 'figure': fig3})

        fig4 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.7, 0.3])
        fig4.add_trace(go.Candlestick(x=frame.index, open=frame['open'], high=frame['high'], low=frame['low'], close=frame['close'], name='Price'), row=1, col=1)
        fig4.add_trace(go.Bar(x=frame.index, y=frame['volume'], marker_color=VisualizationEngine.COLORS['neutral'], name='Volume'), row=2, col=1)
        fig4 = VisualizationEngine._styled_figure(fig4, "Candlestick With Volume", height=500)
        charts.append({'title': 'Candlestick With Volume', 'figure': fig4})

        fig5 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.68, 0.32])
        fig5.add_trace(go.Candlestick(x=frame.index, open=frame['open'], high=frame['high'], low=frame['low'], close=frame['close'], name='Price'), row=1, col=1)
        if 'rsi' in frame.columns:
            fig5.add_trace(go.Scatter(x=frame.index, y=frame['rsi'], mode='lines', line=dict(color=VisualizationEngine.COLORS['neutral']), name='RSI'), row=2, col=1)
            fig5.add_hline(y=30, row=2, col=1, line_dash='dash', line_color=VisualizationEngine.COLORS['profit'])
            fig5.add_hline(y=70, row=2, col=1, line_dash='dash', line_color=VisualizationEngine.COLORS['loss'])
        fig5 = VisualizationEngine._styled_figure(fig5, "Candlestick With RSI", height=500)
        charts.append({'title': 'Candlestick With RSI', 'figure': fig5})

        fig6 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.68, 0.32])
        fig6.add_trace(go.Candlestick(x=frame.index, open=frame['open'], high=frame['high'], low=frame['low'], close=frame['close'], name='Price'), row=1, col=1)
        if 'macd' in frame.columns:
            fig6.add_trace(go.Scatter(x=frame.index, y=frame['macd'], mode='lines', name='MACD', line=dict(color=VisualizationEngine.COLORS['profit'])), row=2, col=1)
        if 'signal_line' in frame.columns:
            fig6.add_trace(go.Scatter(x=frame.index, y=frame['signal_line'], mode='lines', name='Signal', line=dict(color=VisualizationEngine.COLORS['loss'])), row=2, col=1)
        if 'histogram' in frame.columns:
            fig6.add_trace(go.Bar(x=frame.index, y=frame['histogram'], name='Histogram', marker_color=VisualizationEngine.COLORS['neutral']), row=2, col=1)
        fig6 = VisualizationEngine._styled_figure(fig6, "Candlestick With MACD", height=500)
        charts.append({'title': 'Candlestick With MACD', 'figure': fig6})

        fig7 = VisualizationEngine._base_candlestick(frame, "Candlestick With Bollinger Bands")
        for col, color in [('upper_band', VisualizationEngine.COLORS['loss']), ('sma', VisualizationEngine.COLORS['neutral']), ('lower_band', VisualizationEngine.COLORS['profit'])]:
            if col in frame.columns:
                fig7.add_trace(go.Scatter(x=frame.index, y=frame[col], mode='lines', name=col, line=dict(color=color, width=1.2)))
        charts.append({'title': 'Candlestick With Bollinger Bands', 'figure': fig7})

        rolling_high = frame['high'].rolling(20).max()
        rolling_low = frame['low'].rolling(20).min()
        fig8 = VisualizationEngine._base_candlestick(frame, "Candlestick With 20 Day Breakout Range")
        fig8.add_trace(go.Scatter(x=frame.index, y=rolling_high, mode='lines', name='20D High', line=dict(color=VisualizationEngine.COLORS['profit'], dash='dot')))
        fig8.add_trace(go.Scatter(x=frame.index, y=rolling_low, mode='lines', name='20D Low', line=dict(color=VisualizationEngine.COLORS['loss'], dash='dot')))
        charts.append({'title': 'Candlestick With 20 Day Breakout Range', 'figure': fig8})

        candle_body = (frame['close'] - frame['open']).abs()
        strongest = frame.nlargest(min(15, len(frame)), candle_body.name if candle_body.name else 'close')
        fig9 = VisualizationEngine._base_candlestick(frame, "Candlestick With Large Body Signals")
        fig9.add_trace(go.Scatter(x=strongest.index, y=strongest['close'], mode='markers', marker=dict(symbol='diamond', size=9, color=VisualizationEngine.COLORS['neutral']), name='Large Body'))
        charts.append({'title': 'Candlestick With Large Body Signals', 'figure': fig9})

        fig10 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.68, 0.32])
        fig10.add_trace(go.Candlestick(x=frame.index, open=frame['open'], high=frame['high'], low=frame['low'], close=frame['close'], name='Price'), row=1, col=1)
        if 'atr' in frame.columns:
            fig10.add_trace(go.Scatter(x=frame.index, y=frame['atr'], mode='lines', line=dict(color=VisualizationEngine.COLORS['neutral']), name='ATR'), row=2, col=1)
        fig10 = VisualizationEngine._styled_figure(fig10, "Candlestick With ATR", height=500)
        charts.append({'title': 'Candlestick With ATR', 'figure': fig10})

        return charts

    @staticmethod
    def _create_common_strategy_charts(data: pd.DataFrame, trade_history: List, prefix: str) -> List[Dict]:
        frame = VisualizationEngine._signal_frame(data)

        signal_counts = frame['signal_state'].value_counts().reindex([-1, 0, 1], fill_value=0)
        fig1 = go.Figure(data=[go.Bar(x=['Sell', 'Flat', 'Buy'], y=signal_counts.values, marker_color=['#FF006E', '#808080', '#00FF41'])])
        fig1 = VisualizationEngine._styled_figure(fig1, f"{prefix} Signal Balance")

        monthly = frame.groupby('month')['signal_state'].apply(lambda x: np.abs(x).sum())
        fig2 = go.Figure(data=[go.Bar(x=monthly.index, y=monthly.values, marker_color=VisualizationEngine.COLORS['neutral'])])
        fig2 = VisualizationEngine._styled_figure(fig2, f"{prefix} Monthly Signal Activity")

        fig3 = VisualizationEngine._create_transition_heatmap(frame, f"{prefix} Signal Transition Map")
        fig4 = go.Figure(data=[go.Scatter(x=frame.index, y=frame['cum_asset_return_pct'], mode='lines', line=dict(color=VisualizationEngine.COLORS['profit']))])
        fig4 = VisualizationEngine._styled_figure(fig4, f"{prefix} Cumulative Asset Return")
        fig5 = VisualizationEngine._create_monthly_heatmap(frame, 'asset_return_pct', f"{prefix} Monthly Return Heatmap")

        rolling = frame['asset_return_pct'].rolling(20).mean()
        fig6 = go.Figure(data=[go.Scatter(x=frame.index, y=rolling, mode='lines', line=dict(color=VisualizationEngine.COLORS['neutral']))])
        fig6 = VisualizationEngine._styled_figure(fig6, f"{prefix} 20-Day Rolling Return")

        scatter = go.Figure()
        scatter.add_trace(
            go.Scatter(
                x=frame['asset_return_pct'],
                y=frame['next_5d_return_pct'],
                mode='markers',
                marker=dict(
                    color=frame['signal_state'],
                    colorscale='RdYlGn',
                    size=7,
                    opacity=0.7,
                ),
                text=frame.index.astype(str),
            )
        )
        scatter = VisualizationEngine._styled_figure(scatter, f"{prefix} Return vs Forward Return")

        regime = VisualizationEngine._regime_duration_series(frame['signal_state'])
        fig8 = go.Figure(data=[go.Bar(x=['Sell', 'Flat', 'Buy'], y=[regime.get(-1, 0), regime.get(0, 0), regime.get(1, 0)], marker_color=['#FF006E', '#808080', '#00FF41'])])
        fig8 = VisualizationEngine._styled_figure(fig8, f"{prefix} Regime Duration Count")

        common = [
            {'title': f'{prefix} Signal Balance', 'figure': fig1},
            {'title': f'{prefix} Monthly Signal Activity', 'figure': fig2},
            {'title': f'{prefix} Signal Transition Map', 'figure': fig3},
            {'title': f'{prefix} Cumulative Asset Return', 'figure': fig4},
            {'title': f'{prefix} Monthly Return Heatmap', 'figure': fig5},
            {'title': f'{prefix} 20-Day Rolling Return', 'figure': fig6},
            {'title': f'{prefix} Return vs Forward Return', 'figure': scatter},
            {'title': f'{prefix} Regime Duration Count', 'figure': fig8},
        ]
        return common + VisualizationEngine._create_trade_charts(trade_history, prefix)

    @staticmethod
    def create_strategy_visualization_pack(
        data: pd.DataFrame,
        strategy_name: str,
        trade_history: List,
    ) -> List[Dict]:
        frame = VisualizationEngine._signal_frame(data)
        charts: List[Dict] = []

        if strategy_name == 'Moving Average Crossover':
            spread = frame['fast_ma'] - frame['slow_ma']
            spread_pct = (spread / frame['close']) * 100
            slope_fast = frame['fast_ma'].diff()
            slope_slow = frame['slow_ma'].diff()
            buys = frame[frame['position_event'] > 0]
            sells = frame[frame['position_event'] < 0]

            fig1 = VisualizationEngine.create_price_with_signals(frame, signal_column='position', ma_columns=['fast_ma', 'slow_ma'])
            fig2 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=spread, mode='lines', line=dict(color=VisualizationEngine.COLORS['neutral']))]), "MA Spread")
            fig3 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=spread_pct, mode='lines', line=dict(color=VisualizationEngine.COLORS['profit']))]), "MA Spread % of Price")
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=frame.index, y=slope_fast, mode='lines', name='Fast MA Slope'))
            fig4.add_trace(go.Scatter(x=frame.index, y=slope_slow, mode='lines', name='Slow MA Slope'))
            fig4 = VisualizationEngine._styled_figure(fig4, "MA Slope Comparison")
            fig5 = go.Figure(data=[go.Scatter(x=buys.index, y=buys['close'], mode='markers', marker=dict(color=VisualizationEngine.COLORS['profit'], size=9))])
            fig5 = VisualizationEngine._styled_figure(fig5, "Bullish Crossover Points")
            fig6 = go.Figure(data=[go.Scatter(x=sells.index, y=sells['close'], mode='markers', marker=dict(color=VisualizationEngine.COLORS['loss'], size=9))])
            fig6 = VisualizationEngine._styled_figure(fig6, "Bearish Crossover Points")
            fig7 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=((frame['close'] - frame['fast_ma']) / frame['fast_ma']) * 100, mode='lines')]), "Distance From Fast MA")
            fig8 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=((frame['close'] - frame['slow_ma']) / frame['slow_ma']) * 100, mode='lines')]), "Distance From Slow MA")
            forward_group = pd.DataFrame({
                'event': np.where(frame['position_event'] > 0, 'Bullish', np.where(frame['position_event'] < 0, 'Bearish', 'Flat')),
                'forward_return': frame['next_5d_return_pct'],
            }).query("event != 'Flat'")
            fig9 = px.box(forward_group, x='event', y='forward_return', color='event')
            fig9 = VisualizationEngine._styled_figure(fig9, "Forward Return by Crossover Type")
            fig10 = VisualizationEngine._create_monthly_heatmap(frame.assign(ma_spread=spread_pct), 'ma_spread', "MA Spread Monthly Heatmap")
            charts = [
                {'title': 'MA Price With Crossovers', 'figure': fig1},
                {'title': 'MA Spread', 'figure': fig2},
                {'title': 'MA Spread % of Price', 'figure': fig3},
                {'title': 'MA Slope Comparison', 'figure': fig4},
                {'title': 'Bullish Crossover Points', 'figure': fig5},
                {'title': 'Bearish Crossover Points', 'figure': fig6},
                {'title': 'Distance From Fast MA', 'figure': fig7},
                {'title': 'Distance From Slow MA', 'figure': fig8},
                {'title': 'Forward Return by Crossover Type', 'figure': fig9},
                {'title': 'MA Spread Monthly Heatmap', 'figure': fig10},
            ]

        elif strategy_name == 'RSI Momentum':
            zone = pd.cut(frame['rsi'], bins=[-np.inf, 30, 70, np.inf], labels=['Oversold', 'Neutral', 'Overbought'])
            fig1 = VisualizationEngine.create_price_with_signals(frame, signal_column='position')
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=frame.index, y=frame['rsi'], mode='lines', line=dict(color=VisualizationEngine.COLORS['neutral'])))
            fig2.add_hline(y=30, line_dash='dash', line_color=VisualizationEngine.COLORS['profit'])
            fig2.add_hline(y=70, line_dash='dash', line_color=VisualizationEngine.COLORS['loss'])
            fig2 = VisualizationEngine._styled_figure(fig2, "RSI Oscillator")
            fig3 = VisualizationEngine._styled_figure(go.Figure(data=[go.Histogram(x=frame['rsi'], nbinsx=30, marker_color=VisualizationEngine.COLORS['neutral'])]), "RSI Distribution")
            fig4 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=zone.value_counts().index.astype(str), y=zone.value_counts().values)]), "RSI Zone Occupancy")
            fig5 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=frame['rsi'].diff(), mode='lines')]), "RSI Slope")
            zone_returns = pd.DataFrame({'zone': zone.astype(str), 'forward_return': frame['next_5d_return_pct']}).dropna()
            fig6 = VisualizationEngine._styled_figure(px.box(zone_returns, x='zone', y='forward_return', color='zone'), "Forward Return by RSI Zone")
            fig7 = VisualizationEngine._styled_figure(px.scatter(frame, x='rsi', y='next_5d_return_pct', color='signal_state', color_continuous_scale='RdYlGn'), "RSI vs Forward Return")
            roll_rsi = frame['rsi'].rolling(10).mean()
            fig8 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=roll_rsi, mode='lines')]), "Rolling RSI Mean")
            fig9 = VisualizationEngine._create_monthly_heatmap(frame.assign(rsi_value=frame['rsi']), 'rsi_value', "RSI Monthly Heatmap")
            fig10 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=frame['weekday'].value_counts().index, y=frame['weekday'].value_counts().values)]), "Signal Sessions by Weekday")
            charts = [
                {'title': 'RSI Price With Signals', 'figure': fig1},
                {'title': 'RSI Oscillator', 'figure': fig2},
                {'title': 'RSI Distribution', 'figure': fig3},
                {'title': 'RSI Zone Occupancy', 'figure': fig4},
                {'title': 'RSI Slope', 'figure': fig5},
                {'title': 'Forward Return by RSI Zone', 'figure': fig6},
                {'title': 'RSI vs Forward Return', 'figure': fig7},
                {'title': 'Rolling RSI Mean', 'figure': fig8},
                {'title': 'RSI Monthly Heatmap', 'figure': fig9},
                {'title': 'Signal Sessions by Weekday', 'figure': fig10},
            ]
            common = VisualizationEngine._create_common_strategy_charts(frame, trade_history, strategy_name)
            return charts + common[:-4] + VisualizationEngine._create_rsi_trade_charts(frame, trade_history, strategy_name)

        elif strategy_name == 'MACD Crossover':
            hist_slope = frame['histogram'].diff()
            positive_hist = np.where(frame['histogram'] >= 0, 'Positive', 'Negative')
            fig1 = VisualizationEngine.create_price_with_signals(frame, signal_column='position')
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=frame.index, y=frame['macd'], mode='lines', name='MACD'))
            fig2.add_trace(go.Scatter(x=frame.index, y=frame['signal_line'], mode='lines', name='Signal'))
            fig2 = VisualizationEngine._styled_figure(fig2, "MACD vs Signal")
            fig3 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=frame.index, y=frame['histogram'], marker_color=np.where(frame['histogram'] >= 0, VisualizationEngine.COLORS['profit'], VisualizationEngine.COLORS['loss']))]), "MACD Histogram")
            fig4 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=(frame['macd'] - frame['signal_line']), mode='lines')]), "MACD Spread")
            fig5 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=hist_slope, mode='lines')]), "Histogram Momentum")
            fig6 = VisualizationEngine._styled_figure(go.Figure(data=[go.Histogram(x=frame['histogram'], nbinsx=30, marker_color=VisualizationEngine.COLORS['neutral'])]), "Histogram Distribution")
            fig7 = VisualizationEngine._styled_figure(px.box(pd.DataFrame({'state': positive_hist, 'forward_return': frame['next_5d_return_pct']}), x='state', y='forward_return', color='state'), "Forward Return by MACD State")
            fig8 = VisualizationEngine._styled_figure(px.scatter(frame, x='macd', y='next_5d_return_pct', color='histogram', color_continuous_scale='RdYlGn'), "MACD vs Forward Return")
            fig9 = VisualizationEngine._create_monthly_heatmap(frame.assign(histogram_value=frame['histogram']), 'histogram_value', "MACD Histogram Monthly Heatmap")
            fig10 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=['Positive', 'Negative'], y=[(frame['histogram'] >= 0).sum(), (frame['histogram'] < 0).sum()])]), "Positive vs Negative Histogram Bars")
            charts = [
                {'title': 'MACD Price With Signals', 'figure': fig1},
                {'title': 'MACD vs Signal', 'figure': fig2},
                {'title': 'MACD Histogram', 'figure': fig3},
                {'title': 'MACD Spread', 'figure': fig4},
                {'title': 'Histogram Momentum', 'figure': fig5},
                {'title': 'Histogram Distribution', 'figure': fig6},
                {'title': 'Forward Return by MACD State', 'figure': fig7},
                {'title': 'MACD vs Forward Return', 'figure': fig8},
                {'title': 'MACD Histogram Monthly Heatmap', 'figure': fig9},
                {'title': 'Positive vs Negative Histogram Bars', 'figure': fig10},
            ]

        elif strategy_name == 'Mean Reversion':
            band_width = ((frame['upper_band'] - frame['lower_band']) / frame['sma']) * 100
            band_position = (frame['close'] - frame['lower_band']) / (frame['upper_band'] - frame['lower_band'])
            distance_mid = ((frame['close'] - frame['sma']) / frame['sma']) * 100
            zone = pd.cut(band_position, bins=[-np.inf, 0, 1, np.inf], labels=['Below Band', 'Inside Band', 'Above Band'])
            fig1 = VisualizationEngine.create_price_with_signals(frame, signal_column='position', ma_columns=['sma', 'upper_band', 'lower_band'])
            fig2 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=band_width, mode='lines')]), "Bollinger Band Width %")
            fig3 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=distance_mid, mode='lines')]), "Distance From Mid Band")
            fig4 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=band_position, mode='lines')]), "Band Position Ratio")
            fig5 = VisualizationEngine._styled_figure(go.Figure(data=[go.Histogram(x=distance_mid, nbinsx=30, marker_color=VisualizationEngine.COLORS['neutral'])]), "Reversion Distance Distribution")
            fig6 = VisualizationEngine._styled_figure(px.box(pd.DataFrame({'zone': zone.astype(str), 'forward_return': frame['next_5d_return_pct']}), x='zone', y='forward_return', color='zone'), "Forward Return by Band Zone")
            fig7 = VisualizationEngine._styled_figure(px.scatter(frame, x=band_position, y='next_5d_return_pct', color='signal_state', color_continuous_scale='RdYlGn'), "Band Position vs Forward Return")
            fig8 = VisualizationEngine._create_monthly_heatmap(frame.assign(band_width=band_width), 'band_width', "Band Width Monthly Heatmap")
            fig9 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=zone.value_counts().index.astype(str), y=zone.value_counts().values)]), "Band Zone Occupancy")
            fig10 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=['Lower Touch', 'Upper Touch'], y=[(frame['close'] < frame['lower_band']).sum(), (frame['close'] > frame['upper_band']).sum()])]), "Band Touch Count")
            charts = [
                {'title': 'Mean Reversion Price With Bands', 'figure': fig1},
                {'title': 'Bollinger Band Width %', 'figure': fig2},
                {'title': 'Distance From Mid Band', 'figure': fig3},
                {'title': 'Band Position Ratio', 'figure': fig4},
                {'title': 'Reversion Distance Distribution', 'figure': fig5},
                {'title': 'Forward Return by Band Zone', 'figure': fig6},
                {'title': 'Band Position vs Forward Return', 'figure': fig7},
                {'title': 'Band Width Monthly Heatmap', 'figure': fig8},
                {'title': 'Band Zone Occupancy', 'figure': fig9},
                {'title': 'Band Touch Count', 'figure': fig10},
            ]

        else:
            combo_score = ((50 - frame['rsi']) / 50) + (frame['macd'] / frame['close'].replace(0, np.nan))
            quadrant = pd.DataFrame({
                'rsi_zone': np.where(frame['rsi'] >= 50, 'RSI > 50', 'RSI < 50'),
                'macd_zone': np.where(frame['macd'] >= 0, 'MACD > 0', 'MACD < 0'),
            })
            fig1 = VisualizationEngine.create_price_with_signals(frame, signal_column='position')
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=frame.index, y=frame['rsi'], mode='lines', name='RSI'))
            fig2.add_hline(y=50, line_dash='dash')
            fig2 = VisualizationEngine._styled_figure(fig2, "RSI Confirmation")
            fig3 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=frame['macd'], mode='lines')]), "MACD Confirmation")
            fig4 = VisualizationEngine._styled_figure(px.scatter(frame, x='rsi', y='macd', color='signal_state', color_continuous_scale='RdYlGn'), "RSI vs MACD Signal Map")
            quad_table = pd.crosstab(quadrant['rsi_zone'], quadrant['macd_zone'])
            fig5 = VisualizationEngine._styled_figure(go.Figure(data=[go.Heatmap(z=quad_table.values, x=quad_table.columns, y=quad_table.index, colorscale='Viridis')]), "RSI MACD Quadrant Heatmap")
            fig6 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=combo_score, mode='lines')]), "Composite Score")
            combo_regime = pd.DataFrame({'regime': np.where(combo_score > 0, 'Bullish', 'Bearish'), 'forward_return': frame['next_5d_return_pct']})
            fig7 = VisualizationEngine._styled_figure(px.box(combo_regime, x='regime', y='forward_return', color='regime'), "Forward Return by Composite Regime")
            fig8 = VisualizationEngine._create_monthly_heatmap(frame.assign(combo_score=combo_score), 'combo_score', "Composite Score Monthly Heatmap")
            fig9 = VisualizationEngine._styled_figure(go.Figure(data=[go.Scatter(x=frame.index, y=frame['rsi'] - 50, mode='lines', name='RSI Centered'), go.Scatter(x=frame.index, y=frame['macd'], mode='lines', name='MACD')]), "RSI and MACD Divergence")
            combo_duration = VisualizationEngine._regime_duration_series(pd.Series(np.where(combo_score > 0, 1, -1), index=frame.index))
            fig10 = VisualizationEngine._styled_figure(go.Figure(data=[go.Bar(x=['Bearish', 'Bullish'], y=[combo_duration.get(-1, 0), combo_duration.get(1, 0)])]), "Composite Regime Duration")
            charts = [
                {'title': 'RSI MACD Price With Signals', 'figure': fig1},
                {'title': 'RSI Confirmation', 'figure': fig2},
                {'title': 'MACD Confirmation', 'figure': fig3},
                {'title': 'RSI vs MACD Signal Map', 'figure': fig4},
                {'title': 'RSI MACD Quadrant Heatmap', 'figure': fig5},
                {'title': 'Composite Score', 'figure': fig6},
                {'title': 'Forward Return by Composite Regime', 'figure': fig7},
                {'title': 'Composite Score Monthly Heatmap', 'figure': fig8},
                {'title': 'RSI and MACD Divergence', 'figure': fig9},
                {'title': 'Composite Regime Duration', 'figure': fig10},
            ]

        return charts + VisualizationEngine._create_common_strategy_charts(frame, trade_history, strategy_name)
