from odoo import fields, models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_res_groups(self):
        """
        This function gets or create groups for internal department
        """
        cr = self._cr
        cr.execute("""
                SELECT id FROM res_groups 
                WHERE category_id = {} AND name LIKE 'Commercial'
            """.format(self.env.ref('base.module_category_administration').id))
        group = cr.fetchall()
        if group:
            return group[0][0]
        else:
            insert_query = """
                INSERT INTO res_groups (name,category_id) VALUES (%s,%s)
            """
            cr.execute(insert_query,('Commercial',self.env.ref('base.module_category_administration').id))
            cr.commit()
            cr.execute('SELECT LASTVAL()')
            lastid = cr.fetchone()[0]
            return lastid

    @api.model
    def add_group_global_pipeline(self):
        """ ADD GROUPS TO MENUS GLOBAL PIPELINE """
        crm_global_pipeline_tab = [self.env.ref('igy_custom_crm.global_view_pipeline').id,
                                   self.env.ref('igy_custom_crm.crm_global_stage_menu').id]
        res_groups = self.env['res.groups'].sudo().browse(self.get_res_groups())
        res_groups._update_user_groups_view()
        self.env['ir.actions.actions'].clear_caches()
        for crm_global_pipeline_menu in crm_global_pipeline_tab:
            menu = self.sudo().browse(crm_global_pipeline_menu)
            menu.gid = self.get_res_groups()
            menu.update({
                'groups_id': [(4, self.get_res_groups())]
            })
