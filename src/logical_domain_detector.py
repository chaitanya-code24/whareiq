from schema_reader import load_physical_schema
import re

# ---------------------------------
# Rule Dictionaries
# ---------------------------------

TECHNICAL_KEY_PATTERNS = ["id", "_id"]

CONTACT_FIELDS = ["email", "phone", "mobile", "contact"]

NAME_FIELDS = ["name", "first_name", "last_name", "username", "full_name"]

LOCATION_FIELDS = ["city", "state", "country", "region", "zipcode", "pincode"]

TIME_FIELDS = ["date", "time", "created_at", "updated_at", "timestamp"]

NUMERIC_METRIC_TYPES = ["integer", "numeric", "double precision", "real", "bigint", "decimal"]

IGNORE_FIELDS = ["password", "hash", "token", "secret"]


# ---------------------------------
# Column Classification Logic
# ---------------------------------

def classify_column(column_name: str, data_type: str, primary_keys: list):
    col = column_name.lower()

    # 1. Ignore sensitive fields
    if any(x in col for x in IGNORE_FIELDS):
        return "ignored"

    # 2. Technical identifiers
    if column_name in primary_keys or any(col.endswith(x) for x in TECHNICAL_KEY_PATTERNS):
        return "technical_key"

    # 3. Contact dimensions
    if any(x in col for x in CONTACT_FIELDS):
        return "contact_dimension"

    # 4. Name dimensions
    if any(x in col for x in NAME_FIELDS):
        return "name_dimension"

    # 5. Location dimensions
    if any(x in col for x in LOCATION_FIELDS):
        return "location_dimension"

    # 6. Time dimensions
    if any(x in col for x in TIME_FIELDS):
        return "time_dimension"

    # 7. Numeric metrics
    if data_type in NUMERIC_METRIC_TYPES:
        return "numeric_metric"

    # 8. Generic grouping dimension
    return "categorical_dimension"


# ---------------------------------
# Table Logical Role Detection
# ---------------------------------

def detect_table_domain(table_name: str):
    table = table_name.lower()

    if table in ["users", "customers", "clients"]:
        return "customer"

    if table in ["orders", "transactions", "sales"]:
        return "transaction"

    if table in ["payments", "revenue", "billing"]:
        return "revenue"

    if table in ["products", "items", "inventory"]:
        return "product"

    return "generic_entity"


# ---------------------------------
# Full Logical Domain Mapping
# ---------------------------------

def build_logical_domain_map():
    """
    Converts physical schema → logical semantic schema
    """

    physical_schema = load_physical_schema()
    logical_schema = {}

    for table, meta in physical_schema.items():
        logical_schema[table] = {
            "table_domain": detect_table_domain(table),
            "dimensions": [],
            "metrics": [],
            "technical_fields": [],
            "ignored_fields": []
        }

        primary_keys = meta["primary_key"]

        for column, dtype in meta["columns"].items():
            classification = classify_column(column, dtype, primary_keys)

            if classification == "technical_key":
                logical_schema[table]["technical_fields"].append(column)

            elif classification == "numeric_metric":
                logical_schema[table]["metrics"].append(column)

            elif classification == "ignored":
                logical_schema[table]["ignored_fields"].append(column)

            else:
                logical_schema[table]["dimensions"].append(column)

    return logical_schema
