from datetime import datetime, date, timedelta
from odoo import models, fields, modules, tools, api, _
from odoo.exceptions import Warning
import base64


class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    attach_ids = fields.One2many('ir.attachment', 'doc_id', 'Attachments')
    desc_short = fields.Char('Brieve description', compute='_compute_desc_short')
    group_id = fields.Many2one('res.groups', 'Groupe', required=True, default=43)
    document_name = fields.Many2one('employee.checklist', string='Document', required=False)
    name = fields.Char(string='Nom du document', required=True, copy=False)

    @api.multi
    def _compute_desc_short(self):
        for each in self:
            if each.description:
                each.desc_short = str(each.description[0:35]) + '...' if len(each.description) > 30 else each.description

    @api.multi
    def sub_document_view(self):

        # update old values set before the use of this module
        query = "SELECT attach_id3,doc_id FROM doc_attach_rel"
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        for each in res:
            self.env['ir.attachment'].browse(each[0]).sudo().write({'doc_id': each[1], 'public': True})
        return self.env['ir.attachment'].sub_view(self.id)


x = 0


class SubDocument(models.Model):
    _inherit = 'ir.attachment'
    doc_id = fields.Many2one('hr.employee.document', 'Document')

    @api.model_create_multi
    def create(self, vals_list):
        global x
        if self._context.get('default_doc_id'):
            x = int(self._context.get('default_doc_id'))
            for vals_dict in vals_list:
                vals_dict['doc_id'] = x
                vals_dict['public'] = True
        result = super(SubDocument, self).create(vals_list)
        if result and x:
            # Don 't save record with res_model 'ir.attachment'
            if result['res_model'] != 'ir.attachment':
                query = f"INSERT INTO doc_attach_rel(doc_id,attach_id3) VALUES ({x},{result.id})"
                self.env.cr.execute(query)
        return result

    # def write(self, vals):
    #     if len(self) == 1 and self.type == 'empty' and len(self.activity_ids):
    #         if not vals.get('type'):
    #             if vals.get('url'):
    #                 vals['type'] = 'url'
    #             if vals.get('datas'):
    #                 vals['type'] = 'binary'
    #         if vals.get('type') in ['url', 'binary']:
    #             self.activity_ids.action_feedback()
    #
    #     vals = self._set_folder_settings(vals)
    #     return super(SubDocument, self).write(vals)

    @api.multi
    def sub_view(self, d_id=None):
        # raise Warning('Tafa')
        query = f"SELECT attach_id3 FROM doc_attach_rel WHERE doc_id = {d_id}"
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        res2 = []
        for i in res:
            res2.append(i[0])
        domain = ['&', ('id', 'in', res2), '|', ('public', '=', True), ('public', '=', False)]
        return {
            'name': _('Fichiers'),
            'domain': domain,
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,form',
            'view_type': 'kanban',
            # 'views': [(self.env['ir.ui.view'].search('name', '=', 'ir.attachment.inherit3.form_view')[0].id, 'form')],
            # 'help': _('''<p class="oe_view_nocontent_create">
            #                Click to Create for New Documents
            #             </p>'''),
            'limit': 80,
            'context': "{'default_doc_id': '%s'}" % d_id,
        }


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _document_count(self):
        for each in self:
            document_ids = 0
            uid = self.env.user.id
            query = f"SELECT gid FROM res_groups_users_rel WHERE uid = {uid}"
            self.env.cr.execute(query)
            groups = self.env.cr.fetchall()
            res = []
            for g in groups:
                res.append(g[0])
            for r in res:
                document = self.env['hr.employee.document'].search(['&', ('employee_ref', '=', each.id), ('group_id', '=', r)])
                if document:
                    document_ids += len(document)
            each.document_count = document_ids

    @api.multi
    def document_view(self):
        self.ensure_one()
        dm_list = []
        document_ids = self.env['hr.employee.document'].search([('employee_ref', '=', self.id)])
        for each in document_ids:
            for at_ids in each.doc_attachment_id:
                dm_list.append(at_ids.id)

        uid = self.env.user.id
        query = f"SELECT gid FROM res_groups_users_rel WHERE uid = {uid}"
        self.env.cr.execute(query)
        groups = self.env.cr.fetchall()
        res = []
        for each in groups:
            res.append(each[0])

        # dm = []
        # leng = len(dm_list)
        # if leng > 1:
        #     for each in dm_list:
        #         if each == dm_list[-1]:
        #             dm.append(('id', '=', each))
        #         else:
        #             dm.append('|')
        #             dm.append(('id', '=', each))
        # elif leng == 1:
        #     dm.append(('id', '=', dm_list[0]))
        # else:
        #     print('Tsisy oh')
        # print(dm)
        domain = [
            '&',
            ('employee_ref', '=', self.id),
            ('group_id', 'in', res)]

        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'kanban',
            # 'views': [()]
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }
