# 🚀 Deployment Guide

## Deploy to Streamlit Cloud (Recommended)

Streamlit Cloud is **free** and perfect for this app!

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
```bash
cd /Users/Purdue/hyperliquid
git init
```

2. **Add all files**:
```bash
git add .
```

3. **Commit**:
```bash
git commit -m "Initial commit - Hyperliquid Whale Tracker"
```

4. **Create GitHub repository**:
   - Go to [github.com/new](https://github.com/new)
   - Name: `hyperliquid-whale-tracker` (or your choice)
   - Keep it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (we already have one)
   - Click "Create repository"

5. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/hyperliquid-whale-tracker.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**:
   - Click "New app" button
   - Select your repository: `YOUR_USERNAME/hyperliquid-whale-tracker`
   - Branch: `main`
   - Main file path: `app_v2.py`
   - (Optional) App URL: Choose a custom subdomain

3. **Deploy**:
   - Click "Deploy!"
   - Wait 2-3 minutes for initial deployment
   - Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

### Step 3: Share Your App 🎉

Your app is now live! Share the URL with anyone:
```
https://YOUR-APP-NAME.streamlit.app
```

## Environment Variables (Optional)

If you need to add any secrets or API keys in the future:

1. Go to your app settings on Streamlit Cloud
2. Click "Secrets" in the left sidebar
3. Add secrets in TOML format:
```toml
# Example
[api]
key = "your-api-key-here"
```

## Updating Your Deployed App

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Your app will automatically update in 1-2 minutes!

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure all dependencies are in `requirements.txt`

### Issue: "App crashed" or won't start
**Solution**: 
1. Check logs in Streamlit Cloud dashboard
2. Verify `app_v2.py` exists and has no syntax errors
3. Ensure all imports are available

### Issue: Database not persisting
**Note**: Streamlit Cloud uses ephemeral storage. The SQLite database will reset on app restarts. This is fine for most use cases as:
- Seen transactions are tracked in memory during the session
- Most important data is the real-time monitoring, not historical storage

### Issue: App is slow
**Solution**:
- Reduce check interval (but not below 10s)
- Monitor fewer addresses
- Note: Free Streamlit Cloud has resource limits

## Alternative Deployment Options

### Local Network (Raspberry Pi, Home Server)

```bash
# Run on startup
cd /path/to/hyperliquid
streamlit run app_v2.py --server.port 8501 --server.address 0.0.0.0
```

Access from any device on your network: `http://YOUR_LOCAL_IP:8501`

### Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t hyperliquid-tracker .
docker run -p 8501:8501 hyperliquid-tracker
```

### Heroku (Paid/Limited Free Tier)

1. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

2. Create `Procfile`:
```
web: sh setup.sh && streamlit run app_v2.py
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

## Performance Tips

### For Streamlit Cloud:
- Keep transaction limit at 200 or below
- Use 60-second intervals (default)
- Monitor max 20 addresses

### For Local/Docker:
- Can handle more addresses (50+)
- Faster intervals possible (30s)
- Larger transaction history (500+)

## Security Considerations

✅ **No sensitive data**: This app only reads public blockchain data
✅ **No authentication needed**: Hyperliquid API is public
✅ **No wallet connection**: Read-only monitoring
✅ **No API keys required**: All endpoints are public

## Monitoring Your App

Streamlit Cloud provides:
- **Logs**: View real-time logs from your app
- **Metrics**: See visitor count and resource usage
- **Analytics**: Track app performance

## Need Help?

- Check [Streamlit Community](https://discuss.streamlit.io/)
- Review [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- File an issue on your GitHub repo

---

**Happy Tracking! 🐋💚**

