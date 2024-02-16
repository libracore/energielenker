frappe.listview_settings['Material Request'] = {
    onload: function(listview) {
        listview.page.add_menu_item( __("Autocreate Material Request"), function() {
          autocreate_material_requests();
        });  
    }
};

function autocreate_material_requests() {
    frappe.call({
        'method': 'energielenker.energielenker.utils.utils.reorder_item_wrapper',
    });
}
