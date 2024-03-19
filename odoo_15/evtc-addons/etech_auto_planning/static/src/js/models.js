odoo.define('etech_auto_planning.models', function (require) {
    'use strict';

    const models = require('point_of_sale.models');

    models.Orderline = models.Orderline.extend({
        get_phone: function () {
            if (this.sale_order_origin_id) {
                const value = {
                    'phone': this.sale_order_origin_id.phone,
                };
                return value;
            }
            return false;
        },
    });

});
