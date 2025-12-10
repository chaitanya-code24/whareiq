from sql_builder import build_sql

# Matches your current DB: users(email, name)
test_plan = {
    "measures": [],
    "dimensions": ["email", "name"],
    "time_range": None,
    "limit": 10
}

try:
    result = build_sql(test_plan)

    print("\n✅ FINAL SQL BUILD OUTPUT:\n")
    for k, v in result.items():
        print(f"{k}: {v}")

except Exception as e:
    print("❌ SQL build failed:", e)
