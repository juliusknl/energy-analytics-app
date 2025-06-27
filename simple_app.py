import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="German Energy Benchmarking",
    page_icon="⚡",
    layout="wide"
)

# Test if basic streamlit works
st.title("⚡ German Industrial Energy Benchmarking")
st.write("**Testing basic functionality...**")

# Generate sample data (since we might have issues with the modules)
@st.cache_data
def create_sample_data():
    """Create sample German energy data for testing"""
    np.random.seed(42)  # For consistent results
    
    sectors = ["Manufacturing", "Chemical", "Food Production", "Automotive"]
    regions = ["Bayern", "Nordrhein-Westfalen", "Baden-Württemberg", "Niedersachsen"]
    
    companies = []
    for i in range(200):
        sector = np.random.choice(sectors)
        region = np.random.choice(regions)
        employees = np.random.randint(50, 501)
        
        # Realistic energy consumption based on sector
        base_consumption = {
            "Manufacturing": 15000,
            "Chemical": 28000, 
            "Food Production": 9000,
            "Automotive": 17000
        }[sector]
        
        kwh_per_employee = base_consumption * np.random.normal(1.0, 0.3)
        kwh_per_employee = max(5000, kwh_per_employee)
        
        # Regional pricing
        base_prices = {
            "Bayern": 0.148,
            "Nordrhein-Westfalen": 0.142,
            "Baden-Württemberg": 0.153,
            "Niedersachsen": 0.140
        }
        
        cost_per_kwh = base_prices[region] * np.random.normal(1.0, 0.1)
        
        companies.append({
            'sector': sector,
            'region': region,
            'employees': employees,
            'kwh_per_employee': kwh_per_employee,
            'cost_per_kwh': cost_per_kwh,
            'annual_kwh': kwh_per_employee * employees
        })
    
    return pd.DataFrame(companies)

# Test data loading
try:
    df = create_sample_data()
    st.success(f"✅ Data loaded successfully! {len(df)} companies in dataset")
    
    # Show sample data
    if st.checkbox("Show sample data"):
        st.dataframe(df.head())
        
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Sidebar for user input
with st.sidebar:
    st.header("🏭 Your Company Profile")
    
    sector = st.selectbox("Industry Sector", ["Manufacturing", "Chemical", "Food Production", "Automotive"])
    employees = st.number_input("Number of Employees", 50, 500, 150)
    region = st.selectbox("German State", ["Bayern", "Nordrhein-Westfalen", "Baden-Württemberg", "Niedersachsen"])
    annual_kwh = st.number_input("Annual Electricity (kWh)", 100_000, 10_000_000, 2_000_000, step=100_000)
    cost_per_kwh = st.number_input("Cost per kWh (€)", 0.10, 0.30, 0.15, step=0.001, format="%.3f")

# Calculate benchmarks
try:
    # Find peer companies
    peer_companies = df[
        (df['sector'] == sector) & 
        (df['employees'] >= employees * 0.7) & 
        (df['employees'] <= employees * 1.3)
    ]
    
    if len(peer_companies) < 5:
        peer_companies = df[df['sector'] == sector]
    
    user_kwh_per_employee = annual_kwh / employees
    
    # Calculate percentiles
    efficiency_percentile = (peer_companies['kwh_per_employee'] > user_kwh_per_employee).mean() * 100
    cost_percentile = (peer_companies['cost_per_kwh'] < cost_per_kwh).mean() * 100
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Energy Efficiency Ranking",
            f"{efficiency_percentile:.0f}th percentile",
            f"vs {len(peer_companies)} peers"
        )
    
    with col2:
        st.metric(
            "Cost Performance", 
            f"{cost_percentile:.0f}th percentile",
            f"€{cost_per_kwh:.3f}/kWh"
        )
    
    with col3:
        st.metric(
            "Energy Intensity",
            f"{user_kwh_per_employee:,.0f}",
            "kWh/employee"
        )
    
    # Create visualization
    st.subheader("📊 Peer Comparison")
    
    fig = go.Figure()
    
    # Peer distribution
    fig.add_trace(go.Histogram(
        x=peer_companies['kwh_per_employee'],
        name="Peer Companies",
        opacity=0.7,
        nbinsx=15
    ))
    
    # User position
    fig.add_vline(
        x=user_kwh_per_employee,
        line_dash="dash",
        line_color="red",
        annotation_text=f"You: {user_kwh_per_employee:,.0f}"
    )
    
    # Peer median
    peer_median = peer_companies['kwh_per_employee'].median()
    fig.add_vline(
        x=peer_median,
        line_color="green",
        annotation_text=f"Peer Median: {peer_median:,.0f}"
    )
    
    fig.update_layout(
        title="Energy Consumption Distribution",
        xaxis_title="kWh per Employee",
        yaxis_title="Number of Companies",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.subheader("🎯 Key Insights")
    
    if efficiency_percentile < 50:
        st.warning(f"⚠️ **Efficiency Opportunity**: You rank {efficiency_percentile:.0f}th percentile among peers. Top performers use {peer_companies['kwh_per_employee'].quantile(0.25):,.0f} kWh/employee.")
    else:
        st.success(f"✅ **Good Efficiency**: You rank {efficiency_percentile:.0f}th percentile - above average!")
    
    if cost_percentile > 60:
        potential_savings = annual_kwh * (cost_per_kwh - peer_companies['cost_per_kwh'].median())
        st.warning(f"💰 **Cost Opportunity**: You pay more than {cost_percentile:.0f}% of peers. Potential savings: €{potential_savings:,.0f}/year")
    else:
        st.success(f"✅ **Competitive Pricing**: Your costs are competitive with peers.")

except Exception as e:
    st.error(f"❌ Error in calculations: {e}")
    st.write("Debug info:")
    st.write(f"Sector: {sector}")
    st.write(f"Employees: {employees}")
    st.write(f"Peer companies found: {len(peer_companies) if 'peer_companies' in locals() else 'None'}")

# Footer
st.markdown("---")
st.markdown("**Data Source**: Simulated based on German industrial energy statistics")
st.markdown("🚀 **Status**: MVP Testing Version")