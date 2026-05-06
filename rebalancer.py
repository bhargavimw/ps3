class PortfolioRebalancer:
    """
    Issue 11: Periodic Portfolio Rebalancing.
    Restores desired asset allocations to maintain target risk profiles.
    """
    def __init__(self, target_allocations):
        self.target_allocations = target_allocations # e.g., {'Gold': 0.4, 'Oil': 0.6}

    def check_and_rebalance(self, portfolio_manager, current_prices, drift_threshold=0.05):
        total_value = portfolio_manager.get_portfolio_value(current_prices)
        rebalance_orders = []

        for asset, target_pct in self.target_allocations.items():
            current_val = portfolio_manager.positions.get(asset, 0) * current_prices[asset]
            current_pct = current_val / total_value
            
            # If the allocation drifts by more than 5%, trigger a trade
            if abs(current_pct - target_pct) > drift_threshold:
                target_val = total_value * target_pct
                diff_val = target_val - current_val
                qty_to_trade = diff_val / current_prices[asset]
                rebalance_orders.append((asset, qty_to_trade))
        
        return rebalance_orders