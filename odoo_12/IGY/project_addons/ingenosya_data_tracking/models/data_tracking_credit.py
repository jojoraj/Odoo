# -*- coding: utf-8 -*-

from odoo import fields,models,api
from datetime import date,timedelta
class Credit(models.Model):
    _name="data.tracking.credit"
    _order="date asc"

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    recharge = fields.Float(string="Recharge")
    note = fields.Char(string="Comment")
    date = fields.Date(string='Date',default=fields.Date.context_today)
    rate_id = fields.Many2one('data.tracking.rate',string="Data rate")

    data_tracking_id = fields.Many2one('data.tracking')
    has_manager_group = fields.Char(compute='_has_manager_group')

    @api.model
    def create(self,vals):
        res = super(Credit,self).create(vals)
        rate_id = int(res['rate_id'])
        data_rate = self.env['data.tracking.rate'].browse(rate_id)

        data_tracking = self.env['data.tracking'].browse(int(res['data_tracking_id'])) 
        if data_rate['type_validity'] == 'Cumulative':
            if data_tracking['rate_validity'] == False:
                data_tracking['rate_validity'] =  res['date']+ timedelta(data_rate['data_validity'])
            else:
                data_tracking['rate_validity']+= timedelta(data_rate['data_validity'])

        elif data_rate['type_validity'] == 'New':
            data_tracking['rate_validity'] =  res['date']+ timedelta(data_rate['data_validity']) 

        debit = self.env['data.tracking.debit'].search([('date','=',res['date']),('data_tracking_id','=',int(res['data_tracking_id']))], limit=1, order='id desc')
        day_before = res['date'] - timedelta(days=1)
        if date.weekday(day_before) == 6:
            day_before -= timedelta(days=2)
        last_debit = self.env['data.tracking.debit'].search([('date','=',day_before),('data_tracking_id','=',int(res['data_tracking_id']))], limit=1,  order='id desc')
        if debit:
            daily_cons = last_debit['remaining_data'] + res['recharge'] - debit['remaining_data']
            if daily_cons < 0:
                daily_cons = 0
            debit['daily_cons'] = daily_cons
        return res

    @api.multi
    def unlink(self):
        for credit in self:
            data_tracking = self.env['data.tracking'].browse(int(credit['data_tracking_id']))
            data_rate = self.env['data.tracking.rate'].browse(int(credit['rate_id']))
            if data_tracking['rate_validity']:
                data_tracking['rate_validity'] -= timedelta(days=data_rate['data_validity'])

            debit = self.env['data.tracking.debit'].search([('data_tracking_id','=',int(credit['data_tracking_id'])),(['date','=',credit['date']])])
            # update corresponding debit  
            if len(debit) > 0 :
                debit = debit[0]
                debit['daily_cons'] = 0
            

        rec = super(Credit,self).unlink()
        return rec


    @api.onchange('rate_id')
    def change_rate(self):
        for res in self:
            if res.rate_id:
                res.recharge = res.rate_id.data
    
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

       