import datetime
import logging
import numpy as np
import pandas as pd

class PortfolioManager:
    def __init__(self, initial_capital, position_limit=0.20):
        self.cash = initial_capital
        self.positions = {}       # {asset_name: quantity}
        self.position_limit = position_limit
        self.equity_curve = []    # List of (timestamp, total_value) for dashboard
        self.trade_history = []   # Issue 14: Explainable trade logs
        self.commission_rate = 0.001 
        self.slippage_model = 0.0005

    def get_portfolio_value(self, current_prices):
        """
        Calculates the current Net Asset Value (NAV).
        NAV = Cash + Sum(Positions * Market Price)
        """
        assets_value = sum(
            self.positions.get(asset, 0) * price 
            for asset, price in current_prices.items()
        )
        return self.cash + assets_value

    def record_daily_state(self, timestamp, current_prices):
        """
        Issue 18: Aggregates daily portfolio values for visualization.
        This method is required for main.py to track performance trajectory.
        """
        total_val = self.get_portfolio_value(current_prices)
        self.equity_curve.append({
            'timestamp': timestamp,
            'total_value': total_val
        })

    def calculate_position_size(self, asset_price, asset_volatility, total_equity):
        """Issue 9: Determines capital allocation based on risk and limits[cite: 1]."""
        if asset_volatility == 0 or np.isnan(asset_volatility):
            return 0
            
        # Volatility targeting logic[cite: 1]
        risk_amount = total_equity * 0.01 
        qty = risk_amount / (asset_price * asset_volatility)
        
        # Enforce position limits (e.g., max 20% of portfolio)[cite: 1]
        max_qty = (total_equity * self.position_limit) / asset_price
        return min(qty, max_qty)

    def execute_trade(self, asset, quantity, price, timestamp, reason):
        """
        Issue 10 & 15: Simulates trade execution with friction and capital checks[cite: 1].
        """
        # Apply slippage (Buy higher, sell lower)[cite: 1]
        direction = 1 if quantity > 0 else -1
        exec_price = price * (1 + (self.slippage_model * direction))
        
        notional = abs(quantity) * exec_price
        commission = notional * self.commission_rate
        total_cost = (quantity * exec_price) + commission

        # Issue 15: Safeguard against insufficient capital[cite: 1]
        if self.cash < total_cost and quantity > 0:
            self.record_execution_failure(asset, timestamp, "Insufficient Capital")
            return False

        # Update State
        self.cash -= total_cost
        self.positions[asset] = self.positions.get(asset, 0) + quantity
        
        # Issue 14: Log execution for explainability[cite: 1]
        self.trade_history.append({
            'timestamp': timestamp,
            'asset': asset,
            'quantity': quantity,
            'price': exec_price,
            'rationale': reason,
            'status': 'Executed'
        })
        return True

    def record_execution_failure(self, asset, timestamp, reason):
        logging.error(f"Trade Rejected: {asset} at {timestamp} - {reason}[cite: 1]")