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
                                    {2}""".format(get_first_day(first_day_of_month, d_months=-6), get_last_day(first_day_of_month), user_filter), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        for emp in emp_sets:
            block = False
            if user_filters:
                if user_filters != 'false':
                    if emp.lead_owner not in user_filters:
                        block = True
            if not block:
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.lead_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                colors.append(c)
                data_subset = {
                    "name": frappe.db.get_value("User", emp.lead_owner, "middle_name") or frappe.db.get_value("User", emp.lead_owner, "full_name") or emp.lead_owner or 'n/a',
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
        query_selector = """IFNULL(SUM(`grand_total`), 0) AS `qty`"""
    
    if not gl:
        user_filter = """ AND (`ansprechpartner` = '{user}' OR (
                                `ansprechpartner` IS NULL AND `k_ansprechperson` = '{user}') OR (
                                `ansprechpartner` IS NULL AND `k_ansprechperson` IS NULL AND `owner` = '{user}')
                            )""".format(user=user)
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
                                        `k_ansprechperson` AS `fallback_owner`,
                                        `owner` AS `creator`
                                    FROM `tabQuotation`
                                    WHERE `status` = '{3}'
                                    AND `creation` BETWEEN '{0}' AND '{1}'
                                    {2}""".format(get_first_day(first_day_of_month, d_months=-6), get_last_day(first_day_of_month), user_filter, quotation_status), as_dict=True)
        
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            
            dataset['labels'].append(ref_start_date.strftime("%B"))
        
        for emp in emp_sets:
            # get empl name
            if emp.quotation_owner and emp.quotation_owner != '':
                empl_name = frappe.db.get_value("User", emp.quotation_owner, "middle_name") or frappe.db.get_value("User", emp.quotation_owner, "full_name")
                user_for_block_check = emp.quotation_owner
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.quotation_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
            elif emp.fallback_owner and emp.fallback_owner != '':
                empl_name = frappe.db.get_value("User", emp.fallback_owner, "middle_name") or frappe.db.get_value("User", emp.fallback_owner, "full_name")
                user_for_block_check = emp.fallback_owner
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.fallback_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
            elif emp.creator:
                empl_name = frappe.db.get_value("User", emp.creator, "middle_name") or frappe.db.get_value("User", emp.creator, "full_name")
                user_for_block_check = emp.creator
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.creator), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
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
                colors.append(c)
                data_subset = {
                    "name":  empl_name,
                    "values": []
                }
                for month in range(1, 7):
                    m_delta = month - 6
                    ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                    ref_end_date = get_last_day(ref_start_date)
                    
                    ansprechpartner_qty = frappe.db.sql("""SELECT
                                                {4}
                                            FROM `tabQuotation`
                                            WHERE `status` = '{3}'
                                            AND `creation` BETWEEN '{0}' AND '{1}'
                                            AND `ansprechpartner` = '{2}'""".format(ref_start_date, ref_end_date, emp.quotation_owner or emp.fallback_owner, quotation_status, query_selector), as_dict=True)[0].qty
                    
                    k_ansprechperson_qty = frappe.db.sql("""SELECT
                                                {4}
                                            FROM `tabQuotation`
                                            WHERE `status` = '{3}'
                                            AND `creation` BETWEEN '{0}' AND '{1}'
                                            AND `ansprechpartner` IS NULL
                                            AND `k_ansprechperson` = '{2}'""".format(ref_start_date, ref_end_date, emp.quotation_owner or emp.fallback_owner, quotation_status, query_selector), as_dict=True)[0].qty
                    
                    owner_qty = frappe.db.sql("""SELECT
                                                {4}
                                            FROM `tabQuotation`
                                            WHERE `status` = '{3}'
                                            AND `creation` BETWEEN '{0}' AND '{1}'
                                            AND `ansprechpartner` IS NULL
                                            AND `k_ansprechperson` IS NULL
                                            AND `owner` = '{2}'""".format(ref_start_date, ref_end_date, emp.quotation_owner or emp.fallback_owner, quotation_status, query_selector), as_dict=True)[0].qty
                    qty = ansprechpartner_qty + k_ansprechperson_qty + owner_qty
                    data_subset['values'].append(qty)
                dataset['datasets'].append(data_subset)
        if not len(emp_sets) > 0:
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
        query_selector = """IFNULL(SUM(`grand_total`), 0) AS `qty`"""
    
    if not gl:
        user_filter = """ AND (`ansprechpartner` = '{user}' OR (
                            `ansprechpartner` IS NULL AND `vertriebsgruppe` = '{vertriebsgruppe}') OR (
                            `ansprechpartner` IS NULL AND `vertriebsgruppe` IS NULL AND `owner` = '{user}')
                        )""".format(user=user, vertriebsgruppe=vertriebsgruppe)
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
                                        `vertriebsgruppe` AS `fallback_owner`,
                                        `owner` AS `creator`
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
            if emp.so_owner and emp.so_owner != '':
                emp_name = frappe.db.get_value("User", emp.so_owner, "middle_name") or frappe.db.get_value("User", emp.so_owner, "full_name")
                user_for_block_check = emp.so_owner
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.so_owner), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
            elif emp.fallback_owner and emp.fallback_owner != '':
                vertriebsgruppe_ma = frappe.db.sql("""SELECT `user_id` FROM `tabEmployee` WHERE `name` = '{user}'""".format(user=emp.fallback_owner), as_dict=True)[0].user_id
                emp_name = frappe.db.get_value("User", vertriebsgruppe_ma, "middle_name") or frappe.db.get_value("User", vertriebsgruppe_ma, "full_name")
                user_for_block_check = vertriebsgruppe_ma
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(vertriebsgruppe_ma), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
            elif emp.creator:
                emp_name = frappe.db.get_value("User", emp.creator, "middle_name") or frappe.db.get_value("User", emp.creator, "full_name")
                user_for_block_check = emp.creator
                color = frappe.db.sql("""SELECT `color` FROM `tabUser Chart Color` WHERE `user` = '{0}'""".format(emp.creator,), as_dict=True)
                if len(color) > 0:
                    c = color[0].color
                else:
                    c = '#DFFF00'
                # ~ colors.append(c)
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
                colors.append(c)
                data_subset = {
                    "name":  emp_name,
                    "values": []
                }
                for month in range(1, 7):
                    m_delta = month - 6
                    ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
                    ref_end_date = get_last_day(ref_start_date)
                    
                    ansprechpartner_qty = frappe.db.sql("""SELECT
                                                {query_selector}
                                            FROM `tabSales Order`
                                            WHERE `docstatus` = 1
                                            AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            AND `ansprechpartner` = '{ansprechpartner}'""".format(ref_start_date=ref_start_date, ref_end_date=ref_end_date, ansprechpartner=emp.so_owner or emp.fallback_owner, query_selector=query_selector), as_dict=True)[0].qty
                    
                    vertriebsgruppe_qty = frappe.db.sql("""SELECT
                                                {query_selector}
                                            FROM `tabSales Order`
                                            WHERE `docstatus` = 1
                                            AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            AND `ansprechpartner` IS NULL
                                            AND `vertriebsgruppe` = '{ansprechpartner}'""".format(ref_start_date=ref_start_date, ref_end_date=ref_end_date, ansprechpartner=emp.so_owner or emp.fallback_owner, query_selector=query_selector), as_dict=True)[0].qty
                    
                    owner_qty = frappe.db.sql("""SELECT
                                                {query_selector}
                                            FROM `tabSales Order`
                                            WHERE `docstatus` = 1
                                            AND `creation` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                            AND `ansprechpartner` IS NULL
                                            AND `vertriebsgruppe` IS NULL
                                            AND `owner` = '{ansprechpartner}'""".format(ref_start_date=ref_start_date, ref_end_date=ref_end_date, ansprechpartner=emp.so_owner or emp.fallback_owner, query_selector=query_selector), as_dict=True)[0].qty
                    
                    qty = ansprechpartner_qty + vertriebsgruppe_qty + owner_qty
                    
                    data_subset['values'].append(qty)
                dataset['datasets'].append(data_subset)
        if not len(emp_sets) > 0:
            dataset['datasets'].append({
                "name": "",
                "values": []
            })
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value
