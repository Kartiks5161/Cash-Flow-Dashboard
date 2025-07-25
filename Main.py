# main.py

# python data_maker.py
# python Main.py
# streamlit run dash_board/Main_Dashboard.py 

import pandas as pd
import numpy as np
import os
import sys

# Add src directory to path to find modules
sys.path.append('src')

from data_processor import DataProcessor
from analyzer import SeasonalAnalyzer
from forecaster import CashFlowForecaster
from visualizer import CashFlowVisualizer

def main():
    print("Cash Flow Seasonality Optimizer")
    print("=" * 40)
    
    # Create output directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')
        print("Created 'output' directory.")
    
    # Load and process data
    processor = DataProcessor('data/sample_data.csv')
    processor.load_data()
    processor.clean_data()
    monthly_data = processor.aggregate_monthly()
    monthly_data = processor.calculate_kpis()
    
    print(f"Processed {len(monthly_data)} months of data")
    
    # Seasonal analysis
    analyzer = SeasonalAnalyzer(monthly_data)
    seasonal_stats = analyzer.analyze_seasonality()
    
    # Trend analysis
    trend_stats = analyzer.trend_analysis()
    
    # Forecasting
    forecaster = CashFlowForecaster(monthly_data)
    ensemble_forecast = forecaster.ensemble_forecast(periods=6)
    ensemble_forecast = forecaster.calculate_confidence_intervals(ensemble_forecast)
    
    # Visualizations
    visualizer = CashFlowVisualizer(monthly_data)
    
    visualizer.plot_cash_flow_timeline(save_path='output/cash_flow_timeline.png')
    visualizer.plot_seasonal_patterns(save_path='output/seasonal_patterns.png')
    
    # Save interactive plots
    dashboard_fig = visualizer.create_interactive_dashboard()
    dashboard_fig.write_html('output/interactive_dashboard.html')
    forecast_fig = visualizer.plot_forecast_results(ensemble_forecast)
    forecast_fig.write_html('output/forecast_results.html')
    
    ensemble_forecast.to_csv('output/forecast_results.csv', index=False)
    seasonal_stats['monthly_stats'].to_csv('output/seasonal_stats.csv', index=False)
    monthly_data.to_csv('output/processed_monthly_data.csv', index=False)
    
    print("\nAnalysis complete!")
    print("Check the 'output' folder for results.")
    
    negative_months = len(ensemble_forecast[ensemble_forecast['forecast'] < 0])
    if negative_months > 0:
        print(f"\n⚠️  WARNING: {negative_months} months with negative cash flow forecast")
    else:
        print(f"\n✅ All forecast periods show positive cash flow")

if __name__ == "__main__":
    main()
