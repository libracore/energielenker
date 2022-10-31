frappe.listview_settings['Quotation'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Quotation/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
