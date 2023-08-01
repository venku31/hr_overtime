import frappe
from erpnext.utilities.transaction_base import TransactionBase
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

from frappe.utils import flt


class CustomSalarySlip(SalarySlip):
    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
        max_working_hours = frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet")
        base = frappe.db.get_value("Salary Structure Assignment", {"employee":self.employee,"salary_structure":self.salary_structure,"docstatus":1}, "base")
        basic_hourly_rate = base*1/self.payment_days*1/max_working_hours
        normal_overtime = frappe.db.get_single_value("Payroll Settings", "normal_overtime_hous")
        add_rate = frappe.db.get_single_value("Payroll Settings", "add_rate")

        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            # self.hour_rate = self._salary_structure_doc.hour_rate
            # self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            self.hour_rate = basic_hourly_rate
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            if (self.total_working_hours-max_working_hours)>normal_overtime :
                self.total_overtime_hours = normal_overtime or 0.0
            else :
                self.total_overtime_hours = self.total_working_hours-max_working_hours or 0.0

            self.total_add_overtime_hours = self.total_working_hours-max_working_hours-self.total_overtime_hours or 0.0 
            self.add_rate = add_rate
            wages_amount = self.hour_rate * self.total_working_hours

            self.add_earning_for_hourly_wages(
                self, self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)