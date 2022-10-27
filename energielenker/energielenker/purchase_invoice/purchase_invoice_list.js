frappe.listview_settings['Purchase Invoice'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Purchase Invoice/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
