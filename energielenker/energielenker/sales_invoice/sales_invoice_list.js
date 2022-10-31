frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Sales Invoice/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
