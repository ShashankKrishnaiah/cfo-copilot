import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.data_loader import FinanceDataLoader
from agent.tools import FinanceTools

@pytest.fixture
def finance_tools():
    """Load data and create FinanceTools instance"""
    loader = FinanceDataLoader()
    data = loader.load_all_data()
    return FinanceTools(data)

def test_revenue_vs_budget(finance_tools):
    """Test revenue vs budget calculation"""
    result = finance_tools.get_revenue_vs_budget('2025-06')
    
    assert result['month'] == '2025-06'
    assert result['actual'] > 0
    assert result['budget'] > 0
    assert 'variance' in result
    assert 'variance_pct' in result

def test_gross_margin_trend(finance_tools):
    """Test gross margin trend calculation"""
    result = finance_tools.get_gross_margin_trend('2025-04', '2025-06')
    
    assert len(result) == 3  # 3 months
    assert 'gross_margin_pct' in result.columns
    assert result['gross_margin_pct'].mean() > 0
    assert result['gross_margin_pct'].mean() < 100

def test_opex_breakdown(finance_tools):
    """Test opex breakdown"""
    result = finance_tools.get_opex_breakdown('2025-06')
    
    assert len(result) > 0
    assert 'category' in result.columns
    assert 'amount' in result.columns
    assert result['amount'].sum() > 0

def test_ebitda(finance_tools):
    """Test EBITDA calculation"""
    result = finance_tools.get_ebitda('2025-06')
    
    assert result['month'] == '2025-06'
    assert result['revenue'] > 0
    assert result['cogs'] > 0
    assert result['opex'] > 0
    assert 'ebitda' in result
    assert 'ebitda_margin_pct' in result

def test_cash_runway(finance_tools):
    """Test cash runway calculation"""
    result = finance_tools.get_cash_runway()
    
    assert result['current_cash'] > 0
    assert 'latest_month' in result
    assert 'avg_monthly_burn' in result
    assert 'runway_months' in result

def test_usd_conversion(finance_tools):
    """Test that amounts are properly converted to USD"""
    
    eur_data = finance_tools.actuals[finance_tools.actuals['currency'] == 'EUR']
    if len(eur_data) > 0:
      
        usd_data = finance_tools.actuals_usd[
            (finance_tools.actuals_usd['currency'] == 'EUR') &
            (finance_tools.actuals_usd['month'] == eur_data.iloc[0]['month'])
        ]
        assert len(usd_data) > 0
        assert 'amount_usd' in usd_data.columns