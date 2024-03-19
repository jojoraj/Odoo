odoo.define('esanandro_geotab.geotab_post_stop', function (require) {
    'use strict';

    const Cookie = require('web.utils.cookies');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const {isConnectionError} = require('point_of_sale.utils');
    var rpc = require('web.rpc')

    class GeotabPosStopButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        mounted() {
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
            $()
        }

        willUnmount() {
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        async onClick(e) {
            if (!e.target.className.includes("disabled")) {
                try {
                    var self = this;
                    $("#stop-btn").css("background-color", "#9593939e");
                    $("#stop-btn").addClass("disabled");
                    $("#localiz_btn").css("background-color", "#9593939e");
                    $("#localiz_btn").addClass("disabled");
                    Cookie.set_cookie('stop_enabled', false)
                    var collect = self.env.pos.get_order().selected_orderline;
                    var sale_order_origin_id = collect.sale_order_origin_id;
                    var price_unit = self.env.pos.get_order().get_last_orderline().price;
                    var role_id = self.env.pos.config.role_id
                    var lines = self.env.pos.get_order().orderlines
                    await rpc.query({
                        model: 'sale.order',
                        method: 'stop_iteration',
                        args: [
                            []
                        ],
                        kwargs: {
                            "order": sale_order_origin_id,
                            "price_unit": price_unit,
                            "role_id": role_id
                        }
                    }).then(function (result) {
                        if (result) {
                            var distance = result.distance
                            if (!(distance === 0 || distance === undefined)) {
                                lines = self.env.pos.get_order().orderlines
                                for (var line of lines.models) {
                                    if (line.product.uom_id[1] === "km") {
                                        line.set_quantity(distance)
                                    }
                                }
                            }
                        }
                    })
                    this.trigger('close-popup');
                } catch (error) {
                    if (isConnectionError(error)) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Cannot access order management screen if offline.'),
                        });
                    } else {
                        throw error;
                    }
                }
            }
        }

    }

    GeotabPosStopButton.template = 'CustomGeotabStop';
    ProductScreen.addControlButton({
        component: GeotabPosStopButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(GeotabPosStopButton);

    return GeotabPosStopButton;
});
