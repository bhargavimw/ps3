import datetime
import logging
class PortfolioManager:
    """
    Tracks portfolio state and maintains explainable trade logs[cite: 1].
    """
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.positions = {} # {asset: qty}
        self.trade_history = [] # Detailed audit trail[cite: 1]

    def record_execution(self, asset, qty, price, signal_reason, status="Executed"):
        """
        Issue 14: Logs execution details, including indicators and trade rationale[cite: 1].
        """
        log_entry = {
            'timestamp': datetime.datetime.now(),
            'asset': asset,
            'quantity': qty,
            'execution_price': price,
            'signal_rationale': signal_reason,
            'portfolio_capital_after': self.capital,
            'status': status
        }
        
        # Enforce and log constraints[cite: 1]
        if status == "Rejected":
            log_entry['reason'] = "Position limit or capital constraint breach."
        
        self.trade_history.append(log_entry)

    def update_capital(self, amount):
        self.capital += amount
    def execute_trade(self, asset, quantity, price, timestamp):
        """
        Issue 15: Safeguard to intercept trades exceeding available capital.
        """
        notional_value = abs(quantity) * price
        
        # 1. Available Capital Check
        if notional_value > self.cash:
            error_msg = (f"REJECTED: Insufficient capital for {asset} at {timestamp}. "
                         f"Required: ${notional_value:.2f}, Available: ${self.cash:.2f}")
            logging.error(error_msg)
            print(error_msg) # Real-time visibility
            return False # Reject trade and allow simulation to continue

        # 2. Proceed with execution if capital is sufficient
        self.cash -= notional_value
        # ... (update positions and logs) ...
        return True