# analyzer.py
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

class SeasonalAnalyzer:
    def __init__(self, data):
        self.data = data # expects monthly data
        self.decomposition = None
        self.seasonal_stats = None
    
    def decompose_time_series(self, column='net_cash_flow', period=12):
        # Decompose the time series into trend, seasonal, and residual
        if len(self.data) < 2 * period:
            period = max(1, len(self.data) // 2)

        start_date = self.data['year_month'].min().to_timestamp()
        ts = pd.Series(
            self.data[column].values, 
            index=pd.date_range(start=start_date, periods=len(self.data), freq='ME')
        )
        
        self.decomposition = seasonal_decompose(ts, model='additive', period=period)
        return self.decomposition
    
    def analyze_seasonality(self, column='net_cash_flow'):
        # Dig into the seasonal patterns
        if 'month' not in self.data.columns:
            self.data['month'] = pd.to_datetime(self.data['year_month'].astype(str)).dt.month
        
        monthly_stats = self.data.groupby('month')[column].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
        
        overall_mean = self.data[column].mean()
        monthly_stats['seasonal_index'] = monthly_stats['mean'] / overall_mean
        monthly_stats['seasonal_variation'] = ((monthly_stats['mean'] - overall_mean) / overall_mean * 100)
        
        peak_month = monthly_stats.loc[monthly_stats['mean'].idxmax(), 'month']
        trough_month = monthly_stats.loc[monthly_stats['mean'].idxmin(), 'month']
        
        self.seasonal_stats = {
            'monthly_stats': monthly_stats,
            'peak_month': peak_month,
            'trough_month': trough_month,
            'seasonal_range': monthly_stats['mean'].max() - monthly_stats['mean'].min(),
            'coefficient_of_variation': monthly_stats['std'].mean() / monthly_stats['mean'].mean()
        }
        return self.seasonal_stats
    
    def correlation_analysis(self):
        # Check for correlations between key metrics
        numeric_cols = [
            'cash_inflow', 'cash_outflow', 'net_cash_flow', 
            'accounts_receivable', 'accounts_payable', 'dso', 'dpo', 'cash_cycle'
        ]
        
        existing_cols = [col for col in numeric_cols if col in self.data.columns]
        corr_matrix = self.data[existing_cols].corr()
        
        # find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        return corr_matrix, strong_correlations
    
    def trend_analysis(self, column='net_cash_flow'):
        # Analyze the long-term trend
        x = np.arange(len(self.data))
        y = self.data[column].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        start_val = self.data[column].iloc[0]
        end_val = self.data[column].iloc[-1]
        
        total_change = ((end_val - start_val) / abs(start_val)) * 100 if start_val != 0 else np.inf
        monthly_growth = (slope / abs(start_val)) * 100 if start_val != 0 else np.inf

        # adf test for stationarity
        adf_result = adfuller(self.data[column].dropna())
        
        trend_stats = {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'total_change_percent': total_change,
            'is_stationary': adf_result[1] < 0.05,
            'adf_p_value': adf_result[1],
            'monthly_growth_rate_percent': monthly_growth
        }
        return trend_stats
