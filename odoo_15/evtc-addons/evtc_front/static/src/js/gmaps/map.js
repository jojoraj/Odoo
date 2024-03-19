odoo.define("evtc_front.reservations", function(require) {
    "use strict";

    var webPublicWidget = require("web.public.widget");
    const _registry = webPublicWidget.Widget;
    const vehicleRateKm = 0;
    const KmEstimated = 0;

    webPublicWidget.registry.LcasEvtcMap = _registry.extend({
        selector: "#selector-map-content",
        start: async function() {
            this.__fields();
            this.__bases();
            this.__google_callback(); // Load google map correctly
            this.autocompleteSuggestion = {
                bounds: this.TANA_BOUNDS,
                strictBounds: true,
                componentRestrictions: { country: "MG" },
            };
            this._ObjectsParams = await this._processData();
        },
        _getStepByXmlID: function(xmlId) {
            const rangs = this._getRang();
            const stepIndex = this._getStep().indexOf(xmlId);
            let rang = rangs[stepIndex] + "Step";
            if (this._ObjectsParams[rang].xml_id === xmlId) {
                return rang
            }
            return false
        },
        _getStep: function() {
            return [
                "evtc_recuperation",
                "evtc_destination",
                "evtc_appointment",
                "evtc_vehicle",
                "evtc_vehicle_resume",
                "evtc_payement",
                "evtc_payement_resume",
            ];
        },
        _getRang: function() {
            return ["first", "second", "third", "four", "five", "six", "seven", "eigth"];
        },
        _setStep: function(ObjectKey, isValidate, escape, value, lat, long, validationNumber) {
            this._ObjectsParams[ObjectKey].isValidate = isValidate
            this._ObjectsParams[ObjectKey].escape = escape
            this._ObjectsParams[ObjectKey].validationNumber = ++this._ObjectsParams[ObjectKey].validationNumber
            this._ObjectsParams[ObjectKey].value = value
            this._ObjectsParams[ObjectKey].long = long
            this._ObjectsParams[ObjectKey].lat = lat
            this._ObjectsParams[ObjectKey].validationNumber = validationNumber
            if (validationNumber > 1) {
                this._ObjectsParams[ObjectKey].isModify = true
            }
        },
        _processData: function() {
            let evtcProcess = {};
            const steps = this._getStep();
            const rangs = this._getRang();
            steps.forEach((step) => {
                const stepIndex = steps.indexOf(step);
                const rang = rangs[stepIndex] + "Step";
                let vals = '';
                if ('evtc_recuperation' === step){
                    vals = 'De : ';
                } else if ('evtc_destination' === step){
                    vals = 'à : ';
                } else if ('evtc_appointment' === step) {
                    vals = 'Le : '
                } else if ('evtc_vehicle' === step){
                    vals = 'En : ';
                }
                evtcProcess[rang] = {
                    xml_id: step,
                    isValidate: false,
                    isModify: false,
                    escape: false,
                    type: vals,
                    value: "",
                    long: "",
                    lat: "",
                    oeClass: ["evtc_recuperation", "evtc_destination"].includes(step) ? 'picto picto-address-black mr-2' : 'headline headline-2',
                    validationNumber: 0,
                };
            });
            return evtcProcess;
        },
        __selectors: function() {
            this.evtc_object = $(this.el).find("#evtc_maps")[0];
        },
        __bases: function() {
            this.TANA = {
                lat: -18.879293975867682,
                lng: 47.505387887452166,
            };
            this.TANA_BOUNDS = {
                north: -18.620112368599735,
                south: -19.186260186571502,
                west: 46.99684105567152,
                east: 48.02543603182519,
            };
            const restriction = {
                latLngBounds: this.TANA_BOUNDS,
                strictBounds: false,
            };
            const zoom = 13;
            this.vehicle_rate_per_km = vehicleRateKm;
            this.kilometers_estimation = KmEstimated;
            const openingMapOption = {
                mapTypeId: "roadmap",
                zoom: zoom,
                center: this.TANA,
                restriction: restriction,
            };
            openingMapOption.fullscreenControl = false;
            openingMapOption.streetViewControl = false;
            openingMapOption.mapTypeControl = false;
            this.options = openingMapOption;
            this.__selectors();
        },
        __pins_info: function() {
            this.label_info = new google.maps.InfoWindow();
            this.label_info_remisage = new google.maps.InfoWindow();
            this.label_info_content_remisage = $(this.el).find("#infowindow-content2")[0];
        },
        __fields: function() {
            if (
                $(this.el).find("#address_recuperation").length > 0 &&
                $(this.el).find("#address_destination").length
            ) {
                $(this.el).find("#address_recuperation")[0].value = "";
                $(this.el).find("#address_destination")[0].value = "";
            }
        },
        __google_service: function() {
            this.directionsService = new google.maps.DirectionsService();
            this.directionsRenderer = new google.maps.DirectionsRenderer();
        },
        __google_callback: async function() {
            this.googleMap = await new google.maps.Map(this.evtc_object, this.options);
            this.__pins_info();
            this.__google_service();
        },
    });
    return {
        evtcArkeupMap: webPublicWidget.registry.LcasEvtcMap,
    };
});
