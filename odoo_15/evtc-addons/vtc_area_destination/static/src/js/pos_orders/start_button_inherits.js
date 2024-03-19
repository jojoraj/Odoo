odoo.define('vtc_area_destination.start_button_inherits', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const WidgetAction = require("esanandro_geotab.pos_sale_action");
    const Cookie = require('web.utils.cookies');

    const PosStartAction = WidgetAction =>
        class extends WidgetAction {

            /**
             * @override
             */
            async clickStart(event) {
                this.el.style.display = 'none'
                const order_origin = this.env.pos.get_order().orderlines.models.filter(v => v.sale_order_origin_id)
                let order_id = order_origin ? order_origin[0].sale_order_origin_id.id : undefined
                if (order_id != undefined) {
                    Cookie.set_cookie('RideOn',
                        {
                            status: 'onShow',
                            OrderId: order_id
                        }
                    )
                }
                $('#pause-btn')[0].style.display = 'block';
                await super.clickStart(...arguments);
            }
        };

    Registries.Component.extend(WidgetAction, PosStartAction);

    return WidgetAction;

});
