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

@frappe.whitelist()
def get_gebuchte_stunden():
    
    def get_labels():
        label_list = [
            'IoT',
            'Energiesteuerung',
            'Biogas',
            'EZA Regler',
            'Support'
        ]
        return label_list
    
    def label_mapper(label):
        label_list = {
            'IoT': '1000040 - Solutions - IoT (energy monitor, city monitor, Software + Hardware) - S',
            'Energiesteuerung': '1000020 - Solutions - Energiesteuerung (Lobas, Enbas, KI) - S',
            'Biogas': '1000030 - Solutions - Biogas - S',
            'EZA Regler': '1000050 - Solutions - EZA-Regler (VDE 4105, 4110, 4120) - S',
            'Support': ''
        }
        return label_list[label]
    
    def get_soll_stunden_pro_pc():
        soll_stunden = []
        for label in get_labels():
            profit_center = label_mapper(label)
            profit_center_tages_soll = frappe.db.sql("""SELECT SUM(`soll_std`) AS `qty` FROM `tabEmployee` WHERE `default_cost_center` = '{0}'""".format(profit_center), as_dict=True)[0].qty
            if profit_center_tages_soll:
                soll_stunden.append(profit_center_tages_soll)
            else:
                soll_stunden.append(0)
        return soll_stunden
    
    def get_urlaubsstunden():
        urlaubsstunden = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `task` = 'TASK-2021-00007'
                                                            AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet`
                                                                WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 1
                                                            )""".format(first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                urlaubsstunden.append(profit_center_std)
            else:
                urlaubsstunden.append(0)
        return urlaubsstunden
    
    def get_krankheitsstunden():
        krankheitsstunden = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `task` = 'TASK-2021-00008'
                                                            AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet`
                                                                WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 1
                                                            )""".format(first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                krankheitsstunden.append(profit_center_std)
            else:
                krankheitsstunden.append(0)
        return krankheitsstunden
    
    def get_std_per_task(task):
        std_per_task = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `task` = '{task}'
                                                            AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet`
                                                                WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 1
                                                            )""".format(task=task, first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                std_per_task.append(profit_center_std)
            else:
                std_per_task.append(0)
        return std_per_task
    
    def get_ungebuchte_std():
        ungebuchte_std = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet`
                                                                WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 0
                                                            )""".format(first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                ungebuchte_std.append(profit_center_std)
            else:
                ungebuchte_std.append(0)
        return ungebuchte_std
    
    def get_f_und_e_std():
        f_und_e_std = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet` WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 1
                                                                AND `task` NOT IN ('TASK-2021-00010', 'TASK-2021-00524')
                                                                AND `project` IN (
                                                                    SELECT `name` FROM `tabProject`
                                                                    WHERE `forschung_und_entwicklung` = 1
                                                                )
                                                            )""".format(first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                f_und_e_std.append(profit_center_std)
            else:
                f_und_e_std.append(0)
        return f_und_e_std
    
    def get_abrechenbar_std():
        abrechenbar_std = []
        for label in get_labels():
            profit_center = label_mapper(label)
            first_day = get_first_day(getdate(), d_months=-1)
            last_day = get_last_day(first_day)
            profit_center_std = frappe.db.sql("""SELECT
                                                                SUM(`hours`) AS `qty`
                                                            FROM `tabTimesheet Detail`
                                                            WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                            AND `parent` IN (
                                                                SELECT
                                                                    `name`
                                                                FROM `tabTimesheet` WHERE `employee` IN (
                                                                    SELECT `name` FROM `tabEmployee` WHERE `default_cost_center` = '{profit_center}'
                                                                )
                                                                AND `docstatus` = 1
                                                                AND `task` NOT IN ('TASK-2021-00010', 'TASK-2021-00524')
                                                                AND `project` NOT IN (
                                                                    SELECT `name` FROM `tabProject`
                                                                    WHERE `forschung_und_entwicklung` = 1
                                                                )
                                                            )""".format(first_day=first_day, last_day=last_day, profit_center=profit_center), as_dict=True)[0].qty
            if profit_center_std:
                abrechenbar_std.append(profit_center_std)
            else:
                abrechenbar_std.append(0)
        return abrechenbar_std
    
    def get_business_days():
        import numpy as np
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        days = np.busday_count(first_day, last_day)
        return days
    
    def get_support_soll_std():
        soll_stunden = frappe.db.sql("""SELECT SUM(`soll_std`) AS `qty` FROM `tabEmployee` WHERE `name` IN ('HR-EMP-00017', 'HR-EMP-00041')""", as_dict=True)[0].qty
        return soll_stunden * get_business_days()
    
    def get_support_std_per_task(task):
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_std_per_task = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `task` = '{task}'
                                                        AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet`
                                                            WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 1
                                                        )""".format(task=task, first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_std_per_task:
            return support_std_per_task
        else:
            return 0
        
    def get_support_ungebuchte_std():
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_ungebuchte_std = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet`
                                                            WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 0
                                                        )""".format(first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_ungebuchte_std:
            return support_ungebuchte_std
        else:
            return 0
        
    def get_support_f_und_e_std():
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_f_und_e_std = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet` WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 1
                                                            AND `task` NOT IN ('TASK-2021-00010', 'TASK-2021-00524')
                                                            AND `project` IN (
                                                                SELECT `name` FROM `tabProject`
                                                                WHERE `forschung_und_entwicklung` = 1
                                                            )
                                                        )""".format(first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_f_und_e_std:
            return support_f_und_e_std
        else:
            return 0
    
    def get_support_abrechenbar_std():
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_abrechenbar_std = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet` WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 1
                                                            AND `task` NOT IN ('TASK-2021-00010', 'TASK-2021-00524')
                                                            AND `project` NOT IN (
                                                                SELECT `name` FROM `tabProject`
                                                                WHERE `forschung_und_entwicklung` = 1
                                                            )
                                                        )""".format(first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_abrechenbar_std:
            return support_abrechenbar_std
        else:
            return 0
    
    def get_support_urlaubsstunden():
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_urlaubsstunden = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `task` = 'TASK-2021-00007'
                                                        AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet`
                                                            WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 1
                                                        )""".format(first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_urlaubsstunden:
            return support_urlaubsstunden
        else:
            return 0
    
    def get_support_krankheitsstunden():
        first_day = get_first_day(getdate(), d_months=-1)
        last_day = get_last_day(first_day)
        support_krankheitsstunden = frappe.db.sql("""SELECT
                                                            SUM(`hours`) AS `qty`
                                                        FROM `tabTimesheet Detail`
                                                        WHERE `task` = 'TASK-2021-00008'
                                                        AND `from_time` BETWEEN '{first_day}' AND '{last_day}'
                                                        AND `parent` IN (
                                                            SELECT
                                                                `name`
                                                            FROM `tabTimesheet`
                                                            WHERE `employee` IN ('HR-EMP-00017', 'HR-EMP-00041')
                                                            AND `docstatus` = 1
                                                        )""".format(first_day=first_day, last_day=last_day), as_dict=True)[0].qty
        if support_krankheitsstunden:
            return support_krankheitsstunden
        else:
            return 0
    
    def get_datasets():
        datasets = []
        needed_values = [
            ['Vertrieb', get_std_per_task('TASK-2021-00010'), 'bar'],
            ['Overhead', get_std_per_task('TASK-2021-00524'), 'bar'],
            ["Fehlende Std's", get_ungebuchte_std(), 'bar'],
            ['F&E', get_f_und_e_std(), 'bar'],
            ['Abrechenbar', get_abrechenbar_std(), 'bar']
        ]
        soll_stunden_pro_pc = get_soll_stunden_pro_pc()
        urlaubsstunden = get_urlaubsstunden()
        krankheitsstunden = get_krankheitsstunden()
        
        support_soll_std = get_support_soll_std()
        support_urlaubsstunden = get_support_urlaubsstunden()
        support_krankheitsstunden = get_support_krankheitsstunden()
        support_vertrieb = get_support_std_per_task('TASK-2021-00010')
        support_overhead = get_support_std_per_task('TASK-2021-00524')
        support_ungebuchte_std = get_support_ungebuchte_std()
        support_f_und_e_std = get_support_f_und_e_std()
        support_abrechenbar_std = get_support_abrechenbar_std()
        
        for needed_value in needed_values:
            value_dataset = {
                'name': needed_value[0],
                'values': [],
                'chartType': needed_value[2]
            }
            loop = 0
            for label in get_labels():
                if label != 'Support':
                    if soll_stunden_pro_pc[loop] > 0:
                        soll_stunden = (((soll_stunden_pro_pc[loop] * get_business_days()) - urlaubsstunden[loop]) - krankheitsstunden[loop])
                        value = round((100 / soll_stunden) * needed_value[1][loop])
                    else:
                        value = 0
                value_dataset['values'].append(value)
                loop += 1
            if needed_value[0] == 'Support':
                if support_soll_std > 0:
                    prozent_pro_std = 100 / (support_soll_std - support_urlaubsstunden - support_krankheitsstunden)
                    value_dataset['values'].append(prozent_pro_std * support_vertrieb)
                    value_dataset['values'].append(prozent_pro_std * support_overhead)
                    value_dataset['values'].append(prozent_pro_std * support_ungebuchte_std)
                    value_dataset['values'].append(prozent_pro_std * support_f_und_e_std)
                    value_dataset['values'].append(prozent_pro_std * support_abrechenbar_std)
            datasets.append(value_dataset)
        return datasets
    
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(),
        'yMarkers': [
            { 'label': "Zielauslastung 80%", 'value': 80, 'options': { 'labelPos': "left" } },
            { 'label': "Soll-Stunden", 'value': 100, 'options': { 'labelPos': "right" } }
        ]
    }
    
    return_value = {
        'dataset': dataset,
        'colors': []
        }
    return return_value
