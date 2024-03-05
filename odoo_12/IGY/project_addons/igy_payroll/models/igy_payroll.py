# -*- coding: utf-8 -*-

from odoo import api, fields, models
import calendar
from lxml import etree
# <!-- vraharison@ingenosya.mg -->

class IgyPayroll(models.Model):
    _name = 'igy.payroll'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', related='employee_id.user_id')
    partner_id = fields.Many2one('res.partner', related='employee_id.user_id.partner_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)


    status = fields.Selection(
        [
            ('nouveau', 'Nouveau'),
            ('envoye', 'Facture envoyé'), 
            ],
        default = 'nouveau'
    )
    mobile_phone = fields.Char(string="Phone", related="employee_id.mobile_phone", store=True)
    date_payroll = fields.Date(string="Date payroll")
    month = fields.Char(string="Month",  compute='_compute_month', store=True)
    last_day_month = fields.Char(string="Last day of month")

    timesheet_cost = fields.Monetary(string="Timesheet cost", compute='_compute_timesheet_cost', store=True)
    work_day = fields.Float(string="Work day", compute='_compute_work_day', store=True)
    net_salary_without = fields.Monetary(string="Net salary", compute='_compute_net_salary_without_extra_hour', store=True)
    net_salary = fields.Monetary(string="Net salary",  compute='_compute_net_salary', store=True)
    isi = fields.Selection([
        ('zero_percent', '0%'),
        ('five_percent', '5%')
    ], string="ISI", compute='_compute_isi', store=True)
    computer_freight = fields.Monetary(string="Computer freight", compute='_compute_computer_freight', store=True)
    isi_deduction = fields.Monetary(string="ISI deduction", compute='_compute_isi_deduction', store=True)
    total_salary = fields.Monetary(string="Total Salary", compute='_compute_total_salary', store=True)
    total_salary_letter = fields.Char(string="Total Salary Letter",  compute='_compute_total_salary_letter', store=True)
    is_payroll_manager = fields.Boolean(compute='_compute_is_payroll_manager', default=lambda self: True if self.env.user.has_group('igy_payroll.igy_payroll_manager') else False)
    invoice_number = fields.Char(string="Invoice Number", store=True)
    is_user = fields.Boolean(compute='_compute_is_user', default=lambda self: self.default_is_user())
    advance = fields.Monetary(string="Advance", compute='_compute_advance', store=True)
    total_work_day = fields.Float(string="Total work hour", compute='_compute_total_work_day', store=True)
    payment_type = fields.Selection([
        ('madagascar', 'Ingenosya Madagascar'),
        ('business', 'Ingenosya Business')
    ], string="Payment type", compute='_compute_payment_type', store=True)
    other_payment = fields.Float(string="Other payment", compute='_compute_other_payment', store=True)
    extra_hour = fields.Float(string="Extra hour", compute='_compute_extra_hour', store=True)
    extra_hour_unit = fields.Float(string="Extra hour unit", compute='_compute_extra_hour_unit', store=True)
    total_extra_hour = fields.Float(string="Total extra hour", compute='_compute_total_extra_hour', store=True)
    projects = fields.Many2many('project.project',string="Projects")
    niff = fields.Char(string="Niff")
    stat = fields.Char(string="Stat")
    address = fields.Char(string="Address", related='employee_id.address_home_id.name')
    has_extra_hour = fields.Boolean(string="Extra hour", compute='_compute_has_extra_hour', store=True)

    @api.depends('employee_id')
    def _compute_has_extra_hour(self):
        for rec in self:
            if rec.employee_id:
                rec.has_extra_hour = rec.employee_id.has_extra_hour
            else:
                rec.has_extra_hour = False

    @api.depends('employee_id')
    def _compute_extra_hour(self):
        for rec in self:
            if rec.employee_id:
                rec.extra_hour = rec.employee_id.extra_hour
            else:
                rec.extra_hour

    @api.depends('employee_id')
    def _compute_extra_hour_unit(self):
        for rec in self:
            if rec.employee_id:
                rec.extra_hour_unit = rec.employee_id.extra_hour_unit
            else:
                rec.extra_hour_unit = 0

    @api.depends('employee_id')
    def _compute_net_salary_without_extra_hour(self):
        for rec in self:
            if rec.employee_id:
                rec.net_salary_without = rec.employee_id.net_salary_without_extra_hour
            else:
                rec.net_salary_without = 0

    @api.depends('employee_id')
    def _compute_total_extra_hour(self):
        for rec in self:
            if rec.employee_id:
                rec.total_extra_hour = rec.employee_id.total_extra_hour
            else:
                rec.total_extra_hour = 0

    @api.depends('employee_id')
    def _compute_payment_type(self):
        for rec in self:
            if rec.employee_id:
                rec.payment_type = rec.employee_id.payment_type
            else:
                rec.payment_type = ''

    @api.depends('employee_id')
    def _compute_other_payment(self):
        for rec in self:
            if rec.employee_id:
                rec.other_payment = rec.employee_id.other_payment
            else:
                rec.other_payment = 0

    @api.depends('employee_id')
    def _compute_timesheet_cost(self):
        for rec in self:
            if rec.employee_id:
                rec.timesheet_cost = rec.employee_id.timesheet_cost
            else:
                rec.timesheet_cost = 0

    @api.depends('employee_id')
    def _compute_work_day(self):
        for rec in self:
            if rec.employee_id:
                rec.work_day = rec.employee_id.work_day
            else:
                rec.work_day = 0

    @api.depends('employee_id')
    def _compute_net_salary(self):
        for rec in self:
            if rec.employee_id:
                rec.net_salary = rec.employee_id.net_salary
            else:
                rec.net_salary = None

    @api.depends('employee_id')
    def _compute_computer_freight(self):
        for rec in self:
            if rec.employee_id:
                rec.computer_freight = rec.employee_id.computer_freight
            else:
                rec.computer_freight = 0

    @api.depends('employee_id')
    def _compute_isi(self):
        for rec in self:
            if rec.employee_id:
                rec.isi = rec.employee_id.isi
            else:
                rec.isi = 0

    @api.depends('net_salary', 'isi')
    def _compute_isi_deduction(self):
        for rec in self:
            if rec.isi == 'five_percent':
                rec.isi_deduction = rec.net_salary * 0.05
            else:
                rec.isi_deduction = 0

    @api.depends('net_salary', 'isi_deduction', 'computer_freight', 'advance', 'other_payment')
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.net_salary - rec.isi_deduction + rec.computer_freight - rec.advance + rec.other_payment

    @api.depends('employee_id')
    def _compute_total_salary_letter(self):
        for rec in self:
            if rec.employee_id:
                rec.total_salary_letter = rec.employee_id.total_salary_letter
            else:
                rec.total_salary_letter = 0

    @api.depends('employee_id')
    def _compute_advance(self):
        for rec in self:
            if rec.employee_id:
                rec.advance = rec.employee_id.advance
            else:
                rec.advance = 0

    @api.depends('employee_id')
    def _compute_total_work_day(self):
        for rec in self:
            if rec.employee_id:
                rec.total_work_day = rec.employee_id.total_work_day
            else:
                rec.total_work_day = 0

    @api.depends('date_payroll')
    def _compute_month(self):
        months = ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        for rec in self:
            if rec.date_payroll:
                month_day = months[rec.date_payroll.month - 1]
                rec.month = month_day
            else:
                rec.month = None

    @api.onchange('date_payroll')
    def change_date_payroll(self):
        for rec in self:
            if rec.date_payroll:
                rec.last_day_month = str(calendar.monthrange(rec.date_payroll.year, rec.date_payroll.month)[
                                         1]) + '/' + rec.date_payroll.strftime('%m/%Y')
            else:
                rec.last_day_month = None

    # def search_read(self, domain=None, field=None, offset=0, limit=None, order=None):
    #     if not self.env.user.has_group('igy_payroll.igy_payroll_manager'):
    #         employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    #         domain = [('employee_id', '=', employee_id.id)]
    #     res = super(IgyPayroll, self).search_read(domain, field, offset, limit, order)
    #     return res

    def _compute_is_payroll_manager(self):
        for rec in self:
            rec.is_payroll_manager = True if self.env.user.has_group('igy_payroll.igy_payroll_manager') else False

    @api.depends('date_payroll')
    def _compute_invoice_number(self):
        for rec in self:
            if rec.date_payroll:
                rec.invoice_number = rec.date_payroll.strftime('%m')
            else:
                rec.invoice_number = None

    def _compute_is_user(self):
        for rec in self:
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if employee_id:
                rec.is_user = rec.employee_id.id == employee_id.id
            else:
                rec.is_user = False

    def default_is_user(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if employee_id:
            is_user = self._context.get('default_employee_id') == employee_id.id
        else:
            is_user = False
        return is_user

    @api.depends('employee_id')
    def _compute_advance(self):
        for rec in self:
            if rec.employee_id:
                rec.advance = rec.employee_id.advance
            else:
                rec.advance = 0

    @api.onchange('employee_id')
    def update_niff_and_stat(self):
        for rec in self:
            if rec.employee_id:
                rec.niff = rec.employee_id.niff
                rec.stat = rec.employee_id.stat

    @api.model
    def create(self, vals):
        res = super(IgyPayroll, self).create(vals)
        if vals.get('niff'):
            res.sudo().employee_id.niff = vals.get('niff')
        if vals.get('stat'):
            res.sudo().employee_id.stat = vals.get('stat')
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('niff'):
                rec.sudo().employee_id.niff = vals.get('niff')
            if vals.get('stat'):
                rec.sudo().employee_id.stat = vals.get('stat')
        res = super(IgyPayroll, self).write(vals)
        return res

    @api.multi
    def action_send_mail_facture(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('igy_payroll', 'email_template_edi_payroll')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        # self.write({'status':'envoye'})
        ctx = {
            'default_model': 'igy.payroll',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",   
            'force_email': True,
            'igy_payroll_id' : self.id

        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx
        }

