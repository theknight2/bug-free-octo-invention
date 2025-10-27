# 🐋 Hyperliquid Whale Tracker

A real-time transaction scraper for monitoring spot trades on Hyperliquid. Track whale movements and get instant alerts when monitored addresses execute buy or sell orders.

**✨ Live Demo:** [Deploy on Streamlit Cloud](#deployment) 

## 🚀 Features

### Core Functionality
- 📊 **Real-time Monitoring**: Async scraper checks for new transactions every minute
- 🎯 **Multi-Address Support**: Monitor 20+ addresses simultaneously with individual watchers
- 🎭 **Character Names**: Assign epic names (Marvel, DC, GOT, etc.) to tracked addresses
- 📥 **Bulk Upload**: Add multiple addresses via paste or file upload (.txt, .csv)
- 💾 **SQLite Persistence**: Transaction history survives app restarts
- 🔗 **Clickable Hashes**: Direct links to Hyperliquid explorer

### UI & Design
- 🎨 **Sleek Dark Theme**: Emerald green (`#00D9A3`) on dark background (`#0D1117`)
- 🎨 **Color-Coded Addresses**: Each whale gets a unique color (5 colors cycle)
- ⚡ **Transaction Highlighting**: Visual emphasis for $1K+ and $5K+ trades
- 🔍 **Smart Filtering**: Filter by whale, minimum value, or view all
- 📊 **Real-time Metrics**: Live watchers, transaction count, total volume, and status
- 🎭 **Random Name Generator**: 200+ character names from popular franchises

### Export & Analytics
- 📥 **Download Logs**: Export transactions as CSV or JSON
- 🎯 **Address-Specific Exports**: Download logs for individual whales
- 📈 **Detailed Data**: Includes timestamp, coin, quantity, price, value, fee, hash

## 📦 Installation

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd hyperliquid
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the app**
```bash
streamlit run app_v2.py
```

The app will open at `http://localhost:8501`

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free!)

1. **Push your code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app_v2.py`
   - Click "Deploy"!

3. **Done!** Your app will be live at `https://<your-app-name>.streamlit.app`

## 🎯 Usage

### 1. Add Addresses

**Single Address:**
- Go to "Single" tab in sidebar
- Paste address
- (Optional) Add custom name or use 🎲 for random suggestion
- Click "➕ Add Address"

**Bulk Upload:**
- Go to "Bulk" tab
- Paste multiple addresses (one per line or comma-separated)
- Or upload a `.txt` or `.csv` file
- Click "➕ Add All Addresses"

**Example bulk input:**
```
0x37cbd9Eb9c9Ef1Ec23fdc27686E44cF557e8A4F8
0x51396D7fae25D68bDA9f0d004c44DCd696ee5D19
0x727956...
```

### 2. Start Monitoring
- Set check interval (default: 60 seconds)
- Click "▶ Start"
- Watch transactions appear in real-time!

### 3. Filter & Export
- **Filter by Whale**: Click any whale badge to see only their transactions
- **Min Value Filter**: Drag slider to filter by transaction size
- **Download Logs**: Select whale and export as CSV or JSON

## 🏗️ Architecture

### Components

- **`scraper_v2.py`**: Async scraper with individual address watchers
  - `AddressWatcher`: Per-address state management
  - `AsyncHyperliquidScraper`: Orchestrates all watchers
  - SQLite persistence for seen transactions

- **`app_v2.py`**: Streamlit UI
  - Real-time dashboard with metrics
  - Transaction table with highlighting
  - Address management (add/delete/bulk upload)
  - Export functionality (CSV/JSON)

- **`requirements.txt`**: Dependencies
  - streamlit, aiohttp, pandas, etc.

### Data Flow

1. **Fetch**: Async HTTP requests to Hyperliquid API (`/info` endpoint)
2. **Process**: Individual transaction parsing (no aggregation)
3. **Store**: SQLite database tracks seen transaction IDs
4. **Display**: Real-time UI updates via Streamlit

### API Endpoint

```python
POST https://api.hyperliquid.xyz/info
{
  "type": "userFills",
  "user": "0x..."
}
```

## 🎨 Design Philosophy

