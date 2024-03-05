# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import AccessError, UserError, ValidationError

class Holidays(models.Model):
    _inherit = "hr.leave"
    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        employee_id = values.get('employee_id', False)
        #Type de congé

        leave_categorie = values.get("holiday_status_id")
        """
        Dans la base de donées :
            self.env.ref('__export__.hr_leave_type_8_43dc6e2d') : Congé sans solde
            self.env.ref('__export__.hr_leave_type_11_ab0916b0'): Récuperation
        """

        #Etiquette des employés
        categories_ids =self.env['hr.employee'].browse(employee_id).mapped('category_ids')  
        parent_ids = []
        for categorie  in categories_ids :
            parent = categorie.parent_id
            if parent :
                parent_ids.append(categorie.parent_id)  

        """
        Dans la base de donées :
            self.env.ref('__export__.hr_employee_category_8_60ff69b6') :Freelance,
            self.env.ref('__export__.hr_employee_category_13_d1bb1824') :Période d'essai,
            self.env.ref('__export__.hr_employee_category_1_f40ff767') : Consultant
            self.env.ref('__export__.hr_employee_category_3_096f1a02') : Stagiaire 
        """

        freelance = self.env.ref('__export__.hr_employee_category_8_60ff69b6')
        periode = self.env.ref('__export__.hr_employee_category_13_d1bb1824')
        consultant = self.env.ref('__export__.hr_employee_category_3_096f1a02')
        stagiaire = self.env.ref('__export__.hr_employee_category_1_f40ff767')

        #Un employé de type consultant ou stagiaire ne peux prendre qu'un congé de type sans solde
        try :
            if freelance in categories_ids or periode in categories_ids or stagiaire in categories_ids or consultant in categories_ids or freelance in parent_ids or periode in parent_ids or stagiaire in parent_ids or consultant in parent_ids :
                if int(leave_categorie) != 8 or int(leave_categorie) != 11 :
                    raise ValidationError("(Stagiaire ,consultant) Vous ne pouvez prendre que des congés de type : 'Congé sans solde'ou 'Récupération'. ")  
        except :        
            pass    
        if not values.get('department_id'):
            values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})
        holiday = super(Holidays, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        if self._context.get('import_file'):
            holiday._onchange_leave_dates()
        if not self._context.get('leave_fast_create'):
            holiday.add_follower(employee_id)
            if 'employee_id' in values:
                holiday._sync_employee_details()
            if not self._context.get('import_file'):
                holiday.activity_update()
        return holiday
