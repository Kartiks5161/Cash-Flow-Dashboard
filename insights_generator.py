import pandas as pd

class InsightsGenerator:
    
    def __init__(self, monthly_data):
        self.data=monthly_data

    def check_dso(self, threshold=60):
        avg_dso=self.data['dso'].mean()

        if avg_dso>threshold:
            return(
                f"**High DSO Alert:** Your average Days Sales Outstanding is **{avg_dso:.0f} days**. "
                f"This indicates it's taking a long time to collect payments from customers. \n\n"
                f"**Recommendation:** Consider tightening credit policies or offering early payment discounts."
            )
        return None
    
    def check_dpo(self, threshold=30):
        avg_dpo= self.data['dpo'].mean()

        if avg_dpo< threshold:
            return (
                f"**Low DPO Observation:** Your average Days Payable Outstanding is **{avg_dpo:.0f} days**. "
                f"This suggests you might be paying suppliers faster than necessary, which can strain cash flow. \n\n"
                f"**Recommendation:** Review payment terms with suppliers to see if you can extend them without harming relationships."
            )
        return None   
    def check_cash_cycle(self, threshold=90):
        """Checks for a long Cash Conversion Cycle."""
        avg_ccc = self.data['cash_cycle'].mean()
        if avg_ccc > threshold:
            return (
                f"**Long Cash Cycle:** Your Cash Conversion Cycle is **{avg_ccc:.0f} days**. "
                f"This is the time it takes to convert your investments in inventory and other resources into cash. A shorter cycle is better. \n\n"
                f"**Recommendation:** Focus on reducing both DSO and inventory days to shorten the cycle."
            )
        return None

    def check_negative_trend(self, consecutive_months=3):
        """Checks for a trend of consecutive negative net cash flow."""
        net_flow = self.data['net_cash_flow']
        # Find consecutive negative periods
        negative_periods = (net_flow < 0).astype(int).groupby((net_flow >= 0).cumsum()).cumsum()
        if negative_periods.max() >= consecutive_months:
            return (
                f"**Negative Trend Warning:** The data shows at least **{consecutive_months} consecutive months** of negative net cash flow. "
                f"This is a significant burn rate that needs attention. \n\n"
                f"**Recommendation:** Immediately review major expenses and revenue streams to identify the cause of the shortfall."
            )
        return None

    def generate_all_insights(self):
        """Runs all checks and returns a list of actionable insights."""
        insights = []
        
        # List of all check methods
        checks = [
            self.check_dso,
            self.check_dpo,
            self.check_cash_cycle,
            self.check_negative_trend,
        ]
        
        for check_func in checks:
            insight = check_func()
            if insight:
                insights.append(insight)
        
        # Provide a positive message if no issues are found
        if not insights:
            insights.append(
                "**Good Financial Health:** Your key cash flow metrics appear to be within healthy ranges. Keep up the good work!"
            )
            
        return insights
