import os
import pickle
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# Modular imports
from config import ASSET_CONFIGS
from ingestion import UniversalIngestionPipeline
from features import AdvancedFeatureEngineer
from risk_metrics import RiskModeler
from trading_engine import SignalEngine
from portfolio_state import PortfolioManager
from rebalancer import PortfolioRebalancer

# --- ISSUE 17: Global Wrapper for Multi-Asset Scalability ---
def feature_engineer_wrapper(asset_tuple):
    """
    Top-level function required for ProcessPoolExecutor to pickle correctly.
    """
    name, df = asset_tuple
    engineer = AdvancedFeatureEngineer() 
    
    # Issue 3: Volatility and Momentum Features
    df = engineer.add_technical_indicators(df)
    df = engineer.add_risk_features(df)
    
    return name, df.dropna()

def main():
    # 1. INGESTION
    print("Step 1: Starting Multi-Asset Ingestion...")
    pipeline = UniversalIngestionPipeline(data_dir='data/raw', configs=ASSET_CONFIGS)
    assets_data = pipeline.run_pipeline()

    if not assets_data:
        print("Error: No assets loaded. Execution halted.")
        return

    # 2. PARALLEL FEATURE ENGINEERING (Issue 17)
    print(f"Step 2: Scaling features across {os.cpu_count()} cores...")
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(feature_engineer_wrapper, assets_data.items()))
    
    universe = {name: df for name, df in results}

    # 3. SYSTEM INITIALIZATION
    print("Step 3: Initializing Trading & Risk Engine...")
    manager = PortfolioManager(initial_capital=100000)
    signals = SignalEngine()
    risk = RiskModeler()
    
    # Master timeline for backtest synchronization
    all_timestamps = sorted(pd.concat([df.index.to_series() for df in universe.values()]).unique())
    
    # 4. SIMULATION LOOP (Issue 10, 15)[cite: 1]
    print("Step 4: Running Simulation Loop...")
    for ts in all_timestamps:
        current_prices = {}
        
        for name, df in universe.items():
            if ts in df.index:
                history = df.loc[:ts] # Prevents forward-looking bias[cite: 1]
                current_price = history['price'].iloc[-1]
                current_prices[name] = current_price
                
                # Issue 8 & 14: Explainable Signal Generation[cite: 1]
                sig, reason = signals.get_signal(name, history)
                
                if sig != 0:
                    # Issue 9: Risk-Aware Position Sizing[cite: 1]
                    vol = history['volatility_21d'].iloc[-1]
                    qty = manager.calculate_position_size(current_price, vol, manager.get_portfolio_value(current_prices))
                    
                    # Execute with slippage and transaction costs[cite: 1]
                    manager.execute_trade(name, qty * sig, current_price, ts, reason)
        
        # Issue 18: Record daily portfolio state[cite: 1]
        manager.record_daily_state(ts, current_prices)

    # 5. PERFORMANCE EVALUATION & BENCHMARKING (Issue 12, 13)[cite: 1]
    print("Step 5: Calculating Risk-Adjusted Returns...")
    
    # FIXED: Extracting numeric values from list of dictionaries to avoid TypeError
    equity_df = pd.DataFrame(manager.equity_curve)
    
    if not equity_df.empty:
        equity_df.set_index('timestamp', inplace=True)
        # Calculate returns on the numeric 'total_value' column[cite: 1]
        portfolio_rets = equity_df['total_value'].pct_change().dropna()
        
        # Use first asset as a market benchmark for Alpha/Beta demo
        market_proxy_rets = list(universe.values())[0]['log_ret'].reindex(portfolio_rets.index).fillna(0)
        alpha, beta = risk.calculate_alpha_beta(portfolio_rets, market_proxy_rets)
        
        # 6. EXPORT RESULTS (Issue 18 / image_92a71f.png)[cite: 1]
        final_results = {
            'equity_curve': equity_df,
            'trade_logs': manager.trade_history,
            'risk_metrics': {
                'sharpe_ratio': risk.calculate_sharpe_ratio(portfolio_rets),
                'alpha': alpha,
                'beta': beta
            },
            'var_95': risk.calculate_var(portfolio_rets),
            'max_drawdown': risk.calculate_max_drawdown(equity_df['total_value'])
        }

        with open('results.pkl', 'wb') as f:
            pickle.dump(final_results, f)
        
        print("Success: Results saved to results.pkl. Dashboard ready[cite: 1].")
    else:
        print("Error: Simulation produced no equity data.")

if __name__ == "__main__":
    main()