from odoo import models, fields, _

class cours(models.Model):
    _name = "cour.cour"

    name = fields.Char(string="Nom de cours")
    enseignant = fields.Char(string="Enseignant")
    description = fields.Char(string="Déscription")
    support = fields.Char(string="Support")
