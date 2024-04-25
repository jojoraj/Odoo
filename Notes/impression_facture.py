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