import pandas as pd
import numpy as np

class AdvancedFeatureEngineer:
    def __init__(self, daily_data_dict, macro_df=None):
        self.assets = daily_data_dict
        self.macro = macro_df

    def align_macro_data(self, asset_df):
        """Issue 4: Aligns asynchronous macro data with market timeline"""
        if self.macro is None:
            return asset_df
            
        # Reindex macro to match asset timestamps and forward-fill
        # This solves the monthly vs daily frequency mismatch
        aligned_macro = self.macro.reindex(asset_df.index).ffill()
        
        # Normalize macro signals (Z-score) for use in strategy pipeline
        normalized_macro = (aligned_macro - aligned_macro.mean()) / aligned_macro.std()
        
        return pd.concat([asset_df, normalized_macro], axis=1)

    def generate_features(self):
        """Issue 3: Efficient rolling window computations for Risk/Momentum"""
        for name, df in self.assets.items():
            # 1. Momentum: RSI (14-day)
            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df['rsi'] = 100 - (100 / (1 + (gain / loss)))

            # 2. Historical Volatility: Annualized rolling std dev
            df['volatility_21d'] = df['price'].pct_change().rolling(window=21).std() * np.sqrt(252)

            # 3. Trend: Moving Average Crossover
            df['sma_fast'] = df['price'].rolling(window=10).mean()
            df['sma_slow'] = df['price'].rolling(window=50).mean()
            
            # Integrate Macro
            self.assets[name] = self.align_macro_data(df).dropna()
        
        return self.assets
    class PortfolioManager:
        def __init__(self, initial_capital, risk_tolerance, position_limits):
            self.initial_capital = initial_capital
            self.cash = initial_capital
            self.positions = {}  # {asset_name: quantity}
            self.risk_tolerance = risk_tolerance
            self.position_limits = position_limits # e.g., 0.20 for max 20% in one asset
            self.trade_log = []

        def get_portfolio_value(self, current_prices):
            """Calculates total value: Cash + sum(Positions * Price)"""
            asset_value = sum(self.positions.get(name, 0) * price 
                            for name, price in current_prices.items())
            return self.cash + asset_value

        def execute_trade(self, asset_name, quantity, price, timestamp):
            """Enforces constraints and executes simulated trades"""
            total_value = self.get_portfolio_value({asset_name: price})
            trade_cost = quantity * price
            
            # 1. Position Limit Check (Constraint Enforcement)
            new_allocation = (self.positions.get(asset_name, 0) + quantity) * price / total_value
            if new_allocation > self.position_limits:
                return "Trade Rejected: Position Limit Exceeded"

            # 2. Capital Check
            if trade_cost > self.cash:
                return "Trade Rejected: Insufficient Funds"

            # 3. Update State
            self.cash -= trade_cost
            self.positions[asset_name] = self.positions.get(asset_name, 0) + quantity
            self.trade_log.append({
                'timestamp': timestamp,
                'asset': asset_name,
                'qty': quantity,
                'price': price
            })
            return "Trade Executed"