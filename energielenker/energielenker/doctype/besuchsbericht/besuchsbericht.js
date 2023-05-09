// Copyright (c) 2023, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Besuchsbericht', {
    refresh: function(frm) {
        if (cur_frm.doc.customer) {
            cur_frm.fields_dict['contact'].get_query = function(doc) {
              return {
                filters: {
                  "link_doctype": "Customer",
                  "link_name": cur_frm.doc.customer
                }
              }
            };
        }
        if (cur_frm.doc.lead) {
            cur_frm.fields_dict['contact'].get_query = function(doc) {
              return {
                filters: {
                  "link_doctype": "Lead",
                  "link_name": cur_frm.doc.lead
                }
              }
            };
        }
    },
    customer: function(frm) {
        if (cur_frm.doc.customer) {
            cur_frm.fields_dict['contact'].get_query = function(doc) {
              return {
                filters: {
                  "link_doctype": "Customer",
                  "link_name": cur_frm.doc.customer
                }
              }
            };
            frappe.call({
                method: 'set_status',
                doc: cur_frm.doc,
                callback: function(response) {
                   cur_frm.set_value("status", response.message);
                }
            });
        }
    },
    lead: function(frm) {
        if (cur_frm.doc.lead) {
            cur_frm.fields_dict['contact'].get_query = function(doc) {
              return {
                filters: {
                  "link_doctype": "Lead",
                  "link_name": cur_frm.doc.lead
                }
              }
            };
            frappe.call({
                method: 'set_status',
                doc: cur_frm.doc,
                callback: function(response) {
                   cur_frm.set_value("status", response.message);
                }
            });
        }
    }
});
