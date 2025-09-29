from agent.data_loader import FinanceDataLoader
from agent.tools import FinanceTools

# Loading data
loader = FinanceDataLoader()
data = loader.load_all_data()

print("Data loaded successfully!\n")


tools = FinanceTools(data)


result = tools.get_revenue_vs_budget('2025-06')

print("Revenue for June 2025:")
print(f"  Actual: ${result['actual']:,.0f}")
print(f"  Budget: ${result['budget']:,.0f}")
print(f"  Variance: ${result['variance']:,.0f} ({result['variance_pct']:.1f}%)")