# data_processor.py
import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.data = None
        self.monthly_data = None
        self.quarterly_data = None
    
    def load_data(self):
        # Load data from the csv
        if not self.file_path:
            raise ValueError("File path not set.")
        
        self.data = pd.read_csv(self.file_path)
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date').reset_index(drop=True)
        
        print(f"Loaded {len(self.data)} records.")
        return self.data
    
    def clean_data(self):
        # Handle missing values and cap outliers
        if self.data is None:
            raise ValueError("Data not loaded.")
        
        self.data = self.data.dropna()
        
        # cap outliers using iqr
        for col in ['cash_inflow', 'cash_outflow', 'net_cash_flow']:
            Q1 = self.data[col].quantile(0.25)
            Q3 = self.data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            self.data[col] = np.clip(self.data[col], lower, upper)
        
        print("Data cleaned.")
        return self.data
    
    def aggregate_monthly(self):
        # Roll up daily data to monthly summaries
        if self.data is None:
            raise ValueError("Data not loaded.")

        self.data['year_month'] = self.data['date'].dt.to_period('M')
        
        self.monthly_data = self.data.groupby('year_month').agg({
            'cash_inflow': 'sum',
            'cash_outflow': 'sum',
            'net_cash_flow': 'sum',
            'accounts_receivable': 'mean',
            'accounts_payable': 'mean',
            'inventory': 'mean'
        }).reset_index()
        
        self.monthly_data['month'] = self.monthly_data['year_month'].dt.month
        self.monthly_data['year'] = self.monthly_data['year_month'].dt.year
        
        return self.monthly_data
    
    def aggregate_quarterly(self):
        # Roll up daily data to quarterly summaries
        if self.data is None:
            raise ValueError("Data not loaded.")

        self.data['year_quarter'] = self.data['date'].dt.to_period('Q')
        
        self.quarterly_data = self.data.groupby('year_quarter').agg({
            'cash_inflow': 'sum',
            'cash_outflow': 'sum',
            'net_cash_flow': 'sum',
            'accounts_receivable': 'mean',
            'accounts_payable': 'mean',
            'inventory': 'mean'
        }).reset_index()
        
        return self.quarterly_data
    
    def calculate_kpis(self):
        # Calculate standard financial KPIs
        if self.monthly_data is None:
            self.aggregate_monthly()
        
        # dso, dpo, dio, and cash conversion cycle
        self.monthly_data['dso'] = (self.monthly_data['accounts_receivable'] / self.monthly_data['cash_inflow']) * 30
        self.monthly_data['dpo'] = (self.monthly_data['accounts_payable'] / self.monthly_data['cash_outflow']) * 30
        self.monthly_data['dio'] = (self.monthly_data['inventory'] / self.monthly_data['cash_outflow']) * 30
        self.monthly_data['cash_cycle'] = self.monthly_data['dso'] + self.monthly_data['dio'] - self.monthly_data['dpo']
        
        # clean up any inf/-inf values from division by zero
        self.monthly_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.monthly_data.fillna(0, inplace=True)

        return self.monthly_data
