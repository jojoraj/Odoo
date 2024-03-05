# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
import calendar
from lxml import etree



class HrEmployee(models.Model):
    _inherit="hr.employee"

    date_payroll = fields.Date(string="Date payroll")
    timesheet_cost_float = fields.Float()
    month = fields.Char(string="Month")
    last_day_month = fields.Char(string="Last Day Month", )
    work_day = fields.Float(string="Working days")
    computer_freight = fields.Monetary(string="Computer freight", default=35000, currency_field='currency_id')
    isi = fields.Selection([
        ('zero_percent', '0%'),
        ('five_percent', '5%')
    ], string="ISI")

    net_salary_without_extra_hour = fields.Float(string="Net salary", compute='_compute_net_salary_without_extra_hour', store=True)
    net_salary = fields.Monetary(string="Net salary", compute='_compute_net_salary', store=True, currency_field='currency_id')
    isi_deduction = fields.Monetary(string="ISI deduction", compute='_compute_isi_deduction', store=True, currency_field='currency_id')
    total_salary = fields.Monetary(string="Total salary", compute='_compute_total_salary', store=True, currency_field='currency_id')
    total_salary_letter = fields.Char(string="Salary letter", compute='_compute_total_salary_letter')

    payroll_numbers = fields.Float(string="Payments", compute='_compute_payroll_numbers')
    is_payroll_manager = fields.Boolean(compute='_compute_is_payroll_manager', default=lambda self: True if self.env.user.has_group('custom_hr_employee.igy_payroll_manager') else False)

    advance = fields.Monetary(string="Advance")
    payment_type = fields.Selection([
        ('madagascar', 'Ingenosya Madagascar'),
        ('business', 'Ingenosya Business services')
    ], string="Payment type")
    extra_hour = fields.Float(string="Extra time")
    extra_hour_unit = fields.Float(string="Extra hour unit")
    total_extra_hour = fields.Float(string="Total extra", compute='_compute_total_extra_hour', store=True)
    other_payment = fields.Float(string="Others")
    total_work_day = fields.Float()
    niff = fields.Char(string="Niff")
    stat = fields.Char(string="Stat")
    has_niff_stat = fields.Boolean(string="Niff and Stat")

    has_extra_hour = fields.Boolean(string="Extra hour")

    @api.depends('timesheet_cost', 'work_day')
    def _compute_net_salary_without_extra_hour(self):
        for rec in self:
            rec.net_salary_without_extra_hour = rec.timesheet_cost * rec.work_day

    def _compute_is_payroll_manager(self):
        for rec in self:
            rec.is_payroll_manager = True if self.env.user.has_group('igy_payroll.igy_payroll_manager') else False

    @api.depends('timesheet_cost', 'work_day', 'total_extra_hour')
    def _compute_net_salary(self):
        for rec in self:
            rec.net_salary = (rec.timesheet_cost * rec.work_day) + rec.total_extra_hour

    @api.depends('net_salary', 'isi')
    def _compute_isi_deduction(self):
        for rec in self:
            if rec.isi == 'five_percent':
                rec.isi_deduction = rec.net_salary * 0.05
            else:
                rec.isi_deduction = 0

    @api.depends('extra_hour_unit', 'extra_hour')
    def _compute_total_extra_hour(self):
        for rec in self:
            rec.total_extra_hour = rec.extra_hour * rec.extra_hour_unit

    @api.depends('net_salary', 'isi_deduction', 'computer_freight', 'advance', 'other_payment')
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.net_salary - rec.isi_deduction + rec.computer_freight - rec.advance + rec.other_payment

    def _compute_total_salary_letter(self):
        for rec in self:
            if rec.total_salary:
                rec.total_salary_letter = self.env.user.company_id.currency_id.amount_to_text(rec.total_salary)
            else:
                rec.total_salary_letter = 'Zero'

    def open_payroll(self):
        action = self.env.ref('igy_payroll.action_igy_payroll_view').read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}
        return action

    def _compute_payroll_numbers(self):
        for rec in self:
            rec.payroll_numbers = self.env['igy.payroll'].search_count([('employee_id', '=', rec.id)])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id, view_type, toolbar, submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//page[@name='employee_cost']"):
            if not self.env.user.has_group('igy_payroll.igy_payroll_manager'):
                for child in node.iterchildren():
                    node.remove(child)
        res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    @api.model
    def fields_get(self, fields=None):
        hide = ['net_salary_without_extra_hour', 'net_salary', 'total_salary', 'total_salary_letter', 'advance']
        res = super(HrEmployee, self).fields_get(fields)
        if not self.env.user.has_group('employee_documents_expiry.rh_administration'):
            for field in hide:
                res[field]['exportable'] = False
        return res
