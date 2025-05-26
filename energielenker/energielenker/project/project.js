// Copyright (c) 2025, libracore AG and contributors
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
            },
            {
                'label': 'Material',
                'items': [
                    'Work Order',
                    'Depot',
                ],
                'fieldname': "project"
            }
        ]);
    },
    validate: function(frm) {
        set_main_project_title(frm);
        if (!cur_frm.doc.default_external_rate) {
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "energielenker Settings",
                    "name": "energielenker Settings"
                },
                "callback": function(response) {
                    cur_frm.set_value("default_external_rate", response.message.interner_standardtarif);
                }
            });
        }
        frm.set_value("total_amount", cur_frm.doc.auftragsummen_gesamt);
    },
    onload: function (frm) {
        if (cur_frm.doc.__islocal) {
           cur_frm.set_df_property('project_name','read_only', 0);
        }
        frm.trigger("set_contact_query");
        frm.trigger("render_contact");
        prevent_renaming(frm);
        
        if (!cur_frm.doc.default_external_rate) {
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "energielenker Settings",
                    "name": "energielenker Settings"
                },
                "callback": function(response) {
                    cur_frm.set_value("default_external_rate", response.message.interner_standardtarif);
                }
            });
        }
    },
    refresh: function(frm) {
		if ((frm.doc.__islocal) && (frm.doc.sales_order)) {
            cur_frm.set_value("sales_order", null);
        }
        set_timestamps(frm);
        cur_frm.fields_dict.participants.grid.get_field('participant_contact').get_query = function(doc, cdt, cdn) {
          var child = locals[cdt][cdn];
          return {
            filters: {
              "link_doctype": "Customer",
              "link_name": child.participant
            }
          }
        };
        
        frm.add_custom_button(__("Rename Project"), function() {
            frappe.prompt([
                {'fieldname': 'project_name', 'fieldtype': 'Data', 'label': 'Project Name'}
            ],
            function(values){
                cur_frm.set_value("project_name", values.project_name);
                cur_frm.save();
            },
            'Set New Project Name',
            'Save'
            )
        });
        prevent_renaming(frm);
        
        format_time_trend_field(frm);
        
        filter_address(frm);
        
        //Set "Last valid day" mandatory if project is terminated
        last_valid_day_property(frm);
        
        if ((!frm.doc.__islocal) && (frm.doc.project_template)) {
            load_template(frm);
        }
        
        if (cur_frm.doc.auftragsumme_manuell_festsetzen) {
            cur_frm.set_df_property('auftragsummen_gesamt','read_only', 0);
        } else {
            cur_frm.set_df_property('auftragsummen_gesamt','read_only', '1');
        }
        
        if (cur_frm.doc.einkaufskosten_manuell_festsetzen) {
            cur_frm.set_df_property('summe_einkaufskosten_via_einkaufsrechnung','read_only', 0);
        } else {
            cur_frm.set_df_property('summe_einkaufskosten_via_einkaufsrechnung','read_only', '1');
        }
        
        if (!cur_frm.doc.noch_nicht_abgerechnete_stunden_updated) {
            cur_frm.set_value("noch_nicht_abgerechnete_stunden", cur_frm.doc.zeit_gebucht_ueber_zeiterfassung);
            cur_frm.set_value("noch_nicht_abgerechnete_stunden_updated", 1);
        }
        
        if (cur_frm.doc.__islocal) {
            //Handle is_service_project Check
            handle_service_project_check(frm);
        } else {
            //Handle Ready Only of is_service_project Check
            handle_service_project_check_property(frm);
        }
    },
    auftragsumme_manuell_festsetzen: function(frm) {
        if (cur_frm.doc.auftragsumme_manuell_festsetzen) {
            cur_frm.set_df_property('auftragsummen_gesamt','read_only', 0);
        } else {
            cur_frm.set_df_property('auftragsummen_gesamt','read_only', '1');
        }
    },
    einkaufskosten_manuell_festsetzen: function(frm) {
        if (cur_frm.doc.einkaufskosten_manuell_festsetzen) {
            cur_frm.set_df_property('summe_einkaufskosten_via_einkaufsrechnung','read_only', 0);
        } else {
            cur_frm.set_df_property('summe_einkaufskosten_via_einkaufsrechnung','read_only', '1');
        }
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
    },
    project_template: function(frm) {
        load_template(frm);
    },
    no_end_date: function() {
        cur_frm.set_value("expected_end_date", null);
    },
    terminated: function(frm) {
        last_valid_day_property(frm);
    },
    contract_type: function(frm) {
        //Handle is_service_project Check
        handle_service_project_check(frm);
    },
    is_service_project: function(frm) {
        update_service_orders(frm);
    }
});

