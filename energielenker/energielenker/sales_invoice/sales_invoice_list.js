frappe.listview_settings['Sales Invoice'] = {
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
    right_column: "grand_total",
    onload: function(listview) {
        if (frappe.model.can_print("Sales Invoice")) {
            listview.page.add_actions_menu_item(__("Download individual PDFs"), function() {
                const docs = listview.get_checked_items();
                if (!docs.length) {
                    frappe.msgprint(__("Select atleast 1 record for printing"));
                    return;
                }

                const print_settings = frappe.model.get_doc(":Print Settings", "Print Settings");
                const invalid_docs = docs.some(doc => {
                    return !frappe.user.has_role("Administrator") && (
                        (doc.docstatus === 0 && !cint(print_settings.allow_print_for_draft)) ||
                        (doc.docstatus === 2 && !cint(print_settings.allow_print_for_cancelled))
                    );
                });
                if (invalid_docs) {
                    frappe.msgprint(__("You selected Draft or Cancelled documents"));
                    return;
                }

                const print_formats = frappe.meta.get_print_formats("Sales Invoice");
                const dialog = new frappe.ui.Dialog({
                    title: __("Download individual PDFs"),
                    fields: [{
                        fieldtype: "Select",
                        label: __("Print Format"),
                        fieldname: "print_format",
                        options: print_formats,
                        default: print_formats[0],
                        reqd: 1
                    }, {
                        fieldtype: "Check",
                        label: __("With Letterhead"),
                        fieldname: "with_letterhead",
                        default: cint(print_settings.with_letterhead)
                    }]
                });

                dialog.set_primary_action(__("Download"), async function(args) {
                    if (!args) return;
                    dialog.disable_primary_action();
                    dialog.hide();
                    const failed = [];
                    frappe.dom.freeze(__("Downloading PDFs..."));
                    try {
                        // Generate one PDF at a time to avoid concurrent rendering jobs.
                        for (const doc of docs) {
                            try {
                                const response = await fetch(
                                    "/api/method/frappe.utils.print_format.download_pdf?" +
                                    "doctype=" + encodeURIComponent("Sales Invoice") +
                                    "&name=" + encodeURIComponent(doc.name) +
                                    "&format=" + encodeURIComponent(args.print_format) +
                                    "&no_letterhead=" + (args.with_letterhead ? "0" : "1"),
                                    { credentials: "same-origin" }
                                );
                                if (!response.ok || !(response.headers.get("Content-Type") || "")
                                    .toLowerCase().includes("application/pdf")) {
                                    throw new Error("PDF download failed");
                                }
                                const url = URL.createObjectURL(await response.blob());
                                const link = document.createElement("a");
                                link.href = url;
                                link.download = doc.name.replace(/[/\\ ]/g, "-") + ".pdf";
                                document.body.appendChild(link);
                                link.click();
                                link.remove();
                                // Give the browser time to start reading the download.
                                setTimeout(() => URL.revokeObjectURL(url), 60000);
                            } catch (error) {
                                failed.push(doc.name);
                            }
                        }
                    } finally {
                        frappe.dom.unfreeze();
                    }
                    if (failed.length) {
                        frappe.msgprint(__("Could not download PDFs for the following Sales Invoices: {0}",
                            [failed.map(name => frappe.utils.escape_html(name)).join(", ")]));
                    }
                });
                dialog.show();
            }, false);
        }
    }
};
