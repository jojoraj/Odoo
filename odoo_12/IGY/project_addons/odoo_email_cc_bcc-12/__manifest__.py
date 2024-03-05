# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "ODOO Email CC and BCC",
  "summary"              :  """ODOO Email CC and BCC adds option for CC and BCC feature in mail to keep others in the loop.""",
  "category"             :  "Marketing",
  "version"              :  "1.1.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Email-CC-and-BCC.html",
  "description"          :  """Add CC and BCC feature in mail
Email CC
Email Bcc
Mail features
Email cc feature
Email Bcc features
Email CC IDs
Email BCC IDs
Email
Odoo Email
Mails
Mailing System
Electronic Mails
Odoo Mail
Formal Communication
Add CC and BCC option in mails""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_email_cc_bcc",
  "depends"              :  ['mail', 'igy_alterning_mail_server'],
  "data"                 :  ['views/compose_view.xml'],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  200,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
