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

#------------------------------------------------->

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


#------------------------------------------------------

# Ajout pagination

def get_download_link(self):
        domain = [('opportunity_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.env['sale.order'].sudo().search(domain)
        url = self.env['pos.order'].sudo().search(
                [('lines.sale_order_origin_id', 'in', orders.ids)]).account_move
        domain_server = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        page_size = 10
        current_page = 1

        leads = self.search([
            ('stage_id.id', '=', self.env.ref('esanandro_crm.stage_lead6').id)
        ])
        count_lead = len(leads)
        paged_results = []

        start_index = (current_page - 1) * page_size
        end_index = current_page * page_size

        for i, rec in enumerate(leads):
            if i >= start_index and i < end_index:
                if rec.stage_id.id == rec.env.ref('esanandro_crm.stage_lead6').id:
                    print("rec id: ", rec.id, " stage id: ", rec.stage_id.id, " =? ", rec.env.ref('esanandro_crm.stage_lead6').id)
                    for account in url:
                        for url in orders:
                            if url:
                                with_download = domain_server + url.get_portal_url(report_type='pdf', download=True)
                                paged_results.append({
                                                      'page': current_page,
                                                      'content': [
                                                            account,
                                                            with_download
                                                        ],
                                                      'count': count_lead,
                                                      'page_size': page_size,
                                                      })
        return paged_results
