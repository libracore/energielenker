import frappe
from frappe import _

def execute():
    # this will add the main_project to all existing subprojects
    try:
        subprojects = frappe.db.sql("""SELECT `subproject`, `parent` FROM `tabSubproject`""", as_dict=True)
        for subproject in subprojects:
            try:
                subproject_doc = frappe.get_doc("Project", subproject.subproject)
                project = frappe.get_doc("Project", subproject.parent).project_name
                subproject_doc.main_project = project
                subproject_doc.save()
            except Exception as err:
                print("Unable to add the main_project to subproject {0}".format(subproject.subproject))
    except Exception as err:
        print("Unable to add the main_project to all existing subprojects")
    return
