import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Bond Analyzer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data & Constants ---
# Source: IRS for 2024 tax year
FEDERAL_TAX_BRACKETS = {
    'Single': {
        0: 0.10, 11600: 0.12, 47150: 0.22, 100525: 0.24,
        191950: 0.32, 243725: 0.35, 609350: 0.37
    },
    'Married Filing Jointly': {
        0: 0.10, 23200: 0.12, 94300: 0.22, 201050: 0.24,
        383900: 0.32, 487450: 0.35, 731200: 0.37
    },
    'Married Filing Separately': {
        0: 0.10, 11600: 0.12, 47150: 0.22, 100525: 0.24,
        191950: 0.32, 243725: 0.35, 365600: 0.37
    },
    'Head of Household': {
        0: 0.10, 16550: 0.12, 63100: 0.22, 100500: 0.24,
        191950: 0.32, 243700: 0.35, 609350: 0.37
    }
}

# Source: Tax Foundation, top marginal rates for 2024. Simplified for this app.
STATE_TAX_RATES = {
    'None': 0.0, 'Alabama': 0.05, 'Alaska': 0.0, 'Arizona': 0.025, 'Arkansas': 0.049,
    'California': 0.133, 'Colorado': 0.044, 'Connecticut': 0.0699, 'Delaware': 0.066,
    'Florida': 0.0, 'Georgia': 0.0549, 'Hawaii': 0.11, 'Idaho': 0.058, 'Illinois': 0.0495,
    'Indiana': 0.0315, 'Iowa': 0.057, 'Kansas': 0.057, 'Kentucky': 0.05, 'Louisiana': 0.0425,
    'Maine': 0.0715, 'Maryland': 0.0575, 'Massachusetts': 0.05, 'Michigan': 0.0425,
    'Minnesota': 0.0985, 'Mississippi': 0.05, 'Missouri': 0.0495, 'Montana': 0.047,
    'Nebraska': 0.0664, 'Nevada': 0.0, 'New Hampshire': 0.0, 'New Jersey': 0.1075,
    'New Mexico': 0.059, 'New York': 0.109, 'North Carolina': 0.045, 'North Dakota': 0.025,
    'Ohio': 0.0399, 'Oklahoma': 0.0475, 'Oregon': 0.099, 'Pennsylvania': 0.0307,
    'Rhode Island': 0.0599, 'South Carolina': 0.065, 'South Dakota': 0.0, 'Tennessee': 0.0,
    'Texas': 0.0, 'Utah': 0.0465, 'Vermont': 0.0875, 'Virginia': 0.0575,
    'Washington': 0.0, 'West Virginia': 0.0512, 'Wisconsin': 0.0765, 'Wyoming': 0.0
}
STATES_LIST = sorted(STATE_TAX_RATES.keys())

# --- Helper Functions ---
def get_federal_tax_rate(income, status):
    """Calculates the marginal federal tax rate based on income and filing status."""
    brackets = FEDERAL_TAX_BRACKETS[status]
    rate = 0.0
    for bracket_income, bracket_rate in sorted(brackets.items(), reverse=True):
        if income >= bracket_income:
            rate = bracket_rate
            break
    return rate

def calculate_yields(face_value, market_price, coupon_rate, years_to_maturity, years_to_call, call_price):
    """Calculates current yield, YTM, and YTC."""
    annual_coupon = face_value * coupon_rate

    # Current Yield
    current_yield = (annual_coupon / market_price) if market_price > 0 else 0

    # Yield to Maturity (Approximation)
    ytm = ((annual_coupon + (face_value - market_price) / years_to_maturity) /
           ((face_value + market_price) / 2)) if years_to_maturity > 0 and market_price > 0 else 0

    # Yield to Call (Approximation)
    ytc = ((annual_coupon + (call_price - market_price) / years_to_call) /
           ((call_price + market_price) / 2)) if years_to_call > 0 and market_price > 0 and call_price else 0

    return current_yield, ytm, ytc

# --- Sidebar for User Inputs ---
st.sidebar.header("👤 Investor Profile")
annual_income = st.sidebar.number_input("Annual Taxable Income ($)", min_value=0, value=100000, step=1000)
filing_status = st.sidebar.selectbox("Filing Status", list(FEDERAL_TAX_BRACKETS.keys()))
investor_state = st.sidebar.selectbox("State for Tax Purposes", STATES_LIST, index=STATES_LIST.index('California'))
st.sidebar.markdown("---")
st.sidebar.info("This app is for educational purposes only. The tax rates and bond data are simplified and may not reflect current market conditions. Consult a financial advisor for professional advice.")

