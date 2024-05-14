frappe.listview_settings['Depot'] = {
    onload: function (listview) {
        frappe.route_options = {
            "status": ["=", "Open"]
        };
    }
};
