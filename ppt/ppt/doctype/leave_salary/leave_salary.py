# Copyright (c) 2024, Aadhil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeaveSalary(Document):
	pass

@frappe.whitelist()
def get_all_current_salary_component_rate(employee):
    if not employee:
        return []

    salary_component = {
        "base": "Basic",
        "custom_housing": "Housing",
        "custom_transport": "Transportation",
        "custom_others": "Other Allowance",
        "custom_telephone": "Telephone",
    }

    data = []
    for key, value in salary_component.items():
        row = {
            "salary_component": value,
            "current": frappe.db.get_value("Salary Structure Assignment", {
                "employee": employee,
                "docstatus": 1
            }, key, order_by="from_date desc") or 0
        }
        data.append(row)
    return data


@frappe.whitelist()
def get_current_salary_component_rate(employee, salary_component):
    if salary_component == "Basic":
        return frappe.db.get_value("Salary Structure Assignment", {
            "employee": employee,
            "docstatus": 1
        }, "base", order_by="from_date desc")
    else:
        salary_component_abbr =  frappe.db.get_value("Salary Component", {
            "name": salary_component
        }, "salary_component_abbr")
        if salary_component_abbr:
            salary_component_abbr  = salary_component_abbr.lower()
            try:
                return frappe.db.get_value("Salary Structure Assignment", {
                    "employee": employee,
                    "docstatus": 1,
                }, salary_component_abbr, order_by="from_date desc") or 0.0
            except Exception as e:
                return 0.0

