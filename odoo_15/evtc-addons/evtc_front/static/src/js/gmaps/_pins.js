odoo.define('lcas.evtc._pins', function(require) {
    'use strict';

    const LcasObjectRegistry = require('evtc_front.reservations');
    const pinsInitialized = LcasObjectRegistry.evtcArkeupMap;

    const markers = pinsInitialized.include({
        __selectors: function() {
            this._super.apply(this, arguments);
            this.destination_autocomplete = $(this.el).find('#address_destination')[0];
            this.recuperation_autocomplete = $(this.el).find('#address_recuperation')[0];
        },
        __pins_info: function() {
            this._super.apply(this, arguments);
            this.__pins()
        },
        __pins: function() {
            this.initialized_first_marker();
            this.initialized_second_marker();
            // This.__google_service()
        },
        initialized_second_marker: function() {
            this.label_info_remisage.setContent(this.label_info_content_remisage);
            this.marker_end_travel = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            this.label_info.close();
            this.marker_begin_travel.setVisible(false);
        },
        initialized_first_marker: function() {
            this.marker_begin_travel = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            this.marker_begin_travel.setVisible(false);
        },
    });
    return markers;
})
