# Bloom Energy (BE) $220 Strike - BSM Theoretical Pricing App
# Launch Date: November 5, 2025
# Current Spot: $137.00

import streamlit as st
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from datetime import date, datetime

# Page configuration
st.set_page_config(
    page_title="BE $220 Strike - Theoretical Pricing",
    page_icon="📊",
    layout="wide"
)

# Dark theme colors
DARK_BG = "#0D1117"
CARD_BG = "#161B22"
BORDER = "#30363D"
TEXT = "#E6EDF3"
TEXT_MUTED = "#8B949E"
GREEN = "#00D9A3"
RED = "#FF5252"
YELLOW = "#FFD700"
BLUE = "#4A9EFF"

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

    .stApp {{ background: {DARK_BG}; }}

    h1, h2, h3 {{
        color: {TEXT};
        font-weight: 700;
        font-family: 'Roboto', sans-serif;
    }}

    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {GREEN};
        text-align: center;
        margin-bottom: 0.5rem;
    }}

    .subtitle {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }}

    .info-box {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }}

    .info-label {{
        color: {TEXT_MUTED};
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }}

    .info-value {{
        color: {TEXT};
        font-size: 1.3rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }}

    .strike-badge {{
        background: linear-gradient(135deg, {GREEN}, {BLUE});
        color: {DARK_BG};
        font-size: 2rem;
        font-weight: 700;
        padding: 12px 24px;
        border-radius: 8px;
        display: inline-block;
        font-family: 'Roboto Mono', monospace;
    }}

    .price-table {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }}

    .price-row {{
        display: grid;
        grid-template-columns: 140px 80px 110px 90px 90px 90px 90px 90px;
        gap: 0.8rem;
        padding: 12px 16px;
        border-bottom: 1px solid {BORDER};
        align-items: center;
    }}

    .price-row:hover {{
        background: rgba(0, 217, 163, 0.04);
    }}

    .price-header {{
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {TEXT_MUTED};
    }}

    .price-cell {{
        color: {TEXT};
        font-size: 14px;
        font-family: 'Roboto Mono', monospace;
    }}

    .call-badge {{
        color: {GREEN};
        font-weight: 700;
    }}

    .put-badge {{
        color: {RED};
        font-weight: 700;
    }}

    .reference-note {{
        background: rgba(255, 215, 0, 0.1);
        border-left: 4px solid {YELLOW};
        padding: 12px 16px;
        margin: 1rem 0;
        border-radius: 4px;
        color: {TEXT};
    }}

    .warning-box {{
        background: rgba(255, 165, 0, 0.1);
        border: 1px solid rgba(255, 165, 0, 0.3);
        border-radius: 8px;
        padding: 16px;
        margin: 1rem 0;
        color: {TEXT};
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# BSM Functions
def black_scholes_merton(S, K, T, r, q, sigma, option_type='call'):
    """
    Black-Scholes-Merton Option Pricing Model

    Parameters:
    -----------
    S : float - Spot price
    K : float - Strike price
    T : float - Time to expiration in years
    r : float - Risk-free rate
    q : float - Dividend yield
    sigma : float - Implied volatility (in decimal form, e.g., 1.30 for 130%)
    option_type : str - 'call' or 'put'

    Returns:
    --------
    dict with price, delta, gamma, vega, theta, d1, d2
    """
    if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
        return {
            'price': 0.0,
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'd1': 0.0,
            'd2': 0.0
        }

    # Calculate d1 and d2
    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    # Standard normal CDF and PDF
    N = norm.cdf
    n = norm.pdf

    if option_type == 'call':
        price = S*np.exp(-q*T)*N(d1) - K*np.exp(-r*T)*N(d2)
        delta = np.exp(-q*T) * N(d1)
        theta = ((-S*n(d1)*sigma*np.exp(-q*T))/(2*np.sqrt(T))
                 - r*K*np.exp(-r*T)*N(d2)
                 + q*S*np.exp(-q*T)*N(d1)) / 365
    else:  # put
        price = K*np.exp(-r*T)*N(-d2) - S*np.exp(-q*T)*N(-d1)
        delta = -np.exp(-q*T) * N(-d1)
        theta = ((-S*n(d1)*sigma*np.exp(-q*T))/(2*np.sqrt(T))
                 + r*K*np.exp(-r*T)*N(-d2)
                 - q*S*np.exp(-q*T)*N(-d1)) / 365

    # Greeks (same for call and put)
    gamma = np.exp(-q*T)*n(d1) / (S*sigma*np.sqrt(T))
    vega = S*np.exp(-q*T)*n(d1)*np.sqrt(T) / 100  # Per 1% IV change

    return {
        'price': float(price),
        'delta': float(delta),
        'gamma': float(gamma),
        'vega': float(vega),
        'theta': float(theta),
        'd1': float(d1),
        'd2': float(d2)
    }

# Constants
STRIKE = 220.0
RISK_FREE_RATE = 0.043  # 4.3%
DIVIDEND_YIELD = 0.00   # 0% (BE doesn't pay dividends)
CURRENT_DATE = date(2025, 11, 4)

# Expirations
EXPIRATIONS = {
    'January 2026': date(2026, 1, 16),
    'February 2026': date(2026, 2, 20),
    'March 2026': date(2026, 3, 20)
}

# Calculate DTE and T for each expiration
def get_dte_and_t(expiry_date):
    dte = (expiry_date - CURRENT_DATE).days
    T = dte / 365.25
    return dte, T

# Header
st.markdown('<div class="main-title">Bloom Energy (BE) - $220 Strike Theoretical Pricing</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Black-Scholes-Merton Model | Launch Date: November 5, 2025</div>', unsafe_allow_html=True)

# Warning box
st.markdown(f"""
<div class="warning-box">
    <strong>⚠️ NOTE:</strong> $220 strikes launch <strong>TOMORROW</strong> (November 5, 2025).
    These are purely theoretical calculations. Current highest strike is $215.
    Strike is <strong>60.6% OTM</strong> from current spot ($137.00).
</div>
""", unsafe_allow_html=True)

# Display strike prominently
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown(f'<div style="text-align: center;"><span class="strike-badge">${STRIKE:.0f}</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sliders
st.markdown("### Input Parameters")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown('<div class="info-label">Spot Price (S)</div>', unsafe_allow_html=True)
    spot_price = st.slider(
        "Spot Price",
        min_value=120.0,
        max_value=160.0,
        value=137.0,
        step=1.0,
        label_visibility="collapsed",
        key="spot_slider"
    )
    st.markdown(f'<div class="info-value">${spot_price:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown('<div class="info-label">Implied Volatility (σ)</div>', unsafe_allow_html=True)
    iv_percent = st.slider(
        "Implied Volatility",
        min_value=100,
        max_value=130,
        value=130,
        step=1,
        label_visibility="collapsed",
        key="iv_slider"
    )
    st.markdown(f'<div class="info-value">{iv_percent}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

iv_decimal = iv_percent / 100.0

# Reference line value
reference_value = spot_price * 0.125

st.markdown(f"""
<div class="reference-note">
    <strong>📌 12.5% Reference Level:</strong> ${reference_value:.2f} (shown as dotted yellow line in charts)
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Calculate prices for all expirations
st.markdown("### Theoretical Prices & Greeks")

# Create results table
results = []
for exp_name, exp_date in EXPIRATIONS.items():
    dte, T = get_dte_and_t(exp_date)

    # Calculate call and put prices
    call_result = black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, iv_decimal, 'call')
    put_result = black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, iv_decimal, 'put')

    results.append({
        'expiration': exp_name,
        'date': exp_date,
        'dte': dte,
        'call': call_result,
        'put': put_result
    })

# Display table
st.markdown(f"""
<div class="price-table">
    <div class="price-row">
        <div class="price-header">Expiration</div>
        <div class="price-header">Type</div>
        <div class="price-header">Theo Price</div>
        <div class="price-header">Delta (Δ)</div>
        <div class="price-header">Gamma (Γ)</div>
        <div class="price-header">Vega (ν)</div>
        <div class="price-header">Theta (Θ)</div>
        <div class="price-header">vs 12.5%</div>
    </div>
""", unsafe_allow_html=True)

for result in results:
    exp_display = f"{result['expiration'].split()[0][:3]} ({result['dte']} DTE)"

    # Call row
    call = result['call']
    call_vs_ref = ((call['price'] - reference_value) / reference_value) * 100
    call_vs_ref_str = f"{call_vs_ref:+.1f}%"

    st.markdown(f"""
    <div class="price-row">
        <div class="price-cell" style="font-weight: 600;">{exp_display}</div>
        <div class="price-cell call-badge">CALL</div>
        <div class="price-cell" style="font-weight: 700; font-size: 15px;">${call['price']:.2f}</div>
        <div class="price-cell">{call['delta']:.4f}</div>
        <div class="price-cell">{call['gamma']:.5f}</div>
        <div class="price-cell">${call['vega']:.2f}</div>
        <div class="price-cell">${call['theta']:.2f}</div>
        <div class="price-cell" style="color: {'#00D9A3' if call_vs_ref > 0 else '#FF5252'};">{call_vs_ref_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # Put row
    put = result['put']
    put_vs_ref = ((put['price'] - reference_value) / reference_value) * 100
    put_vs_ref_str = f"{put_vs_ref:+.1f}%"

    st.markdown(f"""
    <div class="price-row">
        <div class="price-cell"></div>
        <div class="price-cell put-badge">PUT</div>
        <div class="price-cell" style="font-weight: 700; font-size: 15px;">${put['price']:.2f}</div>
        <div class="price-cell">{put['delta']:.4f}</div>
        <div class="price-cell">{put['gamma']:.5f}</div>
        <div class="price-cell">${put['vega']:.2f}</div>
        <div class="price-cell">${put['theta']:.2f}</div>
        <div class="price-cell" style="color: {'#00D9A3' if put_vs_ref > 0 else '#FF5252'};">{put_vs_ref_str}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.caption("Greeks: Vega (per 1% IV), Theta (per day)")

st.markdown("<br><br>", unsafe_allow_html=True)

# Visualizations
st.markdown("### Interactive Charts")

# Chart 1: Price vs Spot (for all expirations)
st.markdown("#### Theoretical Call Price vs Spot Price (All Expirations)")

spot_range = np.linspace(120, 160, 81)
fig1 = go.Figure()

colors = ['#00D9A3', '#4A9EFF', '#9C6ADE']
for i, result in enumerate(results):
    dte, T = result['dte'], (result['date'] - CURRENT_DATE).days / 365.25
    prices = [black_scholes_merton(s, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, iv_decimal, 'call')['price'] for s in spot_range]

    fig1.add_trace(go.Scatter(
        x=spot_range,
        y=prices,
        mode='lines',
        name=f"{result['expiration']} ({result['dte']} DTE)",
        line=dict(color=colors[i], width=3)
    ))

# Add reference line (12.5% of spot)
reference_line = spot_range * 0.125
fig1.add_trace(go.Scatter(
    x=spot_range,
    y=reference_line,
    mode='lines',
    name='12.5% of Spot',
    line=dict(color=YELLOW, width=2, dash='dot')
))

# Add current spot marker
current_call_prices = [black_scholes_merton(spot_price, STRIKE, (res['date'] - CURRENT_DATE).days / 365.25,
                                            RISK_FREE_RATE, DIVIDEND_YIELD, iv_decimal, 'call')['price']
                       for res in results]
for i, result in enumerate(results):
    fig1.add_trace(go.Scatter(
        x=[spot_price],
        y=[current_call_prices[i]],
        mode='markers',
        name=f'Current ({result["expiration"][:3]})',
        marker=dict(color=colors[i], size=12, symbol='diamond', line=dict(color='white', width=2)),
        showlegend=False
    ))

fig1.update_layout(
    xaxis_title="Spot Price ($)",
    yaxis_title="Call Price ($)",
    hovermode="x unified",
    template="plotly_dark",
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor=CARD_BG,
    paper_bgcolor=DARK_BG,
    font=dict(family="Roboto", color=TEXT)
)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Price vs IV (for all expirations at current spot)
st.markdown("#### Theoretical Call Price vs Implied Volatility (All Expirations)")

iv_range = np.linspace(1.00, 1.30, 31)
fig2 = go.Figure()

for i, result in enumerate(results):
    dte, T = result['dte'], (result['date'] - CURRENT_DATE).days / 365.25
    prices = [black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, iv, 'call')['price'] for iv in iv_range]

    fig2.add_trace(go.Scatter(
        x=iv_range * 100,
        y=prices,
        mode='lines',
        name=f"{result['expiration']} ({result['dte']} DTE)",
        line=dict(color=colors[i], width=3)
    ))

# Add reference line
fig2.add_hline(
    y=reference_value,
    line=dict(color=YELLOW, width=2, dash='dot'),
    annotation_text=f"12.5% of Spot (${reference_value:.2f})",
    annotation_position="right"
)

# Add current IV marker
for i, result in enumerate(results):
    current_price = black_scholes_merton(spot_price, STRIKE, (result['date'] - CURRENT_DATE).days / 365.25,
                                         RISK_FREE_RATE, DIVIDEND_YIELD, iv_decimal, 'call')['price']
    fig2.add_trace(go.Scatter(
        x=[iv_percent],
        y=[current_price],
        mode='markers',
        name=f'Current ({result["expiration"][:3]})',
        marker=dict(color=colors[i], size=12, symbol='diamond', line=dict(color='white', width=2)),
        showlegend=False
    ))

fig2.update_layout(
    xaxis_title="Implied Volatility (%)",
    yaxis_title="Call Price ($)",
    hovermode="x unified",
    template="plotly_dark",
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor=CARD_BG,
    paper_bgcolor=DARK_BG,
    font=dict(family="Roboto", color=TEXT)
)

st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Greeks Comparison
st.markdown("#### Greeks Comparison (Call Options)")

fig3 = go.Figure()

greek_names = ['Delta', 'Gamma × 100', 'Vega', 'Theta']
expirations_list = [r['expiration'].split()[0][:3] for r in results]

# Prepare data
delta_values = [r['call']['delta'] for r in results]
gamma_values = [r['call']['gamma'] * 100 for r in results]  # Scale for visibility
vega_values = [r['call']['vega'] for r in results]
theta_values = [abs(r['call']['theta']) for r in results]  # Use absolute value for display

fig3.add_trace(go.Bar(
    name='Delta',
    x=expirations_list,
    y=delta_values,
    marker_color=colors[0]
))

fig3.add_trace(go.Bar(
    name='Gamma × 100',
    x=expirations_list,
    y=gamma_values,
    marker_color=colors[1]
))

fig3.add_trace(go.Bar(
    name='Vega ($)',
    x=expirations_list,
    y=vega_values,
    marker_color=colors[2]
))

fig3.add_trace(go.Bar(
    name='|Theta| ($)',
    x=expirations_list,
    y=theta_values,
    marker_color='#FF6B6B'
))

fig3.update_layout(
    barmode='group',
    xaxis_title="Expiration",
    yaxis_title="Greek Value",
    template="plotly_dark",
    height=450,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor=CARD_BG,
    paper_bgcolor=DARK_BG,
    font=dict(family="Roboto", color=TEXT)
)

st.plotly_chart(fig3, use_container_width=True)

# Footer info
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">Strike Price (K)</div>
        <div class="info-value">${STRIKE:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">Risk-Free Rate (r)</div>
        <div class="info-value">{RISK_FREE_RATE*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">Dividend Yield (q)</div>
        <div class="info-value">{DIVIDEND_YIELD*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.caption("""
**Disclaimer:** This is a theoretical pricing tool using the Black-Scholes-Merton model.
Actual market prices may differ significantly. Not financial advice. The $220 strikes launch on November 5, 2025.
Model assumes constant volatility and continuous trading, which may not reflect real market conditions.
""")

st.markdown(f"""
<div style="text-align: center; color: {TEXT_MUTED}; font-size: 0.9rem; margin-top: 2rem;">
    <strong>Current Date:</strong> {CURRENT_DATE.strftime('%B %d, %Y')} |
    <strong>Model:</strong> Black-Scholes-Merton |
    <strong>Ticker:</strong> BE (Bloom Energy)
</div>
""", unsafe_allow_html=True)
