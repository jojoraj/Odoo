odoo.define('evtc_pos.ClickStartButton', function(require) {
    'use strict';

    const RegistriesComponent = require('point_of_sale.Registries');
    const WidgetAction = require("esanandro_geotab.pos_sale_action");
    const rpc = require('web.rpc');
    const PosStartAction = WidgetAction =>
        class extends WidgetAction {

            /**
             * @override
             */
            async clickStart(event) {
                if (!event.target.className.includes("disabled")) {
                    const order_origin = this.env.pos.get_order().orderlines.models.filter(v => v.sale_order_origin_id)
                    let order_id = order_origin ? order_origin[0].sale_order_origin_id.id : undefined
                    if (order_id != undefined) {
                        await rpc.query({
                            model: 'sale.order',
                            method: 'set_order_start_datetime',
                            args: [order_id],
                            kwargs: {
                                'order_id': order_id,
                            }
                        })
                    }
                }
                await super.clickStart(...arguments);
            }
        };

    RegistriesComponent.Component.extend(WidgetAction, PosStartAction);

    return WidgetAction;
});
