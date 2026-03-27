"""
QuantBack Pro - LLM Integration
AI-powered strategy analysis and insights
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Optional

from google import genai


class LLMAnalyzer:
    """AI-powered trading strategy analysis"""

    @staticmethod
    def _load_env_file() -> None:
        """Load simple KEY=VALUE pairs from the project .env file."""
        env_path = Path(__file__).resolve().parent / ".env"
        if not env_path.exists():
            return

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM analyzer"""
        self._load_env_file()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def _complete(self, prompt: str) -> str:
        """Call Gemini and return plain text output."""
        if not self.api_key or not self.client:
            return (
                "Gemini API key not configured. Set GEMINI_API_KEY in your environment "
                "or .env file."
            )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if text is None:
                return "Gemini API returned no text content."

            parsed_text = str(text).strip()
            if parsed_text.lower() in {"", "none", "null"}:
                return "Gemini API returned no text content."
            return parsed_text
        except Exception as exc:
            return f"Gemini API request failed: {exc}"

    def analyze_strategy(
        self,
        strategy_name: str,
        ticker: str,
        stats: Dict,
        overfitting_analysis: Dict,
        trade_count: int,
    ) -> str:
        """Generate AI analysis of strategy performance"""

        prompt = f"""
        You are an expert quantitative trading analyst. Analyze the following trading strategy backtest results and provide actionable insights.

        Strategy Details:
        - Strategy Type: {strategy_name}
        - Ticker: {ticker}
        - Total Trades: {trade_count}

        Performance Metrics:
        - Total Return: {stats.get('total_return', 0)*100:.2f}%
        - CAGR: {stats.get('cagr', 0)*100:.2f}%
        - Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}
        - Sortino Ratio: {stats.get('sortino_ratio', 0):.2f}
        - Max Drawdown: {stats.get('max_drawdown', 0)*100:.2f}%
        - Win Rate: {stats.get('win_rate', 0)*100:.2f}%
        - Profit Factor: {stats.get('profit_factor', 0):.2f}
        - Average Trade Return: {stats.get('avg_trade_return', 0)*100:.2f}%

        Walk-Forward Analysis:
        - Average Train Sharpe: {overfitting_analysis.get('avg_train_sharpe', 0) if overfitting_analysis.get('avg_train_sharpe') is not None else 'N/A'}
        - Average Test Sharpe: {overfitting_analysis.get('avg_test_sharpe', 0) if overfitting_analysis.get('avg_test_sharpe') is not None else 'N/A'}
        - Sharpe Degradation: {overfitting_analysis.get('sharpe_degradation', 0) if overfitting_analysis.get('sharpe_degradation') is not None else 'N/A'}
        - Detected Overfitting: {overfitting_analysis.get('is_overfit', 'N/A')}

        Please provide:
        1. Performance Assessment
        2. Risk Analysis
        3. Overfitting Concerns
        4. Improvement Suggestions
        5. Trading Recommendations
        6. Risk Management

        Format your response with clear headers and actionable advice.
        """
        return self._complete(prompt)

    def suggest_improvements(
        self,
        strategy_name: str,
        stats: Dict,
        trade_history: list,
    ) -> str:
        """Suggest strategy improvements"""

        losing_trades = sum(1 for t in trade_history if t.pnl < 0)
        largest_loss = min([t.pnl for t in trade_history]) if trade_history else 0
        largest_win = max([t.pnl for t in trade_history]) if trade_history else 0

        prompt = f"""
        As a quantitative trading expert, suggest specific improvements for a {strategy_name} strategy with these characteristics:

        - Current Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}
        - Current Win Rate: {stats.get('win_rate', 0)*100:.2f}%
        - Losing Trades: {losing_trades}
        - Largest Loss: ${largest_loss:.2f}
        - Largest Win: ${largest_win:.2f}
        - Total Trades: {len(trade_history)}

        Provide:
        1. Three specific parameter adjustments to try
        2. Alternative entry/exit signals that might work better
        3. Risk management rules to reduce drawdowns
        4. Market condition filters
        5. Position sizing strategies

        Be specific and actionable.
        """
        return self._complete(prompt)

    def explain_strategy(self, strategy_code: str) -> str:
        """Explain how a strategy works in simple terms"""

        prompt = f"""
        Explain this trading strategy in simple, non-technical terms suitable for someone learning about trading:

        ```python
        {strategy_code}
        ```

        Provide:
        1. What the strategy does in plain English
        2. When it buys and why
        3. When it sells and why
        4. What market conditions favor this strategy
        5. Common pitfalls of this approach
        """
        return self._complete(prompt)

    def generate_report(
        self,
        strategy_name: str,
        ticker: str,
        stats: Dict,
        trade_count: int,
        time_period: str,
    ) -> str:
        """Generate professional trading report"""

        prompt = f"""
        Generate a professional trading analysis report for:

        Title: {strategy_name} Strategy Backtest Report - {ticker}
        Period: {time_period}

        Key Metrics:
        - Total Return: {stats.get('total_return', 0)*100:.2f}%
        - Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}
        - Max Drawdown: {stats.get('max_drawdown', 0)*100:.2f}%
        - Win Rate: {stats.get('win_rate', 0)*100:.2f}%
        - Total Trades: {trade_count}

        Create a report with:
        1. Executive Summary
        2. Strategy Overview
        3. Detailed Results Analysis
        4. Risk Assessment
        5. Conclusion and Recommendations
        """
        return self._complete(prompt)

    def compare_strategies(self, strategies_stats: Dict[str, Dict]) -> str:
        """Compare multiple strategies"""

        stats_text = "\n".join(
            [
                f"\n{name}:\n" + "\n".join([f"  - {k}: {v}" for k, v in stats.items()])
                for name, stats in strategies_stats.items()
            ]
        )

        prompt = f"""
        Compare these trading strategies and recommend which one to use:

        {stats_text}

        Provide:
        1. Strengths and weaknesses of each
        2. Risk-adjusted performance comparison
        3. Which is best for different market conditions
        4. Recommendation with reasoning
        """
        return self._complete(prompt)


class StrategyOptimizer:
    """AI-assisted strategy optimization suggestions"""

    def __init__(self, api_key: Optional[str] = None):
        self.llm = LLMAnalyzer(api_key)

    def suggest_parameters(
        self,
        strategy_name: str,
        current_params: Dict,
        performance_issue: str,
    ) -> Dict:
        """Suggest new parameters based on performance issues"""

        prompt = f"""
        For a {strategy_name} strategy with current parameters:
        {json.dumps(current_params, indent=2)}

        The strategy has this issue: {performance_issue}

        Suggest specific parameter adjustments as a JSON object. Return ONLY valid JSON.
        Example format:
        {{
            "parameter_name": {{"current": value, "suggested": value, "reasoning": "why"}},
            ...
        }}
        """

        response_text = self.llm._complete(prompt)

        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {}
