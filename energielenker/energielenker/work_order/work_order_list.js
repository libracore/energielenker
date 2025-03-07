frappe.listview_settings['Work Order'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Work Order/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
