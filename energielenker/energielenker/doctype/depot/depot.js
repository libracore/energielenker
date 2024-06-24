// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

var lets_routing = false;

frappe.ui.form.on('Depot', {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            set_default_warehouse(frm);
            cur_frm.fields_dict['sales_order'].get_query = function(doc) {
                if (doc.project) {
                     return {
                         filters: {
                             "project_clone": doc.project
                         }
                     }
                }
            };
        } else {
           frm.add_custom_button(__("Öffne Verarbeitung"), function() {
                window.open(`/desk?depot=${cur_frm.doc.name}#depot-verarbeitung`);
            });
            frm.add_custom_button(__("Get Items"), function() {
                get_so_items(frm);
            });
            frm.add_custom_button(__("Book back items"), function() {
                book_back_items(frm);
            });
            frm.add_custom_button(__("Write off items"), function() {
                write_off_items(frm);
            });
            frm.add_custom_button(__("Etikette erstellen"), function() {
                frappe.prompt([
                    {'fieldname': 'label_printer', 'fieldtype': 'Link', 'label': 'Etikette', 'reqd': 1, 'options': 'Label Printer'}
                ],
                function(values){
                    create_label(frm, values.label_printer);
                },
                'Etiketten Auswahl',
                'Auswählen'
                )
            }).addClass("btn-primary");
            get_items_html(frm);
            
            if (lets_routing) {
                lets_routing = false;
                window.open(`/desk?depot=${cur_frm.doc.name}#depot-verarbeitung`);
            }
            set_read_only(frm);
        }
    },
    sales_order: function(frm) {
        cur_frm.set_value("title", cur_frm.doc.sales_order);
        set_project(frm);
    },
    validate: function(frm) {
        if (frm.doc.__islocal) {
           lets_routing = true;
        }
    },
    project: function(frm) {
        if (cur_frm.doc.project) {
            cur_frm.set_df_property('project', 'read_only', 1);
        }
    },
    status: function(frm) {
        if (frm.doc.status == "Closed") {
            validate_items(frm);
        }
    }
});

function create_label(frm, label_printer) {
    var depot = frm.doc.name;
    var url = `https://erp.energielenker.de/desk?depot=${depot}#depot-verarbeitung`

    frappe.call({
        'method': "energielenker.energielenker.utils.utils.get_label_dimension_settings",
        'args': {
            'label_printer': label_printer
        },
        'async': false,
        'callback': function(response) {
            var dimensions = JSON.parse(response.message);
            console.log(dimensions);
            if (!dimensions[label_printer]) {
                frappe.throw("Für dieses Etikett wurde kein Format hinterlegt.");
            } else {
                var dimensions = dimensions[label_printer];
                var content = `
                    <div style="width: ${dimensions.width}%; position: absolute; height: ${dimensions.height}px;">
                        <div style="position: absolute; z-index: 1;">
                            <div style="padding-top: 10px; font-size: ${dimensions.large_font_size}pt;">
                                <b>${depot}</b>
                            </div>
                        </div>
                        <div style="position: absolute; top: 0px; left: 0px; z-index: 2; min-width: 100%; min-height: 100%;background-image: url('https://data.libracore.ch/phpqrcode/api/qrcode.php?content=${url}&ecc=H&size=6&frame=2'); background-repeat: no-repeat; background-position: right bottom; background-size: 20%;">
                        </div>
                    </div>
                `
                var w = window.open(
                    frappe.urllib.get_full_url("/api/method/erpnextswiss.erpnextswiss.doctype.label_printer.label_printer.download_label"  
                       + "?label_reference=" + encodeURIComponent(label_printer)
                       + "&content=" + encodeURIComponent(content))
               );
               if (!w) {
                   frappe.msgprint(__("Please enable pop-ups")); return;
               }
            }
        }
    });
}

function set_default_warehouse(frm) {
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "energielenker Settings",
            fieldname: "depot_warehouse"
        },
        callback: function(response) {
            var warehouse = response.message['depot_warehouse']
            cur_frm.set_value("to_warehouse", warehouse);
        }
    });
}

function set_project(frm) {
    if (cur_frm.doc.sales_order) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Sales Order",
                name: cur_frm.doc.sales_order
            },
            'async': false,
            callback: function(response) {
                var project = response.message.project_clone
                if (project) {
                    cur_frm.set_value("project", project);
                    cur_frm.set_df_property('project', 'read_only', 1);
                    return project;
                } else {
                    cur_frm.set_value("project", "");
                }
            }
        });
    } else {
        cur_frm.set_value("project", "");
        cur_frm.set_df_property('project', 'read_only', 0);
    }
}

function get_items_html(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.doctype.depot.depot.get_items_html',
        'args': {
            'depot': frm.doc.name,
            'event': "depot"
        },
        'callback': function(response) {
            var html = response.message;
            cur_frm.set_df_property('items','options',html);
        }
    });
}

function set_read_only(frm) {
    cur_frm.set_df_property('project', 'read_only', 1);
    cur_frm.set_df_property('sales_order', 'read_only', 1);
    cur_frm.set_df_property('to_warehouse', 'read_only', 1);
}

function book_back_items(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.doctype.depot.depot.book_back_items',
        'args': {
            'depot': frm.doc.name,
            'warehouse': frm.doc.to_warehouse,
            'project': frm.doc.project
        },
        'callback': function(response) {
            if (response.message) {
                frappe.set_route("Form", "Stock Entry", response.message);
            } else {
                show_alert('Keine Artikel vorhanden', 5, 'red');
            }
        }
    });
}

function write_off_items(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.doctype.depot.depot.write_off_items',
        'args': {
            'depot': frm.doc.name,
            'warehouse': frm.doc.to_warehouse,
            'project': frm.doc.project
        },
        'callback': function(response) {
            if (response.message) {
                frappe.set_route("Form", "Stock Entry", response.message);
            } else {
                show_alert('Keine Artikel vorhanden', 5, 'red');
            }
        }
    });
}

function validate_items(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.doctype.depot.depot.get_items_html',
        'args': {
            'depot': frm.doc.name,
            'event': "close"
        },
        'callback': function(response) {
            var items = response.message;
            for (i=0; i < items.length; i++) {
                if (items[i].balance_qty > 0) {
                    frappe.msgprint("Kommissionierung kann nicht geschlossen werden, da noch Artikel vorhanden sind.", "Fehler");
                    cur_frm.set_value("status", "Open");
                    break;
                }
            }
        }
    });
}
