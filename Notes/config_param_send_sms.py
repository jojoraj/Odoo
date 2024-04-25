send_sms = self.env['ir.config_parameter'].sudo().get_param('evtc_lmfs.customer_sms', 'False')
        for rec in self:
            if values.get('stage_id') == self.env.ref('esanandro_crm.stage_lead6').id and send_sms == 'True':
                rec.send_notification_crm_end()