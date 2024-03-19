from odoo.addons.base_rest.controllers import main


class RestController(main.RestController):
    _root_path = "/callbacks/"
    _collection_name = "trip.callbacks"
