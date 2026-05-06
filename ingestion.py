import pandas as pd
import numpy as np
import os
import logging
from concurrent.futures import ThreadPoolExecutor

# Setup logging for data anomalies and pipeline status
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/data_pipeline.log'
)

class UniversalIngestionPipeline:
    def __init__(self, data_dir, configs):
        """
        Initializes the pipeline with a directory and asset-specific mappings.
        """
        self.data_dir = data_dir
        self.configs = configs
        self.assets_data = {}

    def validate_types(self, df, asset_name):
        """
        Issue 16: Ensures data conforms to expected numeric types.
        Isolates problematic records to prevent pipeline failure.
        """
        try:
            numeric_cols = ['price', 'volume', 'volatility']
            for col in [c for c in numeric_cols if c in df.columns]:
                df[col] = pd.to_numeric(df[col], errors='raise')
            return df
        except Exception as e:
            logging.error(f"Issue 16 - Malformed data types in {asset_name}: {e}")
            return None

    def handle_anomalies(self, df):
        """
        Issue 2: Imputes missing data without forward-looking bias[cite: 1].
        Smoothes price outliers using a rolling Z-score[cite: 1].
        """
        # Forward fill ensures we only use past info to fill gaps[cite: 1]
        df = df.ffill()

        if 'price' in df.columns:
            window = 20
            rolling_mean = df['price'].rolling(window=window).mean()
            rolling_std = df['price'].rolling(window=window).std()
            z_scores = (df['price'] - rolling_mean) / rolling_std
            
            # Smooth outliers exceeding 3 standard deviations[cite: 1]
            outliers = np.abs(z_scores) > 3
            df.loc[outliers, 'price'] = rolling_mean[outliers]
            
        return df

    def process_file(self, file_path):
        """
        Standardizes and cleans an individual file based on its config[cite: 1].
        """
        fname = os.path.basename(file_path).split('.')[0]
        config = self.configs.get(fname)
        
        if not config:
            logging.warning(f"No config found for {fname}. Skipping file[cite: 1].")
            return None

        try:
            df = pd.read_csv(file_path)
            
            # Standardize columns using config mappings[cite: 1]
            df = df.rename(columns=config['mappings'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)

            # Issue 16: Validation and anomaly handling[cite: 1]
            df = self.validate_types(df, fname)
            if df is not None:
                df = self.handle_anomalies(df)
                logging.info(f"Successfully processed asset: {fname}[cite: 1]")
                return {fname: df}
            
            return None
        except Exception as e:
            logging.error(f"Critical error processing {fname}: {e}[cite: 1]")
            return None

    def run_pipeline(self):
        """
        Issue 1: Concurrent ingestion to prevent bottlenecks[cite: 1].
        """
        files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) 
                 if f.endswith('.csv')]
        
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.process_file, files))

        for res in results:
            if res:
                self.assets_data.update(res)
        
        print(f"Ingestion complete. {len(self.assets_data)} assets loaded[cite: 1].")
        return self.assets_data