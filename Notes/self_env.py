def get_partner_info(self):
    partners = self.env['res.partner'].search_read([('email', '!=', False), ('phone', '!=', False)], ['phone', 'name', 'email', 'image_1920'])
    return {'partner': partners}