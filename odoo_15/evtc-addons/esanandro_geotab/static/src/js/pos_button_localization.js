odoo.define('esanandro_geotab.pos_button_localization', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const {isConnectionError} = require('point_of_sale.utils');
    var rpc = require('web.rpc')

    class PosButtonLocalization extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.clickLocalisation);
        }

        mounted() {
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
        }

        willUnmount() {
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        async clickLocalisation(e) {
            if (!e.target.className.includes("disabled")) {
                var collect = this.env.pos.get_order().selected_orderline;
                var sale_order_origin_id = collect.sale_order_origin_id
                try {
                    var latitude, longitude, pick_lat, pick_long, dest_lat, dest_long;
                    await rpc.query({
                        model: 'sale.order',
                        method: 'get_destination',
                        args: [
                            [false]
                        ],
                        kwargs: {
                            "order": sale_order_origin_id
                        }
                    }).then(function (result) {
                        if (result) {
                            latitude = result.latitude;
                            longitude = result.longitude;
                            pick_lat = result.pick_lat;
                            pick_long = result.pick_long;
                            dest_lat = result.dest_lat;
                            dest_long = result.dest_long;
                        } else {
                            dest_lat = '';
                            dest_long = ''
                        }

                    })
                    // Window.location.href = "https://www.google.com/maps/dir/"+longitude+","+latitude+"/"+dest_long+","+dest_lat;
                    window.open("https://www.google.com/maps/dir/" + latitude + "," + longitude + "/" + pick_lat + "," + pick_long + "/" + dest_lat + "," + dest_long, "_blank")
                } catch (error) {
                    if (isConnectionError(error)) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Cannot access order management screen if offline.')
                        });
                    } else {
                        throw error;
                    }
                }

            }
        }
    }

    PosButtonLocalization.template = 'CustomButtonLocalization';
    ProductScreen.addControlButton({
        component: PosButtonLocalization,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(PosButtonLocalization);

    return PosButtonLocalization;
});
