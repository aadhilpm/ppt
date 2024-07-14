frappe.ui.form.on('Leave Application', {
    from_date: function(frm) {
        calculate_custom_leave_balance(frm);
    },
    validate: function(frm) {
        calculate_custom_leave_balance(frm);
    }
});

function calculate_custom_leave_balance(frm) {
    const from_date = new Date(frm.doc.from_date);
    const current_date = new Date();
    const current_month = current_date.getMonth();
    const current_year = current_date.getFullYear();

    if (from_date.getMonth() === current_month && from_date.getFullYear() === current_year) {
        // If from_date is within the same month
        frm.set_value('custom_leave_balance_from_date', frm.doc.leave_balance);
    } else {
        // If from_date is in a later month
        let earned_leave_factor = 0;
        frappe.db.get_value('Leave Type', { 'name': frm.doc.leave_type }, 'is_earned_leave', (r) => {
            if (r && r.is_earned_leave) {
                frappe.db.get_value('Leave Type', { 'name': frm.doc.leave_type }, 'earned_leave_frequency', (r) => {
                    if (r && r.earned_leave_frequency === 'Monthly') {
                        frappe.db.get_value('Leave Type', { 'name': frm.doc.leave_type }, 'rounding', (r) => {
                            if (r && r.rounding) {
                                earned_leave_factor = r.rounding;
                                const months_difference = (from_date.getFullYear() - current_year) * 12 + (from_date.getMonth() - current_month);
                                const additional_leaves = earned_leave_factor * months_difference;
                                const new_leave_balance = frm.doc.leave_balance + additional_leaves;
                                frm.set_value('custom_leave_balance_from_date', new_leave_balance);
                            }
                        });
                    }
                });
            }
        });
    }
}
