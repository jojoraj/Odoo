odoo.define('evtc_recrutement.recrutment', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');

    publicWidget.registry.clearInput = publicWidget.Widget.extend({
        selector: '#recrutment-form',
        start: function () {
            return this._super.apply(this, arguments).then(() => {
                $("input#job")[0].value = '';
                $("textarea#description")[0].value = '';
            });
        },
    });
})