# --- Main App ---
st.title("💼 Bond Analysis Dashboard")
st.markdown("Compare different types of bonds based on your personal financial situation.")

# --- Tax Calculation & Display ---
federal_rate = get_federal_tax_rate(annual_income, filing_status)
state_rate = STATE_TAX_RATES[investor_state]
total_tax_rate = federal_rate + state_rate

st.header("📊 Your Tax Profile & Key Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Federal Tax Bracket", f"{federal_rate:.1%}")
with col2:
    st.metric("State Tax Rate", f"{state_rate:.1%}")
with col3:
    st.metric("Combined Marginal Rate", f"{total_tax_rate:.1%}")

# --- Bond Data Simulation ---
# Let's create some example bonds to compare
# [Name, Coupon Rate, Market Price, Years to Maturity, Callable, Years to Call, Call Price, Tax-Free (Fed), Tax-Free (State)]
bond_data = [
    ["Municipal Bond (In-State)", 0.04, 1020, 10, False, None, None, True, True],
    ["Municipal Bond (Out-of-State)", 0.042, 1030, 12, False, None, None, True, False],
    ["U.S. Treasury Note", 0.05, 990, 10, False, None, None, False, True],
    ["Corporate Bond (Secured)", 0.065, 1050, 15, True, 5, 1025, False, False],
    ["Corporate Bond (Unsecured)", 0.072, 1000, 20, True, 5, 1030, False, False],
    ["Convertible Bond", 0.055, 1100, 8, False, None, None, False, False],
    ["Foreign Bond (Developed)", 0.045, 980, 7, False, None, None, False, False],
]

FACE_VALUE = 1000
results = []

for bond in bond_data:
    name, coupon, price, maturity, _, call_years, call_price, fed_free, state_free = bond
    
    cy, ytm, ytc = calculate_yields(FACE_VALUE, price, coupon, maturity, call_years, call_price)
    
    # Calculate Tax Equivalent Yield
    taxable_yield = ytm
    if fed_free and state_free: # In-state muni
        taxable_equivalent_yield = ytm / (1 - total_tax_rate)
    elif fed_free and not state_free: # Out-of-state muni
        taxable_equivalent_yield = ytm / (1 - federal_rate)
    elif not fed_free and state_free: # Treasury
        taxable_equivalent_yield = ytm * (1 - state_rate)
    else: # Fully taxable
        taxable_equivalent_yield = ytm

    results.append({
        "Bond Type": name,
        "Coupon": coupon,
        "Market Price": price,
        "YTM": ytm,
        "Taxable Equivalent Yield": taxable_equivalent_yield,
        "Current Yield": cy,
        "YTC": ytc if ytc > 0 else "N/A"
    })

df = pd.DataFrame(results)

st.header("📈 Bond Comparison")
st.markdown(f"""
The table below shows a comparison of hypothetical bonds. The **"Taxable Equivalent Yield"** is the most important column for comparison. 
It shows what a fully taxable bond would need to yield to be equivalent to a tax-advantaged bond, given your specific tax rates.
""")

# Displaying the dataframe with formatted percentages
st.dataframe(df.style.format({
    'Coupon': '{:.2%}',
    'YTM': '{:.3%}',
    'Taxable Equivalent Yield': '{:.3%}',
    'Current Yield': '{:.3%}',
    'YTC': lambda x: '{:.3%}'.format(x) if isinstance(x, (int, float)) else x,
    'Market Price': '${:,.2f}'
}), use_container_width=True)


# --- Yield Explanations ---
st.header("💡 Understanding Yield")
st.markdown("Yield is a measure of the return on investment for a bond. Here are the key types:")

yield_tab1, yield_tab2, yield_tab3 = st.tabs(["Current Yield", "Yield to Maturity (YTM)", "Yield to Call (YTC)"])

with yield_tab1:
    st.subheader("Current Yield")
    st.markdown("""
    This is the simplest yield calculation. It represents the annual return based on the bond's coupon payment and its current market price.
    
    - **Formula:** `Annual Coupon Payment / Current Market Price`
    - **Purpose:** Provides a quick snapshot of the return you'd get if you bought the bond and held it for one year.
    - **Limitation:** It doesn't account for the gain or loss you'll realize if you hold the bond until it matures (the difference between the market price and the face value).
    """)

