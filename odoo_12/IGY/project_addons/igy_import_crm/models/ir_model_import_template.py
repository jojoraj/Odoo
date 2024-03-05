from odoo import fields, models, api


class IrModelImportTemplate(models.Model):
    _inherit = 'ir.model.import.template'
    _description = 'Template d\'importation'

    import_progress = fields.Integer(
        string="Progression"
    )
    line_treated = fields.Char(
        string="Line treated"
    )
    action_domain = fields.Char(string="Action domain")


    def _get_import_vals(self, *args):
        return {
            'import_tmpl_id': self.id,
            'test_mode': self._context.get('test_mode'),
            'new_thread': self._context.get('new_thread', self.new_thread),
            'args': repr(args),
            'log_level': self.log_level,
            'log_returns': self.log_returns,
            'file': self.file,
            'file_name': self.file_name
        }
