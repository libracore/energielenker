// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
    refresh: function(frm) {
        set_timestamps(frm);

        // add label button
        frm.add_custom_button(__("Etikette Gross erstellen"), function() {
            create_label(frm, 'Labels 106x48mm');
        }).addClass("btn-primary");

        // add label button
        frm.add_custom_button(__("Etikette Klein erstellen"), function() {
            create_label(frm, 'Labels 60x30mm');
        }).addClass("btn-primary");
    },
    validate: function(frm) {
        if (frm.doc.__islocal) {
           cur_frm.set_value("naming_series", 'A-.#######');
        }
        if (cur_frm.doc.supplier_items) {
            var supplier_items = cur_frm.doc.supplier_items;
            var suchliste_list = [];
            for (var i=0; i < supplier_items.length; i++) {
                suchliste_list.push(supplier_items[i].supplier_part_no);
            }
            var suchliste = suchliste_list.join();
            frm.set_value("suchfeld", suchliste);
        }
        
        // set default warehouse in read only field (just as info)
        // and fail validation if a default warehouse is necessary but missing
        var default_warehouse_readonly = '';
        var missing_default_warehouse = false;
        if (cur_frm.doc.is_stock_item) {
            if (cur_frm.doc.item_defaults.length > 0) {
                if (cur_frm.doc.item_defaults[0].default_warehouse) {
                    default_warehouse_readonly = cur_frm.doc.item_defaults[0].default_warehouse;
                } else {
                    missing_default_warehouse = true;
                }
            } else {
                missing_default_warehouse = true;
            }
        }
        if (!missing_default_warehouse) {
            frm.set_value("default_warehouse_readonly", default_warehouse_readonly);
        } else {
            frappe.msgprint( __("Bei Lagergeführten Artikeln ist die hinterlegung eines Standard-Lagers Pflicht."), __("Validation") );
            frappe.validated=false;
        }
    },
    item_name: function(frm) {
        if (cur_frm.doc.item_name) {
            cur_frm.set_value("item_purchasing_name", cur_frm.doc.item_name);
        }
    }
});

frappe.ui.form.on('Item Default', {
    navision_konto: function(frm, cdt, cdn) {
        var item_defaults = locals[cdt][cdn];
        if (item_defaults.navision_konto) {
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': "Navision Kontenplan",
                    'name': item_defaults.navision_konto
                },
                'async': false,
                'callback': function(response) {
                    var navision_kontonummer = response.message.konto;
                    item_defaults.navision_kontonummer = navision_kontonummer;
                    cur_frm.refresh_field('item_defaults');
                }
            });
        } else {
            item_defaults.navision_kontonummer = '';
            cur_frm.refresh_field('item_defaults');
        }
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

function create_label(frm, label_printer) {
    // html-content of the label
    var dimensions = get_dimensions(label_printer);
    var content = get_label_content(frm, dimensions);
    var w = window.open(
         frappe.urllib.get_full_url("/api/method/erpnextswiss.erpnextswiss.doctype.label_printer.label_printer.download_label"  
		    + "?label_reference=" + encodeURIComponent(label_printer)
		    + "&content=" + encodeURIComponent(content))
    );
    if (!w) {
        frappe.msgprint(__("Please enable pop-ups")); return;
    }
}

function get_label_content(frm, dimensions) {
    var item_name = frm.doc.item_name;
    if ((item_name != frm.doc.item_purchasing_name)&&(frm.doc.item_purchasing_name)) {
        var item_name = frm.doc.item_purchasing_name;
    }
    var item_code = frm.doc.name;
    var url = `https://erp.energielenker.de/desk#Form/Item/${item_code}`
    var supplier_item_entries = '';
    for (var i=0; i < frm.doc.supplier_items.length; i++) {
        var supplier = frm.doc.supplier_items[i].supplier
        var supplier_part_no = frm.doc.supplier_items[i].supplier_part_no
        supplier_item_entries += `${supplier}: ${supplier_part_no}<br>`
    }
    
    var content = `
        <div style="width: ${dimensions.width}%; position: absolute; height: ${dimensions.height}px;">
            <div style="position: absolute; z-index: 1;">
                <div style="padding-top: 10px; font-size: ${dimensions.large_font_size}pt;">
                    <b>${item_name}</b>
                </div>
                <div style="padding-top: 10px; font-size: ${dimensions.small_font_size}pt;">
                    ${supplier_item_entries}
                </div>
                <div style="padding-top: 10px; font-size: ${dimensions.large_font_size}pt;">
                    <b>${item_code}</b>
                </div>
            </div>
            <div style="position: absolute; top: 0px; left: 0px; z-index: 2; min-width: 100%; min-height: 100%;background-image: url('https://data.libracore.ch/phpqrcode/api/qrcode.php?content=${url}&ecc=H&size=6&frame=2'); background-repeat: no-repeat; background-position: right bottom; background-size: 20%;">
            </div>
        </div>
    `
    return content;
}

function get_dimensions(label_printer) {
    if (label_printer == 'Labels 106x48mm') {
        return {
            width: 98,
            height: 220,
            large_font_size: 14,
            small_font_size: 10
        }
    }

    if (label_printer == 'Labels 60x30mm') {
        return {
            width: 97,
            height: 140,
            large_font_size: 8,
            small_font_size: 6
        }
    }
}