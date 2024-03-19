odoo.define('esanandro_geotab.pos_sale_action', function (require) {
    'use strict';
    const Cookie = require('web.utils.cookies');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const {isConnectionError} = require('point_of_sale.utils');
    var rpc = require('web.rpc');


    class GeotabPosOrder extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.clickStart);
        }

        mounted() {
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
            if (Cookie.get_cookie('start_enabled') === 'true') {
                $("#start-btn").css("background-color", "#00d76b");
                $("#start-btn").removeClass("disabled");
                $("#localiz_btn").css("background-color", "#0055ff");
                $("#localiz_btn").removeClass("disabled")

            }
            if (Cookie.get_cookie('stop_enabled') === 'true') {
                $("#stop-btn").css("background-color", "#ff00004f");
                $("#stop-btn").removeClass("disabled");
                $("#localiz_btn").css("background-color", "#0055ff");
                $("#localiz_btn").removeClass("disabled")
            }
        }

        willUnmount() {
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);

        }

        async start() {
            this._super.apply(...arguments);
            if (Cookie.get_cookie('start_disabled') === 'true') {
                this.manageButton();
            }
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        manageButton() {
            $("#start-btn").css("background-color", "#9593939e");
            $("#start-btn").addClass("disabled");
            $("#stop-btn").css("background-color", "#ff00004f");
            $("#stop-btn").removeClass("disabled");
            Cookie.set_cookie('start_enabled', false)
            Cookie.set_cookie('stop_enabled', true)
        }

        async clickStart(e) {
            if (!e.target.className.includes("disabled")) {

                var self = this;
                var collect = self.env.pos.get_order().selected_orderline;
                var role_id = self.env.pos.config.role_id
                var sale_order_origin_id = collect.sale_order_origin_id;
                var lines = self.env.pos.get_order().orderlines
                try {
                    this.manageButton();
                    var status = false
                    // Var test = 0
                    while (!status) {
                        $(".o_blockUI").remove();
                        await rpc.query({
                            model: 'sale.order',
                            method: 'get_done_distance',
                            args: [
                                [false]
                            ],
                            kwargs: {
                                "order": sale_order_origin_id,
                                "role_id": role_id
                            }
                        }).then( (result) => {
                            if (result) {
                                var distance = result.distance
                                if (distance === 0) {
                                } else {
                                    lines = self.env.pos.get_order().orderlines
                                    for (var line of lines.models) {
                                        if (line.product.uom_id[1] === "km") {
                                            line.set_quantity(distance)
                                        }
                                    }
                                }
                            } else {
                                status = true
                            }
                        })
                    }

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

    GeotabPosOrder.template = 'CustomGeotabButton';

    ProductScreen.addControlButton({
        component: GeotabPosOrder,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(GeotabPosOrder);

    return GeotabPosOrder;
});
