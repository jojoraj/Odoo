odoo.define('evtc_location.dragDropPins', function(require) {
    'use strict'

    const dragDrop = require('evtc_location.map');
    const _PrecisionWithPins = dragDrop.evtcLocationMap;

    _PrecisionWithPins.include({
        events: _.extend({}, _PrecisionWithPins.prototype.events, {
            'click .li-street-recuperation': '_onchange_recuperation_markerDrag',
        }),
        _onchange_recuperation_markerDrag: function(index) {
            if (!this.googleMap || !this.evtc_object) {
                return
            }
            if (this.marker_begin_travel) {
                this.marker_begin_travel.setVisible(false);
                this.label_info.close();
            }
            this.marker_begin_travel.setDraggable(true);
            this.marker_begin_travel = new google.maps.Marker({
                icon: "/evtc_location/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            var attributes = index.currentTarget.attributes;
            var position = {
                lat: parseFloat(attributes['data-latitude'].value),
                lng: parseFloat(attributes['data-longitude'].value)
            };
            this.marker_begin_travel.setPosition(position);
            this._center_position(this.marker_begin_travel);
            this.address_value = index.currentTarget.innerText;
            this._init_marker_window(this.address_value);
            this._coordinate_object({ 'latitude': 'latitude_address_recovery', 'value': parseFloat(attributes['data-latitude'].value) }, { 'longitude': 'longitude_address_recovery', 'value': parseFloat(attributes['data-longitude'].value) })
            google.maps.event.addListener(this.marker_begin_travel, 'dragend', (evt) => {
                new google.maps.Geocoder().geocode({
                    'location': { lng: evt.latLng.lng(), lat: evt.latLng.lat() }
                }, (results, status) => {
                    if (status === 'OK') {
                        this.address_value = this._check_formatted_address(results);
                        this._init_marker_window(this.address_value);
                        this._coordinate_object({ 'latitude': 'latitude_address_recovery', 'value': evt.latLng.lat() }, { 'longitude': 'longitude_address_recovery', 'value': evt.latLng.lng() })
                    } else {
                        this._google_not_initialized(status);
                    }
                });
            });
            this._removeViewMap();
        },
    });
})
