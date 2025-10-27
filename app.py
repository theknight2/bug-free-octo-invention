import streamlit as st
import time
from datetime import datetime
from scraper import HyperliquidScraper

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
    .stTextInput input {{
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
    .sidebar-text {{
        color: {HYPERLIQUID_TEXT};
        font-size: 0.9rem;
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
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = HyperliquidScraper()
if 'addresses' not in st.session_state:
    st.session_state.addresses = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False

# Header
st.markdown('<h1 class="header-text">Hyperliquid Whale Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8A8F98; font-size: 1rem; margin-top: -10px;">Track spot transactions from whale addresses in real-time</p>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.markdown("### Configuration")
    
    # Address input
    st.markdown("#### Monitored Addresses")
    address_input = st.text_area(
        "Enter addresses (one per line)",
        value="\n".join(st.session_state.addresses) if st.session_state.addresses else "",
        height=150,
        placeholder="0x37cbd9Eb9c9Ef1Ec23fdc27686E44cF557e8A4F8\n0x51396D7fae25D68bDA9f0d004c44DCd696ee5D19"
    )
    
    if st.button("Update Addresses"):
        addresses = [addr.strip() for addr in address_input.split('\n') if addr.strip()]
        st.session_state.addresses = addresses
        st.success(f"Monitoring {len(addresses)} addresses")
    
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
        help="If an address trades this many or more different coins, show summary instead of individual transactions"
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
            st.rerun()
    
    if st.button("Clear Logs"):
        st.session_state.transactions = []
        st.rerun()

# Main content area
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Addresses</div>
            <div class="metric-value">{len(st.session_state.addresses)}</div>
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

# Monitoring loop
if st.session_state.monitoring and st.session_state.addresses:
    # Check for new transactions
    new_logs = st.session_state.scraper.check_addresses(st.session_state.addresses)
    
    # Add new transactions to the list
    if new_logs:
        st.session_state.transactions.extend(new_logs)
        # Keep only last 50 transactions
        st.session_state.transactions = st.session_state.transactions[-50:]
    
    # Display transactions
    with transaction_container:
        if st.session_state.transactions:
            # Sort by timestamp descending (most recent first)
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
    
    # Auto-refresh
    time.sleep(interval)
    st.rerun()

elif st.session_state.monitoring and not st.session_state.addresses:
    st.warning("⚠️ Please add addresses to monitor in the sidebar")

else:
    with transaction_container:
        if st.session_state.transactions:
            # Display existing transactions when stopped
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

