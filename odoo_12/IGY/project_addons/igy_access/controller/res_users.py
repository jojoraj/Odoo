from logging import raiseExceptions
from odoo import http, api, fields, models, _
from odoo.addons.web.controllers.main import DataSet 
from odoo.http import request
import datetime

class CustomDataSet(DataSet):  
    
    @http.route('/web/dataset/search_read', type='json', auth="user")
    def search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        res = super(CustomDataSet,self).search_read(model, fields, offset, limit, domain, sort)
        domain_externe = ['share', '=', True]
        domain_interne = ['share', '=', False]
        client_group = request.env['res.groups'].search([('id','=',54)], limit=1)
        client_users = client_group.users
        try :
            rec = res["records"]
            name = res["length"]
        except :
            return res
        if domain_externe in domain and domain_interne in domain:
            return res
        try :
            if domain_interne in domain :
                users_name  = []
                for user in client_users :
                    users_name.append(user.name)
                for resultat in res["records"]:
                    if resultat["name"] in users_name :
                        res["records"].remove(resultat)
                res['length'] = int(res['length']) - len(users_name)
                return res
            if domain_externe in domain :
                client = []
                for user in client_users :
                    record = {
                        'id': user.id ,
                        'login': user.login,
                        'name':user.name,
                        'lang':user.lang,
                        'login_date': user.login_date
                    }      
                    client.append(record)
                for re in res['records']:
                    client.append(re)
                res["records"]= client
                res['length'] = len(res["records"])
                return res
        except :
            return res
        return res  