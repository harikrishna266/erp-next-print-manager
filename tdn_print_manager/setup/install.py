import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_custom_fields():
    create_custom_fields({
        "Item": [
            {
                "fieldname": "custom_specifications",
                "label": "Specifications",
                "fieldtype": "Tab Break",
                "insert_after": "description",
            },
            {
                "fieldname": "custom_item_specifications",
                "label": "Item Specifications",
                "fieldtype": "Table",
                "options": "Item Specification",
                "insert_after": "custom_specifications",
            },
        ],
    })
