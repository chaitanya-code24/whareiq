from semantic_storage import store_semantic_mappings, load_semantic_mappings

try:
    store_semantic_mappings()
    print("✅ Semantic mappings stored successfully")

    data = load_semantic_mappings()
    print("\n✅ Loaded Semantic Mappings:\n")
    print(data)

except Exception as e:
    print("❌ Semantic storage failed:", e)
