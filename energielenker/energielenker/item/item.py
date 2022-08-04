# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate
from collections import defaultdict

def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    conditions = []

    description_cond = ''
    if frappe.db.count('Item', cache=True) < 50000:
        # scan description only if items are less than 50000
        description_cond = 'or tabItem.description LIKE %(txt)s'
        
        # check search_fields
        meta = frappe.get_meta(doctype)
        search_fields = []
        or_filters = ''
        if meta.search_fields:
            search_fields.extend(meta.get_search_fields())
            for f in search_fields:
                or_filters += ' or tabItem.{search_field} LIKE %(txt)s'.format(search_field=f)

    return frappe.db.sql("""select tabItem.name,
        if(length(tabItem.item_name) > 40,
            concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
        tabItem.item_group,
        if(length(tabItem.description) > 40, \
            concat(substr(tabItem.description, 1, 40), "..."), description) as decription,
        if(length(tabItem.suchfeld) > 40, \
            concat(substr(tabItem.suchfeld, 1, 40), "..."), suchfeld) as suchfeld
        from tabItem
        where tabItem.docstatus < 2
            and tabItem.has_variants=0
            and tabItem.disabled=0
            and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
            and (tabItem.`{key}` LIKE %(txt)s
                or tabItem.item_code LIKE %(txt)s
                or tabItem.item_group LIKE %(txt)s
                or tabItem.item_name LIKE %(txt)s
                or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
                {description_cond}
                {or_filters})
            {fcond} {mcond}
        order by
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
            idx desc,
            name, item_name
        limit %(start)s, %(page_len)s """.format(
            key=searchfield,
            fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
            mcond=get_match_cond(doctype).replace('%', '%%'),
            description_cond = description_cond,
            or_filters = or_filters),
            {
                "today": nowdate(),
                "txt": "%%%s%%" % txt,
                "_txt": txt.replace("%", ""),
                "start": start,
                "page_len": page_len
            }, as_dict=as_dict)

def check_item_code(item, event):
    # ~ frappe.throw(item.name)
    item_number = item.name.replace("A", "")
    item_number = item_number.replace("-", "")
    item_number = int(item_number)
    
    existing_item_number = frappe.db.sql("""SELECT COUNT(`name`) AS `qty` FROM `tabItem` WHERE `name` != '{item}' AND `name` LIKE '%{item_number}'""".format(item=item.name, item_number=item_number), as_dict=True)[0].qty
    if existing_item_number > 0:
        new_number = frappe.rename_doc("Item", item.name, 'A-' + '{num:07d}'.format(num=item_number + 1))
        new_number = new_number.replace("A", "")
        new_number = new_number.replace("-", "")
        
        frappe.db.sql("""UPDATE `tabSeries` SET `current` = '{new_number}' WHERE `name` = 'A-'""".format(new_number=new_number), as_list=True)
