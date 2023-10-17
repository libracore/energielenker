# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, get_first_day, get_last_day

@frappe.whitelist()
def get_test_chart():
    return {
        "labels": ["A", "B", "C"],
        "datasets": [{
            "name": "Set 1",
            "values": [1, 2, 3]
        }]
    }

@frappe.whitelist()
def get_leads(gl=False):
    dataset = {
        "labels": [],
        "datasets": []
    }
    user = frappe.session.user
    if "GL" in frappe.get_roles(user):
        gl = True
    
    if not gl:
        user_filter = """ AND `lead_owner` = '{user}'""".format(user=user)
    else:
        user_filter = """ GROUP BY `lead_owner`"""
    
    first_day_of_month = get_first_day(getdate())
    
    if not gl:
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            dataset['labels'].append(ref_start_date.strftime("%B"))
           
            qty = frappe.db.sql("""SELECT
                                        COUNT(`name`) AS `qty`
                                    FROM `tabLead`
                                    WHERE `status` = 'Lead'
                                    AND `creation` BETWEEN '{0}' AND '{1}'
                                    {2}""".format(ref_start_date, ref_end_date, user_filter), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        `lead_owner` AS `lead_owner`
                                    FROM `tabLead`
                                    WHERE `status` = 'Lead'
                                    AND `creation` BETWEEN '{0}' AND '{1}'
                                    {2}""".format(get_first_day(first_day_of_month, d_months=-5), get_last_day(first_day_of_month), user_filter), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        for emp in emp_sets:
            data_subset = {
                "name": frappe.db.get_value("User", emp.lead_owner, "middle_name") or frappe.db.get_value("User", emp.lead_owner, "full_name"),
                "values": []
            }
            for month in range(1, 7):
                m_delta = month - 6
                ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                ref_end_date = get_last_day(ref_start_date)
                qty = frappe.db.sql("""SELECT
                                            COUNT(`name`) AS `qty`
                                        FROM `tabLead`
                                        WHERE `status` = 'Lead'
                                        AND `creation` BETWEEN '{0}' AND '{1}'
                                        AND `lead_owner` = '{2}'""".format(ref_start_date, ref_end_date, emp.lead_owner), as_dict=True)[0].qty
                data_subset['values'].append(qty)
            dataset['datasets'].append(data_subset)
        if not len(emp_sets) > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    return dataset

@frappe.whitelist()
def get_quotations(quotation_status, qty=1):
    dataset = {
        "labels": [],
        "datasets": []
    }
    gl=False
    user = frappe.session.user
    if "GL" in frappe.get_roles(user):
        gl = True
    
    if qty == 1:
        query_selector = """COUNT(`name`) AS `qty`"""
    else:
        query_selector = """SUM(`grand_total`) AS `qty`"""
    
    if not gl:
        user_filter = """ AND (`ansprechpartner` = '{user}' OR `k_ansprechperson` = '{user}')""".format(user=user)
    else:
        user_filter = """ GROUP BY `ansprechpartner`"""
    
    first_day_of_month = get_first_day(getdate())
    
    if not gl:
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            dataset['labels'].append(ref_start_date.strftime("%B"))
           
            qty = frappe.db.sql("""SELECT
                                        {4}
                                    FROM `tabQuotation`
                                    WHERE `status` = '{3}'
                                    AND `creation` BETWEEN '{0}' AND '{1}'
                                    {2}""".format(ref_start_date, ref_end_date, user_filter, quotation_status, query_selector), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty or 0]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        `ansprechpartner` AS `quotation_owner`,
                                        `k_ansprechperson` AS `fallback_owner`
                                    FROM `tabQuotation`
                                    WHERE `status` = '{3}'
                                    AND `creation` BETWEEN '{0}' AND '{1}'
                                    {2}""".format(get_first_day(first_day_of_month, d_months=-5), get_last_day(first_day_of_month), user_filter, quotation_status), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        for emp in emp_sets:
            data_subset = {
                "name": frappe.db.get_value("User", emp.quotation_owner, "middle_name") or frappe.db.get_value("User", emp.fallback_owner, "middle_name") or frappe.db.get_value("User", emp.quotation_owner, "full_name") or frappe.db.get_value("User", emp.fallback_owner, "full_name") or 'N/A',
                "values": []
            }
            for month in range(1, 7):
                m_delta = month - 6
                ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                ref_end_date = get_last_day(ref_start_date)
                qty = frappe.db.sql("""SELECT
                                            {4}
                                        FROM `tabQuotation`
                                        WHERE `status` = '{3}'
                                        AND `creation` BETWEEN '{0}' AND '{1}'
                                        AND (`ansprechpartner` = '{2}' OR `k_ansprechperson` = '{2}')""".format(ref_start_date, ref_end_date, emp.quotation_owner or emp.fallback_owner, quotation_status, query_selector), as_dict=True)[0].qty
                data_subset['values'].append(qty)
            dataset['datasets'].append(data_subset)
        if not len(emp_sets) > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    return dataset

@frappe.whitelist()
def get_sales_orders(qty=1):
    dataset = {
        "labels": [],
        "datasets": []
    }
    gl=False
    user = frappe.session.user
    if "GL" in frappe.get_roles(user):
        gl = True
    else:
        vertriebsgruppe_ma = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_dict=True)
        if len(vertriebsgruppe_ma) > 0:
            vertriebsgruppe = vertriebsgruppe_ma[0].name
        else:
            vertriebsgruppe = 'N/A'
    
    if qty == 1:
        query_selector = """COUNT(`name`) AS `qty`"""
    else:
        query_selector = """SUM(`grand_total`) AS `qty`"""
    
    if not gl:
        user_filter = """ AND (`ansprechpartner` = '{user}' OR `vertriebsgruppe` = '{vertriebsgruppe}')""".format(user=user, vertriebsgruppe=vertriebsgruppe)
    else:
        user_filter = """ GROUP BY `ansprechpartner`"""
    
    first_day_of_month = get_first_day(getdate())
    
    if not gl:
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            dataset['labels'].append(ref_start_date.strftime("%B"))
           
            qty = frappe.db.sql("""SELECT
                                        {query_selector}
                                    FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=ref_start_date, ref_end_date=ref_end_date, user_filter=user_filter, query_selector=query_selector), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty or 0]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        `ansprechpartner` AS `so_owner`,
                                        `vertriebsgruppe` AS `fallback_owner`
                                    FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=get_first_day(first_day_of_month, d_months=-5), ref_end_date=get_last_day(first_day_of_month), user_filter=user_filter), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        for emp in emp_sets:
            data_subset = {
                "name": frappe.db.get_value("User", emp.so_owner, "middle_name") or frappe.db.get_value("User", emp.fallback_owner, "middle_name") or frappe.db.get_value("User", emp.so_owner, "full_name") or frappe.db.get_value("User", emp.fallback_owner, "full_name") or 'N/A',
                "values": []
            }
            for month in range(1, 7):
                m_delta = month - 6
                ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                ref_end_date = get_last_day(ref_start_date)
                qty = frappe.db.sql("""SELECT
                                            {query_selector}
                                        FROM `tabSales Order`
                                        WHERE `docstatus` = 1
                                        AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                        AND (`ansprechpartner` = '{ansprechpartner}' OR `vertriebsgruppe` = '{ansprechpartner}')""".format(ref_start_date=ref_start_date, ref_end_date=ref_end_date, ansprechpartner=emp.so_owner or emp.fallback_owner, query_selector=query_selector), as_dict=True)[0].qty
                data_subset['values'].append(qty)
            dataset['datasets'].append(data_subset)
        if not len(emp_sets) > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    return dataset
