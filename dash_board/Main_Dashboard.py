# dashboard/streamlit_app.py
import streamlit as st
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import calendar

# --- Path Setup ---
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from data_processor import DataProcessor
from analyzer import SeasonalAnalyzer
from forecaster import CashFlowForecaster
from visualizer import CashFlowVisualizer
from insights_generator import InsightsGenerator

# --- Page Configuration ---
st.set_page_config(page_title="Cash Flow Optimizer", page_icon="📊", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding: 2rem 3rem;
    }
    .st-emotion-cache-z5fcl4 {
        border: 1px solid #e6e6e6; border-radius: 0.5rem; padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_and_process_data(uploaded_file):
    data = None
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
    else:
        sample_data_path = os.path.join(project_root, 'data', 'sample_data.csv')
        if os.path.exists(sample_data_path):
            data = pd.read_csv(sample_data_path)
            st.sidebar.info("Using sample data.")
        else:
            st.error("Sample data not found. Please run 'python data_generator.py' first.")
            st.stop()
    
    processor = DataProcessor()
    processor.data = data.copy()
    processor.data['date'] = pd.to_datetime(processor.data['date'])
    processor.clean_data()
    processor.aggregate_monthly()
    processor.calculate_kpis()
    return processor.monthly_data

# --- Sidebar ---
st.sidebar.title("Cash Flow Optimizer")
uploaded_file = st.sidebar.file_uploader("Upload Your CSV", type=['csv'])
st.sidebar.divider()

monthly_data = load_and_process_data(uploaded_file)

st.sidebar.header("Navigation")
analysis_type = st.sidebar.radio(
    "Choose an analysis page:",
    ["Executive Overview", "Seasonal Deep Dive", "Cash Flow Forecasting", "Scenario & Stress Testing"]
)
st.sidebar.divider()

# --- Main Content ---
st.title("Cash Flow Analysis Dashboard")
st.markdown("An interactive tool to analyze, forecast, and optimize your business cash flow.")
st.divider()

# == 1. Executive Overview Page ==
if analysis_type == "Executive Overview":
    st.header("Executive Overview")
    
    with st.container(border=True):
        st.subheader("Actionable Insights")
        insights_gen = InsightsGenerator(monthly_data)
        insights = insights_gen.generate_all_insights()
        if "Good Financial Health" in insights[0]:
            st.success(insights[0], icon="✅")
        else:
            st.warning(insights[0], icon="⚠️")
        for insight in insights[1:]:
             st.info(insight, icon="💡")

    with st.container(border=True):
        st.subheader("Key Performance Indicators (Monthly Averages)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg. Monthly Inflow", f"${monthly_data['cash_inflow'].mean():,.0f}")
        col2.metric("Avg. Monthly Outflow", f"${monthly_data['cash_outflow'].mean():,.0f}")
        col3.metric("Avg. Net Cash Flow", f"${monthly_data['net_cash_flow'].mean():,.0f}")
        col4.metric("Avg. DSO (Days)", f"{monthly_data['dso'].mean():.1f}")
    
    with st.container(border=True):
        visualizer = CashFlowVisualizer(monthly_data)
        st.subheader("Interactive Analysis Dashboard")
        fig = visualizer.create_interactive_dashboard()
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("What am I seeing?"):
            st.info("""
                - **Monthly Net Cash Flow:** Shows your profit or loss for each month.
                - **Seasonal Averages:** Highlights your strongest and weakest months on average.
                - **Cumulative Net Cash Flow:** Tracks your total cash position over time. An upward trend is healthy.
            """)

# == 2. Seasonal Analysis Page ==
elif analysis_type == "Seasonal Deep Dive":
    st.header("Seasonal Deep Dive")
    
    analyzer = SeasonalAnalyzer(monthly_data)

    with st.container(border=True):
        st.subheader("Core Seasonal Statistics")
        seasonal_stats = analyzer.analyze_seasonality()
        peak_month_name = calendar.month_name[seasonal_stats['peak_month']]
        trough_month_name = calendar.month_name[seasonal_stats['trough_month']]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Peak Cash Flow Month", peak_month_name)
            st.metric("Trough Cash Flow Month", trough_month_name)
            st.metric("Seasonal Range", f"${seasonal_stats['seasonal_range']:,.0f}")
        with col2:
            stats_df_display = seasonal_stats['monthly_stats'].copy()
            stats_df_display['month'] = stats_df_display['month'].apply(lambda x: calendar.month_abbr[x])
            st.dataframe(stats_df_display.round(2))

    with st.container(border=True):
        st.subheader("Seasonal Decomposition")
        decomposition = analyzer.decompose_time_series()
        
        # --- Customizing the plot ---
        # Get the figure object from the decomposition plot
        fig = decomposition.plot()
        fig.set_size_inches(12, 8)

        # Define a modern color palette
        colors = {
            "observed": "#0d6efd",  # Bootstrap Blue
            "trend": "#dc3545",     # Bootstrap Red
            "seasonal": "#198754",  # Bootstrap Green
            "resid": "#6c757d"      # Bootstrap Gray
        }

        # Iterate through the axes (subplots) of the figure
        for i, ax in enumerate(fig.get_axes()):
            ax.patch.set_alpha(0.0)  # Set axis background to transparent
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', colors='#888') # Lighter gray for ticks
            ax.tick_params(axis='y', colors='#888')
            ax.yaxis.label.set_color('#888')
            ax.title.set_color('#333') # Darker for title

            # Customize lines
            line = ax.get_lines()[0]
            line.set_linewidth(2)
            if ax.get_title() == 'Observed':
                line.set_color(colors['observed'])
            elif ax.get_title() == 'Trend':
                line.set_color(colors['trend'])
            elif ax.get_title() == 'Seasonal':
                line.set_color(colors['seasonal'])
            elif ax.get_title() == 'Residual':
                line.set_color(colors['resid'])
                line.set_marker('.') # Use dots for residuals
                line.set_linestyle('') # Remove connecting line

        fig.patch.set_alpha(0.0) # Set figure background to transparent
        plt.tight_layout()
        st.pyplot(fig)

        with st.expander("What am I seeing?"):
            st.info("""
                - **Observed:** The original, raw data.
                - **Trend:** The long-term direction of your cash flow.
                - **Seasonal:** The repeating, cyclical pattern within a 12-month period.
                - **Residual:** The random, unpredictable noise left over.
            """)

# == 3. Forecasting Page ==
elif analysis_type == "Cash Flow Forecasting":
    st.header("Cash Flow Forecasting")

    with st.container(border=True):
        st.subheader("Forecasting Controls")
        col1, col2 = st.columns(2)
        periods = col1.slider("Forecast Months", 3, 24, 12)
        method = col1.selectbox("Forecasting Method", ["Ensemble", "Exponential Smoothing", "Seasonal Naive"])
        column = col2.selectbox("Metric to Forecast", ["net_cash_flow", "cash_inflow", "cash_outflow"])
        show_components = st.checkbox("Show ensemble components", value=False, help="See the individual models that make up the ensemble forecast.")
    
    with st.container(border=True):
        forecaster = CashFlowForecaster(monthly_data)
        forecast_map = {
            "Ensemble": forecaster.ensemble_forecast,
            "Exponential Smoothing": forecaster.exponential_smoothing_forecast,
            "Seasonal Naive": forecaster.seasonal_naive_forecast
        }
        forecast = forecast_map[method](column, periods)
        forecast = forecaster.calculate_confidence_intervals(forecast, column)
        
        st.subheader("Forecast Visualization")
        visualizer = CashFlowVisualizer(monthly_data)
        # Pass the checkbox value to the plotting function
        fig = visualizer.plot_forecast_results(forecast, show_ensemble_components=(method == "Ensemble" and show_components))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("What am I seeing?"):
            st.info("""
                - **Blue Line:** Your historical cash flow data.
                - **Red Line:** The model's forecast for future periods.
                - **Shaded Area:** The 95% confidence interval, indicating the range of likely outcomes.
            """)

# == 4. Scenario & Stress Testing Page ==
elif analysis_type == "Scenario & Stress Testing":
    st.header("Scenario & Stress Testing")
    
    with st.container(border=True):
        st.subheader("Configure Scenario Multipliers")
        col1, col2, col3 = st.columns(3)
        pess_factor = col1.slider("Pessimistic (%)", 50, 100, 80) / 100
        opt_factor = col2.slider("Optimistic (%)", 100, 150, 120) / 100
        cons_factor = col3.slider("Conservative (%)", 80, 100, 90) / 100
    
    with st.container(border=True):
        forecaster = CashFlowForecaster(monthly_data)
        base_forecast = forecaster.ensemble_forecast('net_cash_flow', 12)
        scenarios = {'pessimistic': pess_factor, 'optimistic': opt_factor, 'conservative': cons_factor}
        scenario_forecast = forecaster.scenario_analysis(base_forecast.copy(), scenarios)
        
        st.subheader("Scenario Forecast Comparison")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=scenario_forecast['date'], y=scenario_forecast['forecast'], name='Base Forecast', line=dict(color='blue', width=3)))
        colors = {'pessimistic': 'red', 'optimistic': 'green', 'conservative': 'orange'}
        for name, _ in scenarios.items():
            fig.add_trace(go.Scatter(x=scenario_forecast['date'], y=scenario_forecast[f'{name}_forecast'], name=name.capitalize(), line=dict(color=colors[name], dash='dash')))
        fig.update_layout(title='Scenario Comparison', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("What am I seeing?"):
            st.info("""
                This chart compares the base forecast against different "what-if" scenarios. This helps you understand potential risks and opportunities.
            """)