### Colors
- **Emerald Green** (`#00D9A3`): Primary accent (buttons, highlights)
- **Dark Background** (`#0D1117`): Main background
- **Card Background** (`#161B22`): Component backgrounds
- **Borders** (`#30363D`): Subtle dividers

### Typography
- **Font**: Roboto (clean, modern, readable)
- **Hierarchy**: Clear heading structure and metric cards

### Interactions
- **Hover Effects**: Cards shift right, transactions glow
- **Pulsing Status**: Live monitoring indicator animates
- **Smooth Transitions**: All state changes fade smoothly

## 📊 Example Output

**Terminal Logs:**
```
2025-10-27 14:23:45 - [0x37cbd9...] BUY 45,458.00 HYPE @ $1.23 ($55,913.34) | Hash: 0xabc123...
2025-10-27 14:24:12 - [0x51396D...] SELL 1,234.56 PURP @ $0.45 ($555.55) | Hash: 0xdef456...
```

**CSV Export:**
```csv
Timestamp,Address,Name,Action,Coin,Quantity,Price,Value_USD,Fee,TX_Hash
2025-10-27 14:23:45,0x37cbd9...,Iron Man,BUY,HYPE,45458.00,1.23,55913.34,0.05,0xabc123...
2025-10-27 14:24:12,0x51396D...,Thor,SELL,PURP,1234.56,0.45,555.55,0.02,0xdef456...
```

## 🧪 Testing

Test with known active addresses:
```python
addresses = [
    '0x31ca8395cf837de08b24da3f660e77761dfb974b',  # High-frequency trader
    '0x727956fFc763c3911d66aFFE8a92BDB23d1a1525',  # Large volume whale
    '0x0ae767f56eAF7c9ad0e871A0e53Fb979e593c8db',  # Consistent $50 buys
    '0x7839e2a52bdd31E5AD3D7E5e75C5da5ee1Ad1Bfc'   # BTC/ETH/XRP trader
]
```

## ⚙️ Configuration

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Check Interval | 60s | 10-300s | How often to fetch new transactions |
| Min Value Filter | $0 | $0-$10,000 | Hide transactions below threshold |
| Transaction Limit | 200 | - | Max transactions kept in memory |
| Display Limit | 50 | - | Max transactions shown in UI |

## 🔧 Advanced Features

### SQLite Database
Transaction IDs are stored in `hyperliquid.db` to prevent duplicates across sessions:
```sql
CREATE TABLE seen_transactions (
    address TEXT,
    transaction_id TEXT,
    timestamp DATETIME,
    PRIMARY KEY (address, transaction_id)
)
```

### Character Name Library
200+ names from:
- Marvel (Iron Man, Thor, Spider-Man...)
- DC (Batman, Superman, Joker...)
- Game of Thrones (Jon Snow, Daenerys...)
- Star Wars (Darth Vader, Yoda...)
- And more!

### Transaction Highlighting
- **Green glow + badge**: $1,000 - $5,000
- **Strong gradient + pulsing badge**: $5,000+

## 📝 Rate Limits

Hyperliquid's public API supports:
- ✅ 20+ addresses
- ✅ 60-second intervals
- ✅ No authentication required
- ✅ Generous rate limits

## 🐛 Troubleshooting

**Issue**: Database locked
```bash
rm hyperliquid.db  # Delete and restart (loses history)
```

**Issue**: App not updating
- Check browser console for errors
- Refresh the page (F5)
- Ensure monitoring is started (▶ button)

**Issue**: Transactions not appearing
- Verify address is correct (case-insensitive)
- Check if address has recent activity on Hyperliquid
- Wait 60 seconds for first check

## 🤝 Contributing

Feel free to:
- Add more character names
- Improve UI/UX
- Add new export formats
- Enhance filtering options

## 📄 License

MIT License - feel free to use and modify!

## 🔗 Links

- [Hyperliquid](https://app.hyperliquid.xyz)
- [Hyperliquid API Docs](https://hyperliquid.gitbook.io/hyperliquid-docs)
- [Streamlit Cloud](https://share.streamlit.io)

---

**Made with 💚 for the Hyperliquid community**
