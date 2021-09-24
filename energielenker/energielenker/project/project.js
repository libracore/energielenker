// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
    setup: function (frm) {
        frm.dashboard.add_transactions([
            {
                'label': 'Sales',
                'items': [
                    'Quotation',
                ],
                'fieldname': "project"
            }
        ]);
    },
    validate: function(frm) {
        frm.set_value("total_amount", cur_frm.doc.total_sales_amount);
    },
    onload: function (frm) {
        frm.trigger("set_contact_query");
        frm.trigger("render_contact");
    },
    refresh: function(frm) {
        cur_frm.fields_dict.participants.grid.get_field('participant_contact').get_query = function(doc, cdt, cdn) {
          var child = locals[cdt][cdn];
          return {
            filters: {
              "link_doctype": "Customer",
              "link_name": child.participant
            }
          }
        };
        
        format_time_trend_field(frm);
    },
    customer: function (frm) {
        frm.set_value("contact", null);
        frm.trigger("set_contact_query");
    },
    contact: function (frm) {
        frm.trigger("render_contact");
    },
    team: function (frm) {
        if (!frm.doc.team) {
            return;
        }
        
        frappe.call({
            method: "energielenker.energielenker.doctype.project_team.project_team.get_members",
            args: {
                "doc": frm.doc.team
            },
            callback: function (r) {
                frm.clear_table('members');

                for (const employee of r.message) {
                    const row = frm.add_child('members');
                    row.employee = employee[0];
                    row.full_name = employee[1];
                }

                frm.refresh_field('members');
                frm.set_value("team", null);
            }
        });
    },
    total_amount: function (frm) {
        if (frm.doc.total_amount) {
            frm.doc.payment_schedule.forEach(row => {
                row.percent = row.amount / frm.doc.total_amount * 100;
            });
            frm.refresh_field("payment_schedule");
        }
    },
    set_contact_query: function (frm) {
        frm.set_query("contact", function () {
            return {
                filters: [
                    ["Dynamic Link", "link_doctype", "=", "Customer"],
                    ["Dynamic Link", "link_name", "=", frm.doc.customer]
                ]
            };
        });
    },
    render_contact: function (frm) {
        if (!frm.doc.contact) {
            $(frm.fields_dict["contact_html"].wrapper).html("")
        } else {
            frappe.call({
                method: "energielenker.energielenker.project.project.get_contact_details",
                args: {
                    "doc": frm.doc.contact
                },
                callback: function (r) {
                    $(frm.fields_dict["contact_html"].wrapper)
                        .html(frappe.render_template("contact_list", r.message))
                        .find(".btn-contact").parent().remove();
                }
            });
        }
    },
    commercial_contact: function(frm) {
        if (!cur_frm.doc.commercial_contact) {
            cur_frm.set_value("commercial_contact_name", '');
        }
    }
});

frappe.ui.form.on("Payment Forecast", {
    amount: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (frm.doc.total_amount) {
            row.percent = row.amount / frm.doc.total_amount * 100;
            frm.refresh_field("payment_schedule");
        }
    },
    percent: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (frm.doc.total_amount) {
            row.amount = row.percent * frm.doc.total_amount / 100;
            frm.refresh_field("payment_schedule");
        }
    },
    create_invoice: function(frm, cdt, cdn) {
        frappe.msgprint("TBD");
    }
});


function format_time_trend_field(frm) {
    var time_trend_field = $('[data-fieldname="voraussichtliche_abweichung"]');
    var value = parseFloat(time_trend_field[0].childNodes[1].childNodes[3].childNodes[3].innerHTML);
    if (value < 0) {
        time_trend_field.css("color","red");
    } else {
        time_trend_field.css("color","green");
    }
    
    var time_trend_field_eur = $('[data-fieldname="voraussichtliche_abweichung_eur"]');
    var value_eur = parseFloat(time_trend_field[0].childNodes[1].childNodes[3].childNodes[3].innerHTML);
    if (value_eur < 0) {
        time_trend_field_eur.css("color","red");
    } else {
        time_trend_field_eur.css("color","green");
    }
}
