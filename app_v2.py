import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
from scraper_v2 import AsyncHyperliquidScraper
import threading
import queue
import logging
import random
import json

# Page configuration
st.set_page_config(
    page_title="Hyperliquid Whale Tracker",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hyperliquid colors
EMERALD = "#00D9A3"
DARK_BG = "#0D1117"
CARD_BG = "#161B22"
BORDER = "#30363D"
TEXT = "#E6EDF3"
TEXT_MUTED = "#8B949E"

# Minimalist CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap');
    
    * {{ font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif; }}
    
    .stApp {{ background: {DARK_BG}; }}
    
    h1, h2, h3 {{ color: {TEXT}; font-weight: 600; }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {CARD_BG};
        border-right: 1px solid {BORDER};
    }}
    
    /* Inputs */
    .stTextArea textarea, .stNumberInput input {{
        background: {DARK_BG} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT} !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }}
    
    /* Buttons */
    .stButton>button {{
        background: {EMERALD};
        color: {DARK_BG};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s;
    }}
    
    .stButton>button:hover {{
        background: #00C090;
        box-shadow: 0 0 20px rgba(0, 217, 163, 0.4);
    }}
    
    .stButton>button:disabled {{
        background: #30363D;
        color: #6E7681;
    }}
    
    /* Transaction table styling */
    .tx-table {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .tx-row {{
        display: grid;
        grid-template-columns: 100px 120px 70px 110px 100px 110px 120px 90px;
        gap: 0.8rem;
        padding: 10px 16px;
        border-bottom: 1px solid {BORDER};
        align-items: center;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }}
    
    .tx-row:hover {{
        background: rgba(0, 217, 163, 0.04);
    }}
    
    .tx-row-large {{
        background: rgba(0, 217, 163, 0.06);
        border-left-color: {EMERALD};
    }}
    
    .tx-row-large:hover {{
        background: rgba(0, 217, 163, 0.1);
        transform: translateX(2px);
    }}
    
    .tx-row-mega {{
        background: linear-gradient(90deg, rgba(0, 217, 163, 0.12), rgba(0, 217, 163, 0.04));
        border-left: 4px solid {EMERALD};
        box-shadow: 0 0 15px rgba(0, 217, 163, 0.15);
    }}
    
    .tx-row-mega:hover {{
        background: linear-gradient(90deg, rgba(0, 217, 163, 0.18), rgba(0, 217, 163, 0.06));
        transform: translateX(3px);
    }}
    
    .tx-header {{
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
    }}
    
    .tx-cell {{
        color: {TEXT};
        font-size: 14px;
    }}
    
    .tx-buy {{
        color: {EMERALD};
        font-weight: 600;
    }}
    
    .tx-sell {{
        color: #FF5252;
        font-weight: 600;
    }}
    
    .tx-limit {{
        color: #FFA500;
        font-weight: 700;
        position: relative;
        padding-left: 20px;
    }}
    
    .tx-limit:before {{
        content: "🎯";
        position: absolute;
        left: 0;
        font-size: 12px;
    }}
    
    .tx-hash {{
        color: {EMERALD};
        text-decoration: none;
        font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
    }}
    
    .tx-hash:hover {{
        text-decoration: underline;
    }}
    
    .address-badge {{
        background: {DARK_BG};
        border: 1px solid {EMERALD};
        color: {EMERALD};
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        display: inline-block;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .address-badge:hover {{
        background: rgba(0, 217, 163, 0.1);
        transform: scale(1.05);
    }}
    
    .address-badge.active {{
        background: {EMERALD};
        color: {DARK_BG};
    }}
    
    .address-color-0 {{ border-color: #00D9A3; }}
    .address-color-1 {{ border-color: #FF6B6B; }}
    .address-color-2 {{ border-color: #4ECDC4; }}
    .address-color-3 {{ border-color: #FFE66D; }}
    .address-color-4 {{ border-color: #A8DADC; }}
    
    .filter-bar {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px 16px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }}
    
    .filter-label {{
        color: {TEXT_MUTED};
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .value-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
    }}
    
    .value-large {{
        background: rgba(0, 217, 163, 0.15);
        color: {EMERALD};
    }}
    
    .value-mega {{
        background: rgba(0, 217, 163, 0.25);
        color: {EMERALD};
        box-shadow: 0 0 10px rgba(0, 217, 163, 0.3);
    }}
    
    .metric-box {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 24px;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {EMERALD};
        line-height: 1;
    }}
    
    .metric-label {{
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
        margin-top: 8px;
    }}
    
    .status-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    
    .status-active {{
        background: {EMERALD};
        animation: pulse 2s infinite;
    }}
    
    .status-inactive {{
        background: #6E7681;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    hr {{
        border: none;
        border-top: 1px solid {BORDER};
        margin: 2rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# Character names from various franchises (200+ names)
CHARACTER_NAMES = [
    # Marvel
    "Iron Man", "Spider-Man", "Thor", "Hulk", "Black Widow", "Captain America", "Hawkeye", "Black Panther",
    "Doctor Strange", "Scarlet Witch", "Vision", "Loki", "Thanos", "Deadpool", "Wolverine", "Storm",
    "Cyclops", "Jean Grey", "Professor X", "Magneto", "Mystique", "Rogue", "Gambit", "Silver Surfer",
    "Ant-Man", "Wasp", "Groot", "Rocket", "Star-Lord", "Gamora", "Drax", "Mantis", "Nick Fury",
    # DC
    "Batman", "Superman", "Wonder Woman", "Flash", "Aquaman", "Green Lantern", "Cyborg", "Joker",
    "Harley Quinn", "Catwoman", "Lex Luthor", "Robin", "Nightwing", "Red Hood", "Batgirl", "Oracle",
    "Green Arrow", "Black Canary", "Shazam", "Martian Manhunter", "Hawkgirl", "Zatanna", "Constantine",
    "Darkseid", "Deathstroke", "Bane", "Riddler", "Penguin", "Two-Face", "Poison Ivy", "Mr Freeze",
    # Game of Thrones
    "Jon Snow", "Daenerys", "Tyrion", "Arya Stark", "Sansa Stark", "Bran Stark", "Cersei", "Jaime",
    "Ned Stark", "Robb Stark", "Theon", "Ramsay", "Joffrey", "Tywin", "The Hound", "The Mountain",
    "Brienne", "Tormund", "Varys", "Littlefinger", "Melisandre", "Davos", "Samwell", "Gilly",
    "Missandei", "Grey Worm", "Jorah", "Drogo", "Viserys", "Oberyn", "Ellaria", "Night King",
    # Lord of the Rings
    "Gandalf", "Frodo", "Aragorn", "Legolas", "Gimli", "Boromir", "Samwise", "Pippin", "Merry",
    "Gollum", "Saruman", "Sauron", "Galadriel", "Elrond", "Arwen", "Eowyn", "Theoden", "Faramir",
    # Harry Potter
    "Harry Potter", "Hermione", "Ron Weasley", "Dumbledore", "Snape", "Voldemort", "Sirius Black",
    "Draco Malfoy", "Luna", "Neville", "Hagrid", "McGonagall", "Dobby", "Bellatrix", "Lupin",
    # Star Wars
    "Luke Skywalker", "Darth Vader", "Yoda", "Obi-Wan", "Princess Leia", "Han Solo", "Chewbacca",
    "R2-D2", "C-3PO", "Kylo Ren", "Rey", "Finn", "Poe", "Mace Windu", "Qui-Gon", "Padme", "Anakin",
    "Ahsoka", "Boba Fett", "Darth Maul", "Emperor", "Lando", "Grogu", "Mandalorian",
    # Breaking Bad / Better Call Saul
    "Walter White", "Jesse Pinkman", "Saul Goodman", "Gus Fring", "Mike Ehrmantraut", "Hank Schrader",
    "Skyler", "Tuco", "Nacho", "Lalo", "Kim Wexler",
    # The Matrix
    "Neo", "Morpheus", "Trinity", "Agent Smith", "Oracle", "Cypher",
    # Anime
    "Goku", "Vegeta", "Naruto", "Sasuke", "Luffy", "Zoro", "Gon", "Killua", "Light Yagami", "L",
    "Eren Yeager", "Mikasa", "Levi", "Saitama", "Edward Elric", "Spike Spiegel", "Ichigo",
    # Mortal Kombat
    "Scorpion", "Sub-Zero", "Raiden", "Liu Kang", "Sonya", "Johnny Cage", "Kitana", "Mileena",
    # Street Fighter
    "Ryu", "Ken", "Chun-Li", "Guile", "M. Bison", "Akuma", "Cammy", "Dhalsim",
    # Misc Popular
    "Jack Sparrow", "Indiana Jones", "James Bond", "John Wick", "The Punisher", "Sherlock Holmes",
    "Rick Sanchez", "Morty", "Homer Simpson", "Bart Simpson", "Peter Griffin", "Stewie",
    "Eleven", "Hopper", "Mike Wheeler", "Dustin", "Steve Harrington", "Max Mayfield",
    "Geralt", "Ciri", "Yennefer", "Joel", "Ellie", "Arthur Morgan", "John Marston",
    "Kratos", "Atreus", "Master Chief", "Cortana", "Link", "Zelda", "Mario", "Luigi",
    "Sonic", "Pikachu", "Ash Ketchum", "Mewtwo", "Charizard"
]

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
if 'selected_address' not in st.session_state:
    st.session_state.selected_address = "All"
if 'min_value_filter' not in st.session_state:
    st.session_state.min_value_filter = 0
if 'address_names' not in st.session_state:
    st.session_state.address_names = {}  # {address: name}
if 'used_names' not in st.session_state:
    st.session_state.used_names = set()
if 'suggested_name' not in st.session_state:
    st.session_state.suggested_name = None

# Async worker
def async_worker(scraper, interval, transaction_queue):
    """Worker thread for async scraper."""
    async def worker_loop():
        while scraper.is_running:
            try:
                transactions = await scraper.check_all_addresses()
                transaction_queue.put(transactions)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Worker error: {e}")
    asyncio.run(worker_loop())

# Helper functions
def get_random_unused_name():
    """Get a random character name that hasn't been used yet."""
    available_names = [name for name in CHARACTER_NAMES if name not in st.session_state.used_names]
    if available_names:
        return random.choice(available_names)
    return "Whale " + str(len(st.session_state.used_names) + 1)

def get_display_name(address):
    """Get display name for an address."""
    return st.session_state.address_names.get(address, f"{address[:6]}...{address[-4:]}")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # Address input with tabs
    st.markdown("#### Add Address")
    
    tab1, tab2 = st.tabs(["Single", "Bulk"])
    
    with tab1:
        # Single address input
        address_input = st.text_area(
            "Wallet Address",
            placeholder="0x123abc...",
            help="Enter the address to track",
            label_visibility="collapsed",
            key="new_address_input",
            height=68,
            max_chars=100
        )
        
        # Name and dice button
        col1, col2 = st.columns([4, 1])
        with col1:
            # Name input with suggestion
            if st.session_state.suggested_name:
                name_placeholder = st.session_state.suggested_name
            else:
                name_placeholder = "e.g., Iron Man, Batman..."
            
            address_name = st.text_input(
                "Name (Optional)",
                placeholder=name_placeholder,
                help="Give this address a memorable name",
                label_visibility="collapsed",
                key="address_name_input"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎲", help="Get random name suggestion", use_container_width=True):
                st.session_state.suggested_name = get_random_unused_name()
                st.rerun()
        
        if st.button("➕ Add Address", use_container_width=True):
            if address_input.strip():
                addr = address_input.strip().replace('\n', '').replace(' ', '')
                
                # Use suggested name if no custom name provided
                if not address_name.strip() and st.session_state.suggested_name:
                    chosen_name = st.session_state.suggested_name
                else:
                    chosen_name = address_name.strip() or f"Whale-{len(st.session_state.addresses) + 1}"
                
                # Check if address already exists
                if addr not in st.session_state.addresses:
                    st.session_state.addresses.append(addr)
                    st.session_state.address_names[addr] = chosen_name
                    st.session_state.used_names.add(chosen_name)
                    st.session_state.scraper.add_address(addr)
                    st.session_state.suggested_name = None  # Clear suggestion
                    st.success(f"✓ Added {chosen_name}")
                    st.rerun()
                else:
                    st.warning("Address already being tracked!")
            else:
                st.error("Please enter an address")
    
    with tab2:
        # Bulk address input
        st.markdown("**Paste multiple addresses (one per line or comma-separated)**")
        bulk_input = st.text_area(
            "Bulk Addresses",
            placeholder="0x123abc...\n0x456def...\nor\n0x123abc..., 0x456def...",
            help="Enter multiple addresses separated by newlines or commas",
            label_visibility="collapsed",
            key="bulk_address_input",
            height=150
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Or upload a file (.txt, .csv)",
            type=["txt", "csv"],
            help="Upload a file with one address per line",
            key="address_file_upload"
        )
        
        if st.button("➕ Add All Addresses", use_container_width=True, key="bulk_add_btn"):
            addresses_to_add = []
            
            # Parse from text area
            if bulk_input.strip():
                # Try comma-separated first
                if ',' in bulk_input:
                    raw_addresses = bulk_input.split(',')
                else:
                    # Try newline-separated
                    raw_addresses = bulk_input.split('\n')
                
                addresses_to_add.extend([addr.strip() for addr in raw_addresses if addr.strip()])
            
            # Parse from uploaded file
            if uploaded_file is not None:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    # Try comma-separated first
                    if ',' in content:
                        raw_addresses = content.split(',')
                    else:
                        # Try newline-separated
                        raw_addresses = content.split('\n')
                    
                    addresses_to_add.extend([addr.strip() for addr in raw_addresses if addr.strip()])
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            
            # Add all addresses
            if addresses_to_add:
                added_count = 0
                skipped_count = 0
                
                for addr in addresses_to_add:
                    # Clean address
                    addr = addr.strip().replace(' ', '')
                    if not addr or addr in st.session_state.addresses:
                        skipped_count += 1
                        continue
                    
                    # Auto-generate name
                    chosen_name = get_random_unused_name()
                    
                    # Add address
                    st.session_state.addresses.append(addr)
                    st.session_state.address_names[addr] = chosen_name
                    st.session_state.used_names.add(chosen_name)
                    st.session_state.scraper.add_address(addr)
                    added_count += 1
                
                if added_count > 0:
                    st.success(f"✓ Added {added_count} address(es)")
                if skipped_count > 0:
                    st.info(f"ℹ️ Skipped {skipped_count} (duplicates or invalid)")
                
                st.rerun()
            else:
                st.error("Please paste addresses or upload a file")
    
    st.markdown("---")
    
    # Settings
    interval = st.number_input("Check Interval (s)", 10, 300, 60, 10)
    
    st.markdown("---")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start", disabled=st.session_state.monitoring, use_container_width=True):
            st.session_state.monitoring = True
            st.rerun()
    with col2:
        if st.button("⏸ Stop", disabled=not st.session_state.monitoring, use_container_width=True):
            st.session_state.monitoring = False
            if st.session_state.worker_thread:
                st.session_state.scraper.stop()
            st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear Txs", use_container_width=True, help="Clear all transactions"):
            st.session_state.transactions = []
            st.rerun()
    with col2:
        if st.button("🔄 Reset All", use_container_width=True, help="Reset everything", type="secondary"):
            st.session_state.addresses = []
            st.session_state.transactions = []
            st.session_state.address_names = {}
            st.session_state.used_names = set()
            st.session_state.scraper = AsyncHyperliquidScraper()
            st.session_state.monitoring = False
            st.success("✓ Reset complete!")
            st.rerun()
    
    st.markdown("---")
    
    # Active watchers with delete buttons
    st.markdown("#### Active Watchers")
    if st.session_state.scraper.watchers:
        for i, addr in enumerate(list(st.session_state.scraper.watchers.keys())):
            col1, col2 = st.columns([4, 1])
            with col1:
                color_class = f"address-color-{i % 5}"
                display_name = get_display_name(addr)
                # Show name with tooltip showing address
                st.markdown(
                    f'<span class="address-badge {color_class}" title="{addr}">{display_name}</span>', 
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("🗑", key=f"del_{addr}", help=f"Delete {display_name}", use_container_width=True):
                    # Remove from all tracking
                    if addr in st.session_state.addresses:
                        st.session_state.addresses.remove(addr)
                    if addr in st.session_state.address_names:
                        name = st.session_state.address_names[addr]
                        st.session_state.used_names.discard(name)
                        del st.session_state.address_names[addr]
                    st.session_state.scraper.remove_address(addr)
                    st.success(f"✓ Removed {display_name}")
                    st.rerun()
    else:
        st.info("No watchers", icon="ℹ️")
    
    st.markdown("---")
    
    # Filters
    st.markdown("#### Filters")
    
    min_val = st.slider("Min Value (USD)", 0, 10000, 0, 100)
    if min_val != st.session_state.min_value_filter:
        st.session_state.min_value_filter = min_val
    
    st.markdown(f"**Current:** ${min_val:,}+")
    
    st.markdown("---")
    
    # Download logs
    st.markdown("#### 📥 Download Logs")
    
    if st.session_state.transactions:
        # Select address to download
        download_options = ["All Addresses"] + [
            f"{get_display_name(addr)} ({addr[:6]}...{addr[-4:]})" 
            for addr in st.session_state.addresses
        ]
        
        selected_download = st.selectbox(
            "Select Address",
            options=download_options,
            label_visibility="collapsed",
            key="download_address_select"
        )
        
        # Get transactions for selected address
        if selected_download == "All Addresses":
            download_txs = st.session_state.transactions
            filename_prefix = "all_addresses"
        else:
            # Extract address from selection
            selected_idx = download_options.index(selected_download) - 1
            selected_addr = st.session_state.addresses[selected_idx]
            download_txs = [tx for tx in st.session_state.transactions if tx['address'] == selected_addr]
            filename_prefix = get_display_name(selected_addr).replace(' ', '_')
        
        st.caption(f"{len(download_txs)} transactions available")
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if download_txs:
                # Prepare CSV
                df_data = []
                for tx in download_txs:
                    df_data.append({
                        'Timestamp': tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'Address': tx['address'],
                        'Name': get_display_name(tx['address']),
                        'Action': tx['action'],
                        'Type': tx.get('order_type', 'FILLED'),
                        'Coin': tx['coin'],
                        'Quantity': tx['quantity'],
                        'Price': tx['price'],
                        'Value_USD': tx['value_usd'],
                        'Fee': tx.get('fee', 0),
                        'TX_Hash': tx['tx_hash']
                    })
                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="CSV",
                    data=csv,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if download_txs:
                # Prepare JSON
                json_data = []
                for tx in download_txs:
                    json_data.append({
                        'timestamp': tx['timestamp'].isoformat(),
                        'address': tx['address'],
                        'name': get_display_name(tx['address']),
                        'action': tx['action'],
                        'order_type': tx.get('order_type', 'FILLED'),
                        'coin': tx['coin'],
                        'quantity': tx['quantity'],
                        'price': tx['price'],
                        'value_usd': tx['value_usd'],
                        'fee': tx.get('fee', 0),
                        'tx_hash': tx['tx_hash'],
                        'closed_pnl': tx.get('closed_pnl', 0)
                    })
                json_str = json.dumps(json_data, indent=2)
                
                st.download_button(
                    label="JSON",
                    data=json_str,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.info("No transactions to download", icon="ℹ️")

# Main content
st.markdown(f'<h1 style="color: {EMERALD};">Hyperliquid Whale Tracker</h1>', unsafe_allow_html=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(st.session_state.scraper.watchers)}</div>
            <div class="metric-label">Watchers</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(st.session_state.transactions)}</div>
            <div class="metric-label">Transactions</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    status_dot = "status-active" if st.session_state.monitoring else "status-inactive"
    status_text = "Live" if st.session_state.monitoring else "Stopped"
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="font-size: 1.5rem; display: flex; align-items: center; justify-content: center;">
                <span class="status-dot {status_dot}"></span>{status_text}
            </div>
            <div class="metric-label">Status</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    total_volume = sum(tx.get('value_usd', 0) for tx in st.session_state.transactions)
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="font-size: 1.8rem;">${total_volume:,.0f}</div>
            <div class="metric-label">Total Volume</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Monitoring loop
if st.session_state.monitoring and st.session_state.addresses:
    # Start worker if needed
    if st.session_state.worker_thread is None or not st.session_state.worker_thread.is_alive():
        st.session_state.scraper.is_running = True
        st.session_state.worker_thread = threading.Thread(
            target=async_worker,
            args=(st.session_state.scraper, interval, st.session_state.transaction_queue),
            daemon=True
        )
        st.session_state.worker_thread.start()
    
    # Check queue
    try:
        while not st.session_state.transaction_queue.empty():
            new_logs = st.session_state.transaction_queue.get_nowait()
            if new_logs:
                st.session_state.transactions.extend(new_logs)
                st.session_state.transactions = st.session_state.transactions[-200:]  # Keep last 200
    except queue.Empty:
        pass

# Display transactions
if st.session_state.transactions:
    st.markdown("### Transactions")
    
    # Filter bar
    if len(st.session_state.addresses) > 1:
        st.markdown(f"""
            <div class="filter-bar">
                <span class="filter-label">Filter by Whale:</span>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(st.session_state.addresses) + 1, 6))
        with cols[0]:
            if st.button("All", key="filter_all", use_container_width=True):
                st.session_state.selected_address = "All"
                st.rerun()
        
        for i, addr in enumerate(st.session_state.addresses[:5]):  # Show first 5
            with cols[i + 1]:
                display_name = get_display_name(addr)
                if st.button(display_name, key=f"filter_{addr}", use_container_width=True):
                    st.session_state.selected_address = addr
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Filter transactions
    sorted_txs = sorted(st.session_state.transactions, key=lambda x: x['timestamp'], reverse=True)
    
    # Apply filters
    filtered_txs = []
    for tx in sorted_txs:
        # Address filter
        if st.session_state.selected_address != "All" and tx['address'] != st.session_state.selected_address:
            continue
        # Value filter
        if tx['value_usd'] < st.session_state.min_value_filter:
            continue
        filtered_txs.append(tx)
    
    # Show stats
    if len(filtered_txs) < len(sorted_txs):
        st.caption(f"Showing {len(filtered_txs)} of {len(sorted_txs)} transactions (filtered)")
    
    # Create table header
    st.markdown(f"""
        <div class="tx-table">
            <div class="tx-row">
                <div class="tx-header">Time</div>
                <div class="tx-header">Whale</div>
                <div class="tx-header">Side</div>
                <div class="tx-header">Amount</div>
                <div class="tx-header">Coin</div>
                <div class="tx-header">Price</div>
                <div class="tx-header">Value</div>
                <div class="tx-header">Hash</div>
            </div>
    """, unsafe_allow_html=True)
    
    # Display filtered transactions
    for tx in filtered_txs[:50]:  # Show last 50
        time_str = tx['timestamp'].strftime("%H:%M:%S")
        
        # Use named address
        display_name = get_display_name(tx['address'])
        
        # Handle limit orders vs filled orders
        is_limit_order = tx.get('order_type') == 'LIMIT_OPEN'
        if is_limit_order:
            # Limit orders show as yellow/orange
            action_class = "tx-limit"
        else:
            action_class = "tx-buy" if "BUY" in tx['action'] else "tx-sell"
        
        hash_short = tx['tx_hash'][:8] if tx['tx_hash'] else "N/A"
        hyperliquid_url = f"https://app.hyperliquid.xyz/explorer/tx/{tx['tx_hash']}"
        
        # Determine row class based on value
        value_usd = tx['value_usd']
        row_class = "tx-row"
        value_class = ""
        if value_usd >= 5000:
            row_class = "tx-row tx-row-mega"
            value_class = "value-mega"
        elif value_usd >= 1000:
            row_class = "tx-row tx-row-large"
            value_class = "value-large"
        
        # Format value with badge for large transactions
        if value_class:
            value_display = f'<span class="value-badge {value_class}">${value_usd:,.0f}</span>'
        else:
            value_display = f'${value_usd:,.2f}'
        
        # Color code address
        addr_index = st.session_state.addresses.index(tx['address']) if tx['address'] in st.session_state.addresses else 0
        addr_color_class = f"address-color-{addr_index % 5}"
        
        st.markdown(f"""
            <div class="{row_class}">
                <div class="tx-cell" style="font-size: 13px;">{time_str}</div>
                <div class="tx-cell {addr_color_class}" style="font-family: 'Roboto', sans-serif; font-size: 12px; font-weight: 600;" title="{tx['address']}">{display_name}</div>
                <div class="tx-cell {action_class}" style="font-size: 13px;">{tx['action']}</div>
                <div class="tx-cell" style="font-size: 13px;">{tx['quantity']:,.2f}</div>
                <div class="tx-cell" style="font-weight: 600; font-size: 13px;">{tx['coin']}</div>
                <div class="tx-cell" style="font-size: 12px;">${tx['price']:,.4f}</div>
                <div class="tx-cell">{value_display}</div>
                <div class="tx-cell"><a href="{hyperliquid_url}" target="_blank" class="tx-hash">{hash_short}</a></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("👆 Add addresses and click Start to begin monitoring", icon="ℹ️")

# Auto-refresh when monitoring
if st.session_state.monitoring:
    import time
    time.sleep(2)
    st.rerun()

