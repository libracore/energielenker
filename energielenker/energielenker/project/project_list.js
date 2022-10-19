frappe.listview_settings['Project'] = {
    add_fields: ["status", "priority", "is_active", "percent_complete", "expected_end_date", "project_name", "subproject"],
    get_indicator: function(doc) {
        if(doc.status=="Open" && doc.percent_complete) {
            return [__("{0}%", [cint(doc.percent_complete)]), "orange", "percent_complete,>,0|status,=,Open"];
        } else {
            return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
        }
    },
    onload: function (listview) {
        frappe.route_options = {
            "subproject": ["=", "No"],
            "status": ["=", "Open"]
        };
        
        listview.page.add_menu_item( __("Aktualisiere KPI's"), function() {
            frappe.confirm(
                "Wollen Sie die KPI's aller Projekte neu laden?",
                function(){
                    // on yes
                    frappe.call({
                    'method': "energielenker.energielenker.project.project.auto_kpi_refresh",
                    'freeze': true,
                    'freeze_message': "Aktualisiere KPI's...",
                    'callback': function(r){}
                    });
                },
                function(){
                    // on no
                }
            )
        });
    }
};
