# forecaster.py
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

class CashFlowForecaster:
    def __init__(self, data):
        self.data = data # expects monthly data
        self.forecasts = {}
        self.model_performance = {}
    
    def moving_average_forecast(self, column='net_cash_flow', window=3, periods=6):
        # Simple moving average
        ma = self.data[column].rolling(window=window).mean()
        last_ma = ma.iloc[-1]
        forecast_vals = [last_ma] * periods
        
        last_date = self.data['year_month'].iloc[-1].to_timestamp()
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=periods, freq='ME')
        
        return pd.DataFrame({'date': forecast_dates, 'forecast': forecast_vals, 'method': 'Moving Average'})
    
    def seasonal_naive_forecast(self, column='net_cash_flow', periods=12):
        # Use last year's value for the same month
        if 'month' not in self.data.columns:
            self.data['month'] = self.data['year_month'].dt.month

        last_date = self.data['year_month'].iloc[-1].to_timestamp()
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=periods, freq='ME')
        
        forecast_vals = []
        for date in forecast_dates:
            # This is the corrected line. .to_period() requires 'M'
            last_year_val = self.data[self.data['year_month'] == (date - pd.DateOffset(years=1)).to_period('M')][column]
            if not last_year_val.empty:
                forecast_vals.append(last_year_val.iloc[0])
            else:
                # fallback to month average if no data for last year
                forecast_vals.append(self.data[self.data['month'] == date.month][column].mean())

        return pd.DataFrame({'date': forecast_dates, 'forecast': forecast_vals, 'method': 'Seasonal Naive'})
    
    def exponential_smoothing_forecast(self, column='net_cash_flow', periods=12):
        # Holt-Winters exponential smoothing
        start_date = self.data['year_month'].min().to_timestamp()
        ts = pd.Series(self.data[column].values, index=pd.date_range(start=start_date, periods=len(self.data), freq='ME'))
        
        try:
            model = ExponentialSmoothing(ts, trend='add', seasonal='add', seasonal_periods=12).fit()
            forecast = model.forecast(steps=periods)
            return pd.DataFrame({'date': forecast.index, 'forecast': forecast.values, 'method': 'Exponential Smoothing'})
        except Exception as e:
            print(f"Exponential smoothing failed: {e}. Falling back.")
            return self.seasonal_naive_forecast(column, periods)
    
    def ensemble_forecast(self, column='net_cash_flow', periods=12):
        # Average a few different models together
        ma_f = self.moving_average_forecast(column, periods=periods)
        seasonal_f = self.seasonal_naive_forecast(column, periods=periods)
        es_f = self.exponential_smoothing_forecast(column, periods=periods)
        
        ensemble_vals = (ma_f['forecast'].values + seasonal_f['forecast'].values + es_f['forecast'].values) / 3
        
        return pd.DataFrame({
            'date': ma_f['date'], 'forecast': ensemble_vals, 'method': 'Ensemble',
            'ma_forecast': ma_f['forecast'], 'seasonal_forecast': seasonal_f['forecast'], 'es_forecast': es_f['forecast']
        })
    
    def calculate_confidence_intervals(self, forecast_df, column='net_cash_flow'):
        # Add confidence intervals based on historical std dev
        hist_std = self.data[column].std()
        
        forecast_df['lower_80'] = forecast_df['forecast'] - 1.28 * hist_std
        forecast_df['upper_80'] = forecast_df['forecast'] + 1.28 * hist_std
        forecast_df['lower_95'] = forecast_df['forecast'] - 1.96 * hist_std
        forecast_df['upper_95'] = forecast_df['forecast'] + 1.96 * hist_std
        
        return forecast_df
    
    def scenario_analysis(self, forecast_df, scenarios=None):
        # Apply different multipliers for scenario planning
        if scenarios is None:
            scenarios = {'pessimistic': 0.8, 'optimistic': 1.2, 'conservative': 0.9}
        
        for name, multiplier in scenarios.items():
            forecast_df[f'{name}_forecast'] = forecast_df['forecast'] * multiplier
        
        return forecast_df
