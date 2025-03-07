frappe.listview_settings['Contact'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Contact/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
