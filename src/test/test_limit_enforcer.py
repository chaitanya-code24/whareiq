from src.limit_enforcer import enforce_limit

sql_no_limit = "SELECT users.email FROM users"
sql_small_limit = "SELECT users.email FROM users LIMIT 50"
sql_big_limit = "SELECT users.email FROM users LIMIT 5000"

print("\n✅ TEST 1 (NO LIMIT)")
print(enforce_limit(sql_no_limit, max_limit=100))

print("\n✅ TEST 2 (SMALL LIMIT)")
print(enforce_limit(sql_small_limit, max_limit=100))

print("\n❌ TEST 3 (BIG LIMIT)")
print(enforce_limit(sql_big_limit, max_limit=100))
