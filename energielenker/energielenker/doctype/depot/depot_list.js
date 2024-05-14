frappe.listview_settings['Project'] = {
    onload: function (listview) {
        frappe.route_options = {
            "status": ["=", "Open"]
        };
    }
};
