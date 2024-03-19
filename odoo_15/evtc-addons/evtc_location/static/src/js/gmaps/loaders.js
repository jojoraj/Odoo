odoo.define('evtc_location.loaders', function (require) {
    'use strict';
    try {
        $('.loading').show();
    } catch (e) {
        console.info('loaders not initialized')
    }
    var StayLoader = require('evtc_location.map');
    var Loader = StayLoader.evtcLocationMap;

    var InitLoader = Loader.include({
        _show_my_position: function () {
            const self = this;
            this._super(...arguments);
            self._show_after(400)
                .then(() => {
                    $('.loading').hide();
                })
        }
    })
    return InitLoader
})
