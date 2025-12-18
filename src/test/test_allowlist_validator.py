from src.allowlist_validator import validate_allowlist

# SAFE: only semantic dimensions
safe_sql = "SELECT users.email AS email, users.name AS name FROM users LIMIT 10"

# UNSAFE: technical field
unsafe_sql_1 = "SELECT users.id FROM users"

# UNSAFE: unknown column
unsafe_sql_2 = "SELECT users.password FROM users"

# UNSAFE: unknown table
unsafe_sql_3 = "SELECT payments.amount FROM payments"


print("\n✅ TEST 1 (SAFE SQL)")
try:
    validate_allowlist(safe_sql)
    print("PASSED")
except Exception as e:
    print("FAILED:", e)


print("\n❌ TEST 2 (TECHNICAL FIELD)")
try:
    validate_allowlist(unsafe_sql_1)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)


print("\n❌ TEST 3 (UNKNOWN COLUMN)")
try:
    validate_allowlist(unsafe_sql_2)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)


print("\n❌ TEST 4 (UNKNOWN TABLE)")
try:
    validate_allowlist(unsafe_sql_3)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)
