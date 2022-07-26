// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seriennummer energielenker', {
    refresh: function(frm) {
        cur_frm.fields_dict['lieferdokumententyp'].get_query = function(doc) {
             return {
                 filters: {
                     "name": ['in',['Sales Invoice','Delivery Note']]
                 }
             }
        }
    },
    lieferdokumentennummer: function(frm) {
        if (cur_frm.doc.lieferdokumentennummer) {
            if (cur_frm.doc.lieferdokumententyp == 'Delivery Note') {
                frappe.call({
                    'method': "frappe.client.get",
                    'args': {
                        'doctype': "Delivery Note",
                        'name': cur_frm.doc.lieferdokumentennummer
                    },
                    'callback': function(response) {
                        var lieferdokument = response.message;

                        if (lieferdokument) {
                            cur_frm.set_value('liefertermin', lieferdokument.posting_date);
                            cur_frm.set_value('lieferung_zeitpunkt', lieferdokument.posting_time);
                            cur_frm.set_value('customer', lieferdokument.customer);
                            cur_frm.set_value('kundenname', lieferdokument.customer_name);
                        }
                    }
                });
            }
        } else {
            cur_frm.set_value('liefertermin', null);
            cur_frm.set_value('lieferung_zeitpunkt', null);
            cur_frm.set_value('customer', null);
            cur_frm.set_value('kundenname', null);
        }
    }
});
