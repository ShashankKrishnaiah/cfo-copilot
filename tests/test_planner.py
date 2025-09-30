import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.planner import QueryPlanner

@pytest.fixture
def planner():
    return QueryPlanner()

def test_revenue_intent(planner):
    """Test revenue vs budget intent classification"""
    questions = [
        "What was June 2025 revenue vs budget?",
        "How did we do in April 2025 compared to budget?",
        "Show me revenue actual vs budget"
    ]
    
    for question in questions:
        result = planner.classify_intent(question)
        assert result == 'revenue_vs_budget'

def test_gross_margin_intent(planner):
    """Test gross margin intent classification"""
    questions = [
        "Show me gross margin trend",
        "What's the GM trend for last 3 months?"
    ]
    
    for question in questions:
        result = planner.classify_intent(question)
        assert result == 'gross_margin_trend'

def test_opex_intent(planner):
    """Test opex breakdown intent classification"""
    questions = [
        "Break down Opex by category",
        "Show me operating expenses breakdown"
    ]
    
    for question in questions:
        result = planner.classify_intent(question)
        assert result == 'opex_breakdown'

def test_cash_runway_intent(planner):
    """Test cash runway intent classification"""
    questions = [
        "What is our cash runway?",
        "How long will our cash last?"
    ]
    
    for question in questions:
        result = planner.classify_intent(question)
        assert result == 'cash_runway'

def test_month_extraction(planner):
    """Test month extraction from questions"""
    test_cases = [
        ("What was June 2025 revenue?", "2025-06"),
        ("Show me April 2025 data", "2025-04"),
        ("December 2024 performance", "2024-12")
    ]
    
    for question, expected_month in test_cases:
        result = planner.extract_month(question)
        assert result == expected_month

def test_date_range_extraction(planner):
    """Test date range extraction"""
    result = planner.extract_date_range("Show me last 3 months")
    assert result == ('LAST_N_MONTHS', 3)
    
    result = planner.extract_date_range("Show me last 6 months")
    assert result == ('LAST_N_MONTHS', 6)