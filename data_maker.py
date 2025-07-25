# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_sample_data(start_date='2020-01-01', end_date='2023-12-31'):
    """Generates a realistic cash flow dataset."""
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    base_flow = []
    for i, date in enumerate(dates):
        # build up the daily flow from different components
        trend = 1000 + (i * 2)
        seasonal = 500 * np.sin(2 * np.pi * date.dayofyear / 365.25 + np.pi/2)
        weekly = -200 if date.weekday() >= 5 else 0 # less activity on weekends
        noise = random.gauss(0, 300)
        
        # add some monthly boosts/dips
        if date.month in [11, 12]:
            monthly_boost = 800
        elif date.month in [1, 2]:
            monthly_boost = -400
        else:
            monthly_boost = 0
        
        daily_flow = trend + seasonal + weekly + noise + monthly_boost
        base_flow.append(daily_flow)
    
    # create the final dataframe
    df = pd.DataFrame({
        'date': dates,
        'cash_inflow': np.maximum(0, base_flow),
        'cash_outflow': np.maximum(0, np.array(base_flow) * 0.8 + np.random.normal(0, 200, len(base_flow))),
        'net_cash_flow': None
    })
    
    df['net_cash_flow'] = df['cash_inflow'] - df['cash_outflow']
    
    # add some other related business metrics
    df['accounts_receivable'] = df['cash_inflow'] * 1.2
    df['accounts_payable'] = df['cash_outflow'] * 33
    df['inventory'] = df['cash_outflow'] * 0.3
    
    return df

def main():
    """Generates and saves the sample data."""
    print("Generating sample data...")
    
    if not os.path.exists('data'):
        os.makedirs('data')

    sample_data = generate_sample_data()
    file_path = 'data/sample_data.csv'
    sample_data.to_csv(file_path, index=False)
    
    print(f"Data saved to '{file_path}'")

if __name__ == '__main__':
    main()
