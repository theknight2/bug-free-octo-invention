import streamlit as st
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from datetime import date

# Page configuration
st.set_page_config(
    page_title="BE $220 Strike Theoretical Pricing",
    page_icon="📊",
    layout="wide"
)

# Minimal styling
st.markdown("""
<style>
    .stApp {
        background: #0a0a0a;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 400;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.5px;
    }
    .dataframe {
        background: #1a1a1a;
        border: 1px solid #333;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #ffffff;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# BSM calculation
def black_scholes_merton(S, K, T, r, q, sigma, option_type='call'):
    if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
        return {'price': 0.0, 'delta': 0.0, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0}

    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    N = norm.cdf
    n = norm.pdf

    if option_type == 'call':
        price = S*np.exp(-q*T)*N(d1) - K*np.exp(-r*T)*N(d2)
        delta = np.exp(-q*T) * N(d1)
        theta = ((-S*n(d1)*sigma*np.exp(-q*T))/(2*np.sqrt(T))
                 - r*K*np.exp(-r*T)*N(d2)
                 + q*S*np.exp(-q*T)*N(d1)) / 365
    else:
        price = K*np.exp(-r*T)*N(-d2) - S*np.exp(-q*T)*N(-d1)
        delta = -np.exp(-q*T) * N(-d1)
        theta = ((-S*n(d1)*sigma*np.exp(-q*T))/(2*np.sqrt(T))
                 + r*K*np.exp(-r*T)*N(-d2)
                 - q*S*np.exp(-q*T)*N(-d1)) / 365

    gamma = np.exp(-q*T)*n(d1) / (S*sigma*np.sqrt(T))
    vega = S*np.exp(-q*T)*n(d1)*np.sqrt(T) / 100

    return {
        'price': float(price),
        'delta': float(delta),
        'gamma': float(gamma),
        'vega': float(vega),
        'theta': float(theta)
    }

# Constants
STRIKE = 220.0
RISK_FREE_RATE = 0.043
DIVIDEND_YIELD = 0.00
CURRENT_DATE = date(2025, 11, 4)

EXPIRATIONS = {
    'Jan 2026': date(2026, 1, 16),
    'Feb 2026': date(2026, 2, 20),
    'Mar 2026': date(2026, 3, 20)
}

def get_dte_and_t(expiry_date):
    dte = (expiry_date - CURRENT_DATE).days
    T = dte / 365.25
    return dte, T

# Header
st.markdown('<div class="main-title">Bloom Energy - $220 Strike Theoretical Pricing</div>', unsafe_allow_html=True)

# Input parameters
col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

with col1:
    spot_price = st.slider("Spot Price", 120.0, 160.0, 137.0, 1.0)

with col2:
    call_iv_percent = st.slider("Call IV (%)", 80, 150, 130, 1)

with col3:
    put_iv_percent = st.slider("Put IV (%)", 80, 150, 130, 1)

with col4:
    reference_value = spot_price * 0.125
    st.metric("12.5% Reference", f"${reference_value:.2f}")

st.markdown("---")

call_iv_decimal = call_iv_percent / 100.0
put_iv_decimal = put_iv_percent / 100.0

# Calculate prices
results = []
for exp_name, exp_date in EXPIRATIONS.items():
    dte, T = get_dte_and_t(exp_date)
    call_result = black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, call_iv_decimal, 'call')
    put_result = black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, put_iv_decimal, 'put')

    results.append({
        'Expiration': f"{exp_name} ({dte} DTE)",
        'Type': 'CALL',
        'Price': f"${call_result['price']:.2f}",
        'Delta': f"{call_result['delta']:.4f}",
        'Gamma': f"{call_result['gamma']:.5f}",
        'Vega': f"${call_result['vega']:.2f}",
        'Theta': f"${call_result['theta']:.2f}"
    })

    results.append({
        'Expiration': '',
        'Type': 'PUT',
        'Price': f"${put_result['price']:.2f}",
        'Delta': f"{put_result['delta']:.4f}",
        'Gamma': f"{put_result['gamma']:.5f}",
        'Vega': f"${put_result['vega']:.2f}",
        'Theta': f"${put_result['theta']:.2f}"
    })

# Display table
import pandas as pd
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Price vs Spot")
    spot_range = np.linspace(120, 160, 81)
    fig1 = go.Figure()

    colors = ['#4A90E2', '#50C878', '#9B59B6']
    for i, (exp_name, exp_date) in enumerate(EXPIRATIONS.items()):
        dte, T = get_dte_and_t(exp_date)
        prices = [black_scholes_merton(s, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, call_iv_decimal, 'call')['price'] for s in spot_range]
        fig1.add_trace(go.Scatter(x=spot_range, y=prices, mode='lines', name=exp_name,
                                   line=dict(color=colors[i], width=2)))

    reference_line = spot_range * 0.125
    fig1.add_trace(go.Scatter(x=spot_range, y=reference_line, mode='lines', name='12.5% Reference',
                               line=dict(color='#999', width=1, dash='dot')))

    fig1.update_layout(
        xaxis_title="Spot Price",
        yaxis_title="Call Price",
        template="plotly_dark",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Price vs IV")
    iv_range = np.linspace(0.80, 1.50, 71)
    fig2 = go.Figure()

    for i, (exp_name, exp_date) in enumerate(EXPIRATIONS.items()):
        dte, T = get_dte_and_t(exp_date)
        prices = [black_scholes_merton(spot_price, STRIKE, T, RISK_FREE_RATE, DIVIDEND_YIELD, iv, 'call')['price'] for iv in iv_range]
        fig2.add_trace(go.Scatter(x=iv_range*100, y=prices, mode='lines', name=exp_name,
                                   line=dict(color=colors[i], width=2)))

    fig2.add_hline(y=reference_value, line=dict(color='#999', width=1, dash='dot'))

    fig2.update_layout(
        xaxis_title="Implied Volatility (%)",
        yaxis_title="Call Price",
        template="plotly_dark",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Model parameters footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Strike", f"${STRIKE:.0f}")
with col2:
    st.metric("Risk-Free Rate", f"{RISK_FREE_RATE*100:.1f}%")
with col3:
    st.metric("Dividend Yield", f"{DIVIDEND_YIELD*100:.1f}%")
