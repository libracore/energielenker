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
def get_leads(user_filters=False, gl=False):
    dataset = {
        "labels": [],
        "datasets": []
    }
    colors = []
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
                                    AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=ref_start_date, \
                                                    ref_end_date=ref_end_date, \
                                                    user_filter=user_filter), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        IFNULL(`lead_owner`, 'N/A') AS `lead_owner`
                                    FROM `tabLead`
                                    WHERE `status` = 'Lead'
                                    AND `creation` BETWEEN '{first}' AND '{second}'
                                    {user_filter}""".format(first=get_first_day(first_day_of_month, d_months=-6), \
                                                    second=get_last_day(first_day_of_month), \
                                                    user_filter=user_filter), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        unblocked_qty = 0
        for emp in emp_sets:
            block = False
            if user_filters:
                if user_filters != 'false':
                    if emp.lead_owner not in user_filters:
                        block = True
            if not block:
                unblocked_qty += 1
                if emp.lead_owner != 'N/A':
                    empl_name = frappe.db.get_value("User", emp.lead_owner, "middle_name") or frappe.db.get_value("User", emp.lead_owner, "full_name") or emp.lead_owner
                    color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.lead_owner), as_dict=True)
                    if len(color) > 0:
                        c = color[0].color
                    else:
                        c = '#DFFF00'
                    colors.append(c)
                else:
                    empl_name = 'N/A'
                    user_for_block_check = ''
                    c = '#DFFF00'
                
                data_subset = {
                    "name": empl_name,
                    "values": []
                }
                for month in range(1, 7):
                    m_delta = month - 6
                    ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                    ref_end_date = get_last_day(ref_start_date)
                    
                    if emp.lead_owner != 'N/A':
                        lead_owner_filter = """AND `lead_owner` = '{lead_owner}'""".format(lead_owner=emp.lead_owner)
                    else:
                        lead_owner_filter = """AND `lead_owner` IS NULL"""
                    
                    qty = frappe.db.sql("""SELECT
                                                COUNT(`name`) AS `qty`
                                            FROM `tabLead`
                                            WHERE `status` = 'Lead'
                                            AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            {lead_owner_filter}""".format(ref_start_date=ref_start_date, \
                                                                                ref_end_date=ref_end_date, \
                                                                                lead_owner_filter=lead_owner_filter), as_dict=True)[0].qty
                    data_subset['values'].append(qty)
                dataset['datasets'].append(data_subset)
        if not unblocked_qty > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    # ~ return dataset
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_quotations(quotation_status, qty=1, user_filters=False):
    dataset = {
        "labels": [],
        "datasets": []
    }
    colors = []
    gl=False
    user = frappe.session.user
    if "GL" in frappe.get_roles(user):
        gl = True
    
    if qty == 1:
        query_selector = """COUNT(`name`) AS `qty`"""
    else:
        query_selector = """IFNULL(SUM(`total`), 0) AS `qty`"""
    
    if not gl:
        user_filter = """ AND `ansprechpartner` = '{user}'""".format(user=user)
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
                                    FROM `tabQuotation`
                                    WHERE `status` = '{quotation_status}'
                                    AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=ref_start_date, \
                                                    ref_end_date=ref_end_date, \
                                                    user_filter=user_filter, \
                                                    quotation_status=quotation_status, \
                                                    query_selector=query_selector), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty or 0]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        IFNULL(`ansprechpartner`, 'N/A') AS `quotation_owner`
                                    FROM `tabQuotation`
                                    WHERE `status` = '{quotation_status}'
                                    AND `transaction_date` BETWEEN '{first}' AND '{second}'
                                    {user_filter}""".format(first=get_first_day(first_day_of_month, d_months=-6), \
                                                            second=get_last_day(first_day_of_month), \
                                                            user_filter=user_filter, \
                                                            quotation_status=quotation_status), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        unblocked_qty = 0
        for emp in emp_sets:
            # get empl name
            if emp.quotation_owner and emp.quotation_owner != '' and emp.quotation_owner != 'N/A':
                empl_name = frappe.db.get_value("User", emp.quotation_owner, "middle_name") or frappe.db.get_value("User", emp.quotation_owner, "full_name")
                user_for_block_check = emp.quotation_owner
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.quotation_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
            else:
                empl_name = 'N/A'
                user_for_block_check = ''
                c = '#DFFF00'
            
            block = False
            if user_filters:
                if user_filters != 'false':
                    if user_for_block_check not in user_filters:
                        block = True
            if not block:
                unblocked_qty += 1
                colors.append(c)
                data_subset = {
                    "name":  empl_name,
                    "values": []
                }
                for month in range(1, 7):
                    m_delta = month - 6
                    ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                    ref_end_date = get_last_day(ref_start_date)
                    
                    if emp.quotation_owner != 'N/A':
                        quotation_owner_filter = """AND `ansprechpartner` = '{quotation_owner}'""".format(quotation_owner=emp.quotation_owner)
                    else:
                        quotation_owner_filter = """AND `ansprechpartner` IS NULL"""
                    
                    qty = frappe.db.sql("""SELECT
                                                {query_selector}
                                            FROM `tabQuotation`
                                            WHERE `status` = '{quotation_status}'
                                            AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            {quotation_owner_filter}""".format(ref_start_date=ref_start_date, \
                                                                                    ref_end_date=ref_end_date, \
                                                                                    quotation_owner_filter=quotation_owner_filter, \
                                                                                    quotation_status=quotation_status, \
                                                                                    query_selector=query_selector), as_dict=True)[0].qty
                    data_subset['values'].append(qty)
                dataset['datasets'].append(data_subset)
        if not unblocked_qty > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    # ~ return dataset
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_sales_orders(qty=1, user_filters=False):
    dataset = {
        "labels": [],
        "datasets": []
    }
    colors = []
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
        query_selector = """IFNULL(SUM(`total`), 0) AS `qty`"""
    
    if not gl:
        user_filter = """ AND `ansprechpartner` = '{user}'""".format(user=user, vertriebsgruppe=vertriebsgruppe)
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
                                    AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=ref_start_date, \
                                                            ref_end_date=ref_end_date, \
                                                            user_filter=user_filter, \
                                                            query_selector=query_selector), as_dict=True)[0].qty
            
            dataset['datasets'].append({
                "name": ref_start_date.strftime("%B"),
                "values": [qty or 0]
            })
    else:
        emp_sets = frappe.db.sql("""SELECT
                                        IFNULL(`ansprechpartner`, 'N/A') AS `so_owner`
                                    FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {user_filter}""".format(ref_start_date=get_first_day(first_day_of_month, d_months=-5), \
                                                            ref_end_date=get_last_day(first_day_of_month), \
                                                            user_filter=user_filter), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        unblocked_qty = 0
        for emp in emp_sets:
            if emp.so_owner and emp.so_owner != '' and emp.so_owner != 'N/A':
                emp_name = frappe.db.get_value("User", emp.so_owner, "middle_name") or frappe.db.get_value("User", emp.so_owner, "full_name")
                user_for_block_check = emp.so_owner
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.so_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
            else:
                emp_name = 'N/A'
                user_for_block_check = ''
                c = '#DFFF00'
            
            block = False
            if user_filters:
                if user_filters != 'false':
                    if user_for_block_check not in user_filters:
                        block = True
            if not block:
                unblocked_qty += 1
                colors.append(c)
                data_subset = {
                    "name":  emp_name,
                    "values": []
                }
                for month in range(1, 7):
                    m_delta = month - 6
                    ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                    ref_end_date = get_last_day(ref_start_date)
                    
                    if emp.so_owner != 'N/A':
                        ansprechpartner_filter = """AND `ansprechpartner` = '{so_owner}'""".format(so_owner=emp.so_owner)
                    else:
                        ansprechpartner_filter = """AND `ansprechpartner` IS NULL"""
                    
                    qty = frappe.db.sql("""SELECT
                                                {query_selector}
                                            FROM `tabSales Order`
                                            WHERE `docstatus` = 1
                                            AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            {ansprechpartner_filter}""".format(ref_start_date=ref_start_date, \
                                                                                                    ref_end_date=ref_end_date, \
                                                                                                    ansprechpartner_filter=ansprechpartner_filter, \
                                                                                                    query_selector=query_selector), as_dict=True)[0].qty
                    
                    data_subset['values'].append(qty)
                dataset['datasets'].append(data_subset)
        if not unblocked_qty > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value
