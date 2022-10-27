frappe.listview_settings['Purchase Receipt'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Purchase Receipt/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
