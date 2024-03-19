odoo.define('lcas.arkeup.routesServices', function(require) {
    'use strict';
    const Services = require('evtc_front.reservations');
    const _routes = Services.evtcArkeupMap;

    _routes.include({
        _set_trip_direction: function() {
            if (!this.marker_begin_travel && (!this.marker_begin_travel || !this.evtc_object)) {
                return
            }
            var origin = this.marker_begin_travel.getPosition();
            var destination = this.marker_end_travel.getPosition();
            if (origin && destination) {
                this.directionsRenderer.setMap(this.googleMap);
                this.directionsRenderer.setOptions({
                    polylineOptions: {
                        strokeColor: 'black',
                        strokeWeight: 5,
                    },
                });
                this.directionsService
                    .route({ origin: origin, destination: destination, travelMode: google.maps.TravelMode.DRIVING, })
                    .then((response) => {
                        this.directionsRenderer.setDirections(response);
                        this.directionsRenderer.setOptions({ 'suppressMarkers': true });
                        const myroute = response.routes[0];
                        if (!myroute) {
                            return;
                        }
                        const distance = myroute.legs[0].distance.text;
                        if (distance.includes('km') || distance.includes('Km')) {
                            this.kilometers_estimation = parseFloat(distance.replace(",", "."));
                        } else {
                            $("#total_to_pay").css('display', 'none');
                            $('#total_min_to_pay').css('display', 'block')
                        }
                        let duration = this.convertHMS(myroute.legs[0].duration.value);
                        if (!duration) {
                            duration = '00:00:00'
                        }
                        $(this.el).find('#length_target')[0].innerText = distance.replace('.', ',');
                        $(this.el).find('#duration')[0].innerText = duration;
                    })
                    .catch((e) => console.info("Directions request failed due to " + e));
            }
        },
    });
})
