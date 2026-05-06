import numpy as np
import pandas as pd

class RiskModeler:
    """
    Computes performance and risk-adjusted metrics to evaluate strategy success.
    """

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """
        Issue 12: Calculates the annualized Sharpe Ratio.
        """
        if returns.empty:
            return 0.0
        
        # Annualize the mean return and volatility
        mean_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        
        if volatility == 0:
            return 0.0
            
        return (mean_return - risk_free_rate) / volatility

    @staticmethod
    def calculate_alpha_beta(portfolio_returns, market_returns, risk_free_rate=0.02):
        """
        Issue 13: Computes Alpha and Beta against a market benchmark.
        """
        if portfolio_returns.empty or market_returns.empty:
            return 0.0, 1.0
            
        # Ensure returns are aligned on the same dates
        combined = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        p_ret = combined.iloc[:, 0]
        m_ret = combined.iloc[:, 1]

        # Calculate Beta: Covariance(p, m) / Variance(m)
        covariance = np.cov(p_ret, m_ret)[0][1]
        market_variance = np.var(m_ret)
        beta = covariance / market_variance if market_variance != 0 else 1.0

        # Calculate Annualized Alpha (Excess Return)
        ann_p_ret = p_ret.mean() * 252
        ann_m_ret = m_ret.mean() * 252
        
        # CAPM Formula: Alpha = Rp - [Rf + Beta * (Rm - Rf)]
        alpha = ann_p_ret - (risk_free_rate + beta * (ann_m_ret - risk_free_rate))
        
        return alpha, beta