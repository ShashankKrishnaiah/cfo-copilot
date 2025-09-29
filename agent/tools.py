import pandas as pd

class FinanceTools:
    def __init__(self, data):
      
        self.actuals = data['actuals']
        self.budget = data['budget']
        self.cash = data['cash']
        self.fx = data['fx']
        
        # Converting everything to USD
        self.actuals_usd = self._convert_to_usd(self.actuals)
        self.budget_usd = self._convert_to_usd(self.budget)
    
    def _convert_to_usd(self, df):
        # Mergeing with FX rates
        df_with_fx = df.merge(
            self.fx[['month', 'currency', 'rate_to_usd']], 
            on=['month', 'currency'], 
            how='left'
        )
        
        # Convertint amount to USD
        df_with_fx['amount_usd'] = df_with_fx['amount'] * df_with_fx['rate_to_usd']
        
        return df_with_fx
    
    def get_revenue_vs_budget(self, month):
        # Filtering for revenue only
        actual_revenue = self.actuals_usd[
            (self.actuals_usd['month'] == month) & 
            (self.actuals_usd['account_category'] == 'Revenue')
        ]['amount_usd'].sum()
        
        budget_revenue = self.budget_usd[
            (self.budget_usd['month'] == month) & 
            (self.budget_usd['account_category'] == 'Revenue')
        ]['amount_usd'].sum()
        
        variance = actual_revenue - budget_revenue
        variance_pct = (variance / budget_revenue * 100) if budget_revenue > 0 else 0
        
        return {
            'month': month,
            'actual': actual_revenue,
            'budget': budget_revenue,
            'variance': variance,
            'variance_pct': variance_pct
        }