frappe.ui.form.on('Issue', {
    project: function(frm) {
       if (frm.doc.__islocal && cur_frm.doc.project) {
           frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Project",
                    'name': cur_frm.doc.project
                },
                'callback': function(response) {
                    var project = response.message;
                    cur_frm.set_value('customer', project.customer);
                }
            });
        }
    }
})

frappe.ui.form.on('Issue', {
    refresh: function(frm) {
           cur_frm.fields_dict['address'].get_query = function(doc, cdt, cdn) {
            var d = locals[cdt][cdn];         
            return {
                filters: {
                    "link_name": frm.doc.customer 
                }                      
            }
           }
    }
})

frappe.ui.form.on('Issue', {
    customer_contact: function(frm) {
        if (cur_frm.doc.customer_contact) {
            if (cur_frm.doc.__islocal) {
                frappe.call({
                    'method': "frappe.client.get",
                    'args': {
                        'doctype': "Contact",
                        'name': frm.doc.customer_contact
                    },
                    'callback': function(response) {
                        var contact = response.message;
                        cur_frm.set_value("raised_by", contact.email_ids[0].email_id);
                    }
                });
            }
       }
    }
})
