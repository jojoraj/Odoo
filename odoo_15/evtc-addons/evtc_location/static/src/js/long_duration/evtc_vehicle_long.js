odoo.define('evtc_location.vehicle_template_long', function(require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.vehicleLongWidget = publicWidget.Widget.extend({
        selector: '.long-duration',
        events: {
            'click #change_package_appointment, #change_choice_package_long': '_on_change_package',
            'click #change_time_appointment': '_on_change_appointment',
            'click #evtc_vehicle_button_long': '_on_click_vehicle_button'
        },
        start: function() {
            var defs = [this._super.apply(this, arguments)];

            this.recuperation = $('#evtc_recuperation');
            this.vehicle = $('#evtc_vehicle');
            this.package = $('#evtc_package');
            this.appointment = $('#evtc_appointment');
            this.payment_resume = $('#evtc_payement_resume');
            this.recuperation_adress_heading_vehicle = $('#recuperation_adress_heading_appointment_choise_vehicle');
            this.recuperation_adress_vehicle = $('#recuperation_adress_vehicle');
            this.address_recuperation = $('#address_recuperation');
            this.choise_vehicle_heading = $('#choise_vehicle_heading');
            this.vehicle_resume = $('#evtc_vehicle_resume');

            return Promise.all(defs);
        },
        _on_change_package: function() {
            this.payment_resume.addClass('d-none');
            this.recuperation.addClass('d-none');
            this.appointment.addClass('d-none');
            this.vehicle.addClass('d-none');
            this.package.removeClass('d-none');
        },
        choosing_vehicle: function(ev) {
            var div_choose = $('#choose_vehicle');
            const label = (div_choose.find("input[type=radio]:checked").next().text()).trim();
            const place = (div_choose.find("input[type=radio]:checked").siblings('p:first').text()).trim();
            return (label + '(' + place + ')').trim();
        },

        _on_click_vehicle_button: async function() {
            this.recuperation_adress_heading_vehicle.contents().eq(4).remove();
            this.recuperation_adress_vehicle.after(this.address_recuperation.val());
            this.choise_vehicle_heading.contents().eq(2).remove();
            this.choise_vehicle_heading.find('span').after(this.choosing_vehicle());

            var id = $('#choose_vehicle').find("input[type=radio]:checked").data('id');
            var selector = $('#choose_rate');
            selector[0].innerHTML = '';
            await this._rpc({
                route: '/price/location',
                params: {
                    id: id,
                },
            }).then((data) => {
                if (data) {
                    for (var i = 0; i < data.length; i++) {
                        this.html = `
                            <div class="form-group col-6 card-radio ">
                                <div class="custom-control text-center custom-radio p-2 ">
                                    <input type="radio"
                                         id="tarif-${data[i].id}"
                                         data-id="${data[i].id}"
                                         data-hour="${data[i].hours}"
                                         data-price="${data[i].price}"
                                         checked=""
                                         name="forfait_customRadio"
                                         class="custom-control-input"/>
                                    <label class="custom-control-label position-relative text-uppercase py-2"
                                         for="tarif-${data[i].id}">
                                        ${data[i].name}
                                    </label>
                                    <hr/>
                                    <p class="font-weight-bold">
                                        <i class="picto picto-etiquette"></i>
                                        ${data[i].price.toLocaleString('fr-FR', {minimumFractionDigits: 2})} Ar
                                    </p>
                                    <div class="boreder-check"/>
                                </div>
                            </div>
                        `
                        selector[0].innerHTML += this.html;
                    };
                    selector[0].innerHTML += `
                        <button id="evtc_package_button_long" type="button"
                                class="btn btn-block text-uppercase btn-evtc btn-outlined rounded-pill">
                          <i class="picto picto-check mr-2"></i>Valider
                        </button>
                    `;
                };
            });
            this._on_change_package();
        },


    })
    return {
        vehicleLongWidget: publicWidget.registry.vehicleLongWidget
    };
})
