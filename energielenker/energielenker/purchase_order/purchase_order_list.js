frappe.listview_settings['Purchase Order'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Purchase Order/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
