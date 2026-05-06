import pandas as pd

class SignalEngine:
    """
    Generates trading signals with comprehensive rationale logs for explainability[cite: 1].
    """
    def __init__(self):
        self.explainable_logs = []

    def get_signal(self, asset_name, df):
        """
        Issue 14: Analyzes features and logs the rationale for 'Buy/Sell/Hold'[cite: 1].
        """
        latest_data = df.iloc[-1]
        timestamp = df.index[-1]
        
        rsi = latest_data.get('rsi', 50)
        sma_fast = latest_data.get('sma_fast', 0)
        sma_slow = latest_data.get('sma_slow', 0)
        
        signal = 0 # Default: Hold
        reason = "Neutral market conditions; no threshold breach."

        # Strategy Logic: Trend-following with Momentum filter[cite: 1]
        if sma_fast > sma_slow and rsi < 35:
            signal = 1
            reason = f"BUY: Fast SMA ({sma_fast:.2f}) > Slow SMA ({sma_slow:.2f}) and RSI ({rsi:.2f}) indicates oversold."
        elif sma_fast < sma_slow and rsi > 65:
            signal = -1
            reason = f"SELL: Fast SMA ({sma_fast:.2f}) < Slow SMA ({sma_slow:.2f}) and RSI ({rsi:.2f}) indicates overbought."

        # Issue 14: Log the rationale for every generated signal[cite: 1]
        self.explainable_logs.append({
            'timestamp': timestamp,
            'asset': asset_name,
            'signal': signal,
            'rationale': reason,
            'metrics': {'rsi': rsi, 'sma_diff': sma_fast - sma_slow}
        })
        
        return signal, reason