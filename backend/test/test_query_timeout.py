from src.query_timeout import execute_with_timeout

# Fast query (should succeed)
print("\n✅ TEST 1 (FAST QUERY)")
try:
    rows = execute_with_timeout("SELECT 1", timeout_ms=1000)
    print("PASSED:", rows)
except Exception as e:
    print("FAILED:", e)

# Slow query (should be canceled)
print("\n❌ TEST 2 (SLOW QUERY)")
try:
    rows = execute_with_timeout("SELECT pg_sleep(3)", timeout_ms=1000)
    print("UNEXPECTED PASS:", rows)
except Exception as e:
    print("BLOCKED AS EXPECTED:", e)
