frappe.listview_settings['ToDo'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/ToDo/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
