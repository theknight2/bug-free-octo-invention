import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
from collections import defaultdict
import sqlite3
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AddressWatcher:
    """Individual watcher for a single address."""
    
    def __init__(self, address: str, scraper: 'AsyncHyperliquidScraper'):
        self.address = address.strip().lower()
        self.scraper = scraper
        self.seen_transaction_ids: Set[str] = set()
        self.is_running = False
        
    async def fetch_fills(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch fills for this address."""
        try:
            # Auto-add 0x prefix if missing
            address = self.address
            if not address.startswith('0x') and len(address) == 40:
                address = '0x' + address
            
            if not address.startswith('0x'):
                logger.error(f"Invalid address format: {address}")
                return []
            
            payload = {
                "type": "userFills",
                "user": address
            }
            
            async with session.post(
                self.scraper.base_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 422:
                    logger.warning(f"[{self.address[:10]}...] No data available")
                    return []
                
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"[{self.address[:10]}...] Error fetching fills: {e}")
            return []
    
    def process_fills(self, fills: List[Dict]) -> Dict[str, Dict]:
        """Process fills and aggregate by coin."""
        aggregated = defaultdict(lambda: {"buy": 0.0, "sell": 0.0, "count_buy": 0, "count_sell": 0})
        
        for fill in fills:
            # Create unique ID
            fill_id = f"{self.address}_{fill.get('tid', '')}_{fill.get('time', '')}"
            
            # Skip if seen
            if fill_id in self.seen_transaction_ids:
                continue
            
            self.seen_transaction_ids.add(fill_id)
            
            # Extract details
            coin = fill.get('coin', 'UNKNOWN')
            side = fill.get('side', '').lower()
            size = float(fill.get('sz', 0))
            
            # Aggregate
            if side == 'b':  # Buy
                aggregated[coin]["buy"] += size
                aggregated[coin]["count_buy"] += 1
            elif side == 'a':  # Sell
                aggregated[coin]["sell"] += size
                aggregated[coin]["count_sell"] += 1
        
        return dict(aggregated)
    
    def should_show_summary(self, num_coins: int) -> bool:
        """Determine if we should show summary or individual transactions."""
        return num_coins >= self.scraper.spam_threshold
    
    def log_transactions(self, aggregated: Dict[str, Dict]) -> List[Dict]:
        """Log and return transaction data."""
        transaction_logs = []
        num_coins = len(aggregated)
        
        if num_coins == 0:
            return []
        
        # If trading many coins, show summary
        if self.should_show_summary(num_coins):
            bought_coins = [(coin, data) for coin, data in aggregated.items() if data["buy"] > 0]
            sold_coins = [(coin, data) for coin, data in aggregated.items() if data["sell"] > 0]
            
            if bought_coins:
                coins_list = ", ".join([coin for coin, _ in bought_coins[:5]])
                total_orders = sum(data["count_buy"] for _, data in bought_coins)
                logger.info(f"[{self.address[:8]}...{self.address[-6:]}] BOUGHT {len(bought_coins)} coins ({total_orders} orders): {coins_list}")
                
                transaction_logs.append({
                    "timestamp": datetime.now(),
                    "address": self.address,
                    "action": "bought",
                    "quantity": len(bought_coins),
                    "coin": f"different coins: {coins_list}",
                    "order_count": total_orders
                })
            
            if sold_coins:
                coins_list = ", ".join([coin for coin, _ in sold_coins[:5]])
                total_orders = sum(data["count_sell"] for _, data in sold_coins)
                logger.info(f"[{self.address[:8]}...{self.address[-6:]}] SOLD {len(sold_coins)} coins ({total_orders} orders): {coins_list}")
                
                transaction_logs.append({
                    "timestamp": datetime.now(),
                    "address": self.address,
                    "action": "sold",
                    "quantity": len(sold_coins),
                    "coin": f"different coins: {coins_list}",
                    "order_count": total_orders
                })
        else:
            # Show individual coin transactions
            for coin, amounts in aggregated.items():
                if amounts["buy"] > 0:
                    qty = f"{amounts['buy']:,.2f}"
                    orders = amounts["count_buy"]
                    logger.info(f"[{self.address[:8]}...{self.address[-6:]}] BOUGHT {qty} {coin} ({orders} orders)")
                    
                    transaction_logs.append({
                        "timestamp": datetime.now(),
                        "address": self.address,
                        "action": "bought",
                        "quantity": amounts["buy"],
                        "coin": coin,
                        "order_count": orders
                    })
                
                if amounts["sell"] > 0:
                    qty = f"{amounts['sell']:,.2f}"
                    orders = amounts["count_sell"]
                    logger.info(f"[{self.address[:8]}...{self.address[-6:]}] SOLD {qty} {coin} ({orders} orders)")
                    
                    transaction_logs.append({
                        "timestamp": datetime.now(),
                        "address": self.address,
                        "action": "sold",
                        "quantity": amounts["sell"],
                        "coin": coin,
                        "order_count": orders
                    })
        
        return transaction_logs
    
    async def check(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Check for new transactions."""
        fills = await self.fetch_fills(session)
        aggregated = self.process_fills(fills)
        return self.log_transactions(aggregated)


class AsyncHyperliquidScraper:
    """Async scraper with individual watchers per address."""
    
    def __init__(self, db_path: str = "hyperliquid.db"):
        self.base_url = "https://api.hyperliquid.xyz/info"
        self.watchers: Dict[str, AddressWatcher] = {}
        self.spam_threshold = 5
        self.db_path = db_path
        self.is_running = False
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seen_transactions (
                    address TEXT,
                    transaction_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (address, transaction_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    address TEXT,
                    action TEXT,
                    quantity REAL,
                    coin TEXT,
                    order_count INTEGER
                )
            """)
            conn.commit()
    
    def add_address(self, address: str):
        """Add an address to monitor."""
        address = address.strip().lower()
        if address not in self.watchers:
            watcher = AddressWatcher(address, self)
            self.watchers[address] = watcher
            logger.info(f"Added watcher for {address[:8]}...{address[-6:]}")
    
    def remove_address(self, address: str):
        """Remove an address from monitoring."""
        address = address.strip().lower()
        if address in self.watchers:
            del self.watchers[address]
            logger.info(f"Removed watcher for {address[:8]}...{address[-6:]}")
    
    async def check_all_addresses(self) -> List[Dict]:
        """Check all addresses concurrently."""
        if not self.watchers:
            return []
        
        async with aiohttp.ClientSession() as session:
            # Run all watchers concurrently
            tasks = [
                watcher.check(session)
                for watcher in self.watchers.values()
            ]
            
            # Gather all results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten and filter errors
            transaction_logs = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Watcher error: {result}")
                elif isinstance(result, list):
                    transaction_logs.extend(result)
            
            # Save to database
            self._save_transactions(transaction_logs)
            
            return transaction_logs
    
    def _save_transactions(self, transactions: List[Dict]):
        """Save transactions to database."""
        if not transactions:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            for tx in transactions:
                conn.execute("""
                    INSERT INTO transaction_logs 
                    (timestamp, address, action, quantity, coin, order_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tx["timestamp"].isoformat(),
                    tx["address"],
                    tx["action"],
                    tx["quantity"],
                    tx["coin"],
                    tx.get("order_count", 1)
                ))
            conn.commit()
    
    async def run(self, interval: int = 60):
        """Run the scraper continuously."""
        self.is_running = True
        logger.info(f"Starting async scraper for {len(self.watchers)} addresses")
        logger.info(f"Check interval: {interval} seconds")
        logger.info(f"Spam threshold: {self.spam_threshold} coins")
        
        while self.is_running:
            try:
                start_time = datetime.now()
                await self.check_all_addresses()
                elapsed = (datetime.now() - start_time).total_seconds()
                
                logger.debug(f"Check completed in {elapsed:.2f}s")
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Scraper stopped")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(interval)
    
    def stop(self):
        """Stop the scraper."""
        self.is_running = False


# Example usage
async def main():
    addresses = [
        '0xc2a30212a8ddac9e123944d6e29faddce994e5f2',
        '0x5b5d51203a0f9079f8aeb098a6523a13f298c060',
        '0x5d2f4460ac3514ada79f5d9838916e508ab39bb7',
    ]
    
    scraper = AsyncHyperliquidScraper()
    scraper.spam_threshold = 5
    
    for address in addresses:
        scraper.add_address(address)
    
    try:
        await scraper.run(interval=60)
    except KeyboardInterrupt:
        scraper.stop()
        logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())

