# -*- coding: utf-8 -*-
# Copyright (c) 2024, libracore and contributors
# For license information, please see license.txt

from frappe import _

def get_data():
   return {
      'fieldname': 'source_depot',
      'transactions': [
         {
            'label': _('Stock'),
            'items': ['Stock Entry']
         }
      ]
   }