from src.schema_reader import load_physical_schema

try:
    schema = load_physical_schema()
    print("✅ Physical Schema Loaded Successfully:\n")

    for table, meta in schema.items():
        print(f"TABLE: {table}")
        print("  Columns:", meta["columns"])
        print("  Primary Key:", meta["primary_key"])
        print("  Foreign Keys:", meta["foreign_keys"])
        print("-" * 50)

except Exception as e:
    print("❌ Schema load failed:", e)
