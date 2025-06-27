import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from benchmark_calculator import GermanEnergyBenchmarker

# Page configuration
st.set_page_config(
    page_title="Energy Benchmarking Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2E8B57;
    }
    .insight-high {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .insight-positive {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'benchmarker' not in st.session_state:
    try:
        st.session_state.benchmarker = GermanEnergyBenchmarker()
    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}")
        st.stop()

if 'benchmark_result' not in st.session_state:
    st.session_state.benchmark_result = None

# Main header
st.markdown('<h1 class="main-header">🇩🇪 German Energy Benchmarking Tool</h1>', unsafe_allow_html=True)

# Sidebar for company input
with st.sidebar:
    st.header("🏭 Company Profile")
    
    # Get unique sectors from the data
    sectors = st.session_state.benchmarker.df['sector'].unique()
    regions = st.session_state.benchmarker.df['region'].unique()
    
    sector = st.selectbox("Industry Sector", sectors, index=0)
    region = st.selectbox("Region", regions, index=0)
    employees = st.number_input("Number of Employees", min_value=1, max_value=5000, value=100)
    annual_kwh = st.number_input("Annual Energy Consumption (kWh)", min_value=1000, max_value=100000000, value=2000000, step=10000)
    cost_per_kwh = st.number_input("Energy Cost (€/kWh)", min_value=0.01, max_value=1.0, value=0.15, step=0.001, format="%.3f")
    
    # Calculate some derived metrics
    kwh_per_employee = annual_kwh / employees
    annual_cost = annual_kwh * cost_per_kwh
    
    st.markdown("---")
    st.subheader("📊 Quick Metrics")
    st.metric("Energy Intensity", f"{kwh_per_employee:,.0f} kWh/employee")
    st.metric("Annual Energy Cost", f"€{annual_cost:,.0f}")
    
    # Benchmark button
    if st.button("🔍 Run Benchmark Analysis", type="primary"):
        company_profile = {
            'sector': sector,
            'region': region,
            'employees': employees,
            'annual_kwh': annual_kwh,
            'cost_per_kwh': cost_per_kwh
        }
        
        with st.spinner('Analyzing your company against German peers...'):
            st.session_state.benchmark_result = st.session_state.benchmarker.benchmark_company(company_profile)

# Main content area
if st.session_state.benchmark_result is None:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Welcome to the German Energy Benchmarking Tool
        
        This tool compares your company's energy performance against similar German companies in your sector.
        
        **How it works:**
        1. Enter your company details in the sidebar
        2. Click "Run Benchmark Analysis" 
        3. Get insights on efficiency, costs, and savings potential
        
        **Based on real German industrial energy data** 📊
        """)
        
        # Show some sample data statistics
        st.markdown("---")
        st.subheader("📈 Dataset Overview")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Total Companies", len(st.session_state.benchmarker.df))
        with col_b:
            st.metric("Sectors Covered", st.session_state.benchmarker.df['sector'].nunique())
        with col_c:
            st.metric("Regions Covered", st.session_state.benchmarker.df['region'].nunique())

else:
    result = st.session_state.benchmark_result
    profile = result['company_profile']
    benchmarks = result['benchmarks']
    insights = result['insights']
    
    # Peer group context
    st.subheader("👥 Peer Group Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Your Sector", profile['sector'])
    with col2:
        st.metric("Your Region", profile['region'])
    with col3:
        st.metric("Similar Companies", f"{result['peer_group_size']:,} peers")
    with col4:
        st.metric("Your Size", f"{profile['employees']:,} employees")
    
    st.info(f"💡 **Peer Group**: We compare your company against {result['peer_group_size']:,} similar companies in the {profile['sector']} sector within {profile['region']}, Germany. This ensures relevant and meaningful benchmarking.")
    
    # Key performance metrics
    st.subheader("📊 Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        efficiency_delta = benchmarks['efficiency_vs_median_pct']
        efficiency_color = "inverse" if efficiency_delta < 0 else "normal"
        st.metric(
            "Energy Intensity", 
            f"{result['user_metrics']['kwh_per_employee']:,.0f} kWh/employee",
            f"{efficiency_delta:+.1f}% vs peers",
            delta_color=efficiency_color
        )
    with col2:
        cost_delta = benchmarks['cost_vs_median_pct']
        cost_color = "inverse" if cost_delta < 0 else "normal"
        st.metric(
            "Energy Cost", 
            f"€{profile['cost_per_kwh']:.3f}/kWh",
            f"{cost_delta:+.1f}% vs peers",
            delta_color=cost_color
        )
    with col3:
        st.metric(
            "Efficiency Ranking", 
            f"{benchmarks['efficiency_percentile']:.0f}th percentile",
            "Higher is better"
        )
    with col4:
        st.metric(
            "Annual Energy Cost", 
            f"€{result['user_metrics']['annual_cost_eur']:,.0f}",
            None
        )
    
    # Visualization section
    st.subheader("📈 Benchmark Visualization")
    
    # Create comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Efficiency comparison
        fig_eff = go.Figure()
        
        # Add peer data
        peers_df = st.session_state.benchmarker._find_peers(profile)
        fig_eff.add_trace(go.Histogram(
            x=peers_df['kwh_per_employee'],
            name='Peer Companies',
            opacity=0.7,
            nbinsx=20
        ))
        
        # Add user position
        fig_eff.add_vline(
            x=result['user_metrics']['kwh_per_employee'],
            line_dash="dash",
            line_color="red",
            annotation_text="Your Company",
            annotation_position="top"
        )
        
        # Add quartiles
        q25 = benchmarks['peer_stats']['kwh_per_employee_q25']
        q75 = benchmarks['peer_stats']['kwh_per_employee_q75']
        fig_eff.add_vline(x=q25, line_dash="dot", line_color="green", annotation_text="Top 25%")
        fig_eff.add_vline(x=q75, line_dash="dot", line_color="orange", annotation_text="Bottom 25%")
        
        fig_eff.update_layout(
            title="Energy Intensity Distribution",
            xaxis_title="kWh per Employee",
            yaxis_title="Number of Companies",
            showlegend=True
        )
        
        st.plotly_chart(fig_eff, use_container_width=True)
    
    with col2:
        # Cost comparison
        fig_cost = go.Figure()
        
        fig_cost.add_trace(go.Histogram(
            x=peers_df['cost_per_kwh'],
            name='Peer Companies',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig_cost.add_vline(
            x=profile['cost_per_kwh'],
            line_dash="dash",
            line_color="red",
            annotation_text="Your Company",
            annotation_position="top"
        )
        
        # Add quartiles
        q25_cost = benchmarks['peer_stats']['cost_per_kwh_q25']
        q75_cost = benchmarks['peer_stats']['cost_per_kwh_q75']
        fig_cost.add_vline(x=q25_cost, line_dash="dot", line_color="green", annotation_text="Lowest 25%")
        fig_cost.add_vline(x=q75_cost, line_dash="dot", line_color="orange", annotation_text="Highest 25%")
        
        fig_cost.update_layout(
            title="Energy Cost Distribution",
            xaxis_title="€ per kWh",
            yaxis_title="Number of Companies",
            showlegend=True
        )
        
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Savings potential
    savings = benchmarks['savings_potential']
    if savings['total_eur'] > 0:
        st.subheader("💰 Savings Potential")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Efficiency Savings", f"€{savings['efficiency_eur']:,.0f}/year")
        with col2:
            st.metric("Cost Optimization", f"€{savings['cost_eur']:,.0f}/year")
        with col3:
            st.metric("Total Potential", f"€{savings['total_eur']:,.0f}/year", "Combined savings")
    
    # Insights and recommendations
    st.subheader("🎯 Key Insights & Recommendations")
    
    for insight in insights:
        if insight['priority'] == 'HIGH':
            st.markdown(f"""
            <div class="insight-high">
                <h4>🔴 {insight['title']}</h4>
                <p><strong>{insight['message']}</strong></p>
                <p>{insight['details']}</p>
                <p><strong>Action:</strong> {insight['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        elif insight['priority'] == 'POSITIVE':
            st.markdown(f"""
            <div class="insight-positive">
                <h4>✅ {insight['title']}</h4>
                <p><strong>{insight['message']}</strong></p>
                <p>{insight['details']}</p>
                <p><strong>Action:</strong> {insight['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"**{insight['title']}**: {insight['message']} - {insight['action']}")
        
        # Show recommendations
        if 'recommendations' in insight:
            with st.expander(f"Recommendations for {insight['title']}"):
                for rec in insight['recommendations']:
                    st.write(f"• {rec}")
    
    # Reset button
    if st.button("🔄 Analyze Another Company"):
        st.session_state.benchmark_result = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("📊 **Data Source**: Real German Industrial Energy Statistics | **Generated**: " + 
           pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))