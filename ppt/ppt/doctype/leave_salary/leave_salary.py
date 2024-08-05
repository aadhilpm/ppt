# Copyright (c) 2024, Aadhil and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class LeaveSalary(Document):
    def before_submit(self):
        if not self.journal_entry:
            self.create_journal_entry()

    def on_cancel(self):
        if self.journal_entry:
            self.cancel_journal_entry()

    def create_journal_entry(self):
        # Create Journal Entry
        journal_entry = frappe.get_doc({
            "doctype": "Journal Entry",
            "posting_date": self.posting_date,
            "user_remark": f"Leave Salary for {self.employee}- {self.employee_name} Ref: {self.name}",
            "voucher_type": "Journal Entry",
            "cheque_no":self.name,
            "cheque_date":self.posting_date,
            "accounts": [
                {
                    "account": self.provision_account,
                    "party_type": "Employee",
                    "party": self.employee,
                    "debit_in_account_currency": self.total_leave_salary,
                },
                {
                    "account": self.paid_from,
                    "credit_in_account_currency": self.total_leave_salary,
                }
            ]
        })

        journal_entry.insert()
        journal_entry.submit()
        self.journal_entry = journal_entry.name  # Set journal entry number into self.journal_entry field
        frappe.msgprint(f"Journal Entry created: {journal_entry.name}")

    def cancel_journal_entry(self):
        # Check if a Journal Entry exists
        if self.journal_entry:
            journal_entry = frappe.get_doc("Journal Entry", self.journal_entry)

            # Only cancel if it's already submitted
            if journal_entry.docstatus == 1:
                journal_entry.cancel()

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

