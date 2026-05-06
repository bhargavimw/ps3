import os
from concurrent.futures import ProcessPoolExecutor
from ingestion import UniversalIngestionPipeline
from features import AdvancedFeatureEngineer
from config import ASSET_CONFIGS

# Define the wrapper at the top level for Issue 17 scalability[cite: 1]
def feature_engineer_wrapper(asset_tuple):
    name, df = asset_tuple
    # Initialize inside the wrapper for ProcessPool compatibility
    engineer = AdvancedFeatureEngineer(macro_df=None) 
    
    df = engineer.add_technical_indicators(df)
    df = engineer.add_risk_features(df)
    df = engineer.align_macro_data(df) # Optional macro integration
    
    return name, df.dropna()

def main():
    # 1. Ingestion[cite: 1]
    pipeline = UniversalIngestionPipeline('data/raw', ASSET_CONFIGS)
    raw_data = pipeline.run_pipeline()

    # 2. Parallel Feature Engineering (Issue 17)[cite: 1]
    # We pass the items of our dictionary as tuples to the executor[cite: 1]
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        print(f"Scaling feature engineering across {os.cpu_count()} cores[cite: 1].")
        results = list(executor.map(feature_engineer_wrapper, raw_data.items()))

    # 3. Reassemble the universe[cite: 1]
    engineered_universe = {name: df for name, df in results}
    
    # ... proceed to Signal Generation and Portfolio Management[cite: 1] ...

if __name__ == "__main__":
    main()