with yield_tab2:
    st.subheader("Yield to Maturity (YTM)")
    st.markdown("""
    YTM is the total return an investor can expect if they hold the bond until its maturity date. It's a more comprehensive measure than current yield.
    
    - **Concept:** It includes all future coupon payments plus the difference between the current market price and the bond's face value (par value).
    - **Purpose:** It provides a standardized way to compare bonds with different coupons, market prices, and maturity dates.
    - **Note:** This calculation assumes all coupon payments are reinvested at the same rate as the YTM, which may not be realistic. The formula used here is a common approximation.
    """)

with yield_tab3:
    st.subheader("Yield to Call (YTC)")
    st.markdown("""
    YTC is the total return an investor can expect if they hold a callable bond until its first call date, and the issuer *does* call the bond.
    
    - **Concept:** Similar to YTM, but it uses the call price instead of the face value and the time until the first call date instead of the time to maturity.
    - **Purpose:** Crucial for evaluating callable bonds. If a bond is trading at a premium and interest rates have fallen, there's a higher chance it will be called. Investors should be aware of the lower of YTM and YTC, known as the "Yield to Worst".
    """)

# --- Bond Type Explanations ---
st.header("📚 Deep Dive into Bond Types")
with st.expander("Municipal Bonds (Munis)"):
    st.markdown("""
    - **Description:** Debt securities issued by states, cities, counties, and other governmental entities to fund public projects.
    - **Key Feature:** The interest income is typically exempt from federal income tax. If you buy a muni issued by your own state, it's often exempt from state and local taxes as well ("double tax-free").
    - **Pros:** Significant tax advantages for high-income earners, generally low default risk.
    - **Cons:** Lower stated yields compared to taxable bonds, subject to interest rate risk.
    """)

with st.expander("U.S. Government & Agency Issues"):
    st.markdown("""
    - **Description:** Debt issued by the U.S. Department of the Treasury (T-bills, T-notes, T-bonds) or other government agencies.
    - **Key Feature:** Considered the safest investment in the world as they are backed by the full faith and credit of the U.S. government. Interest income is taxable at the federal level but exempt from state and local taxes.
    - **Pros:** Extremely low credit/default risk, highly liquid market.
    - **Cons:** Lower yields compared to corporate bonds due to their high safety.
    """)
    
with st.expander("Corporate Bonds"):
    st.markdown("""
    - **Description:** Debt issued by corporations to raise capital. They are fully taxable at all levels (federal, state, and local).
    - **Pros:** Higher yields than government bonds to compensate for higher risk. Wide range of choices across different industries and credit ratings.
    - **Cons:** Higher credit/default risk compared to government bonds. Less liquid than the Treasury market.
    
    ---
    
    #### Secured vs. Unsecured Corporate Debt
    
    **Secured Bonds:**
    - **Definition:** Backed by specific collateral (e.g., property, equipment, or other assets) that can be seized and sold if the issuer defaults.
    - **Risk:** Lower risk for the investor because there is a direct claim on assets in case of bankruptcy.
    - **Yield:** Tend to offer slightly lower yields than unsecured bonds from the same issuer due to the reduced risk.
    
    **Unsecured Bonds (Debentures):**
    - **Definition:** Backed only by the issuer's general creditworthiness and ability to repay, not by any specific collateral.
    - **Risk:** Higher risk for the investor. In a bankruptcy, unsecured bondholders are paid only after secured bondholders.
    - **Yield:** Must offer higher yields to compensate investors for the additional risk.
    """)

with st.expander("Convertible Bonds"):
    st.markdown("""
    - **Description:** A hybrid security that combines features of a bond with those of a stock. It's a corporate bond that can be exchanged for a predetermined number of the issuing company's common stock shares.
    - **Pros:** Offers the safety of fixed coupon payments (like a bond) and the potential for capital appreciation if the stock price goes up (like a stock).
    - **Cons:** Lower yields than non-convertible corporate bonds. The conversion feature comes at a price.
    """)

with st.expander("Foreign Bonds"):
    st.markdown("""
    - **Description:** Bonds issued by foreign governments or corporations.
    - **Pros:** Can offer portfolio diversification and potentially higher yields.
    - **Cons:** Subject to additional risks, including currency risk (fluctuations in the exchange rate between the dollar and the foreign currency) and political/country risk.
    """)
