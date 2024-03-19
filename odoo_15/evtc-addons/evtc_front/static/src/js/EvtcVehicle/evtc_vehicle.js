odoo.define("evtc_front.vehicle_template", function(require) {
    "use strict";

    const vehicleTemplates = require("evtc_front.reservations").evtcArkeupMap;
    vehicleTemplates.include({
        events: _.extend({}, vehicleTemplates.prototype.events, {
            "click #change_recuperation_appointment": "_onChangePickUpZoneAppointment",
            "click #change_destination_appointment": "_onChangeDestinationZoneAppoitment",
            "click #change_time_appointment": "_onChangeAppoitmentTime",
        }),
        start: async function() {
            await this._super.apply(this, arguments);
            await this._checkFirstGameSelected();
        },
        _checkFirstGameSelected: async function() {
            await this._rpc({
                model: "fleet.vehicle.model.category",
                method: "get_first_game_id",
                args: [],
            }).then((toSelectId) => {
                for (const [_objectId, htmlObject] of Object.entries(
                        $("input[name='vehicle_customRadio']")
                    )) {
                    if (htmlObject && _objectId && !isNaN(parseFloat(_objectId))) {
                        if ($(htmlObject).data()["id"] === toSelectId) {
                            htmlObject.setAttribute("checked", true);
                        }
                    }
                }
            });
        },
        _onChangePickUpZoneAppointment: function() {
            this.vehicle.addClass("d-none");
            this.recuperation.removeClass("d-none");
            this._stepByPickupZone()
        },
        _onChangeDestinationZoneAppoitment: function() {
            this.vehicle.addClass("d-none");
            this.destination.removeClass("d-none");
            // add class to button validate
            this._stepByDestinationZone();
        },
        _onChangeAppoitmentTime: function() {
            this.vehicle.addClass("d-none");
            this.appointment.removeClass("d-none");
            this._stepByAppoitment();
        },
        _onClickVehicleButton: async function(events) {
            await this._super.apply(this, arguments)
            this.recuperation_adress_heading_vehicle.contents().eq(4).remove();
            this.recuperation_adress_vehicle.after(this.address_recuperation.val());
            this.destination_adress_heading_vehicle.contents().eq(4).remove();
            if (!this.address_destination.val()){
                let data = this._getStepByXmlID("evtc_destination");
                let step = this._ObjectsParams[data]
                this.address_destination.val(step.value)
            }
            this.destination_adress_vehicule.after(this.address_destination.val());
            this.time_heading_vehicle.contents().eq(2).remove();
            this.time_vehicle.after(this.get_appointment_time());
            this.choise_vehicle_heading.contents().eq(2).remove();
            this.choise_vehicle_heading.find("span").after(this.choosing_vehicle());
            this.vehicle.addClass("d-none");
            this.vehicle_resume.removeClass("d-none");
            await this._additional_trip();
            $("#evtc_aside").animate({
                scrollTop: $("#choise_vehicle_heading").position().top + 20,
            });
            let values = this._renderVehicleDetails();
            this._computeAutoClass(events, 'evtc_vehicle', 'evtc_vehicle_button', values, '', '')
        },
        choosing_vehicle: function() {
            var div_choose = $("#choose_vehicle");
            const label = div_choose.find("input[type=radio]:checked").next().text().trim();
            const place = div_choose
                .find("input[type=radio]:checked")
                .siblings("p:first")
                .text()
                .trim();
            return (label + "(" + place + ")").trim();
        },
        _renderVehicleDetails: function() {
            return $("#choose_vehicle").find("input[type=radio]:checked").next().text().trim();
        },
        choosing_vehicle_model: function() {
            var model_choose = parseInt(
                $("#choose_vehicle").find("input[type=radio]:checked")[0].dataset.id
            );
            return model_choose;
        },
        _additional_trip: function() {
            var getWeekDay = $("#date").datepicker("getDate").getUTCDay();
            var getHours = $("#time").val().split(":")[0];
            var getMinutes = $("#time").val().split(":")[1];
            this._rpc({
                model: "additional.trip",
                method: "update_additional_time",
                args: [{ date: getWeekDay, hours: getHours, minutes: getMinutes }],
            }).then((result) => {
                if (result) {
                    const duration = $("#duration")[0].value * parseFloat(result);
                    $("#duration")[0].innerText = this.convertHMS(duration) || "00 mn";
                }
            });
        },
    });
});
