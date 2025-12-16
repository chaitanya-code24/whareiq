from secure_executor import execute_semantic_query

# Semantic plan matching your current DB
test_plan = {
    "measures": [],
    "dimensions": ["email", "name"],
    "time_range": None,
    "limit": 10
}

try:
    result = execute_semantic_query(test_plan)

    print("\n✅ SECURE EXECUTION OUTPUT:\n")
    print("SQL:", result["sql"])
    print("ROWS:")
    for row in result["rows"]:
        print(row)

except Exception as e:
    print("❌ Secure execution failed:", e)
