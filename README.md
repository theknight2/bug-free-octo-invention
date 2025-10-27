# Hyperliquid Whale Tracker

Real-time monitoring of whale transactions on Hyperliquid DEX. Track large trades, limit orders, and position changes across multiple addresses.

## Features

- **Live Transaction Monitoring** - Tracks both filled orders and open limit orders
- **Multi-Address Support** - Monitor 20+ addresses simultaneously
- **Custom Names** - Assign memorable names to tracked addresses
- **Smart Alerts** - Highlights transactions over $1,000
- **Bulk Import** - Upload multiple addresses via text or CSV
- **Export Data** - Download transaction history as CSV or JSON
- **Retry Logic** - Exponential backoff ensures no missed transactions

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 and start tracking whales.

## Usage

1. Add wallet addresses (one at a time or bulk upload)
2. Assign custom names (optional)
3. Click "Start Monitoring"
4. Watch real-time transactions appear

## Configuration

The scraper checks for new transactions every 60 seconds by default. Adjust the interval in the sidebar.

## Requirements

- Python 3.8+
- Internet connection for Hyperliquid API access

## License

MIT
