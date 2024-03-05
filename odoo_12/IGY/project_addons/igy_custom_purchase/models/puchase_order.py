# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderCustoms(models.Model):
    _inherit = "purchase.order" 
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
        'raison': [('readonly', True)],
    }
    raison_rh = fields.Html(default= """
    <p style="color: #B9B9B9;"> Veuillez préciser l'ordre de priorité de vos demandes  :
    [Urgent] 
    [Critique] 
    [Normal]
    <p/><p> </br> <p/>
    """)    
    state = fields.Selection([
        ('raison',"Demande d'achat"),
        ('draft', 'En attente de confirmation'),
        ('to approve', 'Demande à approuver'),
        ('purchase', 'Demande approuvé'),
        ('livraison', 'En attente de livraison'),
        ('recu', "Demande livré"),
        ('termine', "Demande terminé"),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='raison', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=False, states=READONLY_STATES, change_default=True, track_visibility='always', help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    @api.multi
    def button_raison(self):
        self.state = 'draft'

    @api.multi
    def button_livraison(self):
        mail_obj = self.env['mail.mail']

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/mail/view?model=%s&res_id=%d' % (self._name, self.id)

        body_html = """<p>
                Bonjour , <br/><br/>
                    Votre demande d'achat est payé, et maintenant en attente de livraison.
                    <br/>
                    <br/>
                    <a style="padding: 8px 12px; font-size: 12px; color: #FFFFFF; text-decoration: none !important; font-weight: 400; background-color: #875A7B; 
                              border: 0px solid #875A7B; border-radius: 3px" 
                       href="""+base_url+""" target="_blank" rel="noreferrer">Voir Commande fournisseur</a>
                <br/><br/>
                INGENOSYA MADAGASCAR
            </p>
        """
        for abonnes in self.message_partner_ids :
            mail = mail_obj.create({
                'subject': f"INGENOSYA | Demande d'achat-ref({self.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to':abonnes.email,
                'state': 'outgoing',
                'notif_layout':'mail.mail_notification_light',
            })
            mail.send()
            
        self.state = 'livraison'
    @api.multi 
    def button_approve(self,force=False):
        mail_obj = self.env['mail.mail']


        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/mail/view?model=%s&res_id=%d' % (self._name, self.id)

        body_html = """<p>
                Bonjour , <br/><br/>
                    Votre commande a été approuvé par notre Directeur Géneral ,et en attente de signature de chèque.
                    <br/>
                    <br/>
                    <a style="padding: 8px 12px; font-size: 12px; color: #FFFFFF; text-decoration: none !important; font-weight: 400; background-color: #875A7B; 
                              border: 0px solid #875A7B; border-radius: 3px" 
                       href="""+base_url+""" target="_blank" rel="noreferrer">Voir Commande fournisseur</a>
                    <br/><br/>
                INGENOSYA MADAGASCAR
                </p>
            """
        mail = mail_obj.create({
            'subject': f"INGENOSYA | Demande d'achat-ref({self.name})",
            'body_html': body_html,
            'email_from': 'contact@ingenosya.mg',
            'email_to': self.partner_id.email,
            'auto_delete': True,
            'state': 'outgoing',
            'notif_layout':'mail.mail_notification_light',
        })
        mail.send()
        for abonnes in self.message_partner_ids :
            mail = mail_obj.create({
                'subject': f"INGENOSYA | Demande d'achat-ref({self.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to':abonnes.email,
                'state': 'outgoing',
                'notif_layout':'mail.mail_notification_light',
            })
            mail.send()
        self.state  = 'purchase'

    @api.multi
    def button_recu(self):
        mail_obj = self.env['mail.mail']

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/mail/view?model=%s&res_id=%d' % (self._name, self.id)

        body_html = """<p>
                Bonjour , <br/><br/>
                    Votre demande d'achat est maintenant dans nos locaux, vous pouvez passez dans le bureaux des administrations pour le récuperer.
                    <br/>
                    <br/>
                    <a style="padding: 8px 12px; font-size: 12px; color: #FFFFFF; text-decoration: none !important; font-weight: 400; background-color: #875A7B; 
                              border: 0px solid #875A7B; border-radius: 3px" 
                       href="""+base_url+""" target="_blank" rel="noreferrer">Voir Commande fournisseur</a>
                <br/><br/>
                INGENOSYA MADAGASCAR
            </p>
        """
        for abonnes in self.message_partner_ids :
            mail = mail_obj.create({
                'subject': f"INGENOSYA | Demande d'achat-ref({self.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to':abonnes.email,
                'state': 'outgoing',
                'notif_layout':'mail.mail_notification_light',
            })
            mail.send()
        self.state = 'recu'

    @api.multi
    def button_finish(self):
        self.state = 'termine'

    @api.multi 
    def button_confirm(self):
        mail_obj = self.env['mail.mail']

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/mail/view?model=%s&res_id=%d' % (self._name, self.id)

        body_html = """<p>
                Bonjour , <br/><br/>
                    Votre demande a été confirmée, et en attente d'approbation.
                    <br/>
                    <br/>
                    <a style="padding: 8px 12px; font-size: 12px; color: #FFFFFF; text-decoration: none !important; font-weight: 400; background-color: #875A7B; 
                              border: 0px solid #875A7B; border-radius: 3px" 
                       href="""+base_url+""" target="_blank" rel="noreferrer">Voir Commande fournisseur</a>
                <br/><br/>
                INGENOSYA MADAGASCAR
            </p>
        """
        for abonnes in self.message_partner_ids :
            mail = mail_obj.create({
                'subject': f"INGENOSYA | Demande d'achat-ref({self.name})",
                'body_html': body_html,
                'email_from': 'contact@ingenosya.mg',
                'auto_delete': True,
                'email_to':abonnes.email,
                'state': 'outgoing',
                'notif_layout':'mail.mail_notification_light',
            })
            mail.send()
        self.state  = 'to approve'

    @api.multi
    def button_draft(self):
        self.state = 'raison'
    
    @api.model
    def _default_employee_id(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    request_id = fields.Many2one('hr.employee', string='Demandeur', default=_default_employee_id, required=False, readonly=True)
    recepient_id = fields.Many2one('hr.employee', string='Bénéficiaire', required=False)
    recepient_ids = fields.Many2many('hr.employee', string='Bénéficiaires', required=False)
    char_recepient_ids = fields.Char(string='Bénéficiaires', compute="compute_recepients", required=False, store=False)
    categorie = fields.Char(store=False, string="Catégorie", compute="_compute_category")

    @api.multi
    def _compute_category(self):
        for purchase in self:
            articles_ids = purchase.order_line
            if len(articles_ids) != 0:
                purchase.categorie = ", ".join(articles_ids.mapped('product_id.categ_id.name'))

    @api.multi
    def compute_recepients(self):
        for purchase in self:
            if purchase.recepient_id:
                if purchase.recepient_id.id not in purchase.recepient_ids.ids:
                    purchase.write({'recepient_ids': [(4,purchase.recepient_id.id)] })
                    purchase.recepient_ids = [(4, purchase.recepient_id.id)]
            recepient_ids = purchase.recepient_ids
            if len(recepient_ids) != 0:
                purchase.char_recepient_ids = ", ".join(recepient_ids.mapped('name'))
            else:
                purchase.char_recepient_ids = ""