frappe.ui.form.on("Payment Forecast", {
    create_invoice: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.call({
            "method": "energielenker.energielenker.project.project.check_order_payment_forecast_errors",
            "args": {
                "order": row.order
            },
            "async": true,
            "callback": function(response) {
                if (response.message.errors > 0){
                    frappe.msgprint(response.message.msg);
                } else {
                    frappe.call({
                        "method": "energielenker.energielenker.project.project.get_order_payment_forecast_details",
                        "args": {
                            "order": row.order,
                            'amount': row.amount
                        },
                        "async": true,
                        "callback": function(response) {
                            var data = response.message;
                            var percent_to_bill = data.percent_to_bill;
                            if (data.percent_already_billed > 0) {
                                var percent_already_billed = data.percent_already_billed
                            } else {
                                var percent_already_billed = 0;
                            }
                            if (percent_already_billed > 0) {
                                var order_amount_total = (data.grand_total / 100) * percent_already_billed;
                                // fallback
                                if (percent_to_bill == 0) {
                                    percent_to_bill = 100 - percent_already_billed;
                                }
                            } else {
                                var order_amount_total = 0.00;
                            }
                            if (percent_already_billed >= 101) {
                                frappe.msgprint("Es wurden bereits 100% dieses Auftrags in Rechnung gestellt.");
                            } else {
                                var orderindexrow = 0;
                                var options;
                                var defaults;
                                
                                // Check if the row you click is the last target order from the table
                                frm.doc.payment_schedule.forEach(function (paymentrow) {
                                    if (paymentrow.order === row.order) {
                                    orderindexrow = paymentrow.idx; 
                                    }
                                });
                                if (row.idx === orderindexrow) {
                                    //Check if the last invoice amount match with the last payment schedule made for the order
                                    frappe.call({
                                        "method": "frappe.client.get",
                                        "args": {
                                            "doctype": "Sales Order",
                                            "name": row.order ,
                                        },
                                        'callback': function (response) {
                                            var payment_schedule = response.message.payment_schedule;
                                            if (payment_schedule) {
                                                if (payment_schedule[payment_schedule.length - 1].payment_amount === row.amount ) {
                                                    options = "Schlussrechnung";
                                                    defaults = "Schlussrechnung";
                                                    options_list(row, percent_to_bill, percent_already_billed, order_amount_total, data, options, defaults)
                                                } else {
                                                    options = "Teilrechnung\nSchlussrechnung";
                                                    defaults = "Teilrechnung";
                                                    options_list(row, percent_to_bill, percent_already_billed, order_amount_total, data, options, defaults)
                                                }
                                            }
                                        }
                                    });
                                } else {
                                    options = "Teilrechnung\nSchlussrechnung";
                                    defaults = "Teilrechnung";
                                    options_list(row, percent_to_bill, percent_already_billed, order_amount_total, data, options, defaults)
                                }
                            }
                        }
                    });
                }
            }
        });
    },
    projektbewertung_ignorieren: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        // Update all the rows containing the same order name with the checkbox changes
        frm.doc.payment_schedule.forEach(order => {
            if (order.order == row.order && order.name != row.name) {
                frappe.model.set_value(order.doctype, order.name, 'projektbewertung_ignorieren', row.projektbewertung_ignorieren);
            }
        });
    },
    rollback_invoice: function(frm, cdt, cdn) {
        frappe.confirm(
            'Achtung Rechnung wird gelöscht - Bitte bestätigen.',
            function(){
                // on yes
                let row = frappe.get_doc(cdt, cdn);
                console.log(row)
                frappe.call({
                    "method": "energielenker.energielenker.project.project.payment_forecast_rollback_invoice",
                    "args": {
                        "so": row.order,
                        'so_ref': row.so_ref,
                        "sinv": row.invoice,
                        "project": row.parent
                    },
                    "async": true,
                    "callback": function(response) {
                        var data = response.message;
                        if (data.status == 200) {
                            cur_frm.reload_doc();
                            if (data.typ == 'Teilrechnung') {
                                frappe.msgprint("Die Teilrechnung wurde zurückgebaut.")
                            } else {
                                frappe.msgprint("Die Schlussrechnung wurde zurückgebaut.")
                            }
                        } else {
                            var msg = get_rollback_error_msg(data.status);
                            frappe.msgprint(`${msg}<br><br>${data.info}`);
                        }
                        console.log(response)
                    }
                });
            },
            function(){
                // on no
            }
        )
    }
});

