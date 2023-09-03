import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, flt, get_datetime, getdate, time_diff_in_hours
import datetime
from erpnext.controllers.queries import get_match_cond
from erpnext.setup.utils import get_exchange_rate

# class Timesheet(Document):
    
# 	def calculate_total_amounts(self):
# 		self.total_hours = 0.0
# 		self.overtime_hours = 0.0
# 		self.total_billable_hours = 0.0
# 		self.total_billed_hours = 0.0
# 		self.total_billable_amount = self.base_total_billable_amount = 0.0
# 		self.total_costing_amount = self.base_total_costing_amount = 0.0
# 		self.total_billed_amount = self.base_total_billed_amount = 0.0

# 		for d in self.get("time_logs"):
# 			self.update_billing_hours(d)
# 			self.update_time_rates(d)

# 			self.total_hours += flt(d.hours)
            
# 			self.total_costing_amount += flt(d.costing_amount)
# 			self.base_total_costing_amount += flt(d.base_costing_amount)
# 			if d.is_billable:
# 				self.total_billable_hours += flt(d.billing_hours)
# 				self.total_billable_amount += flt(d.billing_amount)
# 				self.base_total_billable_amount += flt(d.base_billing_amount)
# 				self.total_billed_amount += flt(d.billing_amount) if d.sales_invoice else 0.0
# 				self.base_total_billed_amount += flt(d.base_billing_amount) if d.sales_invoice else 0.0
# 				self.total_billed_hours += flt(d.billing_hours) if d.sales_invoice else 0.0
# 		self.overtime_hours = 8.0

@frappe.whitelist()
def update_timesheet_overtime(self,method=None):
    max_working_hrs = frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet")
    normal_overtime = frappe.db.get_single_value("Payroll Settings", "normal_overtime_hous")
    no = self.start_date.weekday()
    print("//////",no)
    if no > 5:
        if (self.total_hours-max_working_hrs) >normal_overtime :
            self.custom_sunday_overtime_hours = normal_overtime or 0.0
            self.overtime_hours = 0.0
            self.add_rate_overtime_hours = self.total_hours-max_working_hrs-normal_overtime
        else :
            self.custom_sunday_overtime_hours = self.total_hours-max_working_hrs or 0.0
            self.overtime_hours = 0.0
            self.add_rate_overtime_hours =0.0
    if no < 6:
        if (self.total_hours-max_working_hrs) >normal_overtime :
            self.overtime_hours = normal_overtime or 0.0
            self.custom_sunday_overtime_hours = 0.0
            self.add_rate_overtime_hours = self.total_hours-max_working_hrs-normal_overtime
        else :
            self.overtime_hours = self.total_hours-max_working_hrs or 0.0
            self.custom_sunday_overtime_hours =0.0
            self.add_rate_overtime_hours =0.0
    self.add_rate = frappe.db.get_single_value("Payroll Settings", "add_rate")