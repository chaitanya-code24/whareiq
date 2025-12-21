from logical_domain_detector import build_logical_domain_map

# ---------------------------------
# Measure Auto-Mapping
# ---------------------------------

def build_measure_map():
    """
    Automatically map logical measures to physical numeric columns.

    Output Format:
    {
        "table": {
            "logical_metric_name": "physical_column_name"
        }
    }
    """

    logical_schema = build_logical_domain_map()
    measure_map = {}

    for table, meta in logical_schema.items():
        measure_map[table] = {}

        for column in meta["metrics"]:
            # Direct 1-to-1 auto-mapping for V1
            logical_metric = column.lower()
            measure_map[table][logical_metric] = column

    return measure_map
