// Copyright (c) 2021, libracore AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Task", {
    onload: function(frm) {
        fetch_project_from_issue(frm);
    }
});

function fetch_project_from_issue(frm) {
    if (cur_frm.doc.issue) {
        frappe.call({
            'method': "frappe.client.get",
            'args': {
                'doctype': "Issue",
                'name': cur_frm.doc.issue
            },
            'callback': function(response) {
                var issue = response.message;
                cur_frm.set_value('project', issue.project);
            }
        });
    }
}
