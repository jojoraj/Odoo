odoo.define("vtc_area_destination.area_pins", function(require) {
    "use strict";

    const vtcMap = require("evtc_front.reservations");

    vtcMap.evtcArkeupMap.include({
        events: _.extend({}, vtcMap.evtcArkeupMap.prototype.events, {}),
        /**
         * @override
         */

        start: async function() {
            await this._super.apply(this, arguments);
            this.direction_service_error = { state: false, body: null };
        },

        _areaDomId: async function() {
            const _context = await this._super.apply(this, arguments);
            _context.getXmlPins = "vtc_area_destination.area_pins_destination";
            return _context;
        },

        _close_markers: function(marker, label) {
            if (!this.txContext && marker && label) {
                this._super.apply(this, arguments);
            }
        },

        _remove_new_unused_marker: function(transient_id) {
            const current_marker = this.transientMarker.filter(
                (marker) => marker.marker_id === transient_id
            );
            if (current_marker) {
                current_marker.slice(0, -1);
                if (current_marker.length > 1) {
                    current_marker.forEach((els) => {
                        els.marker.setVisible(false);
                        els.label.close();
                    });
                }
            }
        },

        _init_new_window: function(text) {
            if (this.marker_end_travel) {
                this.marker_end_travel.setVisible(false);
                this.label_info_remisage.close();
            }
            if (this.transientMarker.length === 0) {
                // Initialized marker when no record marker in transientMarker
                this.marker_end_travel = new google.maps.Marker({
                    icon: "/evtc_front/static/src/images/marker/trip.svg",
                    map: this.googleMap,
                    draggable: true,
                });
            }
            this.marker_end_travel.setDraggable(false);
            const contentInfo = new google.maps.InfoWindow();
            const marker_id = this.txContext.destination.length + 1;
            const params = { customDestination: marker_id, customValue: text.trim() };
            this._appendQweb(
                this.txContext.selector.mainXmlClass,
                this.txContext.selector.getXmlPins,
                params
            );
            const checkSelector = this.$("#infowindow-content-" + marker_id.toString())[0];
            contentInfo.setContent(checkSelector);
            const newMarker = {
                marker_id: marker_id,
                qweb: checkSelector,
                customValue: text.trim(),
                marker: this.marker_end_travel,
                label: contentInfo,
                active: false,
                modify: false,
            };
            // Remove marker only on modification
            const onModify = this.$(".oe-new-address-review")[0];
            if (onModify && onModify.classList.contains("edit-mode")) {
                const currentID = this.render_selector_id(
                    onModify.classList[onModify.classList.length - 1]
                );
                if (currentID) {
                    const marks = this.txContext.marker.filter(
                        (res_id) => res_id.marker_id === currentID
                    );
                    if (marks) {
                        marks.forEach((element) => {
                            element.marker.setVisible(false);
                            element.qweb.remove();
                            element.label.close();
                        });
                        this.txContext.marker = this.txContext.marker.filter(
                            (res_id) => res_id.marker_id !== currentID
                        );
                    }
                }
                // This.txContext.marker.filter(resId => resId)
            }
            this.transientMarker.push(newMarker);
            this._remove_new_unused_marker(marker_id);
            this._show_after(200).then(() => {
                this._query_selector("infowindow-content-" + marker_id.toString()).css(
                    "display",
                    "block"
                );
                this.marker_end_travel.setVisible(true);
                contentInfo.open(this.googleMap, this.marker_end_travel);
            });
            if (this.on_first_destination) {
                this.txContext.marker.push(this.transientMarker[0]);
            }
        },

        make_way_points: function(modify_id = false, status = "new") {
            this.customWay_points = [];
            this.txContext.destination.forEach((destination) => {
                if (destination.marker) {
                    this.customWay_points.push({
                        location: destination.marker.marker.getPosition(),
                        stopover: false,
                    });
                }
            });
        },

        _set_trip_direction: async function(myMod = null) {
            await this._super.apply(this, arguments)
            const origin = this.marker_begin_travel.getPosition();
            this.make_way_points(myMod ? myMod : false);
            let destination;
            if (
                this.txContext.destination.length > 0 &&
                this.txContext.destination.slice(-1)[0].marker
            ) {
                destination = this.txContext.destination
                    .slice(-1)[0]
                    .marker.marker.getPosition();
            } else {
                destination = null;
            }
            const hasOnErrors = $(".direction_server");
            if (hasOnErrors.length > 0) {
                hasOnErrors.remove();
            }
            if (origin && destination) {
                this.directionsRenderer.setMap(this.googleMap);
                this.directionsRenderer.setOptions({
                    polylineOptions: {
                        strokeColor: "black",
                        strokeWeight: 5,
                    },
                });
                await this.directionsService
                    .route({
                        origin: origin,
                        destination: destination,
                        waypoints: this.customWay_points,
                        optimizeWaypoints: true,
                        travelMode: google.maps.TravelMode.DRIVING,
                    })
                    .then((response) => {
                        this._remove_mail_route();
                        this.directionsRenderer.setDirections(response);
                        this.directionsRenderer.setOptions({ suppressMarkers: true });
                        const myroute = response.routes[0];
                        if (!myroute) {
                            return;
                        }
                        const distance = myroute.legs[0].distance.text;
                        if (distance.includes("km") || distance.includes("Km")) {
                            this.kilometers_estimation = parseFloat(distance.replace(",", "."));
                        } else {
                            $("#total_to_pay").css("display", "none");
                            $("#total_min_to_pay").css("display", "block");
                        }
                        let duration = this.convertHMS(myroute.legs[0].duration.value);
                        if (!duration) {
                            duration = "00:00:00";
                        }
                        $(this.el).find("#length_target")[0].innerText = distance.replace(",", ".");
                        $(this.el).find("#duration")[0].innerText = duration;
                        $(this.el).find("#duration")[0].value = myroute.legs[0].duration.value; // Add by max to additionnal_trip
                        this.lengthDistanceStrip = distance.replace(",", ".");
                        this.DurationStrip = duration;
                        this.direction_service_error.state = false;
                        this.direction_service_error.body = "";
                    })
                    .catch((e) => {
                        this.direction_service_error.state = true;
                        this.direction_service_error.body =
                            "Geocode was not successful for the following reason: " + e;
                        console.info("Directions request failed due to " + e);
                    });
            }
            this.customWay_points = [];
        },

        /*
         *  @override
         * replace function to another target
         * create new marker on address click
         *
         * */
        _onchange_destination_markerDrag: function(current) {
            const newData = this.$(".oe-new-address-review");
            if (!newData[0] && !this.$("#address_destination")[0]) {} else {
                this._render_dest_click(current);
            }
        },

        _render_dest_click: function(current) {
            let modificationData = this.$(".oe-new-address-review");
            const attributes = current.currentTarget.attributes;
            this.marker_end_travel = new google.maps.Marker({
                icon: "/evtc_front/static/src/images/marker/trip.svg",
                map: this.googleMap,
                draggable: true,
            });
            this._init_new_window(attributes["data-street"].value.trim());
            const position = {
                lat: parseFloat(attributes["data-latitude"].value),
                lng: parseFloat(attributes["data-longitude"].value),
            };
            this.marker_end_travel.setPosition(position);
            this.marker_end_travel.setDraggable(true);
            this._center_position(this.marker_end_travel);
            this.label_info_remisage.setContent(this.label_info_content_remisage);
            this.destination_value = current.currentTarget.innerText.trim();
            this.label_info_content_remisage.children["place-name2"].textContent =
                this.destination_value;
            $(this.el).find("#infowindow-content2").css("display", "block");
            this.label_info_remisage.open(this.googleMap, this.marker_end_travel);
            this.marker_end_travel.setVisible(true);
            this.$("#latitude_address_destination")[0].value = parseFloat(
                attributes["data-latitude"].value
            );
            this.$("#longitude_address_destination")[0].value = parseFloat(
                attributes["data-longitude"].value
            );
            if (modificationData[0]) {
                const nowValues = [
                    current.currentTarget.innerText.trim(),
                    position.lat,
                    position.lng,
                ];
                const modificationDataOnClick = modificationData.find("input");
                nowValues.forEach((input, index) => {
                    if (modificationDataOnClick[index]) {
                        modificationDataOnClick[index].value = input;
                    }
                });
            }
            google.maps.event.addListener(this.marker_end_travel, "dragend", (evt) => {
                new google.maps.Geocoder().geocode({
                        location: { lng: evt.latLng.lng(), lat: evt.latLng.lat() },
                    },
                    (results, status) => {
                        if (status === "OK") {
                            this.destination_value = this._check_formatted_address(results);
                            // This.$('#place-name2')[0].textContent = results[0].formatted_address;
                            this.label_info_content_remisage.children["place-name2"].textContent =
                                this.destination_value;
                            this.$("#address_destination")[0].value = this.destination_value;
                            this.$("#latitude_address_destination")[0].value = evt.latLng.lat();
                            this.$("#longitude_address_destination")[0].value = evt.latLng.lng();
                            this._coordinate_object({
                                latitude: "latitude_address_destination",
                                value: evt.latLng.lat(),
                            }, { longitude: "longitude_address_destination", value: evt.latLng.lng() });
                            if (this.transientMarker.length > 0) {
                                // $(this.transientMarker.slice(-1)[0].label.content).find('.oe-place-name')[0].innerText = this.address_value;
                                this.transientMarker.slice(-1)[0].label.close();
                            } else if (modificationData[0]) {
                                modificationData = modificationData[0];
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
                        } else {
                            console.info(
                                "Geocode was not successful for the following reason: " + status
                            );
                        }
                    }
                );
            });
        },
    });
});
