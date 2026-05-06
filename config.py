ASSET_CONFIGS = {
    'equity_dataset': {
        'mappings': {'Date': 'timestamp', 'Price': 'price', 'Volume': 'volume'},
        'features': ['Returns', 'SMA_10']
    },
    'oil_dataset': {
        'mappings': {'Date': 'timestamp', 'Price': 'price', 'Volume': 'volume', 'Volatility': 'volatility'},
        'features': ['Returns']
    },
    'macro_dataset': {
        'mappings': {'Date': 'timestamp', 'USD_Index': 'price'}, # Mapping index as 'price' for consistency
        'features': ['Inflation', 'Interest_Rate', 'Sentiment']
    },
    'multi_asset_dataset': {
        'mappings': {'Date': 'timestamp'},
        'split_assets': {
            'Oil_Asset': {'price': 'Oil', 'returns': 'Oil_Returns'},
            'Gold_Asset': {'price': 'Gold', 'returns': 'Gold_Returns'}
        }
    }
}