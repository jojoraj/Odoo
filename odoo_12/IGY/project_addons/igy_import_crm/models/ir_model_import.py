from odoo import fields, models, api


class IrModelImport(models.Model):
    _inherit = 'ir.model.import'
    _description = 'Import template line'

    file = fields.Binary(
        string="Fichier d'import",
        attachment=True
    )
    file_name = fields.Char(
        string="Nom du fichier"
    )

