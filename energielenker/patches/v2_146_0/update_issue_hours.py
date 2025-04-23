import frappe

def execute():
    frappe.reload_doc("Support", "doctype", "Issue")
    
    affected_issues = frappe.db.sql("""
                                    SELECT
                                        `name`
                                    FROM
                                        `tabIssue`""", as_dict=True)
    
    for issue in affected_issues:
        sql_query = """
            SELECT SUM(`hours`) AS `total_hours`
            FROM `tabTimesheet Detail`
            WHERE `issue` = '{issue}'
            AND `docstatus` = 1;""".format(issue=issue.get('name'))
    
        total_hours = frappe.db.sql(sql_query, as_dict=True)

        if len(total_hours) > 0:
            booked_hours = total_hours[0].total_hours
        else:
            booked_hours = 0
        
        if not booked_hours:
            booked_hours = 0
        
        frappe.db.set_value("Issue", issue, "booked_hours", booked_hours)
    
    frappe.db.commit()

    return
