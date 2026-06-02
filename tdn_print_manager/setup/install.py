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
        "Quotation Item": [
            {
                "fieldname": "custom_item_specifications_section",
                "label": "Specifications",
                "fieldtype": "Section Break",
                "insert_after": "image_view",
            },
            {
                "fieldname": "custom_item_specifications",
                "label": "Item Specifications",
                "fieldtype": "Table",
                "options": "Quotation Item Specification",
                "insert_after": "custom_item_specifications_section",
            },
        ],
    })
