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

    def get_gross_margin_trend(self, start_month, end_month):
   
        actuals_filtered = self.actuals_usd[
            (self.actuals_usd['month'] >= start_month) & 
            (self.actuals_usd['month'] <= end_month)
        ]
     
        monthly = actuals_filtered.groupby('month').apply(
            lambda x: pd.Series({
                'revenue': x[x['account_category'] == 'Revenue']['amount_usd'].sum(),
                'cogs': x[x['account_category'] == 'COGS']['amount_usd'].sum()
            })
        ).reset_index()
        
        # Calculating gross margin %
        monthly['gross_margin_pct'] = (
            (monthly['revenue'] - monthly['cogs']) / monthly['revenue'] * 100
        )
        
        return monthly[['month', 'revenue', 'cogs', 'gross_margin_pct']]
    
    def get_opex_breakdown(self, month):
       
        opex_data = self.actuals_usd[
            (self.actuals_usd['month'] == month) & 
            (self.actuals_usd['account_category'].str.startswith('Opex:'))
        ]
        
        breakdown = opex_data.groupby('account_category')['amount_usd'].sum().reset_index()
        breakdown.columns = ['category', 'amount']
        breakdown['category'] = breakdown['category'].str.replace('Opex:', '')
        
        total_opex = breakdown['amount'].sum()
        breakdown['pct_of_total'] = (breakdown['amount'] / total_opex * 100)
        
        return breakdown.sort_values('amount', ascending=False)
    
    def get_ebitda(self, month):
       
        month_data = self.actuals_usd[self.actuals_usd['month'] == month]
        
        revenue = month_data[month_data['account_category'] == 'Revenue']['amount_usd'].sum()
        cogs = month_data[month_data['account_category'] == 'COGS']['amount_usd'].sum()
        opex = month_data[month_data['account_category'].str.startswith('Opex:')]['amount_usd'].sum()
        
        ebitda = revenue - cogs - opex
        ebitda_margin = (ebitda / revenue * 100) if revenue > 0 else 0
        
        return {
            'month': month,
            'revenue': revenue,
            'cogs': cogs,
            'opex': opex,
            'ebitda': ebitda,
            'ebitda_margin_pct': ebitda_margin
        }
    
    def get_cash_runway(self):
       
       
        latest_cash = self.cash.sort_values('month', ascending=False).iloc[0]['cash_usd']
        latest_month = self.cash.sort_values('month', ascending=False).iloc[0]['month']
        
       
        all_months = sorted(self.actuals_usd['month'].unique(), reverse=True)
        last_3_months = all_months[:3]
        
        # Calculating monthly burn for each month
        monthly_burn = []
        for month in last_3_months:
            ebitda_data = self.get_ebitda(month)
            burn = -ebitda_data['ebitda']  # Negative EBITDA = cash burn
            monthly_burn.append(burn)
        
        avg_monthly_burn = sum(monthly_burn) / len(monthly_burn)
        
        # Calculating runway in months
        runway_months = latest_cash / avg_monthly_burn if avg_monthly_burn > 0 else float('inf')
        
        return {
            'current_cash': latest_cash,
            'latest_month': latest_month,
            'avg_monthly_burn': avg_monthly_burn,
            'runway_months': runway_months,
            'last_3_months_burn': monthly_burn
        }