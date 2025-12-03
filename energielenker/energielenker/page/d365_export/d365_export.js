// Copyright (c) 2025, libracore AG and contributors
// For license information, please see license.txt

frappe.pages['d365-export'].on_page_load = function(wrapper) {
    var me = this;
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'D365 Export',
        single_column: true
    });
    
    page.set_primary_action('Daten Laden', () => {
        frappe.d365_export.daten_laden(page)
    });
    page.set_secondary_action('Exportieren', () => {
        frappe.d365_export.daten_exportieren(page)
    });
    
    page.main.html(frappe.render_template("d365_export", {}));
    page.search_fields = {};
    
    page.search_fields.date_von = frappe.d365_export.create_date_von(page);
    page.search_fields.date_von.refresh();
    page.search_fields.date_bis = frappe.d365_export.create_date_bis(page);
    page.search_fields.date_bis.refresh();
    page.search_fields.ansicht_auswahl = frappe.d365_export.create_ansicht_auswahl(page);
    page.search_fields.ansicht_auswahl.set_value("SalesHeader");
    page.search_fields.ansicht_auswahl.refresh();
    page.search_fields.resultat_html = frappe.d365_export.create_resultat_html(page);
    page.search_fields.resultat_html.refresh();
}

frappe.d365_export = {
    create_date_von: function(page) {
        var date_von = frappe.ui.form.make_control({
            parent: page.main.find(".datum_von"),
            df: {
                fieldtype: "Date",
                options: "",
                fieldname: "date_von",
                placeholder: "Datum von",
                read_only: 0
            },
            only_input: true,
        });
        return date_von
    },
    create_date_bis: function(page) {
        var date_bis = frappe.ui.form.make_control({
            parent: page.main.find(".datum_bis"),
            df: {
                fieldtype: "Date",
                options: "",
                fieldname: "date_bis",
                placeholder: "Datum bis",
                read_only: 0
            },
            only_input: true,
        });
        return date_bis
    },
    create_ansicht_auswahl: function(page) {
        var ansicht_auswahl = frappe.ui.form.make_control({
            parent: page.main.find(".ansicht-auswahl"),
            df: {
                fieldtype: "Select",
                options: "SalesHeader\nSalesLine",
                fieldname: "ansicht_auswahl",
                read_only: 0,
                change: function() {
                    frappe.d365_export.daten_nachladen(page);
                }
            },
            only_input: true,
        });
        return ansicht_auswahl
    },
    create_resultat_html: function(page) {
        var resultat_html = frappe.ui.form.make_control({
            parent: page.main.find(".resultat-html"),
            df: {
                fieldtype: "HTML",
                options: "",
                fieldname: "resultat_html"
            },
            only_input: true,
        });
        return resultat_html
    },
    daten_laden: function(page) {
        datum_von = page.search_fields.date_von.get_value();
        datum_bis = page.search_fields.date_bis.get_value();
        
        if (datum_von&&datum_bis) {
            console.log("laden....");
            frappe.show_alert("Die Suche wurde gestartet, bitte warten...", 5);
            var search_data = {};
            for (const [ key, value ] of Object.entries(page.search_fields)) {
                if (value.get_value()) {
                    search_data[key] = value.get_value();
                } else {
                    search_data[key] = false;
                }
            }
            frappe.call({
                method: "energielenker.energielenker.page.d365_export.d365_export.get_data",
                args:{
                        'suchparameter': search_data
                },
                freeze: true,
                freeze_message: 'Suche nach Rechnungen...',
                callback: function(r)
                {
                    if (r.message) {
                        page.search_fields.resultat_html.set_value(r.message);
                        frappe.show_alert({message:"Die Suchresultate werden angezeigt.", indicator:'green'}, 5);
                    } else {
                        page.search_fields.resultat_html.set_value("<center><p>Keine Suchresultate vorhanden.</p></center>");
                        frappe.show_alert({message:"Keine Suchresultate vorhanden.", indicator:'orange'}, 5);
                    }
                }
            });
        } else {
            frappe.msgprint("Bitte Von- und Bis-Datum auswählen", "Fehlende Kriterien");
        }
    },
    daten_exportieren: function(page) {
        frappe.confirm(
            'Wollen Sie die Daten exportieren?<br>Dadurch werden die Rechnungen als exportiert markiert.',
            function(){
                // on yes
                datum_von = page.search_fields.date_von.get_value();
                datum_bis = page.search_fields.date_bis.get_value();
                
                if (datum_von&&datum_bis) {
                    frappe.show_alert("Der Export wurde gestartet, bitte warten...", 5);
                    var search_data = {};
                    for (const [ key, value ] of Object.entries(page.search_fields)) {
                        if (value.get_value()) {
                            search_data[key] = value.get_value();
                        } else {
                            search_data[key] = false;
                        }
                    }
                    frappe.call({
                        method: "energielenker.energielenker.page.d365_export.d365_export.get_data",
                        args:{
                                'suchparameter': search_data,
                                'exportieren': 1 
                        },
                        freeze: true,
                        freeze_message: 'Exportiere Rechnungen...',
                        callback: function(r)
                        {
                            if (r.message) {
                                frappe.show_alert({message:"Der Export wurde abgeschlossen.", indicator:'green'}, 5);
                                frappe.set_route('List/File/Home/D365Export');
                            }
                        }
                    });
                } else {
                    frappe.msgprint("Bitte Von- und Bis-Datum auswählen", "Fehlende Kriterien");
                }
            },
            function(){
                // on no
            }
        );
    },
    daten_nachladen: function(page) {
        datum_von = page.search_fields.date_von.get_value();
        datum_bis = page.search_fields.date_bis.get_value();
        
        if (datum_von&&datum_bis) {
            frappe.d365_export.daten_laden(page)
        }
    }
}
