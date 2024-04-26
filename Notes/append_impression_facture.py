def get_download_link(self):
        domain = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.env['sale.order'].sudo().search(domain)
        url = self.env['pos.order'].sudo().search(
                [('lines.sale_order_origin_id', 'in', orders.ids)]).account_move
        domain_server = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        result = []
        for account in url:
            for url in orders:
                if url:
                    with_download = domain_server + url.get_portal_url(report_type='pdf', download=True)
                    result.append({'account': account,
                                   'with_download': with_download})
        return result

#principe append --------------------------------

liste = [1, 2, 3]
liste.append(4)
nombre = "cinq"
liste.append(nombre)
print(liste)   # Sortie : [1, 2, 3, 4, ‘cinq’]

------------------------------------------------->

def get_minimum_price(self):
    prices = []
    name = self.env['fleet.vehicle.model.category'].search_read([], ['name'])
    prices.append(self.env['account.minimum.price'].search_read([], ['minimum_price']))
    return {'price': prices}

>>

def get_minimum_price(self):
    result = []
    category_ids = self.env['fleet.vehicle.model.category'].search([])
    for category in category_ids:
        result.append({'name': category.name, 'price': category.minimum_price_id.minimum_price})
    return {'result': result}