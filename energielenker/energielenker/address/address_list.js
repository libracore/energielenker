frappe.listview_settings['Address'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Address/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
