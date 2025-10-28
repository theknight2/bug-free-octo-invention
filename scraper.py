import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
import sqlite3
from asyncio import sleep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AddressWatcher:
    """Individual watcher for a single address - tracks BOTH fills and open orders."""
    
    def __init__(self, address: str, scraper: 'AsyncHyperliquidScraper'):
        self.address = address.strip().lower()
        if not self.address.startswith('0x') and len(self.address) == 40:
            self.address = '0x' + self.address
        self.scraper = scraper
        self.seen_transaction_ids: Set[str] = set()
        self.seen_open_order_ids: Set[str] = set()  # Track open orders separately
        self.previously_open_orders: Set[str] = set()  # Track what was open before
        
    async def _make_request_with_retry(
        self, 
        session: aiohttp.ClientSession, 
        payload: Dict,
        max_retries: int = 3
    ) -> Optional[List[Dict]]:
        """Make POST request with exponential backoff retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with session.post(
                    self.scraper.base_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 422:
                        # Unprocessable entity - don't retry
                        return []
                    
                    response.raise_for_status()
                    return await response.json()
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"[{self.address[:10]}...] Request failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    await sleep(wait_time)
                else:
                    logger.error(
                        f"[{self.address[:10]}...] All {max_retries} attempts failed. Last error: {e}"
                    )
            except Exception as e:
                # Unexpected error - don't retry
                logger.error(f"[{self.address[:10]}...] Unexpected error: {e}")
                return []
        
        return []
    
    async def fetch_fills(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch filled orders for this address with retry logic."""
        if not self.address.startswith('0x'):
            logger.error(f"Invalid address format: {self.address}")
            return []
        
        payload = {
            "type": "userFills",
            "user": self.address
        }
        
        result = await self._make_request_with_retry(session, payload)
        return result if result is not None else []
    
    async def fetch_open_orders(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch open orders for this address with retry logic."""
        if not self.address.startswith('0x'):
            logger.error(f"Invalid address format: {self.address}")
            return []
        
        payload = {
            "type": "openOrders",
            "user": self.address
        }
        
        result = await self._make_request_with_retry(session, payload)
        return result if result is not None else []
    
    def process_fills(self, fills: List[Dict]) -> List[Dict]:
        """Process fills - return INDIVIDUAL transactions, no aggregation."""
        transactions = []
        
        if not isinstance(fills, list):
            logger.error(f"Expected list, got {type(fills)}")
            return []
        
        for fill in fills:
            try:
                # Extract hash and transaction ID
                raw_hash = fill.get('hash', '')
                tx_id = str(fill.get('tid', fill.get('oid', '')))
                
                # Validate hash - filter out empty/zero hashes
                # Zero hash is 66 chars: 0x + 64 zeros
                zero_hash = '0x' + '0' * 64
                if raw_hash and raw_hash != '0x' and raw_hash != zero_hash and len(str(raw_hash)) == 66:
                    tx_hash = str(raw_hash)
                else:
                    tx_hash = None
                
                fill_id = f"{self.address}_{tx_id}"
                
                # Skip if seen
                if fill_id in self.seen_transaction_ids:
                    continue
                
                self.seen_transaction_ids.add(fill_id)
                
                # Extract details
                coin = fill.get('coin', 'UNKNOWN')
                side = fill.get('side', '').upper()
                size = float(fill.get('sz', 0))
                price = float(fill.get('px', 0))
                timestamp_ms = int(fill.get('time', 0))
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000) if timestamp_ms else datetime.now()
                fee = float(fill.get('fee', 0))
                
                # Determine action
                action = "BUY" if side == 'B' else "SELL"
                
                # Create transaction record
                tx = {
                    "timestamp": timestamp,
                    "address": self.address,
                    "action": action,
                    "coin": coin,
                    "quantity": size,
                    "price": price,
                    "value_usd": size * price,
                    "fee": fee,
                    "tx_hash": tx_hash,  # Always use actual hash for explorer links
                    "closed_pnl": float(fill.get('closedPnl', 0)),
                    "order_type": "FILLED"
                }
                
                transactions.append(tx)
                
                # Log individual transaction
                if tx_hash:
                    hash_display = tx_hash[:10]
                    logger.info(
                        f"[{self.address[:8]}...{self.address[-6:]}] "
                        f"{action} {size:,.2f} {coin} @ ${price:,.4f} "
                        f"(${size * price:,.2f}) | Hash: {hash_display}..."
                    )
                else:
                    logger.info(
                        f"[{self.address[:8]}...{self.address[-6:]}] "
                        f"{action} {size:,.2f} {coin} @ ${price:,.4f} "
                        f"(${size * price:,.2f}) | TID: {tx_id}"
                    )
            except Exception as e:
                logger.error(f"Error processing fill: {e} | Fill: {fill}")
                continue
        
        return transactions
    
    def process_open_orders(self, orders: List[Dict]) -> List[Dict]:
        """Process open orders - alert on NEW limit orders."""
        new_orders = []
        
        if not isinstance(orders, list):
            logger.error(f"Expected list, got {type(orders)}")
            return []
        
        current_open_order_ids = set()
        
        for order in orders:
            try:
                order_id = str(order.get('oid', ''))
                if not order_id:
                    continue
                
                current_open_order_ids.add(order_id)
                
                # Only alert on NEW orders (not previously seen)
                if order_id not in self.seen_open_order_ids:
                    self.seen_open_order_ids.add(order_id)
                    
                    # Extract order details
                    coin = order.get('coin', 'UNKNOWN')
                    side = order.get('side', '').upper()
                    size = float(order.get('sz', 0))
                    limit_px = float(order.get('limitPx', 0))
                    timestamp_ms = int(order.get('timestamp', 0))
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000) if timestamp_ms else datetime.now()
                    
                    action = "BUY" if side == 'B' else "SELL"
                    value_usd = size * limit_px
                    
                    # Create order record (no tx_hash for open orders, they haven't executed yet)
                    order_record = {
                        "timestamp": timestamp,
                        "address": self.address,
                        "action": f"{action} LIMIT",  # Mark as limit order
                        "coin": coin,
                        "quantity": size,
                        "price": limit_px,
                        "value_usd": value_usd,
                        "fee": 0,  # No fee for open orders yet
                        "tx_hash": None,  # No hash yet - order hasn't executed
                        "closed_pnl": 0,
                        "order_type": "LIMIT_OPEN"
                    }
                    
                    new_orders.append(order_record)
                    
                    # Log new limit order
                    logger.info(
                        f"[{self.address[:8]}...{self.address[-6:]}] "
                        f"🎯 NEW LIMIT ORDER: {action} {size:,.2f} {coin} @ ${limit_px:,.4f} "
                        f"(${value_usd:,.2f}) | OID: {order_id[:10]}..."
                    )
            except Exception as e:
                logger.error(f"Error processing open order: {e} | Order: {order}")
                continue
        
        # Detect cancelled/filled orders (were open, now closed)
        closed_orders = self.previously_open_orders - current_open_order_ids
        if closed_orders:
            for oid in closed_orders:
                logger.info(
                    f"[{self.address[:8]}...{self.address[-6:]}] "
                    f"📝 Limit order closed/filled: {oid[:10]}..."
                )
        
        # Update previously open orders
        self.previously_open_orders = current_open_order_ids
        
        return new_orders
    
    async def check(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Check for both new fills AND open orders."""
        # Fetch both concurrently
        fills_task = self.fetch_fills(session)
        orders_task = self.fetch_open_orders(session)
        
        fills, orders = await asyncio.gather(fills_task, orders_task)
        
        # Process both
        filled_txs = self.process_fills(fills)
        open_order_alerts = self.process_open_orders(orders)
        
        # Combine results
        return filled_txs + open_order_alerts


class AsyncHyperliquidScraper:
    """Async scraper with individual watchers - ALL transactions visible."""
    
    def __init__(self, db_path: str = "hyperliquid.db"):
        self.base_url = "https://api.hyperliquid.xyz/info"
        self.watchers: Dict[str, AddressWatcher] = {}
        self.db_path = db_path
        self.is_running = False
        self._logged_addresses = set()  # Track logged addresses to avoid duplicates
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    address TEXT,
                    action TEXT,
                    coin TEXT,
                    quantity REAL,
                    price REAL,
                    value_usd REAL,
                    fee REAL,
                    tx_hash TEXT,
                    closed_pnl REAL,
                    order_type TEXT DEFAULT 'FILLED',
                    UNIQUE(address, tx_hash, timestamp)
                )
            """)
            conn.commit()
    
    def add_address(self, address: str):
        """Add an address to monitor."""
        address = address.strip().lower()
        if not address.startswith('0x') and len(address) == 40:
            address = '0x' + address
        
        if address not in self.watchers:
            watcher = AddressWatcher(address, self)
            self.watchers[address] = watcher
            # Only log if not already logged
            if not hasattr(self, '_logged_addresses'):
                self._logged_addresses = set()
            if address not in self._logged_addresses:
                logger.info(f"✓ Watcher added: {address[:8]}...{address[-6:]}")
                self._logged_addresses.add(address)
    
    def remove_address(self, address: str):
        """Remove an address from monitoring."""
        address = address.strip().lower()
        if address in self.watchers:
            del self.watchers[address]
            logger.info(f"✗ Watcher removed: {address[:8]}...{address[-6:]}")
    
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
            transactions = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Watcher error: {result}")
                elif isinstance(result, list):
                    transactions.extend(result)
            
            # Save to database
            self._save_transactions(transactions)
            
            return transactions
    
    def _save_transactions(self, transactions: List[Dict]):
        """Save transactions to database."""
        if not transactions:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            for tx in transactions:
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO transactions 
                        (timestamp, address, action, coin, quantity, price, value_usd, fee, tx_hash, closed_pnl, order_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tx["timestamp"].isoformat(),
                        tx["address"],
                        tx["action"],
                        tx["coin"],
                        tx["quantity"],
                        tx["price"],
                        tx["value_usd"],
                        tx["fee"],
                        tx["tx_hash"],
                        tx["closed_pnl"],
                        tx.get("order_type", "FILLED")
                    ))
                except Exception as e:
                    logger.error(f"DB error: {e}")
            conn.commit()
    
    async def run(self, interval: int = 60):
        """Run the scraper continuously."""
        self.is_running = True
        logger.info(f"🚀 Async scraper started: {len(self.watchers)} watchers")
        logger.info(f"⏱️  Check interval: {interval}s")
        
        while self.is_running:
            try:
                start_time = datetime.now()
                await self.check_all_addresses()
                elapsed = (datetime.now() - start_time).total_seconds()
                
                logger.debug(f"✓ Check completed in {elapsed:.2f}s")
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("⏹️  Scraper stopped")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(interval)
    
    def stop(self):
        """Stop the scraper."""
        self.is_running = False

