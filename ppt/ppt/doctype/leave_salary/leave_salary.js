frappe.ui.form.on("Leave Salary", {
    get_latest_salary_details: function (frm) {
        frm.clear_table('leave_salary_details');
        frm.set_value("leave_salary_details", []);
        frappe.call({
            method: 'ppt.ppt.doctype.leave_salary.leave_salary.get_all_current_salary_component_rate',
            args: {
                "employee": frm.doc.employee
            },
            callback: function (r) {
                $.each(r.message || [], function (i, d) {
                    var row = frappe.model.add_child(frm.doc, "Leave Salary Details", "leave_salary_details");
                    row.salary_component = d.salary_component;
                    row.amount = d.current;
                });
                frm.refresh_field("leave_salary_details");
                calculate_totals(frm);
            }
        });
    },
    refresh: function (frm) {
        calculate_totals(frm);
        if (frm.fields_dict.leave_salary_details && frm.fields_dict.leave_salary_details.grid) {
            frm.fields_dict.leave_salary_details.grid.grid_buttons.addClass('hidden');
        }
    },
    leave_payment_days: function (frm) {
        if (frm.doc.leave_payment_days > frm.doc.leave_balance_before_from_date) {
            frappe.msgprint("Leave Payment Days cannot be more than Available Leave Balance");
            frm.set_value('leave_payment_days', 0);
            calculate_totals(frm);
        } else {
            calculate_totals(frm);
        }
    },    
    validate:function (frm) {
        if (frm.doc.docstatus === 0) {
            frm.set_value('journal_entry', '');
        }
    },
    onload: function (frm) {
        if (frm.fields_dict.leave_salary_details && frm.fields_dict.leave_salary_details.grid) {
            frm.fields_dict.leave_salary_details.grid.grid_buttons.addClass('hidden');
        }
    }
});

function calculate_totals(frm) {
    let total_salary = 0;
    let total_considered_salary = 0;
    let leave_payment_days = frm.doc.leave_payment_days|| 0;

    frm.doc.leave_salary_details.forEach(row => {
        total_salary += row.amount || 0;

        if (row.leave_salary_calculation == 1) {
            total_considered_salary += row.amount || 0;
        }
    });

    let per_day_salary = total_considered_salary / 30;
    let total_leave_salary = per_day_salary * leave_payment_days;

    frm.set_value('total_salary', total_salary);
    frm.set_value('total_considered_salary', total_considered_salary);
    frm.set_value('per_day_salary', per_day_salary);
    frm.set_value('total_leave_salary', total_leave_salary);
}

frappe.ui.form.on("Leave Salary Details", {
    salary_component: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.call({
            method: 'ppt.ppt.doctype.leave_salary.leave_salary.get_current_salary_component_rate',
            args: {
                "employee": frm.doc.employee,
                "salary_component": row.salary_component
            },
            callback: function (r) {
                frappe.model.set_value(cdt, cdn, "amount", r.message);
                calculate_totals(frm);
            }
        });
    },
    amount: function (frm, cdt, cdn) {
        calculate_totals(frm);
    },
    leave_salary_calculation: function (frm, cdt, cdn) {
        calculate_totals(frm);
    }
});
