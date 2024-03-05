
from odoo import api, fields, models, tools
import base64
import io


class NewsLetter(models.Model):
    _name = 'news.letter'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Titre")
    description = fields.Html(string="Description")
    author_id = fields.Many2one('res.users', string="Autheur", default=lambda self: self.env.user.id)
    date = fields.Date(string="Date publication", default=fields.Date.today())
    image = fields.Binary(string="Image", store=True)
    is_anonymous = fields.Boolean(string="Publier de maniere anomyme", default=True)
    tag_ids = fields.Many2many('news.letter.tag', string="Tags")
    video = fields.Binary(string='Video')
    video_filename = fields.Char(string='Video Filename')
    video_embed_code = fields.Char(string='Video Embed Code')

    image_1 = fields.Binary(string="Image 1")
    image_2 = fields.Binary(string="Image 2")
    image_3 = fields.Binary(string="Image 3")
    image_4 = fields.Binary(string="Image 4")
    image_5 = fields.Binary(string="Image 5")
    image_6 = fields.Binary(string="Image 6")
    image_7 = fields.Binary(string="Image 7")
    image_8 = fields.Binary(string="Image 8")
    image_9 = fields.Binary(string="Image 9")


    @api.model
    def create(self, vals_list):
        res = super(NewsLetter,self).create(vals_list)
        if res and res.video:
            res.video_embed_code = '<iframe width="560" height="315" src="data:video/mp4;base64,%s" frameborder="0" allow="autoplay; clipboard-write; encrypted-media;" allowfullscreen></iframe>' % (res.video.decode("utf-8"))
        else:
            res.video_embed_code = False
        return res

    def write(self, vals):
        if "video" in vals:
            vals["video_embed_code"] = '<iframe width="560" height="315" src="data:video/mp4;base64,%s" frameborder="0" allow="autoplay; clipboard-write; encrypted-media;" allowfullscreen></iframe>' % (vals["video"]) if vals["video"] else False
        res = super(NewsLetter, self).write(vals)
        return res

