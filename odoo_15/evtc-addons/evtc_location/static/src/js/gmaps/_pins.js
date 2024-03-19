odoo.define('evtc_location._pins', function (require) {
    'use strict';

    const LcasObjectRegistry = require('evtc_location.map');
    const pinsInitialized = LcasObjectRegistry.evtcLocationMap;

    const markers = pinsInitialized.include({
        __selectors: function(){
            this._super.apply(this, arguments);
            this.recuperation_autocomplete = $(this.el).find('#address_recuperation')[0];
        },
        __pins_info: function(){
            this._super.apply(this, arguments);
            this.__pins()
        },
        __pins: function () {
            this.initialized_first_marker();
        },
        initialized_first_marker: function() {
            this.marker_begin_travel = new google.maps.Marker({
                icon: "/evtc_location/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            this.marker_begin_travel.setVisible(false);
        },
    })
    return markers
})