function get_rollback_error_msg(statuscode) {
    var msg = {
        '301': "Es existiert bereits eine Schlussrechnung.",
        '302': "Die Zahlung zur Teilrechnung konnte nicht storniert werden.",
        '303': "Die Rechnung konnte nicht storniert werden.",
        '304': "Die Rechnung konnte nicht aus der Sales Order entfernt werden.",
        '305': "Die Rechnung konnte nicht aus dem Projekt entfernt werden.",
        "306": "Gutschriften konnten nicht storniert werden",
        "307": "Unbekannter Rechnungstyp (Weder Teil- noch Schlussrechnung)",
        "308": "Zuvor stornierte Teilrechnungs-Zahlungen konnten nicht neu gebucht werden."
    }
    return msg[statuscode]
}

function options_list(row, percent_to_bill, percent_already_billed, order_amount_total, data, options, defaults) {
    console.log(percent_to_bill);
    if (options != "message" ) {
        var d = new frappe.ui.Dialog({
            'fields': [
                {'fieldname': 'section_auftrag', 'label': 'Auftrags Details', 'fieldtype': 'Section Break'},
                {'fieldname': 'order_percent', 'label': 'Zu Verrechnen in Prozent', 'fieldtype': 'Percent', 'default': percent_to_bill, 'read_only': 1},
                {'fieldname': 'order_amount', 'label': 'Zu Verrechnen als Betrag', 'fieldtype': 'Currency', 'default': row.amount, 'read_only': 1},
                {'fieldname': 'cb_1', 'fieldtype': 'Column Break'},
                {'fieldname': 'order_percent_total', 'label': 'Bereits Verrechnet in Prozent', 'fieldtype': 'Percent', 'default': percent_already_billed, 'read_only': 1},
                {'fieldname': 'order_amount_total', 'label': 'Bereits Verrechnet als Betrag', 'fieldtype': 'Currency', 'default': order_amount_total, 'read_only': 1},
                {'fieldname': 'order_amount_grand_total', 'label': 'Gesamtbetrag', 'fieldtype': 'Currency', 'default': data.grand_total, 'read_only': 1},
                {'fieldname': 'section_invoice', 'label': 'Rechnungs Details', 'fieldtype': 'Section Break'},
                {'fieldname': 'invoice_type', 'label': 'Rechnungstyp', 'fieldtype': 'Select', 'options': options, 'reqd': 1, 'default': defaults,
                    'change': function() {
                        if (cur_dialog.fields_dict.invoice_type.value == 'Teilrechnung') {
                            cur_dialog.fields_dict.invoice_percent.df.hidden = 0;
                            cur_dialog.fields_dict.invoice_percent.refresh();
                            cur_dialog.fields_dict.invoice_amount.df.hidden = 0;
                            cur_dialog.fields_dict.invoice_amount.refresh();
                            cur_dialog.fields_dict.invoice_gestaltung.df.hidden = 0;
                            cur_dialog.fields_dict.invoice_gestaltung.refresh();
                        } else {
                            cur_dialog.fields_dict.invoice_percent.toggle();
                            cur_dialog.fields_dict.invoice_amount.toggle();
                            cur_dialog.fields_dict.invoice_gestaltung.toggle();
                        }
                    }
                },
                {'fieldname': 'invoice_gestaltung', 'label': 'Rechnungsgestaltung', 'fieldtype': 'Select', 'options': 'In Prozent\nAls Betrag', 'reqd': 1, 'default': 'In Prozent',
                    'change': function() {
                        if (cur_dialog.fields_dict.invoice_gestaltung.get_value() == 'In Prozent') {
                            cur_dialog.fields_dict.invoice_amount.df.read_only = 1;
                            cur_dialog.fields_dict.invoice_amount.refresh();
                            cur_dialog.fields_dict.invoice_percent.df.read_only = 0;
                            cur_dialog.fields_dict.invoice_percent.refresh();
                        } else {
                            cur_dialog.fields_dict.invoice_amount.df.read_only = 0;
                            cur_dialog.fields_dict.invoice_amount.refresh();
                            cur_dialog.fields_dict.invoice_percent.df.read_only = 1;
                            cur_dialog.fields_dict.invoice_percent.refresh();
                        }
                    }
                },
                {'fieldname': 'invoice_date', 'label': 'Rechnungsdatum', 'fieldtype': 'Date', 'default': frappe.datetime.nowdate(), 'reqd': 1},
                {'fieldname': 'invoice_percent', 'label': 'Prozent (zu Verrechnen)', 'fieldtype': 'Percent', 'default': percent_to_bill, 'precision': 9, 'reqd': 1, 'read_only': 0,
                    'change': function() {
                        if (cur_dialog.fields_dict.invoice_gestaltung.get_value() == 'In Prozent') {
                            if ((d.get_value('invoice_percent') + percent_already_billed) <= 100) {
                                    var new_amount = (d.get_value('order_amount_grand_total') / 100) * d.get_value('invoice_percent');
                                    d.set_value('invoice_amount',  new_amount);
                            } else {
                                frappe.msgprint("Es können total maximal 100% verrechnet werden.");
                                d.set_value('invoice_amount',  row.amount);
                                d.set_value('invoice_percent',  data.percent_to_bill);
                            }
                        }
                    }
                },
                {'fieldname': 'invoice_amount', 'label': 'Betrag (zu Verrechnen)', 'fieldtype': 'Currency', 'default': row.amount, 'read_only': 1,
                    'change': function() {
                        if (cur_dialog.fields_dict.invoice_gestaltung.get_value() == 'Als Betrag') {
                            if ((d.get_value('invoice_amount') + order_amount_total) <= data.grand_total) {
                                    var new_percent = (100 / d.get_value('order_amount_grand_total')) * d.get_value('invoice_amount');
                                    d.set_value('invoice_percent', new_percent);
                            } else {
                                frappe.msgprint("Es können total maximal 100% verrechnet werden.");
                                d.set_value('invoice_amount',  row.amount);
                            }
                        }
                    }
                }
            ],
            primary_action: function(){
                if (d.get_value('invoice_type') == 'Schlussrechnung') {
                    d.hide();
                    frappe.call({
                        "method": "energielenker.energielenker.project.project.make_final_sales_invoice",
                        "args": {
                            "order": row.order,
                            'invoice_date': d.get_value('invoice_date')
                        },
                        "async": false,
                        "callback": function(response) {
                            var invoice_data = response.message;
                            frappe.call({
                                "method": "energielenker.energielenker.project.project.update_payment_scheudle",
                                "args": {
                                    'name': row.name,
                                    'invoice_date': d.get_value('invoice_date'),
                                    'invoice': invoice_data.invoice,
                                    'amount': invoice_data.amount,
                                    'schlussrechnung': 1
                                },
                                "async": false,
                                "callback": function(response) {
                                    setTimeout(function(){
                                        frappe.set_route("Form", "Sales Invoice", invoice_data.invoice);
                                        location.reload();
                                    }, 1000);
                                }
                            });
                        }
                    });
                } else {
                    d.hide();
                    frappe.call({
                        "method": "energielenker.energielenker.project.project.make_sales_invoice",
                        "args": {
                            "order": row.order,
                            'percent': d.get_value('invoice_percent'),
                            'amount': d.get_value('invoice_amount'),
                            'percent_billed': percent_already_billed,
                            'invoice_date': d.get_value('invoice_date'),
                            'invoice_type': d.get_value('invoice_type')
                        },
                        "async": false,
                        "callback": function(response) {
                            frappe.call({
                                "method": "energielenker.energielenker.project.project.update_payment_scheudle",
                                "args": {
                                    'name': row.name,
                                    'invoice_date': d.get_value('invoice_date'),
                                    'invoice': response.message
                                },
                                "async": false,
                                "callback": function(r) {
                                    setTimeout(function(){
                                        frappe.set_route("Form", "Sales Invoice", response.message);
                                        location.reload();
                                    }, 1000);
                                }
                            });
                        }
                    });
                }
            },
            primary_action_label: __('Rechnung erstellen')
        });
        if (percent_to_bill === 0) {
            d.set_value('invoice_percent',  0);
            d.set_value('invoice_amount',  0);
        }
        d.show();
    } else {
        frappe.msgprint("Eine Schlussrechnung für diese Bestellung ist bereits erstellt worden.");
	}
}

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

