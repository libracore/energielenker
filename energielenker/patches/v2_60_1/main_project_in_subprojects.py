import frappe
from frappe import _

def execute():
    # this will add the main_project to all existing subprojects
    print("Updating Subprojects")
    try:
        subprojects = frappe.db.sql("""SELECT `subproject`, `parent` FROM `tabSubproject`""", as_dict=True)
        loop = 1
        for subproject in subprojects:
            print("Updating {0} of {1}".format(loop, len(subprojects)))
            try:
                subproject_doc = frappe.get_doc("Project", subproject.subproject)
                subproject_doc.main_project = subproject.parent
                subproject_doc.save()
            except Exception as err:
                print("Unable to add the main_project to subproject {0}".format(subproject.subproject))
            loop += 1
    except Exception as err:
        print("Unable to add the main_project to all existing subprojects")
    return
