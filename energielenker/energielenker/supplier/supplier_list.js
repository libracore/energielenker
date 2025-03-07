frappe.listview_settings['Supplier'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Supplier/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
