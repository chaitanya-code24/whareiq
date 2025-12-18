from src.sql_validator import validate_sql

safe_sql = "SELECT users.email FROM users LIMIT 10"
unsafe_sql_1 = "DELETE FROM users"
unsafe_sql_2 = "SELECT * FROM users; DROP TABLE users"
unsafe_sql_3 = "SELECT * FROM users -- comment"


print("\n✅ TEST 1 (SAFE SQL)")
try:
    validate_sql(safe_sql)
    print("PASSED")
except Exception as e:
    print("FAILED:", e)


print("\n❌ TEST 2 (DELETE)")
try:
    validate_sql(unsafe_sql_1)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)


print("\n❌ TEST 3 (STACKED QUERY)")
try:
    validate_sql(unsafe_sql_2)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)


print("\n❌ TEST 4 (COMMENT INJECTION)")
try:
    validate_sql(unsafe_sql_3)
    print("UNEXPECTED PASS")
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)
