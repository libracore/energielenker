frappe.listview_settings['Timesheet'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Timesheet/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    }
};
