import pandas as pd
import numpy as np
import logging

class AdvancedFeatureEngineer:
    def __init__(self, macro_df=None):
        """
        Initializes the engineer with optional macroeconomic data for integration.
        """
        self.macro = macro_df

    def add_technical_indicators(self, df):
        """
        Issue 3: Calculates momentum and trend indicators.
        Ensures explainable strategy inputs.
        """
        # 1. RSI (Momentum)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi'] = 100 - (100 / (1 + (gain / loss)))

        # 2. SMA Crossover (Trend)
        df['sma_fast'] = df['price'].rolling(window=10).mean()
        df['sma_slow'] = df['price'].rolling(window=50).mean()
        
        return df

    def add_risk_features(self, df):
        """
        Issue 3: Calculates historical volatility over rolling windows[cite: 1].
        Critical for risk-aware position sizing[cite: 1].
        """
        # Annualized rolling volatility (21-day window)
        df['volatility_21d'] = df['price'].pct_change().rolling(window=21).std() * np.sqrt(252)
        
        # Log returns for statistical modeling
        df['log_ret'] = np.log(df['price'] / df['price'].shift(1))
        
        return df

    def align_macro_data(self, asset_df):
        """
        Issue 4: Synchronizes daily market data with monthly macro indicators[cite: 1].
        Uses forward-filling to prevent forward-looking bias[cite: 1].
        """
        if self.macro is None:
            return asset_df
            
        # Aligns dates and carries forward the last known macro value[cite: 1]
        aligned_macro = self.macro.reindex(asset_df.index).ffill()
        
        # Z-score normalization for strategy pipeline use[cite: 1]
        normalized_macro = (aligned_macro - aligned_macro.mean()) / aligned_macro.std()
        
        return pd.concat([asset_df, normalized_macro], axis=1)