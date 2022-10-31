frappe.listview_settings['Delivery Note'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Delivery Note/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
};
