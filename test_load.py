from agent.data_loader import FinanceDataLoader
from agent.tools import FinanceTools

loader = FinanceDataLoader()
data = loader.load_all_data()


tools = FinanceTools(data)

print("="*60)
print("TEST 1: Revenue vs Budget (June 2025)")
print("="*60)
result = tools.get_revenue_vs_budget('2025-06')
print(f"Actual: ${result['actual']:,.0f}")
print(f"Budget: ${result['budget']:,.0f}")
print(f"Variance: ${result['variance']:,.0f} ({result['variance_pct']:.1f}%)")

print("\n" + "="*60)
print("TEST 2: Gross Margin Trend (Apr-Jun 2025)")
print("="*60)
gm_trend = tools.get_gross_margin_trend('2025-04', '2025-06')
print(gm_trend)

print("\n" + "="*60)
print("TEST 3: Opex Breakdown (June 2025)")
print("="*60)
opex = tools.get_opex_breakdown('2025-06')
print(opex)

print("\n" + "="*60)
print("TEST 4: EBITDA (June 2025)")
print("="*60)
ebitda = tools.get_ebitda('2025-06')
print(f"Revenue: ${ebitda['revenue']:,.0f}")
print(f"COGS: ${ebitda['cogs']:,.0f}")
print(f"Opex: ${ebitda['opex']:,.0f}")
print(f"EBITDA: ${ebitda['ebitda']:,.0f} ({ebitda['ebitda_margin_pct']:.1f}%)")

print("\n" + "="*60)
print("TEST 5: Cash Runway")
print("="*60)
runway = tools.get_cash_runway()
print(f"Current Cash: ${runway['current_cash']:,.0f}")
print(f"As of: {runway['latest_month']}")
print(f"Avg Monthly Burn: ${runway['avg_monthly_burn']:,.0f}")
print(f"Runway: {runway['runway_months']:.1f} months")