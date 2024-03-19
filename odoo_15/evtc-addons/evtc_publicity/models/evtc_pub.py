##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2021 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models


class EvtcPub(models.Model):
    _name = 'evtc.pub'
    _description = 'evtc which manage media video'

    name = fields.Char('Name Pub')
    video_pub = fields.Binary('Video')


class RatingOpinion(models.Model):
    _inherit = 'rating.rating'
    _description = """
        Add field for rating.rating
        show opinion for public user
    """

    opinions = fields.Text()
