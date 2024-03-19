odoo.define('evtc_front.payment_template', function(require) {
    'use strict';
    const EvtcMaps = require("evtc_front.reservations")
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            'click #change_recuperation_vehicle_resume': '_onChangePickUpZoneResume',
            'click #change_destination_vehicle_resume': '_onChangeDestinationZoneResume',
            'click #change_time_vehicle_resume': '_onChangeAppoitmentResume',
            'click #change_choise_vehicle_resume': '_onChangeVehicleResume',
            'click #evtc_payement_button': '_onClickPaymentButton'
        }),
        start: async function() {
            await this._super.apply(this, arguments);
        },
        _onChangePickUpZoneResume: function() {
            this.payment.addClass('d-none');
            this.recuperation.removeClass('d-none');
            this._stepByPickupZone()
        },
        _onChangeDestinationZoneResume: function() {
            this.payment.addClass('d-none');
            this.destination.removeClass('d-none');
            this._stepByDestinationZone()
        },
        _onChangeAppoitmentResume: function() {
            this.payment.addClass('d-none');
            this.appointment.removeClass('d-none');
            this._stepByAppoitment();
        },
        _onChangeVehicleResume: function() {
            this.payment.addClass('d-none');
            this.vehicle.removeClass('d-none');
            this._stepByVehicle()
        },
        _onClickPaymentButton: function(events) {
            this.recuperation_adress_heading_payment.contents().eq(4).remove();
            this.recuperation_adress_payment.after(this.address_recuperation.val());
            this.destination_adress_heading_payment.contents().eq(4).remove();
            this.destination_adress_payment.after(this.address_destination.val());
            this.time_heading_payment.contents().eq(2).remove();
            this.time_payment.after(this.get_appointment_time());
            this.choise_vehicle_payment_heading.contents().eq(2).remove();
            this.choise_vehicle_payment.after(this.choosing_vehicle());
            this.choose_payment_method.text(this.get_payment_method());
            this.payment.addClass('d-none');
            this.payment_resume.removeClass('d-none');
            // $("#evtc_aside").animate({ scrollTop: $('#evtc_aside').height() });
            $("#evtc_aside").animate({ scrollTop: $('.payement-resume').position().top });
            let values = this.get_payment_method();
            this._computeAutoClass(events, 'evtc_payement', 'evtc_payement_button', values, '', '')
        },
        get_payment_method: function() {
            var choose_payment = $('#choose_payment');
            return (choose_payment.find('input[type=radio]:checked').next().text()).trim();
        },
    })
})
