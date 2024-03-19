odoo.define('lcas.arkeup.dragDropPins', function(require) {
    'use strict'

    const dragDrop = require('evtc_front.reservations');
    const _PrecisionWithPins = dragDrop.evtcArkeupMap;

    _PrecisionWithPins.include({
        events: _.extend({}, _PrecisionWithPins.prototype.events, {
            'click .li-street-recuperation': '_onchange_recuperation_markerDrag',
            'click .li-street-destination': '_onchange_destination_markerDrag',
        }),
        start: function() {
            this._super.apply(this, arguments);
        },

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
                icon: "/evtc_front/static/src/images/marker/trip.svg",
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
            this._set_trip_direction();
            google.maps.event.addListener(this.marker_begin_travel, 'dragend', (evt) => {
                new google.maps.Geocoder().geocode({
                    'location': { lng: evt.latLng.lng(), lat: evt.latLng.lat() }
                }, (results, status) => {
                    if (status === 'OK') {
                        this.address_value = this._check_formatted_address(results);
                        this._init_marker_window(this.address_value);
                        this._coordinate_object({ 'latitude': 'latitude_address_recovery', 'value': evt.latLng.lat() }, { 'longitude': 'longitude_address_recovery', 'value': evt.latLng.lng() })
                        this._set_trip_direction();
                    } else {
                        this._google_not_initialized(status);
                    }
                });
            });
            this._removeViewMap();
        },
        _onchange_destination_markerDrag: function(current) {
            if (!this.googleMap || !this.evtc_object) {
                return
            }
            if (this.marker_end_travel) {
                this.marker_end_travel.setVisible(false);
                this.label_info_remisage.close();
            }
            this.marker_end_travel.setDraggable(true);
            this.marker_end_travel = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            var attributes = current.currentTarget.attributes;
            var position = {
                lat: parseFloat(attributes['data-latitude'].value),
                lng: parseFloat(attributes['data-longitude'].value)
            };
            this.marker_end_travel.setPosition(position);
            this._center_position(this.marker_end_travel);
            this.label_info_remisage.setContent(this.label_info_content_remisage);
            // This.label_info_content_remisage.children["place-name2"].textContent = current.currentTarget.innerText;
            this.destination_value = current.currentTarget.innerText.trim();
            this.label_info_content_remisage.children["place-name2"].textContent = this.destination_value;
            $(this.el).find("#infowindow-content2").css('display', 'block');
            this.label_info_remisage.open(this.googleMap, this.marker_end_travel);
            this.marker_end_travel.setVisible(true);
            this.$('#latitude_address_destination')[0].value = parseFloat(attributes['data-latitude'].value);
            this.$('#longitude_address_destination')[0].value = parseFloat(attributes['data-longitude'].value);
            this._set_trip_direction();
            google.maps.event.addListener(this.marker_end_travel, 'dragend', (evt) => {
                new google.maps.Geocoder().geocode({
                    'location': { lng: evt.latLng.lng(), lat: evt.latLng.lat() }
                }, (results, status) => {
                    if (status === 'OK') {
                        this.destination_value = this._check_formatted_address(results);
                        // This.$('#place-name2')[0].textContent = results[0].formatted_address;
                        this.label_info_content_remisage.children["place-name2"].textContent = this.destination_value;
                        this.$('#address_destination')[0].value = this.destination_value;
                        this.$('#latitude_address_destination')[0].value = evt.latLng.lat();
                        this.$('#longitude_address_destination')[0].value = evt.latLng.lng();
                        this._set_trip_direction();
                    } else {
                        console.info('Geocode was not successful for the following reason: ' + status);
                    }
                });
            })
        },
    });
})
