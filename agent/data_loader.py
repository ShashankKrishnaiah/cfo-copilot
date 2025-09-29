import pandas as pd
import os

class FinanceDataLoader:
    def __init__(self, fixtures_path='fixtures'):
        self.fixtures_path = fixtures_path
        #loadind data
    def load_all_data(self):
        """Load all data from Excel file"""
        excel_path = os.path.join(self.fixtures_path, 'data.xlsx')
        
        data = {}
        data['actuals'] = pd.read_excel(excel_path, sheet_name='actuals')
        data['budget'] = pd.read_excel(excel_path, sheet_name='budget')
        data['cash'] = pd.read_excel(excel_path, sheet_name='cash')
        data['fx'] = pd.read_excel(excel_path, sheet_name='fx')
        
        return data
    
    def print_data_summary(self, data):
        """Print summary of loaded data"""
        for name, df in data.items():
            print(f"\n{name.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {df.columns.tolist()}")
            if 'month' in df.columns:
                print(f"  Date range: {df['month'].min()} to {df['month'].max()}")