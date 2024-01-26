try {
    cur_frm.dashboard.add_transactions([
        {
            'label': 'Timesheet',
            'items': ['Timesheet']
        }
    ]);
} catch { /*do nothing for older versions */ }

frappe.ui.form.on('Issue', {
    refresh: function(frm) {
           set_timestamps(frm);
           cur_frm.fields_dict['address'].get_query = function(doc, cdt, cdn) {
                var d = locals[cdt][cdn];
                return {
                    filters: {
                        "link_name": frm.doc.customer
                    }
               }
           }
    },
    validate: function(frm) {
        if (cur_frm.doc.status == 'Replied') {
            cur_frm.set_value("status", 'Warte auf Rückantwort');
        }
    },
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
    },
    address: function(frm) {
        if (frm.doc.address) {
            console.log("address", frm.doc.address)
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Address",
                    'name': frm.doc.address
                },
                'callback': function(response) {
                    var addrss_links = response.message.links;
                    for (var i = 0; i < addrss_links.length; i++) {
                        if (addrss_links[i].link_doctype == "Customer") {
                            cur_frm.set_value('customer', addrss_links[i].link_name);
                        }
                    }
                }
            });
        }
    },
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
    },
    issue_type: function(frm) {
        if (cur_frm.doc.issue_type == "Reklamation") {
			
            frm.set_df_property("reklamationsverfolgung", "reqd", 1);
        } else {
			cur_frm.set_value("reklamationsverfolgung", "");
		}
    },
})


// Change the timeline specification, from "X days ago" to the exact date and time
function set_timestamps(frm){
    setTimeout(function() {
        // mark navbar
        var timestamps = document.getElementsByClassName("frappe-timestamp");
        for (var i = 0; i < timestamps.length; i++) {
            timestamps[i].innerHTML = timestamps[i].title
        }
    }, 1000);
}
