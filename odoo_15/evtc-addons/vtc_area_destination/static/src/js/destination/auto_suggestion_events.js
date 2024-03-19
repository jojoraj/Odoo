odoo.define("vtc_area_destination.suggestion_events ", function (require) {
    "use strict";

    const vtcMap = require("evtc_front.reservations");

    vtcMap.evtcArkeupMap.include({
        start: async function () {
            await this._super.apply(this, arguments);
            this.is_second_validation = true;
        },

        /*
         * @override
         * inherit method to add position to the current marker
         * @params:
         *   { events } index: the current event link to click place suggestion
         *
         * */
        _coordinate_object: function (lat, lng) {
            // Modify by max
            this._super.apply(this, arguments);
            const accessObject = this.$("#autocomplete-x1dCV");
            if (
                accessObject[0] &&
                accessObject[0].classList.contains("next-content-suggestion")
            ) {
                accessObject.next()[0].value = lat.value;
                accessObject.next().next()[0].value = lng.value;
            } else if (
                this.$("input#latitude_address_destination").length > 0 &&
                this.$("input#longitude_address_destination").length > 0
            ) {
                this.$("input#" + lat.latitude)[0].value = lat.value;
                this.$("input#" + lng.longitude)[0].value = lng.value;
            }
        },

        _reorderSequence: async function () {
            $(this.el).find(".oe_dest_qweb_selector").empty();
            const loader = `
                <span id="destination-loader" class="position-absolute"
                        style="inset: 0; z-index:999; height: auto;background-color: white !important;">
                    <div class="d-flex justify-content-center w-100 h-100 align-items-center">
                    <div class="spinner-border" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                    </div>
                </span>
                `;
            $(this.el).find(".oe_dest_qweb_selector").append(loader);

            let x = 0;

            this.googleMap.setOptions({
                center: this.marker_begin_travel.getPosition(),
                zoom: 13,
            });
            this.txContext.marker = [];
            const streamDestination = this.txContext.destination.filter((r) => r.marker);
            for (const value of streamDestination) {
                x += 1;
                if (value.marker && value.marker.marker_id) {
                    value.id = x;
                    const params = {
                        nextCall: x,
                        objects: this.txContext.details,
                        Price: value.details,
                        _Context: this.txContext,
                        _CurrentTarget: this.txContext.destinationCount,
                        _CurrentObject: value,
                    };
                    const myMarker = value.marker;
                    $(myMarker.qweb).find(".oe-place-content")[0].innerText = x;
                    this.txContext.marker.push(myMarker.marker);
                    this._createLiOption(params);
                    //
                    const latlng = new google.maps.LatLng(
                        parseFloat(value.position.lat),
                        parseFloat(value.position.lng)
                    );
                    myMarker.marker.setPosition(latlng);
                    $(myMarker.label.content).find(".oe-place-name")[0].innerText =
                        value.name.trim();
                    myMarker.marker.setVisible(true);
                    myMarker.marker.setDraggable(false);
                    myMarker.label.open(this.googleMap, myMarker.marker);
                }
            }
            this.lastDestination =
                this.txContext.destination.length > 0 ?
                    this.txContext.destination.slice(-1)[0].name :
                    "";
            this.txContext.destination = streamDestination;
            this._set_trip_direction();
            this.transientMarker = [];
            $("#destination-loader").remove();
            this._enable_modification();
        },

        _onchange_recuperation_markerDrag: function () {
            this._super.apply(this, arguments);
        },

        place_drag_destination: function (index) {
            this._remove_all_errors_message();
            const new_index = index.currentTarget.querySelector("p");
            const place_ids = new_index.attributes.place_ids.value;
            this._input_value("address_destination", new_index.innerText);
            this._remove_autocompletion("autocomplete-x1dCV");
            new google.maps.places.PlacesService(this.googleMap).getDetails({
                    placeId: place_ids,
                },
                (result, status) => {
                    if (status !== google.maps.places.PlacesServiceStatus.OK) {
                        this._google_not_initialized(status);
                        return;
                    }
                    this._init_new_window(new_index.innerText);
                    this._center_marker(this.marker_end_travel, result.geometry.location);
                    this._coordinate_object({
                        latitude: "latitude_address_destination",
                        value: result.geometry.location.lat(),
                    }, {
                        longitude: "longitude_address_destination",
                        value: result.geometry.location.lng(),
                    });
                    this._center_marker(this.marker_end_travel, result.geometry.location);
                    google.maps.event.addListener(this.marker_end_travel, "dragend", (evt) => {
                        new google.maps.Geocoder().geocode({
                                location: {lng: evt.latLng.lng(), lat: evt.latLng.lat()},
                            },
                            (results, status) => {
                                if (status === "OK") {
                                    this.address_value = this._check_formatted_address(results);
                                    this._input_value("address_destination", this.address_value);
                                    this._coordinate_object({
                                        latitude: "latitude_address_destination",
                                        value: evt.latLng.lat(),
                                    }, {
                                        longitude: "longitude_address_destination",
                                        value: evt.latLng.lng(),
                                    });
                                    if (this.transientMarker.length > 0) {
                                        $(this.transientMarker.slice(-1)[0].label.content).find(
                                            ".oe-place-name"
                                        )[0].innerText = this.address_value;
                                    } else {
                                        const modificationData = this.$(".oe-new-address-review")[0];
                                        if (modificationData) {
                                            if (modificationData.classList.item(4)) {
                                                const myAddressId = this.render_selector_id(
                                                    modificationData.classList.item(4)
                                                );
                                                const destination = this.txContext.destination.filter(
                                                    (des) => des.id === myAddressId
                                                )[0];
                                                if (destination) {
                                                    $(destination.marker.label.content).find(
                                                        ".oe-place-name"
                                                    )[0].innerText = this.address_value;
                                                }
                                            }
                                        }
                                    }
                                } else {
                                    this._google_not_initialized(status);
                                }
                            }
                        );
                    });
                }
            );
            this._removeViewMap();
        },

        put_polyline: function () {
            if (this.on_first_destination) {
                this._set_trip_direction();
            }
        },

        _onClickDestinationButton: async function (events) {
            if ($('ul.oe_dest_qweb_selector').find('.oe-new-address-review').length > 0){
                $('ul.oe_dest_qweb_selector').find('.oe-new-address-review').addClass('oe_errors_validation')
                return
            }
            const data_spinner = `<i class="spinner-border mr-2" style="margin-bottom: -7px;"></i> Valider `;
            const last_inside_button = `<i class="picto picto-check mr-2"></i>Valider`;
            const lastDestination = this.txContext.destination[this.txContext.destination.length - 1]
            this.address_destination.val(lastDestination ? lastDestination.name : this.address_destination.val())
            const divContent = this.$("#evtc_destination_button");
            if (divContent[0]) {
                divContent.empty();
                divContent.append(data_spinner);
            }
            if (this.on_first_destination) {
                await this._onClickDestination(false);
            }
            await this._calculate_destination_distance();
            this.txContext.is_first = this.on_first_destination
            await this.put_polyline();
            await this._performOnclickDestination(events)
            if (divContent[0]) {
                divContent.empty();
                divContent.append(last_inside_button);
            }
        },

        _calculate_destination_distance: async function (z = 200, wayErrors = 0) {
            let markerDefaultValue = this.marker_begin_travel;

            const streamDestination = this.txContext.destination.filter((r) => r.marker);

            this.AllDistance = 0;

            this.allTimeWait = 0;

            for (const value of streamDestination) {
                let increment = 0;

                const myMarker = value.marker;

                if (myMarker && myMarker.marker_id) {
                    increment += 1;
                    try {
                        await this._show_after(increment * z).then(async () => {
                            if (markerDefaultValue.getPosition() && myMarker.marker.getPosition()) {
                                await this.directionsService
                                    .route({
                                        origin: markerDefaultValue.getPosition(),
                                        destination: myMarker.marker.getPosition(),
                                        optimizeWaypoints: true,
                                        travelMode: google.maps.TravelMode.DRIVING,
                                    })
                                    .then((response) => {
                                        const myroute = response.routes[0];
                                        const distance = myroute.legs[0].distance.text;

                                        this.AllDistance += parseFloat(myroute.legs[0].distance.value);

                                        this.allTimeWait += parseFloat(value.details.minutes);

                                        let duration = this.convertHMS(myroute.legs[0].duration.value);
                                        if (!duration) {
                                            duration = "00:00:00";
                                        }
                                        value.route = {
                                            distance: distance.replace(".", ","),
                                            duration: duration,
                                            first_destination: markerDefaultValue,
                                            second_destination: myMarker.marker,
                                        };

                                        markerDefaultValue = myMarker.marker;
                                    });
                            }
                        });
                    } catch (e) {
                        wayErrors += 1;
                        console.error(e);
                        if (wayErrors < 3) {
                            await this._show_after(increment * z).then(async () => {
                                await this._calculate_destination_distance(z + 100, wayErrors);
                                return true;
                            });
                        }
                    }
                }
            }
            this.AllDistance = (this.AllDistance / 1000).toFixed(1).toString() + " km";
            this.allPaiedMoney = (this.AllDistance / 1000).toFixed(1);
            let time = "";
            const hours = parseInt(this.allTimeWait / 60);
            const min = parseFloat(this.allTimeWait % 60);
            if (hours > 0) {
                time = time + hours.toString() + " h ";
            }
            if (min > 0) {
                time = time + min.toString() + " mn";
            }
            window.allTimeWait = time;

            this.kilometers_estimation =
                parseFloat(this.allPaiedMoney) > 0 ?
                    this.allPaiedMoney :
                    this.kilometers_estimation;
            return true
        },
    });
});
