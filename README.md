# Hedge Fund Risk Modeling & Semi-Automated Trading System

## Team Information
- **Team Name**: NoIdea
- **Year**: 1
- **All-Female Team**: Yes

## Architecture Overview

Our system utilizes a configuration-driven pipeline to concurrently ingest diverse data sources, standardizing market and macro indicators while preventing look-ahead bias through forward-filling.Macro and sentiment datasets are synchronized and normalized to ensure a consistent strategy timeline
For risk modeling, we selected historical Value at Risk (VaR) and Maximum Drawdown to establish robust boundaries for portfolio exposure
These metrics are integrated into the pipeline via volatility-targeted position sizing, which ensures capital allocation adheres to strict portfolio constraints and equalizes risk contributions across all assets
The semi-automated engine generates explainable signals using rule-based logic (SMA/RSI), filtered through realistic market conditions such as transaction costs and slippage.
Safeguards documented intercept trades that would exceed available capital, preventing overexposure and ensuring system stability
Finally,the dashboard delivers explainable insights by visualizing key metrics like Sharpe Ratio, Alpha, and Beta.
Rationale logs provide a transparent audit trail for every trade, ensuring all decisions are understandable.