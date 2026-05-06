import numpy as np
import pandas as pd

class RiskModeler:
    """
    Implements risk modeling techniques required for portfolio evaluation.
    """

    @staticmethod
    def calculate_var(returns, confidence_level=0.95):
        """
        Issue 6: Value at Risk (VaR) via Historical Simulation.
        Calculates potential loss over a 1-day period at a given confidence interval.
        """
        if returns.empty:
            return 0.0
        # Historical simulation accounts for 'fat tails' in financial data[cite: 1].
        # Percentile is calculated based on the lower tail of returns.
        return np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def calculate_max_drawdown(equity_series):
        """
        Issue 7: Tracks the largest peak-to-trough drop in portfolio value[cite: 1].
        Essential for evaluating the strategy's risk profile[cite: 1].
        """
        if equity_series.empty:
            return 0.0
            
        # Calculate the running maximum of the equity curve
        rolling_max = equity_series.cummax()
        # Calculate drawdown percentage from the peak
        drawdowns = (equity_series - rolling_max) / rolling_max
        return drawdowns.min() # Returns the deepest negative value

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """
        Issue 12: Calculates annualized risk-adjusted returns[cite: 1].
        """
        if returns.empty or returns.std() == 0:
            return 0.0
            
        mean_ann_ret = returns.mean() * 252
        ann_vol = returns.std() * np.sqrt(252)
        
        return (mean_ann_ret - risk_free_rate) / ann_vol

    @staticmethod
    def calculate_alpha_beta(portfolio_returns, market_returns, risk_free_rate=0.02):
        """
        Issue 13: Benchmarks strategy performance against market trends[cite: 1].
        Determines excess return (Alpha) and relative volatility (Beta)[cite: 1].
        """
        if portfolio_returns.empty or market_returns.empty:
            return 0.0, 1.0
            
        # Ensure returns are aligned on the same timeline
        combined = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        if combined.empty:
            return 0.0, 1.0
            
        p_ret = combined.iloc[:, 0]
        m_ret = combined.iloc[:, 1]

        # Beta calculation: Covariance / Market Variance[cite: 1]
        covariance = np.cov(p_ret, m_ret)[0][1]
        market_var = np.var(m_ret)
        beta = covariance / market_var if market_var != 0 else 1.0

        # Annualized Alpha (excess return independent of market trends)[cite: 1]
        ann_p_ret = p_ret.mean() * 252
        ann_m_ret = m_ret.mean() * 252
        alpha = ann_p_ret - (risk_free_rate + beta * (ann_m_ret - risk_free_rate))
        
        return alpha, beta