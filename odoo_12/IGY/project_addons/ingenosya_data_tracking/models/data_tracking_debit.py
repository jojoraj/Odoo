# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from odoo import http
from datetime import date, timedelta


class Debit(models.Model):
    _name = "data.tracking.debit"
    _order = "date asc"

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id.id)
    remaining_data = fields.Float(string="Remaining data", copy=False)
    note = fields.Char(string="Comment", copy=False)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    daily_cons = fields.Float(string="Daily consumption", copy=False)

    data_tracking_id = fields.Many2one(
        string='Data tracking',
        comodel_name='data.tracking',
        ondelete='restrict',
    )
    project_ids = fields.Many2many(
        comodel_name='project.project',
        string='Projects',
        relation="data_tracking_debit_project",
        column1='data_tracking_id',
        column2='project_id'
    )
    _sql_constraints = [
        # ('unique_date','unique(date,data_tracking_id)','You have already entered this date')
    ]
    #ALTER TABLE data_tracking_debit DROP CONSTRAINT data_tracking_debit_unique_date;

    
    