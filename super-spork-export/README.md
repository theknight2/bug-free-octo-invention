# 📊 BE $220 Strike - Theoretical Options Pricing Calculator

A comprehensive **Black-Scholes-Merton** theoretical pricing calculator for **Bloom Energy (BE) $220 strike options** launching November 5, 2025.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🎯 Overview

This Streamlit web application calculates theoretical option prices and Greeks using the **Black-Scholes-Merton model** for Bloom Energy's upcoming **$220 strike options** across three expiration dates.

### **Key Features:**

✅ **Interactive Sliders**
- Spot Price: $120 - $160 (increment: $1, default: $137)
- Implied Volatility: 100% - 130% (increment: 1%, default: 130%)

✅ **Three Expirations**
- January 16, 2026 (73 DTE)
- February 20, 2026 (108 DTE)
- March 20, 2026 (136 DTE)

✅ **Complete Greeks Analysis**
- **Delta (Δ)** - Directional exposure
- **Gamma (Γ)** - Delta sensitivity
- **Vega (ν)** - IV sensitivity (per 1%)
- **Theta (Θ)** - Time decay (per day)

✅ **Visual Analytics**
- Call price vs spot price (all expirations)
- Call price vs implied volatility
- Greeks comparison charts
- 12.5% reference line (dotted yellow)

---

## 🚀 Quick Start

### **1. Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/be-options-pricing.git
cd be-options-pricing
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Run the App**
```bash
streamlit run be_220_theo.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📐 Model Parameters

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| **Strike Price** | K | $220.00 | Launching Nov 5, 2025 |
| **Current Spot** | S | $137.00 | Market price (Nov 4, 2025) |
| **Risk-Free Rate** | r | 4.3% | 10-Year Treasury Yield |
| **Dividend Yield** | q | 0.0% | BE doesn't pay dividends |
| **Implied Volatility** | σ | 100-130% | User adjustable |

### **Strike Distance**
The $220 strike is currently **60.6% OTM** from the spot price of $137.

---

## 📊 Sample Output

**At Default Settings** (Spot: $137, IV: 130%):

| Expiration | Type | Theo Price | Delta | Gamma | Vega | Theta |
|------------|------|------------|-------|-------|------|-------|
| Jan 2026 (73 DTE) | CALL | $11.78 | 0.3052 | 0.0044 | $3.56 | -$0.48 |
| Jan 2026 (73 DTE) | PUT | $92.89 | -0.6948 | 0.0044 | $3.56 | -$0.09 |

**12.5% Reference Level:** $17.13 (shown as dotted yellow line)

---

## 🧮 Black-Scholes-Merton Formula

The app implements the classic BSM formula with continuous dividends:

### **Call Option Price:**
```
C = S·e^(-q·T)·N(d₁) - K·e^(-r·T)·N(d₂)
```

### **Put Option Price:**
```
P = K·e^(-r·T)·N(-d₂) - S·e^(-q·T)·N(-d₁)
```

Where:
```
d₁ = [ln(S/K) + (r - q + σ²/2)·T] / (σ·√T)
d₂ = d₁ - σ·√T
```

---

## 🎨 Features

### **Interactive Dashboard**
- Real-time calculations as sliders adjust
- Dark theme matching modern trading platforms
- Responsive design for all screen sizes

### **Comprehensive Tables**
- Side-by-side call and put prices
- All Greeks in one view
- Comparison vs 12.5% benchmark

### **Advanced Charts (Plotly)**
1. **Price vs Spot Analysis** - See how option prices change with underlying movement
2. **Price vs IV Sensitivity** - Understand vega exposure across IV range
3. **Greeks Comparison** - Visual comparison of all Greeks across expirations

---

## 📦 Dependencies

```
streamlit>=1.28.0
numpy>=1.24.0
scipy>=1.11.0
plotly>=5.17.0
```

---

## 🔧 Technical Details

### **Time Calculation**
- Uses 365.25 days per year for accuracy
- Dynamically calculates DTE from current date
- Handles leap years correctly

### **Greeks Implementation**
- **Delta:** First derivative with respect to spot price
- **Gamma:** Second derivative with respect to spot price
- **Vega:** Derivative with respect to volatility (per 1% move)
- **Theta:** Time decay per calendar day

### **Numerical Precision**
- Uses `scipy.stats.norm` for CDF/PDF calculations
- All values rounded appropriately for display
- Handles edge cases (T=0, S=0, etc.)

---

## 📈 Use Cases

1. **Pre-Launch Analysis** - Estimate fair value before $220 strikes go live
2. **Strategy Planning** - Compare different expirations and strikes
3. **Risk Assessment** - Understand Greeks exposure before entering trades
4. **Educational Tool** - Learn how BSM pricing works interactively
5. **Sensitivity Analysis** - Test various spot and IV scenarios

---

## ⚠️ Disclaimer

**IMPORTANT:** This is a **theoretical pricing tool** using the Black-Scholes-Merton model.

- Actual market prices may differ significantly
- Not financial advice
- Model assumes constant volatility and continuous trading
- Does not account for market microstructure, liquidity, or bid-ask spreads
- $220 strikes launch on **November 5, 2025** (not yet available)

**For educational and analytical purposes only.**

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

## 🌟 Acknowledgments

- Black-Scholes-Merton model (1973)
- Streamlit framework
- Plotly for interactive visualizations
- SciPy for statistical functions

---

**Built with ❤️ for options traders**

*Last Updated: November 4, 2025*
