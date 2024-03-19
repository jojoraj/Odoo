odoo.define('etech_auto_planning.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const ExtendsPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                setTimeout(function () {
                    if ($('.js_invoice') && !$('.js_invoice').hasClass('highlight')) {
                        $('.js_invoice').trigger('click');
                    }
                }, 250); // 250 milliseconds delay


            }
        };

    Registries.Component.extend(PaymentScreen, ExtendsPaymentScreen);
    return ExtendsPaymentScreen;
})
;
