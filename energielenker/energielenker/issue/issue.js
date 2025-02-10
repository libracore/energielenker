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
           // custom mail dialog (prevent duplicate icons on creation)
            if (document.getElementsByClassName("fa-envelope-o").length === 0) {
                cur_frm.page.add_action_icon(__("fa fa-envelope-o"), function() {
                    custom_mail_dialog(frm);
                });
                var target ="span[data-label='" + __("Email") + "']";
                $(target).parent().parent().remove();   // remove Menu > Email
            }
            
            //query to filter contacts
            frm.set_query('contact_customer', function() {
                return {
                    filters: {
                        'link_doctype': 'Customer',
                        'link_name': frm.doc.customer
                    }
                };
            });
            
            //Make Field "Contact Customer" mandatory when User opens the Issue
            if (!frm.doc.__islocal) {
                cur_frm.set_df_property('contact_customer', 'reqd', 1);
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
    before_save: function(frm) {
        send_invoice_notification(frm);
    },
    contact_customer: function(frm) {
        display_contact_information(frm);
    }
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

function custom_mail_dialog(frm) {
    var recipient = cur_frm.doc.raised_by;
    new frappe.erpnextswiss.MailComposer({
        doc: cur_frm.doc,
        frm: cur_frm,
        subject: "Anfrage " + cur_frm.doc.name,
        recipients: recipient,
        //~ cc: cc,
        attach_document_print: false
        //~ txt: get_email_body(frm)
    });
}

function send_invoice_notification(frm) {
    if (frm.doc.zur_berechnung_freigegeben && !frm.doc.berechnung_email_sent) {
        frappe.call({
            'method': 'energielenker.energielenker.issue.issue.send_invoice_notification',
            'args': {
                'issue': frm.doc.name
            },
            'callback': function(response) {
                cur_frm.set_value("berechnung_email_sent", 1);
            }
        });
    }
}

function display_contact_information(frm) {
    if (frm.doc.contact_customer) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Contact",
                'name': frm.doc.contact_customer
            },
            'callback': function(response) {
                let contact_doc = response.message;
                if (contact_doc) {
                    cur_frm.set_value("contact_customer_salutation", contact_doc.salutation);
                    cur_frm.set_value("contact_customer_name", contact_doc.last_name + " " + contact_doc.first_name);
                    cur_frm.set_value("contact_customer_email", contact_doc.email_id);
                }
            }
        });
    } else {
        cur_frm.set_value("contact_customer_salutation", null);
        cur_frm.set_value("contact_customer_name", null);
        cur_frm.set_value("contact_customer_email", null);
    }
}
