from src.time_filter_resolver import resolve_time_filter

# 1) Plan with NO time_range → should produce no filter
plan_no_time = {
    "measures": [],
    "dimensions": ["email", "name"],
    "time_range": None
}

print("\n✅ TEST 1: No time range\n")
result1 = resolve_time_filter(plan_no_time, base_table="users")
print(result1)


# 2) Plan WITH time_range on a table with no time column
#    This should raise a clear, expected error.

plan_with_time = {
    "measures": [],
    "dimensions": ["email", "name"],
    "time_range": {
        "type": "relative_days",
        "last_n_days": 7
    }
}

print("\n✅ TEST 2: With time range (expected to fail for 'users')\n")

try:
    result2 = resolve_time_filter(plan_with_time, base_table="users")
    print(result2)
except Exception as e:
    print("Expected failure:", e)
