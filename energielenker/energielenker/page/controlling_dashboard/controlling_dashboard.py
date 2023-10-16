# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, get_first_day, get_last_day

@frappe.whitelist()
def get_auftragsvolumen():
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs():
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabSales Order`
                                    WHERE `docstatus` = 1
                                    AND `transaction_date` BETWEEN '{0}' AND '{1}'""".format(ref_start_date, ref_end_date), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`grand_total`) AS `sum_total`
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
            datasets.append({
                'name': pc[0].replace("Solutions - ", "").replace(" - S", ""),
                'values': get_pc_values(pc[0])
            })
        return datasets
    
    pcs = get_pcs()
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    return dataset

@frappe.whitelist()
def get_angebotsvolumen():
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs():
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabQuotation`
                                    WHERE `docstatus` = 1
                                    AND `transaction_date` BETWEEN '{0}' AND '{1}'
                                    AND `status` NOT IN ('Lost', 'Ordered')""".format(ref_start_date, ref_end_date), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`grand_total`) AS `sum_total`
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
                datasets.append({
                    'name': pc[0].replace("Solutions - ", "").replace(" - S", ""),
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    pcs = get_pcs()
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    return dataset

@frappe.whitelist()
def get_ausgangsrechnungen():
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs():
        first_day_of_month = get_first_day(getdate())
        ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        ref_end_date = get_last_day(first_day_of_month)
        cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        `cost_center`
                                    FROM `tabSales Invoice`
                                    WHERE `docstatus` = 1
                                    AND `posting_date` BETWEEN '{0}' AND '{1}'""".format(ref_start_date, ref_end_date), as_list=True)
        return cost_centers
    
    def get_pc_values(pc):
        pc_values = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            sum_total = frappe.db.sql("""SELECT
                                            SUM(`grand_total`) AS `sum_total`
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
                datasets.append({
                    'name': pc[0].replace("Solutions - ", "").replace(" - S", ""),
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    pcs = get_pcs()
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    return dataset

@frappe.whitelist()
def get_eingangsrechnungen():
    def get_labels():
        label_list = []
        first_day_of_month = get_first_day(getdate())
        for month in range(1, 7):
            m_delta = month - 6
            ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            ref_end_date = get_last_day(ref_start_date)
            label_list.append(ref_start_date.strftime("%B"))
        return label_list
    
    def get_pcs():
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
        for p_or_w in projects_warehouses:
            cc = None
            if p_or_w.project:
                cc = frappe.db.get_value("Project", p_or_w.project, 'cost_center')
                if cc:
                    if cc not in no_duplicates:
                        cost_centers.append([cc])
                        no_duplicates.append(cc)
            if not cc:
                if p_or_w.warehouse:
                    if p_or_w.warehouse not in no_duplicates:
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
                                            SUM(`grand_total`) AS `sum_total`
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
                datasets.append({
                    'name': pc[0].replace("Solutions - ", "").replace(" - S", ""),
                    'values': get_pc_values(pc[0])
                })
            return datasets
        else:
            return [{'name':'', 'values':[]}]
    
    pcs = get_pcs()
    dataset = {
        'labels': get_labels(),
        'datasets': get_datasets(pcs)
    }
    
    return dataset

@frappe.whitelist()
def get_lagerwert():
    from erpnext.stock.report.stock_analytics.stock_analytics import get_data
    # ~ class filters_dict:
        # ~ def __init__(self, from_date, to_date, value_quantity, range, item_code, brand, item_group, warehouse, warehouse_type, include_uom, show_variant_attributes):
            # ~ self.from_date = from_date
            # ~ self.to_date = to_date
            # ~ self.value_quantity = value_quantity
            # ~ self.range = range
            # ~ self.item_code = item_code
            # ~ self.brand = brand
            # ~ self.item_group = item_group
            # ~ self.warehouse = warehouse
            # ~ self.warehouse_type = warehouse_type
            # ~ self.include_uom = include_uom
            # ~ self.show_variant_attributes = show_variant_attributes
        # ~ def get(self, key, default_value=0):
            # ~ return getattr(self, key)
    
    # ~ filters = filters_dict('2022-01-01', '2022-12-31', 'Value', 'Monthly', None, None, None, None, None, None, 0)
    # ~ filters = frappe._dict(from_date='2022-01-01', to_date='2022-12-31', value_quantity='Value', range='Monthly')
    # ~ frappe.throw(str(x))
    # ~ data = get_data(filters)
    
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
    # ~ datas = []
    values = []
    for month in range(1, 7):
        m_delta = month - 18
        ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
        ref_end_date = get_last_day(ref_start_date)
        filters = frappe._dict(from_date=ref_start_date, to_date=ref_end_date, value_quantity='Value', range='Monthly')
        data = get_data(filters)
        # ~ frappe.throw(str(data))
        value = 0
        for d in data:
            value += d['total']
        values.append(value)
    # ~ frappe.throw(str(values))
    
    dataset = {
        'labels': get_labels(),
        'datasets': [{'name':'Lagerwert', 'values':values}]
    }
        
    # ~ frappe.throw(str(data))
    
    
    
    # ~ def get_pcs():
        # ~ first_day_of_month = get_first_day(getdate())
        # ~ ref_start_date = get_first_day(first_day_of_month, d_months=-6)
        # ~ ref_end_date = get_last_day(first_day_of_month)
        # ~ cost_centers = frappe.db.sql("""SELECT DISTINCT
                                        # ~ `cost_center`
                                    # ~ FROM `tabSales Invoice`
                                    # ~ WHERE `docstatus` = 1
                                    # ~ AND `posting_date` BETWEEN '{0}' AND '{1}'""".format(ref_start_date, ref_end_date), as_list=True)
        # ~ return cost_centers
    
    # ~ def get_pc_values(pc):
        # ~ pc_values = []
        # ~ first_day_of_month = get_first_day(getdate())
        # ~ for month in range(1, 7):
            # ~ m_delta = month - 6
            # ~ ref_start_date = get_first_day(first_day_of_month, d_months=m_delta)
            # ~ ref_end_date = get_last_day(ref_start_date)
            # ~ sum_total = frappe.db.sql("""SELECT
                                            # ~ SUM(`grand_total`) AS `sum_total`
                                        # ~ FROM `tabSales Invoice`
                                        # ~ WHERE `docstatus` = 1
                                        # ~ AND `posting_date` BETWEEN '{0}' AND '{1}'
                                        # ~ AND `cost_center` = '{2}'""".format(ref_start_date, ref_end_date, pc), as_dict=True)[0].sum_total
            # ~ if not sum_total:
                # ~ sum_total = 0
            # ~ pc_values.append(sum_total)
        
        # ~ return pc_values
    
    # ~ def get_datasets(pcs):
        # ~ datasets = []
        # ~ if len(pcs) > 0:
            # ~ for pc in pcs:
                # ~ datasets.append({
                    # ~ 'name': pc[0].replace("Solutions - ", "").replace(" - S", ""),
                    # ~ 'values': get_pc_values(pc[0])
                # ~ })
            # ~ return datasets
        # ~ else:
            # ~ return [{'name':'', 'values':[]}]
    
    # ~ pcs = get_pcs()
    # ~ dataset = {
        # ~ 'labels': get_labels(),
        # ~ 'datasets': get_datasets(pcs)
    # ~ }
    
    return dataset
