odoo.define('geolocalie.device', function (require) {
    'use strict';

    const MyDevice = require('evtc_front.reservations');
    const MyDeviceLocalisation = MyDevice.evtcArkeupMap;

    MyDeviceLocalisation.include({
        start: async function () {
            await this._super.apply(this, arguments)
            await this._show_my_position();
        },
        _show_my_position: function () {
            this.bounds = new google.maps.LatLngBounds();
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const pos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                        };
                        this.bounds.extend(pos);
                        this._init_marker_window("Votre Position actuelle")
                        this._center_marker(this.marker_begin_travel, pos)
                        $("#latitude_address_recovery").val(position.coords.latitude)
                        $("#longitude_address_recovery").val(position.coords.longitude)
                        new google.maps.Geocoder().geocode({'location': pos}, (results, status) => {
                            if (status === 'OK') {
                                this._input_value('address_recuperation', this._check_formatted_address(results))
                            } else {
                                this._google_not_initialized(status)
                            }
                        });
                        this._fix_marker(this.marker_begin_travel);
                    },
                    (errors) => {
                        this._google_not_initialized(errors)
                    },
                );
            } else {
                console.error("Browser doesn't support Geolocation")
            }
        },
    })
});
