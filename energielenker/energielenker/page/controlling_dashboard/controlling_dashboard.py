# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, get_first_day, get_last_day

@frappe.whitelist()
def get_auftragsvolumen(pc_filters=False):
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs(pc_filters):
        if pc_filters:
            if pc_filters != 'false':
                cost_center_filters = []
                for pcf in pc_filters.split(","):
                    cc_name = frappe.db.sql("""SELECT `name` FROM `tabCost Center` WHERE `cost_center_number` = '{0}'""".format(pcf), as_dict=True)[0].name
                    cost_center_filters.append("'{0}'".format(cc_name))
                ccf = ", ".join(cost_center_filters)
                pc_filter = """AND `cost_center` IN ({ccf})""".format(ccf=ccf)
            else:
                pc_filter = ''
        else:
            pc_filter = ''
        
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {pc_filter}""".format(ref_start_date=ref_start_date, \
                                                            ref_end_date=ref_end_date, \
                                                            pc_filter=pc_filter), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`total`) AS `sum_total`
                                        FROM `tabSales Order`
                                        WHERE `docstatus` = 1
                                        AND `transaction_date` BETWEEN '{0}' AND '{1}'
                                        AND `cost_center` = '{2}'""".format(ref_start_date, ref_end_date, pc), as_dict=True)[0].sum_total
            if not sum_total:
                sum_total = 0
            pc_values.append(sum_total)
        
        return pc_values
    
    def get_datasets(pcs):
        datasets = []
        for pc in pcs:
            dashboard_kuerzel = frappe.db.get_value("Cost Center", pc[0], 'dashboard_kuerzel')
            datasets.append({
                'name': dashboard_kuerzel or pc[0],
                'values': get_pc_values(pc[0])
            })
        return datasets
    
    def get_colors(pcs):
        colors = []
        for pc in pcs:
            pc_color = frappe.db.get_value("Cost Center", pc[0], 'dashboard_farbe') or '#DFFF00'
            colors.append(pc_color)
        return colors
    
    pcs = get_pcs(pc_filters)
    
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    colors = get_colors(pcs)
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_angebotsvolumen(pc_filters=False):
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs(pc_filters):
        if pc_filters:
            if pc_filters != 'false':
                cost_center_filters = []
                for pcf in pc_filters.split(","):
                    cc_name = frappe.db.sql("""SELECT `name` FROM `tabCost Center` WHERE `cost_center_number` = '{0}'""".format(pcf), as_dict=True)[0].name
                    cost_center_filters.append("'{0}'".format(cc_name))
                ccf = ", ".join(cost_center_filters)
                pc_filter = """AND `cost_center` IN ({ccf})""".format(ccf=ccf)
            else:
                pc_filter = ''
        else:
            pc_filter = ''
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabQuotation`
                                    WHERE `docstatus` = 1
                                    AND `transaction_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    AND `status` NOT IN ('Lost', 'Ordered')
                                    {pc_filter}""".format(ref_start_date=ref_start_date, \
                                                            ref_end_date=ref_end_date, \
                                                            pc_filter=pc_filter), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`total`) AS `sum_total`
                                        FROM `tabQuotation`
                                        WHERE `docstatus` = 1
                                        AND `transaction_date` BETWEEN '{0}' AND '{1}'
                                        AND `cost_center` = '{2}'
                                        AND `status` NOT IN ('Lost', 'Ordered')""".format(ref_start_date, ref_end_date, pc), as_dict=True)[0].sum_total
            if not sum_total:
                sum_total = 0
            pc_values.append(sum_total)
        
        return pc_values
    
    def get_datasets(pcs):
        datasets = []
        if len(pcs) > 0:
            for pc in pcs:
                dashboard_kuerzel = frappe.db.get_value("Cost Center", pc[0], 'dashboard_kuerzel')
                datasets.append({
                    'name': dashboard_kuerzel or pc[0],
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    def get_colors(pcs):
        colors = []
        for pc in pcs:
            pc_color = frappe.db.get_value("Cost Center", pc[0], 'dashboard_farbe') or '#DFFF00'
            colors.append(pc_color)
        return colors
    
    pcs = get_pcs(pc_filters)
    
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    colors = get_colors(pcs)
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_ausgangsrechnungen(pc_filters=False):
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs(pc_filters):
        if pc_filters:
            if pc_filters != 'false':
                cost_center_filters = []
                for pcf in pc_filters.split(","):
                    cc_name = frappe.db.sql("""SELECT `name` FROM `tabCost Center` WHERE `cost_center_number` = '{0}'""".format(pcf), as_dict=True)[0].name
                    cost_center_filters.append("'{0}'".format(cc_name))
                ccf = ", ".join(cost_center_filters)
                pc_filter = """AND `cost_center` IN ({ccf})""".format(ccf=ccf)
            else:
                pc_filter = ''
        else:
            pc_filter = ''
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabSales Invoice`
                                    WHERE `docstatus` = 1
                                    AND `posting_date` BETWEEN '{ref_start_date}' AND '{ref_end_date}'
                                    {pc_filter}""".format(ref_start_date=ref_start_date, \
                                                            ref_end_date=ref_end_date, \
                                                            pc_filter=pc_filter), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`total`) AS `sum_total`
                                        FROM `tabSales Invoice`
                                        WHERE `docstatus` = 1
                                        AND `posting_date` BETWEEN '{0}' AND '{1}'
                                        AND `cost_center` = '{2}'""".format(ref_start_date, ref_end_date, pc), as_dict=True)[0].sum_total
            if not sum_total:
                sum_total = 0
            pc_values.append(sum_total)
        
        return pc_values
    
    def get_datasets(pcs):
        datasets = []
        if len(pcs) > 0:
            for pc in pcs:
                dashboard_kuerzel = frappe.db.get_value("Cost Center", pc[0], 'dashboard_kuerzel')
                datasets.append({
                    'name': dashboard_kuerzel or pc[0],
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    def get_colors(pcs):
        colors = []
        for pc in pcs:
            pc_color = frappe.db.get_value("Cost Center", pc[0], 'dashboard_farbe') or '#DFFF00'
            colors.append(pc_color)
        return colors
    
    pcs = get_pcs(pc_filters)
    
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    colors = get_colors(pcs)
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_eingangsrechnungen(pc_filters=False, warehouse_filters=False):
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs(pc_filters):
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = []
        no_duplicates = []
        projects_warehouses = frappe.db.sql("""SELECT
                                        `project`,
                                        `set_warehouse` AS `warehouse`
                                    FROM `tabPurchase Invoice`
                                    WHERE `docstatus` = 1
                                    AND `posting_date` BETWEEN '{0}' AND '{1}'""".format(ref_start_date, ref_end_date), as_dict=True)
        
        cost_center_filters = []
        if pc_filters:
            if pc_filters != 'false':
                for pcf in pc_filters.split(","):
                    cc_name = frappe.db.sql("""SELECT `name` FROM `tabCost Center` WHERE `cost_center_number` = '{0}'""".format(pcf), as_dict=True)[0].name
                    cost_center_filters.append(cc_name)
        warehouse_filter_list = []
        if warehouse_filters:
            if warehouse_filters != 'false':
                for wf in warehouse_filters.split(","):
                    warehouse_filter_list.append(wf)
        
        for p_or_w in projects_warehouses:
            cc = None
            if p_or_w.project:
                cc = frappe.db.get_value("Project", p_or_w.project, 'cost_center')
                if cc:
                    if cc not in no_duplicates:
                        if (cc in cost_center_filters) or (len(cost_center_filters) == 0):
                            cost_centers.append([cc])
                            no_duplicates.append(cc)
            if not cc:
                if p_or_w.warehouse:
                    if p_or_w.warehouse not in no_duplicates:
                        if (p_or_w.warehouse in warehouse_filter_list) or (len(warehouse_filter_list) == 0):
                            cost_centers.append([p_or_w.warehouse])
                            no_duplicates.append(p_or_w.warehouse)
        
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`total`) AS `sum_total`
                                        FROM `tabPurchase Invoice`
                                        WHERE `docstatus` = 1
                                        AND `posting_date` BETWEEN '{0}' AND '{1}'
                                        AND (
                                            `project` IN (
                                                SELECT `name`
                                                FROM `tabProject`
                                                WHERE `cost_center` = '{2}'
                                            )
                                            OR
                                            `set_warehouse` = '{2}'
                                        )""".format(ref_start_date, ref_end_date, pc), as_dict=True)[0].sum_total
            if not sum_total:
                sum_total = 0
            pc_values.append(sum_total)
        
        return pc_values
    
    def get_datasets(pcs):
        datasets = []
        if len(pcs) > 0:
            for pc in pcs:
                dashboard_kuerzel = frappe.db.get_value("Cost Center", pc[0], 'dashboard_kuerzel')
                datasets.append({
                    'name': dashboard_kuerzel or pc[0],
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    def get_colors(pcs):
        colors = []
        for pc in pcs:
            pc_color = frappe.db.get_value("Cost Center", pc[0], 'dashboard_farbe') or frappe.db.get_value("Warehouse", pc[0], 'dashboard_farbe') or '#DFFF00'
            colors.append(pc_color)
        return colors
    
    pcs = get_pcs(pc_filters)
    
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    colors = get_colors(pcs)
    
    return_value = {
        'dataset': dataset,
        'colors': colors
        }
    return return_value

@frappe.whitelist()
def get_lagerwert():
    
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    first_day_of_month = get_first_day(getdate())
    values = []
    
    for month in range(1, 7):
        m_delta = month - 6
        ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
        ref_end_date = get_last_day(ref_start_date)
        value = frappe.db.sql("""SELECT SUM(`stock_value_difference`) AS `value` FROM `tabStock Ledger Entry` WHERE `docstatus` = 1 AND `posting_date` <= '{ref_end_date}'""".format(ref_end_date=ref_end_date), as_dict=True)[0].value
        values.append(value)
    
    dataset = {
        'labels': get_labels(),
        'datasets': [{'name':'Lagerwert', 'values':values}]
    }
    
    return_value = {
        'dataset': dataset,
        'colors': ['light-blue']
        }
    return return_value
