// Copyright (c) 2024, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Depot', {
    refresh: function(frm) {
        frm.add_custom_button(__("Öffne Verarbeitung"), function() {
            window.open(`/desk?depot=${cur_frm.doc.name}#depot-verarbeitung`);
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
