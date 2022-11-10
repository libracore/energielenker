frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) {
        var pg_button = document.getElementById('page-List/Sales Invoice/List').getElementsByClassName("btn-paging")[2];
        pg_button.click();
    },
    
    add_fields: ["customer", "customer_name", "base_grand_total", "outstanding_amount", "due_date", "company",
        "currency", "is_return"],
    get_indicator: function(doc) {
        var status_color = {
            "Draft": "grey",
            "Unpaid": "orange",
            "Paid": "green",
            "Return": "darkgrey",
            "Credit Note Issued": "darkgrey",
            "Unpaid and Discounted": "orange",
            "Overdue and Discounted": "red",
            "Overdue": "red"

        };
        return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
    },
    right_column: "grand_total"
};
