frappe.listview_settings['Sales Order'] = {
    onload: function(listview) {
		var pg_button = document.getElementById('page-List/Sales Order/List').getElementsByClassName("btn-paging")[2];
		pg_button.click();
    },
};
