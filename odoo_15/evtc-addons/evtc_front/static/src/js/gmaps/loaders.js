odoo.define('lcas.evtc.loaders', function (require) {
    'use strict';
    try {
        $('.loading').show();
    } catch (e) {
        console.info('loaders not initialized')
    }
    const StayLoader = require('evtc_front.reservations');
    const Loader = StayLoader.evtcArkeupMap;

    Loader.include({
        _show_my_position: async function () {
            await this._super.apply(this, arguments)
            this._show_after(400)
                .then(() => {
                    $('.loading').hide();
                })
        }
    })
})