function load_template(frm) {
    frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Project Template",
            "name": frm.doc.project_template
        },
        "callback": function(response) {
            var template = response.message;
            if (!cur_frm.doc.project_type) {
                cur_frm.set_value("project_type", template.project_type);
            }
            if (!cur_frm.doc.contract_type) {
                cur_frm.set_value("contract_type", template.contract_type);
            }
            if (!cur_frm.doc.cost_center) {
                cur_frm.set_value("cost_center", template.default_cost_center);
            }
        }
    });
}


function prevent_renaming(frm) {
    //prevent renaming of title
    $(".title-text").off("click");
    //remove 'rename' in menu
    $("span[data-label='Rename']").parent().parent().remove();
    $("span[data-label='Umbenennen']").parent().parent().remove();
}

function filter_address(frm) {
    cur_frm.fields_dict['shipping_address'].get_query = function(doc, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
            filters: {
                    "link_name": frm.doc.customer
            }
        }
    }
}


//set the name of the main project in the subprojects 
function set_main_project_title(frm) {
    var subprojects = cur_frm.doc.subprojects || [];    // set to empty list in case this child table is empty
    
    subprojects.forEach(function(entry) {
        frappe.call({
            'method': "frappe.client.set_value",
            'args': {
                'doctype': "Project",
                'name': entry.subproject,
                "fieldname": {
                    "main_project": cur_frm.doc.name
                },
            },
        });
    });
}

function last_valid_day_property(frm) {
    if (frm.doc.terminated) {
        cur_frm.set_df_property("last_valid_day", "reqd", 1);
    } else {
        cur_frm.set_df_property("last_valid_day", "reqd", 0);
        cur_frm.set_value("last_valid_day", null);
    }
}

function handle_service_project_check(frm) {
    if (frm.doc.contract_type && frm.doc.contract_type == "Dienstleistungsvertrag") {
        cur_frm.set_value("is_service_project", 1);
    } else {
        cur_frm.set_value("is_service_project", 0);
    }
}

function handle_service_project_check_property(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.project.project.check_service_project_orders',
        'args': {
            'project': frm.doc.name
        },
        'callback': function(response) {
            if (response.message && response.message.length > 0) {
                cur_frm.set_df_property('is_service_project', 'read_only', 1);
            }
        }
    });
}

function update_service_orders(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.project.project.update_service_orders',
        'args': {
            'project': frm.doc.name,
            'service_check': frm.doc.is_service_project
        }
    });
}
