import streamlit as st
import asyncio
from datetime import datetime
from scraper_async import AsyncHyperliquidScraper
import threading
import queue

# Hyperliquid brand colors - grey and emerald
HYPERLIQUID_EMERALD = "#00D9A3"   # Darker emerald green
HYPERLIQUID_DARK = "#1A1D29"      # Dark grey background
HYPERLIQUID_CARD = "#23262F"      # Card grey
HYPERLIQUID_BORDER = "#2D3139"    # Border grey
HYPERLIQUID_TEXT = "#E8E8E8"      # Light grey text

# Page configuration
st.set_page_config(
    page_title="Hyperliquid Whale Tracker",
    page_icon="🐋",
    layout="wide"
)

# Custom CSS with sleek Hyperliquid styling
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .stApp {{
        background-color: {HYPERLIQUID_DARK};
    }}
    .main {{
        background-color: {HYPERLIQUID_DARK};
    }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
        color: {HYPERLIQUID_TEXT} !important;
    }}
    .stTextArea textarea {{
        background-color: {HYPERLIQUID_CARD} !important;
        border: 1px solid {HYPERLIQUID_BORDER} !important;
        color: {HYPERLIQUID_TEXT} !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 13px !important;
    }}
    .stNumberInput input {{
        background-color: {HYPERLIQUID_CARD} !important;
        border: 1px solid {HYPERLIQUID_BORDER} !important;
        color: {HYPERLIQUID_TEXT} !important;
        border-radius: 8px !important;
    }}
    .transaction-card {{
        background-color: {HYPERLIQUID_CARD};
        border: 1px solid {HYPERLIQUID_BORDER};
        border-left: 3px solid {HYPERLIQUID_EMERALD};
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 8px;
        transition: all 0.2s ease;
    }}
    .transaction-card:hover {{
        border-left-width: 4px;
        transform: translateX(2px);
    }}
    .transaction-buy {{
        border-left-color: {HYPERLIQUID_EMERALD};
    }}
    .transaction-sell {{
        border-left-color: #FF5252;
    }}
    .header-text {{
        color: {HYPERLIQUID_EMERALD} !important;
        font-weight: 600;
        font-size: 2.5rem;
        letter-spacing: -0.02em;
    }}
    .metric-card {{
        background-color: {HYPERLIQUID_CARD};
        border: 1px solid {HYPERLIQUID_BORDER};
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: {HYPERLIQUID_EMERALD};
    }}
    .metric-label {{
        color: #8A8F98;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }}
    .metric-value {{
        color: {HYPERLIQUID_EMERALD};
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    .stButton>button {{
        background-color: {HYPERLIQUID_EMERALD};
        color: {HYPERLIQUID_DARK};
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.2s ease;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }}
    .stButton>button:hover {{
        background-color: #00C090;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 217, 163, 0.3);
    }}
    .stButton>button:disabled {{
        background-color: #3A3D47;
        color: #666;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {HYPERLIQUID_CARD};
        border-right: 1px solid {HYPERLIQUID_BORDER};
    }}
    hr {{
        border-color: {HYPERLIQUID_BORDER} !important;
        margin: 24px 0 !important;
    }}
    .status-active {{
        color: {HYPERLIQUID_EMERALD};
        animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    .watcher-badge {{
        display: inline-block;
        background-color: {HYPERLIQUID_CARD};
        border: 1px solid {HYPERLIQUID_EMERALD};
        padding: 4px 12px;
        border-radius: 16px;
        margin: 4px;
        font-size: 0.85rem;
        color: {HYPERLIQUID_EMERALD};
    }}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = AsyncHyperliquidScraper()
if 'addresses' not in st.session_state:
    st.session_state.addresses = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'worker_thread' not in st.session_state:
    st.session_state.worker_thread = None
if 'transaction_queue' not in st.session_state:
    st.session_state.transaction_queue = queue.Queue()

# Header
st.markdown('<h1 class="header-text">Hyperliquid Whale Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8A8F98; font-size: 1rem; margin-top: -10px;">Real-time async monitoring with individual watchers per address</p>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.markdown("### Configuration")
    
    # Address input
    st.markdown("#### Monitored Addresses")
    address_input = st.text_area(
        "Enter addresses (one per line)",
        value="\n".join(st.session_state.addresses) if st.session_state.addresses else "",
        height=150,
        placeholder="0xc2a30212a8ddac9e123944d6e29faddce994e5f2\n0x5b5d51203a0f9079f8aeb098a6523a13f298c060"
    )
    
    if st.button("Update Addresses"):
        old_addresses = set(st.session_state.addresses)
        new_addresses = [addr.strip() for addr in address_input.split('\n') if addr.strip()]
        
        # Remove old watchers
        for addr in old_addresses - set(new_addresses):
            st.session_state.scraper.remove_address(addr)
        
        # Add new watchers
        for addr in set(new_addresses) - old_addresses:
            st.session_state.scraper.add_address(addr)
        
        st.session_state.addresses = new_addresses
        st.success(f"Monitoring {len(new_addresses)} addresses with individual watchers")
    
    st.markdown("---")
    
    # Check interval
    interval = st.number_input(
        "Check Interval (seconds)",
        min_value=10,
        max_value=300,
        value=60,
        step=10
    )
    
    # Spam threshold
    st.session_state.scraper.spam_threshold = st.number_input(
        "Spam Threshold (coins)",
        min_value=3,
        max_value=20,
        value=5,
        step=1,
        help="If an address trades this many or more different coins, show summary"
    )
    
    st.markdown("---")
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start", disabled=st.session_state.monitoring):
            st.session_state.monitoring = True
            st.rerun()
    with col2:
        if st.button("Stop", disabled=not st.session_state.monitoring):
            st.session_state.monitoring = False
            if st.session_state.worker_thread:
                st.session_state.scraper.stop()
            st.rerun()
    
    if st.button("Clear Logs"):
        st.session_state.transactions = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### Active Watchers")
    if st.session_state.scraper.watchers:
        for addr in st.session_state.scraper.watchers.keys():
            st.markdown(f'<div class="watcher-badge">{addr[:6]}...{addr[-4:]}</div>', unsafe_allow_html=True)
    else:
        st.info("No active watchers")

# Main content area
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Watchers</div>
            <div class="metric-value">{len(st.session_state.scraper.watchers)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Transactions</div>
            <div class="metric-value">{len(st.session_state.transactions)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    status_color = HYPERLIQUID_EMERALD if st.session_state.monitoring else "#666666"
    status_text = "Active" if st.session_state.monitoring else "Stopped"
    status_class = "status-active" if st.session_state.monitoring else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Status</div>
            <div class="metric-value {status_class}" style="color: {status_color};">{status_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Transaction log section
st.markdown("### Recent Transactions")

# Placeholder for live updates
transaction_container = st.container()

# Async worker function
def async_worker(scraper, interval, transaction_queue):
    """Worker thread that runs the async scraper."""
    async def worker_loop():
        while scraper.is_running:
            try:
                transactions = await scraper.check_all_addresses()
                transaction_queue.put(transactions)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Worker error: {e}")
    
    asyncio.run(worker_loop())

# Monitoring loop
if st.session_state.monitoring and st.session_state.addresses:
    # Start worker thread if not running
    if st.session_state.worker_thread is None or not st.session_state.worker_thread.is_alive():
        st.session_state.scraper.is_running = True
        st.session_state.worker_thread = threading.Thread(
            target=async_worker,
            args=(st.session_state.scraper, interval, st.session_state.transaction_queue),
            daemon=True
        )
        st.session_state.worker_thread.start()
    
    # Check for new transactions from queue
    try:
        while not st.session_state.transaction_queue.empty():
            new_logs = st.session_state.transaction_queue.get_nowait()
            if new_logs:
                st.session_state.transactions.extend(new_logs)
                # Keep only last 100 transactions
                st.session_state.transactions = st.session_state.transactions[-100:]
    except queue.Empty:
        pass
    
    # Display transactions
    with transaction_container:
        if st.session_state.transactions:
            sorted_transactions = sorted(
                st.session_state.transactions,
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            for tx in sorted_transactions:
                action_color = HYPERLIQUID_EMERALD if tx['action'] == "bought" else "#FF5252"
                border_class = "transaction-buy" if tx['action'] == "bought" else "transaction-sell"
                formatted_qty = f"{tx['quantity']:,.2f}"
                timestamp_str = tx['timestamp'].strftime("%H:%M:%S")
                order_count = tx.get('order_count', 1)
                
                st.markdown(
                    f"""
                    <div class="transaction-card {border_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <div style="color: #8A8F98; font-size: 0.8rem; margin-bottom: 6px; font-weight: 500;">
                                    {tx['address'][:8]}...{tx['address'][-6:]}
                                </div>
                                <div style="color: {action_color}; font-size: 1.4rem; font-weight: 600; letter-spacing: -0.01em;">
                                    {tx['action'].upper()} <span style="color: {HYPERLIQUID_TEXT};">{formatted_qty}</span> {tx['coin']}
                                </div>
                                <div style="color: #6B7280; font-size: 0.75rem; margin-top: 4px;">
                                    {order_count} orders
                                </div>
                            </div>
                            <div style="color: #6B7280; font-size: 0.85rem; font-weight: 500;">
                                {timestamp_str}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No transactions detected yet. Waiting for activity...")
    
    # Auto-refresh every 2 seconds
    import time
    time.sleep(2)
    st.rerun()

elif st.session_state.monitoring and not st.session_state.addresses:
    st.warning("⚠️ Please add addresses to monitor in the sidebar")

else:
    # Display existing transactions when stopped
    with transaction_container:
        if st.session_state.transactions:
            sorted_transactions = sorted(
                st.session_state.transactions,
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            for tx in sorted_transactions:
                action_color = HYPERLIQUID_EMERALD if tx['action'] == "bought" else "#FF5252"
                border_class = "transaction-buy" if tx['action'] == "bought" else "transaction-sell"
                formatted_qty = f"{tx['quantity']:,.2f}"
                timestamp_str = tx['timestamp'].strftime("%H:%M:%S")
                order_count = tx.get('order_count', 1)
                
                st.markdown(
                    f"""
                    <div class="transaction-card {border_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <div style="color: #8A8F98; font-size: 0.8rem; margin-bottom: 6px; font-weight: 500;">
                                    {tx['address'][:8]}...{tx['address'][-6:]}
                                </div>
                                <div style="color: {action_color}; font-size: 1.4rem; font-weight: 600; letter-spacing: -0.01em;">
                                    {tx['action'].upper()} <span style="color: {HYPERLIQUID_TEXT};">{formatted_qty}</span> {tx['coin']}
                                </div>
                                <div style="color: #6B7280; font-size: 0.75rem; margin-top: 4px;">
                                    {order_count} orders
                                </div>
                            </div>
                            <div style="color: #6B7280; font-size: 0.85rem; font-weight: 500;">
                                {timestamp_str}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("👆 Add addresses in the sidebar and click Start to begin monitoring")

