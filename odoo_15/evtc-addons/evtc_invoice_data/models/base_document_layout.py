from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    logo_all = fields.Binary(related='company_id.logo_all', readonly=False)
