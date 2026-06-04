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
            {
                "fieldname": "custom_pricing_section",
                "label": "Pricing",
                "fieldtype": "Section Break",
                "insert_after": "custom_item_specifications",
            },
            {
                "fieldname": "custom_pricing_engine",
                "label": "Pricing Engine",
                "fieldtype": "Select",
                "options": "Bundle Based\nArea Based",
                "default": "Bundle Based",
                "insert_after": "custom_pricing_section",
            },
            {
                "fieldname": "custom_area_unit",
                "label": "Area Unit",
                "fieldtype": "Select",
                "options": "Square Foot\nSquare Inch",
                "default": "Square Foot",
                "insert_after": "custom_pricing_engine",
                "depends_on": "eval:doc.custom_pricing_engine=='Area Based'",
            },
            {
                "fieldname": "custom_pricing_matrix",
                "label": "Pricing Matrix",
                "fieldtype": "Long Text",
                "insert_after": "custom_area_unit",
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
