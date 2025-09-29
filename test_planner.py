from agent.planner import QueryPlanner

planner = QueryPlanner()

# Test questions
test_questions = [
    "What was June 2025 revenue vs budget?",
    "Show me gross margin trend for the last 3 months",
    "Break down Opex by category for June",
    "What is our cash runway right now?",
    "Show me EBITDA for June 2025",
    "How did we do in April 2025 compared to budget?"
]

print("="*60)
print("INTENT CLASSIFICATION TESTS")
print("="*60)

for question in test_questions:
    result = planner.parse_query(question)
    print(f"\nQuestion: {question}")
    print(f"  Intent: {result['intent']}")
    print(f"  Month: {result['month']}")
    print(f"  Date Range: {result['date_range']}")