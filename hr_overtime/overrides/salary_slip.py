import frappe
from erpnext.utilities.transaction_base import TransactionBase
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

from frappe.utils import flt,rounded



class CustomSalarySlip(SalarySlip):
    def set_time_sheet(self):
        if self.salary_slip_based_on_timesheet:
            self.set("timesheets", [])

            Timesheet = frappe.qb.DocType("Timesheet")
            timesheets = (
                frappe.qb.from_(Timesheet)
                .select(Timesheet.star)
                .where(
                    (Timesheet.employee == self.employee)
                    & (Timesheet.start_date.between(self.start_date, self.end_date))
                    & ((Timesheet.status == "Submitted") | (Timesheet.status == "Billed"))
                )
            ).run(as_dict=1)

            for data in timesheets:
                self.append("timesheets", {"time_sheet": data.name, "working_hours": data.total_hours,"overtime_hours": data.overtime_hours,"add_overtime_hours":data.add_rate_overtime_hours})

    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
        max_working_hours = frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet")
        # base = frappe.db.get_value("Salary Structure Assignment", {"employee":self.employee,"salary_structure":self.salary_structure,"docstatus":1}, "base")
        # basic_hourly_rate = base*1/self.payment_days*1/max_working_hours
        normal_overtime = frappe.db.get_single_value("Payroll Settings", "normal_overtime_hous")
        add_rate = frappe.db.get_single_value("Payroll Settings", "add_rate")

        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            # self.hour_rate = self._salary_structure_doc.hour_rate
            # self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            base = frappe.db.get_value("Salary Structure Assignment", {"employee":self.employee,"salary_structure":self.salary_structure,"docstatus":1}, "base")
            basic_hourly_rate = flt(base*1/self.payment_days*1/max_working_hours)
            self.hourly_rate = flt(str(round(basic_hourly_rate, 2)))
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            self.total_overtime_hours = sum([d.overtime_hours or 0.0 for d in self.timesheets])
            self.total_add_overtime_hours = sum([d.add_overtime_hours or 0.0 for d in self.timesheets])
            # if (self.total_working_hours-max_working_hours)>normal_overtime :
            #     self.total_overtime_hours = normal_overtime or 0.0
            # else :
            #     self.total_overtime_hours = self.total_working_hours-max_working_hours or 0.0

            # self.total_add_overtime_hours = self.total_working_hours-max_working_hours-self.total_overtime_hours or 0.0 
            self.add_rate = frappe.db.get_single_value("Payroll Settings", "add_rate")
            wages_amount = self.hourly_rate * self.total_working_hours

            self.add_earning_for_hourly_wages(
                self, self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)
    def add_earning_for_hourly_wages(self, doc, salary_component, amount):
        row_exists = False
        for row in doc.earnings:
            if row.salary_component == salary_component:
                row.amount = amount
                row_exists = True
                break

        if not row_exists:
            wages_row = {
                "salary_component": salary_component,
                "abbr": frappe.db.get_value("Salary Component", salary_component, "salary_component_abbr"),
                "amount": self.hourly_rate * self.total_working_hours,
                "default_amount": 0.0,
                "additional_amount": 0.0,
            }
            doc.append("earnings", wages_row)
    
    def set_net_pay(self):
        self.total_deduction = self.get_component_totals("deductions")
        self.base_total_deduction = flt(
            flt(self.total_deduction) * flt(self.exchange_rate), self.precision("base_total_deduction")
        )
        self.net_pay = flt(self.gross_pay) - (
            flt(self.total_deduction) + flt(self.get("total_loan_repayment"))
        )
        self.rounded_total = rounded(self.net_pay)
        self.base_net_pay = flt(
            flt(self.net_pay) * flt(self.exchange_rate), self.precision("base_net_pay")
        )
        self.base_rounded_total = flt(rounded(self.base_net_pay), self.precision("base_net_pay"))
        if self.hourly_rate:
            self.base_hour_rate = flt(
                flt(self.hourly_rate) * flt(self.exchange_rate), self.precision("base_hour_rate")
            )
        self.set_net_total_in_words()

    def calculate_total_for_salary_slip_based_on_timesheet(self):
        if self.timesheets:
            self.total_working_hours = 0
            for timesheet in self.timesheets:
                if timesheet.working_hours:
                    self.total_working_hours += timesheet.working_hours

        wages_amount = self.total_working_hours * self.hourly_rate
        self.base_hour_rate = flt(self.hourly_rate) * flt(self.exchange_rate)
        salary_component = frappe.db.get_value(
            "Salary Structure", {"name": self.salary_structure}, "salary_component"
        )
        if self.earnings:
            for i, earning in enumerate(self.earnings):
                if earning.salary_component == salary_component:
                    self.earnings[i].amount = wages_amount
                self.gross_pay += flt(self.earnings[i].amount, earning.precision("amount"))
        self.net_pay = flt(self.gross_pay) - flt(self.total_deduction)