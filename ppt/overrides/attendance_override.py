import frappe
from frappe.utils import getdate, nowdate, add_days, format_date
from hrms.hr.doctype.attendance.attendance import Attendance
from frappe import _

def custom_validate_attendance_date(self, *args, **kwargs):
    date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

    # Get today's date
    today = getdate(nowdate())

    # Allow attendance marking for today and the next 3 days
    future_limit_date = add_days(today, 3)

    # Check if attendance date is in the allowed future range
    if (
        self.status != "On Leave"
        and not self.leave_application
        and getdate(self.attendance_date) > future_limit_date
    ):
        frappe.throw(
            _("Attendance can only be marked for today and the next 3 days: {0}").format(
                frappe.bold(format_date(self.attendance_date)),
            )
        )
    elif date_of_joining and getdate(self.attendance_date) < getdate(date_of_joining):
        frappe.throw(
            _("Attendance date {0} cannot be less than employee {1}'s joining date: {2}").format(
                frappe.bold(format_date(self.attendance_date)),
                frappe.bold(self.employee),
                frappe.bold(format_date(date_of_joining)),
            )
        )

# Override the original validate_attendance_date method
Attendance.validate_attendance_date = custom_validate_attendance_date
