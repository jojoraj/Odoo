odoo.define("evtc_front.vehicle_resume_template", function(require) {
    "use strict";

    const EvtcMaps = require("evtc_front.reservations");
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            "click #change_recuperation_vehicle": "_onChangePickupZoneVehicle",
            "click #change_destination_vehicle": "_on_change_destination",
            "click #change_time_vehicle": "_onChangeTimeVehicle",
            "click #change_choise_vehicle": "_onChangeVehicles",
            "click #evtc_vehicle_resume_button": "_onClickVehicleResumeButton",
        }),
        start: async function() {
            await this._super.apply(this, arguments);
        },
        _onChangePickupZoneVehicle: function() {
            this.vehicle_resume.addClass("d-none");
            this.recuperation.removeClass("d-none");
            this._stepByPickupZone()
        },
        _onChangeDestinationVehicle: function() {
            this.vehicle_resume.addClass("d-none");
            this.destination.removeClass("d-none");
            this._stepByDestinationZone()
        },
        _onChangeTimeVehicle: function() {
            this.vehicle_resume.addClass("d-none");
            this.appointment.removeClass("d-none");
            this._stepByAppoitment()
        },
        _onChangeVehicles: function() {
            this.vehicle_resume.addClass("d-none");
            this.vehicle.removeClass("d-none");
            this._stepByVehicle()
        },
        _onClickVehicleResumeButton: function(events) {
            this.recuperation_adress_heading_vehicle_resume.contents().eq(4).remove();
            this.recuperation_adress_vehicle_resume.after(this.address_recuperation.val());
            this.destination_adress_heading_vehicle_resume.contents().eq(4).remove();
            this.destination_adress_vehicule_resume.after(this.address_destination.val());
            this.time_heading_vehicle_resume.contents().eq(2).remove();
            this.time_vehicle_resume.after(this.get_appointment_time());
            this.choise_vehicle_resume_heading.contents().eq(2).remove();
            this.choise_vehicle_resume.after(this.choosing_vehicle());
            this.vehicle_resume.addClass("d-none");
            this.payment.removeClass("d-none");
            // $("#evtc_aside").animate({ scrollTop: $('#evtc_aside').height() });
            $("#evtc_aside").animate({ scrollTop: $("#choose_payment").position().top });
            this._computeAutoClass(events, 'evtc_vehicle_resume', 'evtc_vehicle_resume_button', '', '', '')
        },
    });
});
