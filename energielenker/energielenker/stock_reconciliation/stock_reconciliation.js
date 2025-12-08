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
        frm.add_custom_button(__("Artikel Nullen"), function() {
            var items = cur_frm.doc.items;
            items.forEach(function(entry) {
                entry.qty = 0;
                if (!entry.valuation_rate) {
                    frappe.call({
                        method: 'energielenker.energielenker.stock_reconciliation.stock_reconciliation.get_single_valuation_rate',
                        args: {
                            item: entry.item_code
                        },
                        callback: function(response) {
                            entry.valuation_rate = response.message;
                            // cur_frm.reload_doc()
                        }
                    });
                }
            });
            
        });
    },
    validate: function(frm) {
        var items = cur_frm.doc.items;
        items.forEach(function(entry) {
            if (!entry.qty) {
                entry.qty = 0;
            }
            if (entry.qty == entry.current_qty) {
                entry.quantity_difference = 0;
                entry.amount_difference = 0;
            }
        });
    }
});