from measure_auto_mapper import build_measure_map
from dimension_auto_mapper import build_dimension_map

try:
    measures = build_measure_map()
    dimensions = build_dimension_map()

    print("\n✅ MEASURE MAP:\n", measures)
    print("\n✅ DIMENSION MAP:\n", dimensions)

except Exception as e:
    print("❌ Auto-Mapping Failed:", e)
