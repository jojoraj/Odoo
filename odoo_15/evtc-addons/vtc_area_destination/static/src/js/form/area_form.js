odoo.define("vtc_area_destination.destination_zone", function(require) {
    "use strict";

    const AreaZone = require("evtc_front.reservations");
    const core = require("web.core");

    AreaZone.evtcArkeupMap.include({
        xmlDependencies: [
            "vtc_area_destination/static/src/xml/newOption.xml",
            "vtc_area_destination/static/src/xml/modify_address.xml",
            "vtc_area_destination/static/src/xml/area_owl.xml",
            "vtc_area_destination/static/src/xml/area_pins.xml",
        ],

        events: _.extend({}, AreaZone.evtcArkeupMap.prototype.events, {
            "click .new-delete": "onRemoveDestination",
            "change #waiting_time": "onChangePrice_resume",
        }),

        start: async function() {
            await this._super.apply(this, arguments);
            let _context = {
                destinationCount: 0,
                destination: [],
                selector: "",
                marker: "",
                details: "",
            };
            this.on_first_destination = true;

            _context.selector = await this._areaDomId();
            _context.marker = [];
            this.transientMarker = [];
            this.customWay_points = [];

            await this._rpc({
                route: "/destination/area/wait/time",
                params: {},
            }).then((times) => {
                _context.details = times;
                this.active_details_id =
                    _context.details && _context.details.length > 0 ? _context.details[0].id : 0;
            });

            this.try_laters = 0;

            this.txContext = _context;
        },

        onChangePrice_resume: function(event) {
            const input_values = event.currentTarget.value.trim().split(",");
            $(this.el).find(".price-mod")[0].innerHTML = input_values[1];
            this.active_details_id = parseInt(input_values[0]);
        },

        _filter_li_data: function(DomId) {
            const classname = "destination-list-" + DomId;
            return $(this.txContext.selector.mainXmlClass)
                .children("li")
                .filter(
                    (key, values) =>
                    !values.classList.contains("oe-new-address-review") &&
                    values.classList.contains(classname)
                );
        },

        _appendQweb: function(main, els, params) {
            const qwebView = this._renderQwebForm(els, params);
            main.append(qwebView);
        },

        _afterQweb: function(DOM, el, params) {
            return DOM.after(this._renderQwebForm(el, params));
        },

        _filter_destination_address: function(r = -1) {
            const _context = this.txContext.destination.filter((x) => x.marker);
            this.txContext.destination = _context;
            if (r > 0) {
                const destinations = _context.filter((z) => z.id === r);
                return destinations[0];
            }
            return false;
        },

        _set_property_marker: function(onlyRemove = false, hasTransientMarker = false) {
            const self = this;
            if (onlyRemove && self.marker_end_travel) {
                self.marker_end_travel.setVisible(false);
                self.label_info_remisage.close();
                self.marker_end_travel.setMap(null);
            }
            if (hasTransientMarker && self.transientMarker.length > 0) {
                if (self.txContext.destination.length >= 1) {
                    self.marker_end_travel =
                        self.txContext.destination.slice(-1)[0].marker.marker;
                }
                self.transientMarker.slice(0, -1).forEach((transient_markers) => {
                    transient_markers.marker.setVisible(false);
                    transient_markers.label.close();
                    transient_markers.marker.setMap(null);
                });
            }
        },

        onRemoveDestination: async function() {
            const self = this;
            self._filter_destination_address();
            self._set_property_marker(true, true);

            if (self.txContext.destination.length > 0) {
                self._hide_onInsert();
                self._toggle_add_destination();
                this.marker_end_travel = this.txContext.destination.slice(-1)[0].marker.marker;
            }

            await self._reorderSequence();

            if (self.txContext.destination.length <= 0) {
                await self._onClickDestination(true, true);
            }
        },

        _get_destination_count: function(z) {
            return z - 1 > -1 ? this.txContext.destination[z - 1] : {};
        },

        _disable_modification: function() {
            const destinationList = this.$(".destination-list");
            if (
                destinationList.length &&
                $(".oe-new-address-review").length > 0 &&
                destinationList.hasClass("ui-sortable")
            ) {
                $(".destination-list").sortable("disable");
                if (destinationList.find("li").length) {
                    destinationList
                        .find("li")
                        .toArray()
                        .forEach((z) => {
                            if (z) {
                                z.style.cursor = "auto";
                            }
                        });
                }
            }
        },

        _enable_modification: async function() {
            if ($(".destination-list").length && $(".oe-new-address-review").length <= 0) {
                const destinationList = this.$(".destination-list");
                if (destinationList.hasClass("ui-sortable-disabled")) {
                    destinationList.sortable("enable");
                } else if (!destinationList.hasClass("ui-sortable")) {
                    destinationList.sortable();
                }
                if (destinationList.find("li").length) {
                    destinationList
                        .find("li")
                        .toArray()
                        .forEach((z) => {
                            if (z) {
                                z.style.cursor = "all-scroll";
                            }
                        });
                }
                const DestinationToArray = [];
                destinationList.on("sortupdate", async(event, ui) => {
                    destinationList.sortable("toArray").forEach((toId) => {
                        const widgetSelector = parseInt(this.render_selector_id(toId));
                        const destSelect = this.txContext.destination.filter(
                            (z) => z.id === widgetSelector
                        )[0];
                        DestinationToArray.push(destSelect);
                    });
                    if (
                        DestinationToArray.length &&
                        DestinationToArray.length === this.txContext.destination.length
                    ) {
                        this.txContext.destination = DestinationToArray;
                        await this._reorderSequence();
                    }
                });
            }
        },
        _get_params: async function(hasObject) {
            const self = this;
            if (hasObject.status !== "draft") {
                await self._hasUpdate(
                    hasObject.hasRegister,
                    hasObject.isUpdate,
                    hasObject.lat,
                    hasObject.lng
                );
            }
            const destinationCount = self.txContext.destination.length;
            let nextCall = destinationCount + 1;
            let destinationCall = self._get_destination_count(destinationCount);
            let myPrice = self.txContext.details ? self.txContext.details[0] : null;
            destinationCall.status = hasObject.status;
            if (Boolean(hasObject.modification_id) && hasObject.modification_id > 0) {
                destinationCall = self._filter_destination_address(hasObject.modification_id);
                destinationCall.status = "edit";
                hasObject.status = "edit";
                destinationCall.lastModify = destinationCall;
                nextCall = destinationCall.id;
                myPrice = destinationCall.details;
            }
            const onCall = hasObject.status === "draft" ? null : destinationCall;
            return {
                status: hasObject.status,
                nextCall: nextCall,
                objects: this.txContext.details,
                Price: myPrice,
                _Context: this.txContext,
                _CurrentTarget: this.txContext.destinationCount,
                _CurrentObject: onCall,
            };
        },

        render_selector_id: function(identifier) {
            return parseInt(identifier.split("-")[2]);
        },

        _hide_destination: (li) => li.attr("style", "display: none !important"),

        _show_destination: (li) => li.removeAttr("style"),

        initialized_coordinate_value: function() {
            this.txContext.selector.latitude.DOM.value = "";
            this.txContext.selector.longitude.DOM.value = "";
            this.txContext.selector.destinationZone.DOM.value = "";
        },

        check_validate_coordinate: function() {
            const allData = this.$("#autocomplete-x1dCV");
            return Boolean(
                allData[0] && allData.next()[0].value && allData.next().next()[0].value
            );
        },
        _init_destination: function(isRegister) {
            const self = this;
            const latitude = isRegister ?
                $(self.el).find("#latitude_address_destination")[0].value :
                "";
            const longitude = isRegister ?
                $(self.el).find("#longitude_address_destination")[0].value :
                "";
            const pos = { lat: latitude, lng: longitude };
            const destination_name = isRegister ?
                $(self.el).find("#address_destination")[0].value :
                "";

            const destination = {
                name: destination_name,
                position: pos,
                details: null,
            };
            if (this.active_details_id > 0) {
                destination.details = this.txContext.details.filter(
                    (x) => x.id === this.active_details_id
                )[0];
            }
            return destination;
        },

        _toggle_add_destination: function() {
            const addDestination = this.$("#add_destination");
            const liGetDestination = this.$(".oe-new-address-review");
            if (liGetDestination.length > 0) {
                addDestination.attr("style", "display: none !important;");
                $(this.$(".save-recently-wrap")).attr("style", "display: block !important;");
            } else {
                addDestination.attr("style", "display: block !important;");
                $(this.$(".save-recently-wrap")).attr("style", "display: none !important;");
            }
        },

        _is_destinationInput: function() {
            const customInputField = $(this.el).find("#address_destination")[0];
            if (customInputField) {
                customInputField.remove();
                $(this.el)
                    .find("#oe_evtc_dest_insert > #remove_val_input_recuperation")[0]
                    .remove();
            }
        },

        _hide_onInsert: function() {
            const oe_address = $(this.el).find(".oe-new-address-review")[0];
            if (oe_address) {
                oe_address.remove();
            }
        },

        _hasUpdate: function(context, isUpdate = false, lat = null, lng = null) {
            const self = this;
            if (context && context.name && context.position.lat && context.position.lng) {
                self.txContext.selector.destinationZone.DOM.value = context.name;
                self.txContext.selector.latitude.DOM.value = context.position.lat;
                self.txContext.selector.longitude.DOM.value = context.position.lng;
                $(self.el).find(".oe-new-address-review")[0].remove();
            } else {
                context.name = this.txContext.selector.destinationZone.DOM.value.trim();
                context.position.lat = lat ?
                    lat :
                    this.txContext.selector.latitude.value.trim();
                context.position.lng = lng ?
                    lng :
                    this.txContext.selector.longitude.value.trim();
            }
            this._update_description(context);
            this._insertContext(context, this.active_details_id, isUpdate);
            return context;
        },

        _insertContext: function(destination, details_id, onUpdate = false) {
            if (details_id > 0 && !destination.details) {
                destination.details = this.txContext.details.filter(
                    (res) => res.id === details_id
                )[0];
            }
            if (!destination.details && this.txContext.details.length > 1) {
                destination.details = this.txContext.details[0];
            }
            destination.status = "done";
            if (onUpdate) {
                const dest = this.txContext.destination.filter(
                    (myAddress) => myAddress.id === onUpdate
                )[0];
                if (dest) {
                    dest.details = destination.details;
                    dest.name = destination.name;
                    dest.position = destination.position;
                }
            } else {
                destination.id = this.txContext.destination.length + 1;
                const dest = this.txContext.destination;
                dest.push(destination);
                this.txContext.destination = dest;
            }
            this._initialized_thirst_wait_time();
        },

        _initialized_thirst_wait_time: function() {
            if (this.txContext.details && this.txContext.details.length > 0) {
                this.active_details_id = this.txContext.details[0].id;
            }
        },

        _update_selector_value: function() {
            this.txContext.selector.latitude.DOM.value = this.$(
                "#latitude_address_destination"
            )[0].value;
            this.txContext.selector.longitude.DOM.value = this.$(
                "#longitude_address_destination"
            )[0].value;
            this.txContext.selector.destinationZone.DOM.value =
                this.$("#address_destination")[0].value;
        },

        _update_description: function(value) {
            this.txContext.selector.latitude.value = value.position.lat;
            this.txContext.selector.longitude.value = value.position.lng;
            this.txContext.selector.destinationZone.value = value.name;
        },

        _renderQwebForm: function(el, parameters) {
            return $(core.qweb.render(el, parameters))[0];
        },

        _areaDomId: function() {
            return {
                getXmlID: "vtc_area_destination.set_delivery_address",
                setXmlID: "vtc_area_destination.modify_delivery_address",
                mainXmlClass: this.$("ul.oe_dest_qweb_selector")[0],
                destinationID: "destination_list_register",
                destinationZone: {
                    DOM: this.$("#address_destination")[0],
                    value: this.$("#address_destination")[0].value,
                },
                destinationMode: "none",
                destinationLiRegister: "vtc_area_destination.destination_list_register",
                latitude: {
                    DOM: this.$("#latitude_address_destination")[0],
                    value: this.$("#latitude_address_destination")[0].value,
                },
                longitude: {
                    DOM: this.$("#longitude_address_destination")[0],
                    value: this.$("#longitude_address_destination")[0].value,
                },
                street: {
                    DOM: this.$("#destination_address_destination")[0],
                    value: this.$("#destination_address_destination")[0].value,
                },
                newDestination: {
                    DOM: this.$("#add_destination")[0],
                },
            };
        },

        _removeQweb: (DOM) => DOM.remove(),

        _updateCount_destination: function() {
            this.txContext.destinationCount = this.txContext.destination.length;
        },

        _createLiOption: function(parameter) {
            if (!this.txContext.destination.filter((exists) => exists.id === parameter.id)[0]) {
                this._appendQweb(
                    this.txContext.selector.mainXmlClass,
                    this.txContext.selector.destinationLiRegister,
                    parameter
                );
            }
        },

        _remove_all_errors_message: function() {
            const fieldInput = this.$("#address_destination");
            this.$(".oe_errors_message").remove();
            if (fieldInput.length > 0) {
                fieldInput.css("border-color", "black");
            }
        },

        _show_erros: function() {
            this._remove_all_errors_message();
            const fieldInput = this.$("#address_destination");
            if (fieldInput.length > 0) {
                fieldInput.css("border-color", "red");
                fieldInput.after(
                    '<small class="text-danger oe_errors_message">Veuillez remplir le champ où sélectionné parmi les adresses enregistrer</small>'
                );
            }
        },
    });
});
