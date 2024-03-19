from odoo.addons.base_rest.controllers import main


class RestController(main.RestController):
    _root_path = "/services/"
    _collection_name = "taxi.services"
