# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClasseClasse(models.Model):

    _name = 'classe.classe'
    _description = 'Class record'
    _sql_constraints = [
        ('class_uniq', 'UNIQUE (name)', 'Classe existante!')
    ]

    name = fields.Char(string='New class')
    student_class_ids = fields.One2many('student.student', 'student_class')
                                        # classe, champ


