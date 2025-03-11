frappe.listview_settings['Lead'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Lead/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
