odoo.define('evtc_pos.ClickStopButton', function(require) {
    'use strict';

    const RegistriesComponent = require('point_of_sale.Registries');
    const PosStopIteration = require("esanandro_geotab.geotab_post_stop");
    const rpc = require('web.rpc');
    const PosStopAction = PosStopIteration =>
        class extends PosStopIteration {

            /**
             * @override
             */
            async onClick(event) {
                if (!event.target.className.includes("disabled")) {
                    const order_origin = this.env.pos.get_order().orderlines.models.filter(v => v.sale_order_origin_id)
                    let order_id = order_origin ? order_origin[0].sale_order_origin_id.id : undefined
                    let list_order = this.env.pos.get_order_list()
                    let amount = 0
                    let existing_obj = []
                    list_order.forEach(order => {
                        Object.entries(order.orderlines._byId).forEach(el => {
                            let record = el[1];
                            if (!existing_obj.includes(record.cid)) {
                                existing_obj.push(record.cid);
                                amount += record.quantity * record.price
                            }
                        })
                    });
                    if (order_id != undefined) {
                        await rpc.query({
                            model: 'sale.order',
                            method: 'set_order_stop_datetime',
                            args: [order_id],
                            kwargs: {
                                'order_id': order_id,
                                'amount': amount
                            }
                        })
                    }
                }
                await super.onClick(...arguments);
            }
        };

    RegistriesComponent.Component.extend(PosStopIteration, PosStopAction);

    return PosStopIteration;
});
