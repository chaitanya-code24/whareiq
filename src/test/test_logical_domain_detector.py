from src.logical_domain_detector import build_logical_domain_map

try:
    logical_schema = build_logical_domain_map()

    print("\n✅ LOGICAL DOMAIN DETECTION OUTPUT:\n")

    for table, meta in logical_schema.items():
        print(f"TABLE: {table}")
        print(f"  Domain: {meta['table_domain']}")
        print(f"  Dimensions: {meta['dimensions']}")
        print(f"  Metrics: {meta['metrics']}")
        print(f"  Technical Fields: {meta['technical_fields']}")
        print(f"  Ignored Fields: {meta['ignored_fields']}")
        print("-" * 60)

except Exception as e:
    print("❌ Logical Domain Detection Failed:", e)
