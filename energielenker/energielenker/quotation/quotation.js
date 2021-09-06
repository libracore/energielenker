frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
       setTimeout(function(){ 
        cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
            function() {                                                                      
            return {
                    query: "energielenker.energielenker.item.item.item_query",
					filters: {'is_sales_item': 1}
                }
            }
        }, 1000);
    },
    party_name: function(frm) {
        if (cur_frm.doc.quotation_to == 'Customer') {
            setTimeout(function(){ shipping_address_query(frm); }, 500);
        }
    }
})

frappe.ui.form.on("Quotation Item", "textposition", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
});

frappe.ui.form.on("Quotation Item", "alternative_position", function(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    check_text_and_or_alternativ(item);
});

function check_text_and_or_alternativ(item) {
    if (item.textposition == 1 || item.alternative_position == 1) {
        item.discount_percentage = 100.00;
        cur_frm.refresh_field('items');
    } else {
        item.discount_percentage = 0.00;
        item.discount_amount = 0.00;
        cur_frm.refresh_field('items');
    }
}

function shipping_address_query(frm) {
    cur_frm.fields_dict['shipping_address_name'].get_query = function(doc) {
        return {
            query: 'frappe.contacts.doctype.address.address.address_query',
            filters: {
                'link_doctype': cur_frm.doc.quotation_to,
                'link_name': cur_frm.doc.party_name,
                'produktionsstandort': 1
            }
        }
    };
}
