# -*- coding: utf-8 -*-
from datetime import date, datetime

from odoo import models, fields, api, _

# from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    additional_note = fields.Char(string='Additional Note')

class StudentStudent(models.Model):

    _name = 'student.student'
    _inherit = 'mail.thread'
    _description = 'Student Record'

    # class_id = fields.Many2one('anaran le classe')
    partner_related_rel = fields.Many2one('classe.classe', string="Class")
    name = fields.Char(string='Name', requierd=True, track_visibility='always')
    age = fields.Integer(string='Age', track_visibility='onchange')
    matricule = fields.Char(string='matricule')
    blood_type_A = fields.Boolean(string='Groupe sanguin A')
    blood_type_B = fields.Boolean(string='Groupe sanguin B')
    blood_type_O = fields.Boolean(string='Groupe sanguin O')
    blood_type_AB = fields.Boolean(string='Groupe sanguin AB')
    photo = fields.Binary(string='Image')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others','Others')], string='Gender')
    student_dob = fields.Date(string="Date of Birth")
    student_blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        string= 'Blood Group')
    nationality = fields.Many2one('res.country', string='Nationality')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], required=True, default='draft')

    matricule = fields.Char(string="Service Number", readonly=True, required=True, copy=False, default=' ')

    @api.model

    def create(self, vals):
        if vals.get('student_dob'):
            date_str = vals['student_dob']
            date_format = '%Y-%m-%d'

            date_obj = datetime.strptime(date_str, date_format)

            vals['age'] = self.calculate_age(date_obj)

        if vals.get('matricule', ' '):
           vals['matricule'] = self.env['ir.sequence'].next_by_code(
               'self.service') or (' ')
        result = super(StudentStudent, self).create(vals)
        # le super manampy sy manao appel an'ilay fonction predefinit
        return result

    def calculate_age(self, date_obj):
        if date_obj:
            today = date.today()
            return today.year - date_obj.year

    def action_test(self):
        print("Boutton cliquéééé!!!!!!!!!!!!!")

    @api.multi
    def write(self, vals):
        if vals.get('student_dob'):
            date_str = vals['student_dob']
            date_format = '%Y-%m-%d'
            date_obj = datetime.strptime(date_str, date_format)

            vals['age'] = self.calculate_age(date_obj)

        res = super(StudentStudent, self).write(vals)
        return res

    def action_blood(self):
        if self.student_blood_group in ('A+', 'A-'):
            self.blood_type_A = True
        elif self.student_blood_group in ('B+', 'B-'):
            self.blood_type_B = True
        elif self.student_blood_group in ('O+', 'O-'):
            self.blood_type_O = True
        elif self.student_blood_group in ('AB+', 'AB-'):
            self.blood_type_AB = True
