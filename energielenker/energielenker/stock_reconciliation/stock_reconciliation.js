frappe.ui.form.on("Stock Reconciliation", {
    refresh: function(frm) {
        frm.add_custom_button(__("Get Valuation Rate"), function() {
            if (cur_frm.is_dirty()) {
                frappe.msgprint("Bitte speichern Sie den Datensatz zuerst.");
            } else {
                frappe.call({
                    method: 'energielenker.energielenker.stock_reconciliation.stock_reconciliation.get_valuation_rate',
                    args: {
                        stock_rec: cur_frm.doc.name
                    },
                    callback: function(response) {
                        cur_frm.reload_doc()
                    }
                });
            }
        });
    }
});