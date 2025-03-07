frappe.listview_settings['Stock Entry'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Stock Entry/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
