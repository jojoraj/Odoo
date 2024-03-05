# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from datetime import date, timedelta


class Tracking(models.Model):
    _name = "data.tracking"

    name = fields.Char(
        string="Name", default=lambda self: self.get_employee_name(), copy=False)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", default=lambda self: self.get_employee_id(), copy=False)
    numero = fields.Char(string="Numéro de telephone")
    user_id = fields.Many2one(
        'res.users', default=lambda self: self.env.uid, copy=False)
    employee_image = fields.Binary(
        string="Image", related='employee_id.image_small')
    rate_validity = fields.Date(string="Rate validity", copy=False)
    weekly_cons = fields.Float(
        string="Average daily consumption (mo)", compute="_compute_weekly_cons", copy=False)
    average_base = fields.Integer(string="Average base", default=5, copy=False)
    active = fields.Boolean(string="Active", default=True, related='employee_id.active', store=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id)
    remaining_data = fields.Float(
        string='Remaining data (mo)', compute="_get_last_remaining_data", store=True, copy=False, default=0)
    data_tracking_debit_ids = fields.One2many(
        string='Debit',
        comodel_name='data.tracking.debit',
        inverse_name='data_tracking_id',
        copy=False
    )
    data_tracking_credit_ids = fields.One2many(
        string='Credit',
        comodel_name='data.tracking.credit',
        inverse_name='data_tracking_id',
        copy=False
    )

    has_manager_group = fields.Char(compute='_has_manager_group', copy=False)

    weekly_data_mean = fields.Float(string="Average weekly consumption (mo)",compute="_compute_weekly_data_consumptions")
    data_to_predict = fields.Float(string="Data to predict (mo)",compute='_compute_data_to_predict')
    data_to_buy = fields.Float(string="Data to buy (mo)",compute='_compute_data_to_buy')

    #fonction for data cron
    def get_date(self):
        today = date.today()
        data_trackings =   self.env["data.tracking"].search([('rate_validity','<',today)]) 

        if len(data_trackings)== 0:
            return 0
        for data  in data_trackings :
                
            data['rate_validity']= False
            data['remaining_data']=float(0)
            new_debit = self.env['data.tracking.debit'].create({
            'company_id' : int(data["currency_id"]) ,
            'currency_id':int(data["company_id"]),
            'note': str('Les données sont éxpirées.'), 
            'project_ids': False,
            'data_tracking_id':int(data["id"]) ,
            'remaining_data':float(0),    
            'daily_cons' :  False,         
                })    
          
    @api.model
    @api.depends('data_to_predict')
    def _compute_data_to_buy(self):
        if self.data_to_predict:
            data_to_predict = self.data_to_predict/1000
            data_to_predict = int(data_to_predict)
            data_to_predict+=1
            data_to_predict = data_to_predict * 1000
            self.data_to_buy = data_to_predict

    @api.model
    @api.depends('weekly_data_mean')
    def _compute_data_to_predict(self):
        if self.weekly_data_mean:
            last_debit = self.data_tracking_debit_ids[-1].remaining_data
            data_to_predict = self.weekly_data_mean -last_debit
            if data_to_predict < 0:
                data_to_predict = 0
            self.data_to_predict = data_to_predict


    @api.model
    @api.depends('weekly_cons')
    def _compute_weekly_data_consumptions(self):
        if self.weekly_cons:
            number_week = self.average_base / 5
            self.weekly_data_mean = self.weekly_cons * (6*number_week)

    @api.multi
    @api.constrains('employee_id')
    def unique_data_tracking(self):
        for rec in self:
            employee_id = int(rec.employee_id)
            data_tracking = self.env['data.tracking'].search([('employee_id','=',employee_id),('id','!=',rec.id)])
            if data_tracking and data_tracking.active:
                raise exceptions.ValidationError(_("Employee already have data tracking"))
    @api.multi
    @api.constrains('average_base')
    def not_null_average_base(self):
        for rec in self:
            if  rec.average_base == 0:
                raise exceptions.ValidationError(_("Average base cannot be equal to 0"))

    @api.onchange('employee_id')
    def change_employee_id(self):
        for data_tracking in self:
            if data_tracking['employee_id']:
                employee = self.env['hr.employee'].browse(
                    int(data_tracking['employee_id']))

                data_tracking['name'] = _("Data Tracking of ")+employee.name
                data_tracking['user_id'] = employee.user_id

    @api.model
    def get_employee_id(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)])
        if employee:
            return employee.id
        else:
            return

    @api.model
    def get_employee_name(self):
        """Get the current employee name """
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)])
        if employee:
            res = _("Data Tracking of"),employee.name
            return res
        else:
            return ''

    @api.multi
    def _compute_weekly_cons(self):
        for rec in self:
            debits_data_trackings = rec.data_tracking_debit_ids
            debits = debits_data_trackings[-1:-(rec.average_base+1):-1]
            consumptions = []
            for debit in debits:
                consumptions.append(debit.daily_cons)
            if rec.average_base == 0:
                rec.weekly_cons = 0
            else:
                mean = sum(consumptions)/rec.average_base
                rec.weekly_cons = mean

    @api.depends('data_tracking_debit_ids', 'data_tracking_credit_ids')
    def _get_last_remaining_data(self):
        for data_tracking in self:
            debits = data_tracking.data_tracking_debit_ids
            credits = data_tracking.data_tracking_credit_ids
            last_credit = None
            last_debit = None

            remaining_data = 0

            if len(debits) > 0:
                last_debit = debits[-1]
                remaining_data_debit = last_debit.remaining_data
                remaining_data = remaining_data_debit
            
            if len(credits) > 0:
                last_credit = credits[-1]
                remaining_data_credit = remaining_data + last_credit.recharge
                remaining_data = remaining_data_credit
                
            

            if last_credit != None and last_debit != None:
                if last_credit.date > last_debit.date:
                    remaining_data = remaining_data_credit
                elif last_credit.date < last_debit.date:
                    remaining_data = remaining_data_debit
                else:
                    remaining_data = remaining_data_debit
            if remaining_data < 0:
                raise exceptions.ValidationError("Votre données restants ne doit pas être négatifs.")

            data_tracking.remaining_data = remaining_data

    @api.multi
    def _has_manager_group(self):
        for res in self:
            user_id = self.env.uid
            has_manager_group = self.env.user.has_group('hr.group_hr_manager')
            if has_manager_group:
                result = 'True'
            else:
                result = 'False'

            res.has_manager_group = result

    @api.onchange('data_tracking_debit_ids')
    def onchange_change_remaining_data(self):
        id = self._origin.id
        for res in self:
            debits = list(res.data_tracking_debit_ids)
            debits.sort(key=lambda k: k.date)
            if len(debits) > 0:
                if debits[-1].remaining_data:
                    for i in range(len(debits)):
                        difference_one_day = debits[i].date - debits[i-1].date != timedelta(days=1)
                        is_not_monday = date.weekday(debits[i].date) != 0
                        is_monday = date.weekday(debits[i].date) == 0
                        last_day_not_friday = debits[i].date - debits[i-1].date != timedelta(days=3)


                        (daily_consumption,credit_response) = self.create_data_tracking(debits[i-1], debits[i], id,i)

                        

                        if (difference_one_day and is_not_monday and i !=0 and not credit_response) or  (is_monday and last_day_not_friday and i!=0)  :
                            daily_consumption = 0

                        debits[i].daily_cons = daily_consumption
                        

    @api.model
    def create_data_tracking(self, last_debit, res, id,i):
        day_before = res['date'] - timedelta(days=1)
        # Check if the day is monday
        if date.weekday(day_before) == 6:
            day_before -= timedelta(days=2)

        data_tracking_id = id
        # Check if there is a credit
        credit_dates = self.env['data.tracking.credit'].search(
            [('date', '=', res['date']), ('data_tracking_id', '=', data_tracking_id)])
        if len(credit_dates) > 0:
            credit = []
            for credit_date in credit_dates:
                credit.append(credit_date.recharge)
            credit = sum(credit)
            #credit = credit_date[0].recharge
            credit_response=True
        else:
            credit = 0
            credit_response = False

        difference_one_day = res.date - last_debit.date != timedelta(days=1)
        is_not_monday = date.weekday(res.date) != 0
        is_monday = date.weekday(res.date) == 0
        last_day_not_friday = res.date - last_debit.date != timedelta(days=3)
        print(i,res.date)
        if (difference_one_day and is_not_monday ) or  (is_monday and last_day_not_friday )  :
            remaining_data = 0
        
        else:
            remaining_data = last_debit.remaining_data

        update_daily_consumption = remaining_data + credit - res.remaining_data
        if update_daily_consumption < 0:
            update_daily_consumption = 0
        return (update_daily_consumption,credit_response)
    
    