import requests
import logging
import time
from datetime import datetime
from typing import List, Dict, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class HyperliquidScraper:
    """Scraper for Hyperliquid spot transactions."""
    
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz/info"
        self.seen_transaction_ids: Set[str] = set()
        self.spam_threshold = 5  # Default: 5+ coins = spam
        
    def get_user_fills(self, address: str) -> List[Dict]:
        """Fetch user fills (executed orders) from Hyperliquid API."""
        try:
            # Ensure address is properly formatted
            address = address.strip().lower()  # Lowercase for case-insensitive matching
            
            # Auto-add 0x prefix if missing but address looks valid (40 hex chars)
            if not address.startswith('0x') and len(address) == 40:
                address = '0x' + address
                logger.info(f"Auto-added 0x prefix to address")
            
            if not address.startswith('0x'):
                logger.error(f"Invalid address format: {address}")
                return []
            
            payload = {
                "type": "userFills",
                "user": address
            }
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                logger.warning(f"No data available for address {address}")
            else:
                logger.error(f"HTTP error for {address}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching fills for {address}: {e}")
            return []
    
    def process_fills(self, address: str, fills: List[Dict]) -> Dict[str, Dict]:
        """
        Process fills and aggregate by coin to prevent spam.
        Returns dict with coin as key and aggregated data.
        """
        aggregated = defaultdict(lambda: {"buy": 0.0, "sell": 0.0})
        new_fills = []
        
        for fill in fills:
            # Create unique ID for this fill
            fill_id = f"{address}_{fill.get('tid', '')}_{fill.get('time', '')}"
            
            # Skip if we've seen this transaction before
            if fill_id in self.seen_transaction_ids:
                continue
            
            self.seen_transaction_ids.add(fill_id)
            new_fills.append(fill)
            
            # Extract transaction details
            coin = fill.get('coin', 'UNKNOWN')
            side = fill.get('side', '').lower()
            size = float(fill.get('sz', 0))
            
            # Aggregate by coin and side
            if side == 'b':  # Buy
                aggregated[coin]["buy"] += size
            elif side == 'a':  # Sell (ask)
                aggregated[coin]["sell"] += size
        
        return dict(aggregated)
    
    def format_quantity(self, quantity: float) -> str:
        """Format quantity with thousand separators."""
        # Format with 2 decimal places and add thousand separators
        return f"{quantity:,.2f}"
    
    def log_transaction(self, address: str, coin: str, side: str, quantity: float):
        """Log a transaction in the required format."""
        formatted_qty = self.format_quantity(quantity)
        action = "bought" if side == "buy" else "sold"
        logger.info(f"{address} {action} {formatted_qty} {coin}")
    
    def check_addresses(self, addresses: List[str]) -> List[Dict]:
        """
        Check all addresses for new transactions and return logs.
        Returns list of transaction logs for display.
        
        Anti-spam: Only shows summary if address has 5+ different coins traded,
        otherwise shows individual coin transactions.
        """
        transaction_logs = []
        
        for address in addresses:
            fills = self.get_user_fills(address)
            aggregated = self.process_fills(address, fills)
            
            # Count total number of coin transactions
            num_coins = len(aggregated)
            
            # Anti-spam: If trading threshold+ different coins, show summary instead
            if num_coins >= self.spam_threshold:
                total_buy_coins = sum(1 for amounts in aggregated.values() if amounts["buy"] > 0)
                total_sell_coins = sum(1 for amounts in aggregated.values() if amounts["sell"] > 0)
                
                if total_buy_coins > 0:
                    logger.info(f"{address} bought {total_buy_coins} different coins (e.g., {', '.join(list(aggregated.keys())[:3])}...)")
                    transaction_logs.append({
                        "timestamp": datetime.now(),
                        "address": address,
                        "action": "bought",
                        "quantity": total_buy_coins,
                        "coin": f"coins ({', '.join(list(aggregated.keys())[:3])}...)"
                    })
                
                if total_sell_coins > 0:
                    logger.info(f"{address} sold {total_sell_coins} different coins (e.g., {', '.join([k for k, v in aggregated.items() if v['sell'] > 0][:3])}...)")
                    transaction_logs.append({
                        "timestamp": datetime.now(),
                        "address": address,
                        "action": "sold",
                        "quantity": total_sell_coins,
                        "coin": f"coins ({', '.join([k for k, v in aggregated.items() if v['sell'] > 0][:3])}...)"
                    })
            else:
                # Show individual transactions for addresses trading < 5 coins
                for coin, amounts in aggregated.items():
                    if amounts["buy"] > 0:
                        self.log_transaction(address, coin, "buy", amounts["buy"])
                        transaction_logs.append({
                            "timestamp": datetime.now(),
                            "address": address,
                            "action": "bought",
                            "quantity": amounts["buy"],
                            "coin": coin
                        })
                    
                    if amounts["sell"] > 0:
                        self.log_transaction(address, coin, "sell", amounts["sell"])
                        transaction_logs.append({
                            "timestamp": datetime.now(),
                            "address": address,
                            "action": "sold",
                            "quantity": amounts["sell"],
                            "coin": coin
                        })
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return transaction_logs
    
    def run(self, addresses: List[str], interval: int = 60):
        """
        Run the scraper continuously.
        
        Args:
            addresses: List of Ethereum addresses to monitor
            interval: Check interval in seconds (default: 60)
        """
        logger.info(f"Starting Hyperliquid scraper for {len(addresses)} addresses")
        logger.info(f"Check interval: {interval} seconds")
        
        while True:
            try:
                self.check_addresses(addresses)
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Scraper stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(interval)


if __name__ == "__main__":
    # Example usage
    addresses = [
        '0x37cbd9Eb9c9Ef1Ec23fdc27686E44cF557e8A4F8',
        '0x51396D7fae25D68bDA9f0d004c44DCd696ee5D19'
    ]
    
    scraper = HyperliquidScraper()
    scraper.run(addresses)

