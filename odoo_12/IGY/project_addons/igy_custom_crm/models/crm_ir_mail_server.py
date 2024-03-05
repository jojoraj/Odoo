from odoo import models

class crmIrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                    attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                    body_alternative=None, subtype_alternative='plain'):
        res = super(crmIrMailServer, self).build_email(email_from, email_to, subject, body, email_cc, email_bcc, reply_to,
                    attachments, message_id, references, object_id, subtype, headers,
                    body_alternative, subtype_alternative)
        if object_id:
            sep = object_id.index('-')
            res_id = object_id[:sep]
            model_id = object_id[sep+1:]

            if model_id == 'crm.lead':
                crm_mail_from = self.env["crm.lead"].browse(int(res_id)).email_from
                if crm_mail_from:
                    if crm_mail_from != email_to:
                        del res["To"]
                        res["To"] = crm_mail_from
                        return res
        return res

