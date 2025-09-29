from agent.data_loader import FinanceDataLoader

# Loading data
loader = FinanceDataLoader()
data = loader.load_all_data()

loader.print_data_summary(data)


print("\n\nACTUALS - First 5 rows:")
print(data['actuals'].head())