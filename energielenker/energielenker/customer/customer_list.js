frappe.listview_settings['Customer'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Customer/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
