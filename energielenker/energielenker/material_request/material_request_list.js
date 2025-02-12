frappe.listview_settings['Material Request'] = {
    get_indicator: function(doc) {
        if (doc.status== "Stopped") {
            return [__("Stopped"), "red", "status,=," + "Stopped"]
        
        } else if (doc.status== "Partially Ordered") {
            return [__("Partially Ordered"), "yellow", "status,=," + "Partially Ordered"]
        
        } else if (doc.status== "Ordered") {
            return [__("Ordered"), "green", "status,=," + "Ordered"]
        
        } else if (doc.status== "Issued") {
            return [__("Issued"), "green", "status,=," + "Issued"]
        
        } else if (doc.status== "Transferred") {
            return [__("Transferred"), "green", "status,=," + "Transferred"]
        
        } else if (doc.status== "Received") {
            return [__("Received"), "green", "status,=," + "Received"]
        
        } else if (doc.status== "Pending") {
            return [__("Pending"), "grey", "status,=," + "Pending"]
        }
    },
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
