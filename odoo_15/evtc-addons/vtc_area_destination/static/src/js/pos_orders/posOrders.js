odoo.define('vtc_area_destination.posOrders', function (require) {
    'use strict';

    const PosOrders = require('point_of_sale.models');

    PosOrders.load_fields("product.product", ["time_wait_ok"]);

    PosOrders.Orderline = PosOrders.Orderline.extend({
        get_notes: function () {
            if (this.sale_order_origin_id) {
                if (this.product.time_wait_ok) {
                    this.customerNote = this.hasNote ? this.hasNote : "Temps d'attente  00:00"
                }
                return this.product.time_wait_ok;
            }
            return false;
        },
    });
});
