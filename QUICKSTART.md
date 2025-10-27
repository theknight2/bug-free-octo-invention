# ⚡ Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Option 1: Deploy to Cloud (Easiest)

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-tracker.git
git push -u origin main
```

2. **Deploy**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repo, branch `main`, file `app_v2.py`
   - Click "Deploy"!

3. **Done!** Your app is live at `https://YOUR-APP.streamlit.app`

## 💻 Option 2: Run Locally

1. **Install**:
```bash
pip install -r requirements.txt
```

2. **Run**:
```bash
streamlit run app_v2.py
```

3. **Open**: `http://localhost:8501`

## 🎯 First Steps

1. **Add a Whale**:
   - Click "Single" tab
   - Paste: `0x7839e2a52bdd31E5AD3D7E5e75C5da5ee1Ad1Bfc`
   - Click 🎲 for a random name (e.g., "Iron Man")
   - Click "➕ Add Address"

2. **Start Monitoring**:
   - Click "▶ Start" button
   - Wait 60 seconds for first check

3. **Watch Transactions**:
   - See real-time trades appear!
   - Click hash links to verify on Hyperliquid
   - Filter by whale or minimum value

## 🎭 Add Multiple Whales (Bulk Upload)

1. Click "Bulk" tab
2. Paste these addresses:
```
0x7839e2a52bdd31E5AD3D7E5e75C5da5ee1Ad1Bfc
0x31ca8395cf837de08b24da3f660e77761dfb974b
0x727956fFc763c3911d66aFFE8a92BDB23d1a1525
0x0ae767f56eAF7c9ad0e871A0e53Fb979e593c8db
```
3. Click "➕ Add All Addresses"
4. Each gets an auto-assigned character name!

## 📥 Download Data

1. Scroll to sidebar → "📥 Download Logs"
2. Select a whale (or "All Addresses")
3. Click "CSV" or "JSON"
4. Analyze in Excel, Python, etc.!

## 🎨 Customize

- **Change interval**: Use slider in sidebar (10-300 seconds)
- **Filter transactions**: Use "Min Value" slider
- **Focus on one whale**: Click their name badge
- **Delete whale**: Click 🗑 next to their name

## 📊 Example Addresses to Track

High activity addresses (for testing):

| Address | Activity | Typical Volume |
|---------|----------|---------------|
| `0x7839e2...1Bfc` | BTC/ETH/XRP whale | $10K-$30K/trade |
| `0x31ca83...974b` | High-frequency trader | 100+ trades/hour |
| `0x727956...1525` | HYPE whale | $1K-$5K/trade |
| `0x0ae767...c8db` | Consistent $50 buys | Many coins |

## ⚠️ Tips

- **First check takes 60s**: Be patient after clicking Start
- **Transaction limit**: App keeps last 200 transactions
- **Browser refresh**: If stuck, just refresh (F5)
- **Database reset**: Delete `hyperliquid.db` to reset history

## 🎯 Pro Tips

1. **Name your whales**: Use recognizable names for easy tracking
2. **Set min value**: Filter noise by hiding small trades
3. **Download regularly**: Export data for offline analysis
4. **Use filters**: Focus on specific whales during key market events

## 🐛 Common Issues

**Q: No transactions showing up?**
- Wait 60 seconds for first check
- Verify address has recent activity on Hyperliquid
- Check monitoring is started (green "Live" status)

**Q: App is slow?**
- Try fewer addresses (< 20)
- Increase check interval (120s)
- Use min value filter

**Q: Duplicate transactions?**
- This shouldn't happen (SQLite deduplication)
- If it does: delete `hyperliquid.db` and restart

## 🚀 Next Steps

- Read full [README.md](README.md) for all features
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for cloud hosting
- Customize colors in `.streamlit/config.toml`
- Add your own character names to the list!

---

**Happy Whale Watching! 🐋💚**

