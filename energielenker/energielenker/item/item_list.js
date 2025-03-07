frappe.listview_settings['Item'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Item/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
