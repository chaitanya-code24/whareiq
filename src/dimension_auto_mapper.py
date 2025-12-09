from logical_domain_detector import build_logical_domain_map

# ---------------------------------
# Dimension Auto-Mapping
# ---------------------------------

def build_dimension_map():
    """
    Automatically map logical dimensions to physical dimension columns.

    Output Format:
    {
        "table": {
            "logical_dimension_name": "physical_column_name"
        }
    }
    """

    logical_schema = build_logical_domain_map()
    dimension_map = {}

    for table, meta in logical_schema.items():
        dimension_map[table] = {}

        for column in meta["dimensions"]:
            logical_dimension = column.lower()
            dimension_map[table][logical_dimension] = column

    return dimension_map
