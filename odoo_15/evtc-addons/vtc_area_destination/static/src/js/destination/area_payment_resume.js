odoo.define("vtc_area_destination.area_payment_resume", function(require) {
    "use strict";

    const events = require("evtc_front.reservations");
    events.evtcArkeupMap.include({

        start: async function() {
            await this._super.apply(this, arguments);
        },
        converTodestination: function(allDestinations) {
            let values = [];
            allDestinations.forEach((destination) => {
                const coodinateX = destination.marker.marker.getPosition().lat();
                const coodinateY = destination.marker.marker.getPosition().lng();
                values.push({
                    name: destination.marker.customValue ?? destination.name,
                    latitude: coodinateX,
                    longitude: coodinateY,
                    delay: true,
                    kilometers_estimted: destination.route.distance,
                    kilometers_real: destination.route.distance,
                    coordinate: coodinateX + ", " + coodinateY,
                    wait_time: destination.details.id,
                });
            });
            return values;
        },
        _UpdateDestinationCoordinate: function(data, lastDestination) {
            lastDestination.forEach((dest) => {
                data.dest_lat = dest.marker.marker.getPosition().lat().toString();
                data.dest_long = dest.marker.marker.getPosition().lng().toString();
                data.destination_zone = dest.marker.customValue ?? dest.name;
            });
            return data;
        },
        prepareCrmData: async function(partner, maps) {
            let result = await this._super(partner, maps);
            let _context = this.txContext;
            let userDestination = _context.destination;
            if (_context && userDestination.length > 1) {
                result.as_many_course = true;
                result.others_destination = this.converTodestination(userDestination);
            } else if (_context && userDestination.length == 1) {
                result = this._UpdateDestinationCoordinate(result, userDestination);
            }
            return result;
        },
    });
});
