# visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import calendar

class CashFlowVisualizer:
    def __init__(self, data):
        self.data = data # expects monthly data
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def plot_cash_flow_timeline(self, save_path=None):
        # Creates a static plot of the cash flow timeline
        fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        fig.suptitle('Cash Flow Timeline', fontsize=16, fontweight='bold')

        axes[0].plot(self.data['year_month'].astype(str), self.data['cash_inflow'], label='Inflow', color='green', marker='.', linestyle='-')
        axes[0].plot(self.data['year_month'].astype(str), self.data['cash_outflow'], label='Outflow', color='red', marker='.', linestyle='-')
        axes[0].set_title('Cash Inflow vs. Outflow')
        axes[0].set_ylabel('Amount ($)')
        axes[0].legend()
        axes[0].grid(True)

        colors = ['green' if x >= 0 else 'red' for x in self.data['net_cash_flow']]
        axes[1].bar(self.data['year_month'].astype(str), self.data['net_cash_flow'], color=colors, alpha=0.8)
        axes[1].set_title('Net Cash Flow')
        axes[1].set_ylabel('Amount ($)')
        axes[1].axhline(0, color='black', linestyle='--')
        
        plt.xticks(rotation=45)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close(fig)

    def plot_seasonal_patterns(self, save_path=None):
        # Creates static plots for seasonal analysis
        fig, axes = plt.subplots(2, 1, figsize=(12, 12))
        fig.suptitle('Seasonal Patterns', fontsize=16, fontweight='bold')

        sns.boxplot(data=self.data, x='month', y='net_cash_flow', ax=axes[0])
        axes[0].set_title('Net Cash Flow Distribution by Month')
        axes[0].set_xlabel('Month')
        axes[0].set_ylabel('Net Cash Flow ($)')

        corr_cols = ['cash_inflow', 'cash_outflow', 'net_cash_flow', 'dso', 'dpo', 'cash_cycle']
        corr_matrix = self.data[corr_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1], fmt='.2f')
        axes[1].set_title('Correlation Matrix of Key Metrics')

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close(fig)

    def plot_forecast_results(self, forecast_df, show_ensemble_components=False, save_path=None):
        # Interactive forecast plot with plotly
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.data['year_month'].astype(str), y=self.data['net_cash_flow'],
            mode='lines+markers', name='Historical', line=dict(color='royalblue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['forecast'],
            mode='lines+markers', name='Forecast', line=dict(color='crimson', width=3)
        ))
        
        if 'lower_95' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['upper_95'],
                mode='lines', line=dict(width=0), showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['lower_95'],
                mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(255, 0, 0, 0.1)',
                name='95% Confidence'
            ))
        
        # Add traces for individual ensemble models if requested
        if show_ensemble_components and 'ma_forecast' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['ma_forecast'],
                mode='lines', name='Moving Average', line=dict(dash='dot', color='gray')
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['seasonal_forecast'],
                mode='lines', name='Seasonal Naive', line=dict(dash='dot', color='purple')
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].dt.strftime('%Y-%m'), y=forecast_df['es_forecast'],
                mode='lines', name='Exp. Smoothing', line=dict(dash='dot', color='orange')
            ))

        fig.update_layout(title='Cash Flow Forecast', xaxis_title='Date', yaxis_title='Net Cash Flow ($)', hovermode='x unified')
        
        if save_path:
            fig.write_html(save_path)
        
        return fig

    def create_interactive_dashboard(self):
        # The main overview dashboard with a new layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Monthly Net Cash Flow', 'Seasonal Averages', 'Cumulative Net Cash Flow', 'Monthly Distribution'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"colspan": 2}, None]]
        )

        # Monthly Net Cash Flow Bar Chart
        colors = ['green' if x >= 0 else 'red' for x in self.data['net_cash_flow']]
        fig.add_trace(go.Bar(x=self.data['year_month'].astype(str), y=self.data['net_cash_flow'], name='Net Flow', marker_color=colors), row=1, col=1)

        # Seasonal Averages Bar Chart
        monthly_avg = self.data.groupby('month')['net_cash_flow'].mean()
        month_abbrs = [calendar.month_abbr[i] for i in monthly_avg.index]
        fig.add_trace(go.Bar(x=month_abbrs, y=monthly_avg.values, name='Avg Monthly Flow', marker_color='skyblue'), row=1, col=2)

        # Cumulative Net Cash Flow Line Chart
        self.data['cumulative_net_flow'] = self.data['net_cash_flow'].cumsum()
        fig.add_trace(go.Scatter(x=self.data['year_month'].astype(str), y=self.data['cumulative_net_flow'], name='Cumulative Flow', mode='lines+markers', line=dict(color='purple')), row=2, col=1)

        fig.update_layout(height=700, showlegend=False, title_text="Cash Flow Overview Dashboard")
        
        return fig
