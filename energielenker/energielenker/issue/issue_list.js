frappe.listview_settings['Issue'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Issue/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
