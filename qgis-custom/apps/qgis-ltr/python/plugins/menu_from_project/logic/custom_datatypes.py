#! python3  # noqa: E265

# Standard library
from collections import namedtuple

# Constants
REGISTERED_PROJECT = namedtuple(
    "RegisteredProject", ["name", "type_storage", "type_menu_location", "uri"]
)

TABLE_COLUMNS_ORDER = namedtuple(
    "ColumnsIndex", ["edit", "name", "type_menu_location", "type_storage", "uri"]
)
