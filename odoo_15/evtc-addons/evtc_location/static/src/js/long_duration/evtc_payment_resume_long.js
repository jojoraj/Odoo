odoo.define('evtc_location.payment_resume_template_long', function (require) {

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var appointementLongWidget = require('evtc_location.evtc_appointment_long').appointementLongWidget;
    var vehicleLongWidget = require('evtc_location.vehicle_template_long').vehicleLongWidget;
    var rpc = require('web.rpc');
    window.LcasCondition = 0;


    publicWidget.registry.paymentResumeLongWidget = publicWidget.Widget.extend({
        selector: '.long-duration',
        events: {
            'click #change_recuperation_appointment_long': '_on_change_recuperation',
            'click #change_choice_appointment_long': '_on_change_appointment',
            'click #change_choice_vehicle_long': '_on_change_vehicle',
            // 'click #change_choice_package_long': '_on_change_package',
            'change #customRadio10': '_on_get_check_user',
            'change #customRadio11': '_on_get_check_user',
            'keyup #tel': '_on_change_tel',
            'keydown #tel': '_on_change_tel',
            'change #tel': '_on_change_tel',
            'focusout #tel': '_on_change_tel',
            'keyup #name': '_on_change_name',
            'keydown #name': '_on_change_name',
            'change #name': '_on_change_name',
            'focusout #name': '_on_change_name',
            'click #evtc_payement_resume_button_long': '_on_click_payment_resume_button'
        },
        start: function () {
            var defs = [this._super.apply(this, arguments)];
            window.PartnerSelectedId = 0;
            this.small_tel = $('.small-tel');
            this.small_name = $('.small-name');
            this.recuperation = $('#evtc_recuperation');
            this.payment_resume = $('#evtc_payement_resume');
            this.appointment = $('#evtc_appointment');
            this.vehicle = $('#evtc_vehicle');
            this.payment = $('#evtc_payement');
            this.custom_yes = $('#customRadio10');
            this.custom_no = $('#customRadio11');
            this.tel = $('#tel');
            this.name = $('#name');
            this.here_we_go_resume = $('#evtc_here_we_go_resume');
            this.address_recuperation = $('#address_recuperation');

            this.recuperation_adress_heading_payment_resume = $('#recuperation_adress_heading_payment_resume');
            this.recuperation_adress_heading_payment_resume_modal = $('#recuperation_adress_heading_payment_resume_modal');
            this.recuperation_adress_payment_resume = $('#recuperation_adress_payment_resume');
            this.time_heading_payment_resume = $('#time_heading_payment_resume');
            this.time_heading_payment_resume_modal = $('#time_heading_payment_resume_modal');
            this.time_payment_resume = $('#time_payment_resume');
            this.time_payment_resume_modal = $('#time_payment_resume_modal');
            this.choise_vehicle_payment_resume_heading = $('#choise_vehicle_payment_resume_heading');
            this.choise_vehicle_payment_resume_heading_modal = $('#choise_vehicle_payment_resume_heading_modal');
            this.tel_payment_resume = $('#tel_payment_resume');
            this.tel_payment_resume_modal = $('#tel_payment_resume_modal');
            this.div_choose = $('#choose_vehicle');
            this.choose_payment = $('#choose_payment');
            this.package = $('#evtc_package');
            this.choice_package_resume_heading_modal = $('#choice_package_resume_heading_modal');
            this.choice_package_resume_modal = $('#choice_package_resume_modal');
            this.choice_package_resume_heading = $('#choice_package_resume_heading');
            this.choice_package_resume = $('#choice_package_resume');

            this.small_name.hide();
            this.small_tel.hide();
            this.get_user_info();
            this.check_label_string();

            this.mine_obj = 0;
            return Promise.all(defs);
        },
        _on_change_recuperation: function () {
            this.payment_resume.addClass('d-none');
            this.appointment.addClass('d-none');
            this.package.addClass('d-none');
            this.vehicle.addClass('d-none');
            this.recuperation.removeClass('d-none');
        },
        _on_change_appointment: function () {
            this.payment_resume.addClass('d-none');
            this.package.addClass('d-none');
            this.recuperation.addClass('d-none');
            this.vehicle.addClass('d-none');
            this.appointment.removeClass('d-none');
        },
        /* _on_change_package: function() {
            this.payment_resume.addClass('d-none');
            this.recuperation.addClass('d-none');
            this.appointment.addClass('d-none');
            this.vehicle.addClass('d-none');
            this.package.removeClass('d-none');
        },*/
        _on_change_vehicle: function () {
            this.payment_resume.addClass('d-none');
            this.recuperation.addClass('d-none');
            this.appointment.addClass('d-none');
            this.package.addClass('d-none');
            this.vehicle.removeClass('d-none');
        },

        get_user_info: function () {
            var inside = this;
            if (this.custom_yes.is(":checked")) {
                ajax.jsonRpc('/user/info/', 'call', {}).then(function (data) {
                    const workphone = data.work_phone ? data.work_phone : "";
                    const user_name = data.name ? data.name : "";
                    inside.tel.val(workphone);
                    inside.name.val(user_name);
                    inside._manage_input_contact();
                });
            } else if (this.custom_no.is(":checked")) {
                this.tel.val("");
                this.name.val("");
                this._manage_input_contact();
            }
        },
        _manage_input_contact: function () {
            if (this.custom_yes.is(":checked")) {
                if (!this.tel.val()) {
                    this.small_tel.show();
                    this.tel.css('border-color', 'red')
                } else if (!this.name.val()) {
                    this.small_name.show();
                    this.name.css('border-color', 'red')
                } else {
                    this.small_tel.hide();
                    // This.tel.css('border-color', 'black');
                    this.small_name.hide();
                    // This.name.css('border-color', 'black')
                }
            }
        },
        check_label_string: function () {
            if (this.custom_yes.is(":checked")) {
                this.tel.parents('.form-group').find('#for-tel').text('Mon numéro *');
                this.name.siblings('label').text('Mon nom et prénom *');
            } else if (this.custom_no.is(":checked")) {
                this.tel.parents().find('#for-tel').text('Son numéro *');
                this.name.siblings('label').text('Son nom et prénom *');
            }
        },
        _on_get_check_user: function () {
            this.get_user_info();
            this.check_label_string();
        },
        _on_change_tel: function () {
            if (this.custom_yes.is(":checked")) {
                if (!this.tel.val()) {
                    this.small_tel.show();
                    this.tel.css('border-color', 'red')
                } else {
                    this.small_tel.hide();
                    // This.tel.css('border-color', 'black')
                }
            }
        },
        _on_change_name: function () {
            if (!this.name.val()) {
                this.small_name.show();
                this.name.css('border-color', 'red')
            } else {
                this.small_name.hide();
                // This.name.css('border-color', 'black')
            }
        },
        reformat_date_time_final: function (date, time) {
            return date + " " + time + ":" + '00';
        },
        _convert_to_appropriate_format: function (date, format = '-') {
            const daySplited = date.split('/');
            const y = daySplited[2];
            const m = daySplited[1];
            const d = daySplited[0];
            return y + format + m + format + d
        },
        _create_rpc_crm: async function (partner_id = false, maps_image = false) {
            const date_off_set = new Date();
            const off_set = date_off_set.getTimezoneOffset();
            const real_street = $('#real_address_recovery').val()
            const pickup_zone = real_street ? real_street : this.address_recuperation.val()
            const date_start = this._convert_to_appropriate_format($('#date').val());
            const time_start = $('#time').val();
            const price = $('#choose_rate').find("input[type=radio]:checked").data('price');
            const location_duration = $('#choose_rate').find("input[type=radio]:checked").data('id');
            const client_note = $('#details').val();
            const category_id = $("input[name='vehicle_customRadio']:checked").data('id')
            const crm = {
                'partner_id': partner_id,
                'pick_up_zone': pickup_zone,
                'duration': $('#choose_rate').find("input[type=radio]:checked").data('hour') + ' h ' + ' 00 mn',
                'pick_up_datetime': this.reformat_date_time_final(date_start, time_start),
                'off_set': off_set,
                'expected_revenue': parseFloat(price),
                'pick_up_lat': $('#latitude_address_recovery').val(),
                'pick_up_long': $('#longitude_address_recovery').val(),
                'vehicle_note': vehicleLongWidget.prototype.choosing_vehicle(),
                'phone_in_moment': this.tel.val(),
                'type': 'opportunity',
                'maps_image': maps_image,
                'is_location': true,
                'location_duration': parseInt(location_duration),
                'client_note': client_note,
                'by_website': true,
                'model_category_id': category_id
            };
            const self = this;
            rpc.query({
                model: 'crm.lead',
                method: 'create_crm_lead',
                args: [crm]
            }).then(function (result) {
                $('.loading').hide();
                if ($(window).width() <= 767) {
                    self.payment_resume.addClass('d-none');
                    self.here_we_go_resume.removeClass('d-none');
                    $("#evtc_aside").animate({scrollTop: 0});
                }
                if ($(window).width() > 767) {
                    $('#confirmationModalLongDuration').modal('show');
                }
            })
        },
        create_new_client: async function (maps_image) {
            let route_method = '/update/partner'
            const partner = {
                'name': this.name.val(),
                'phone': this.tel.val(),
            };
            if (window.PartnerSelectedId && window.PartnerSelectedId !== 0) {
                partner.partner_id = parseInt(window.PartnerSelectedId)
            }
            if (this.custom_no.is(':checked')) {
                route_method = '/new/partner';
                const country = $('#own_country').val();
                const email = $('#mail_no_partner').val();
                partner.country_id = country;
                partner.email = email;
            }
            const er = $('.small-constrains');
            er.empty();
            await ajax.jsonRpc(route_method, 'call', partner).then(function (result) {
                if (!result.arch) {
                    er.append('<p>' + result.details + '</p>');
                    er.show();
                    return
                }
                window.LcasCondition = result.id
            })
        },
        middle_object: function (image) {
            this._create_rpc_crm(window.LcasCondition, image)
        },
        _prepare_screen_shot: function (element) {
            var userAgent = navigator.userAgent || navigator.vendor || window.opera;
            if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
                return new Promise(function (resolve, reject) {
                    resolve(false);
                })
            }
                $("#evtc_location_maps .gm-style .gm-style-iw-c").css({
                    "box-shadow": "initial",
                    "transform": "initial"
                });
                $("#evtc_location_maps .gm-style .gm-style-iw-tc").css({"transform": "initial"});
                return new Promise(function (resolve, reject) {
                    html2canvas(document.getElementById(element), {
                        backgroundColor: null,
                        useCORS: true
                    }).then(canvas => {
                        resolve(canvas)
                    }).catch(error => {
                        reject(error);
                    });
                })

        },
        _get_appointment_time_modal: function () {
            const date_start = $('#date').val();
            const time_start = $('#time').val();
            const date_end = $('#date_end').val();
            const time_end = $('#time_end').val();
            const details = $('.details_run').val();

            const date_modal_start = appointementLongWidget.prototype.reformat_date_time(date_start, time_start);
            const date_modal_end = appointementLongWidget.prototype.reformat_date_time(date_end, time_end);

            $('#modal_start').text('Début: ' + date_modal_start)
            $('#modal_end').text('Fin: ' + date_modal_end)
            $('#modal_details_value').text('Détails: ' + details)
        },
        _get_appointment_time_resume: function () {
            const date_start = $('#date').val();
            const time_start = $('#time').val();
            const date_end = $('#date_end').val();
            const time_end = $('#time_end').val();
            const details = $('.details_run').val();
            const date_resume_start = appointementLongWidget.prototype.reformat_date_time(date_start, time_start);
            const date_resume_end = appointementLongWidget.prototype.reformat_date_time(date_end, time_end);
            $('#resume_start').text('Début: ' + date_resume_start)
            $('#resume_end').text('Fin: ' + date_resume_end)
            $('#resume_details_value').text('Détails: ' + details)
        },
        _on_click_payment_resume_button: async function () {
            var self = this;
            if (!self.tel.val()) {
                self.small_tel.show();
                self.tel.css('border-color', 'red')
                self.tel.parents('.form-group').find('.select-contact').css('border-color', 'red')

                return
            }
            if (!self.name.val()) {
                self.small_name.show();
                self.name.css('border-color', 'red')
                return
            }
            if (self.custom_no.is(":checked")) {
                const country = $('#own_country').val();
                const small_email = $('.small-email');
                const input_mail = $('#mail_no_partner');
                if (country !== 'MG' && !input_mail.val()) {
                    small_email.show();
                    input_mail.css('border-color', 'red');
                    return
                }
                    small_email.hide();

            }
            $('#evtc_payement_resume_button_long').prop("disabled", true);
            $('.loading').show();
            await self.create_new_client()
            if (window.LcasCondition === 0) {
                $('.loading').hide();
                $('#evtc_payement_resume_button').prop("disabled", false);
                return;
            }
            self._prepare_screen_shot('evtc_location_maps').then(function (canvas) {
                const maps_image = canvas ? canvas.toDataURL('image/jpeg', 0.3) : false;
                const duration_resume = $('#choose_rate').find("input[type=radio]:checked").data('hour');
                self.recuperation_adress_heading_payment_resume.contents().eq(4).remove();
                self.recuperation_adress_heading_payment_resume.find('.place_val').after(self.address_recuperation.val());
                self._get_appointment_time_resume();
                self.choise_vehicle_payment_resume_heading.contents().eq(2).remove();
                self.choise_vehicle_payment_resume_heading.find('span').after(vehicleLongWidget.prototype.choosing_vehicle());
                self.choice_package_resume_heading.contents().eq(2).remove();
                self.choice_package_resume.after(duration_resume + ' H');
                self.tel_payment_resume.text(self.tel.val());

                self.recuperation_adress_heading_payment_resume_modal.contents().eq(4).remove();
                self.recuperation_adress_heading_payment_resume_modal.find('.place_val').after(self.address_recuperation.val());

                self._get_appointment_time_modal();
                self.choise_vehicle_payment_resume_heading_modal.contents().eq(2).remove();
                self.choise_vehicle_payment_resume_heading_modal.find('span').after(vehicleLongWidget.prototype.choosing_vehicle());
                self.choice_package_resume_heading_modal.contents().eq(2).remove();
                self.choice_package_resume_modal.after(duration_resume + ' H');
                self.tel_payment_resume_modal.text(self.tel.val());

                if (maps_image){
                    self.middle_object(maps_image);
                }else{
                    self._create_rpc_crm(window.LcasCondition, false)
                }
                self.small_name.hide();
                self.small_tel.hide();
            }).catch(function (error) {
                $('#evtc_payement_resume_button_long').prop("disabled", false);
                $('.loading').hide();
            })

        },
    })
    return {
        paymentResumeLongWidget: publicWidget.registry.paymentResumeLongWidget
    };
})
