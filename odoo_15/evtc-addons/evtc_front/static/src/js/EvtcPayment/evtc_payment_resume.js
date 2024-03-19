odoo.define("evtc_front.payment_resume_template", function (require) {
    "use strict";

    const ajax = require("web.ajax");
    const rpc = require("web.rpc");
    window.LcasCondition = 0;
    const EvtcMaps = require("evtc_front.reservations");
    EvtcMaps.evtcArkeupMap.include({
        events: _.extend({}, EvtcMaps.evtcArkeupMap.prototype.events, {
            "click #change_recuperation_payment": "_on_change_recuperation",
            "click #change_destination_payment": "_on_change_destination",
            "click #change_choise_vehicle_payment": "_on_change_vehicle",
            "click #change_time_payment": "_on_change_time",
            "click #change_payment_method": "_on_change_payment",
            "change #customRadio10": "_on_get_check_user",
            "change #customRadio11": "_on_get_check_user",
            "keyup #tel": "_on_change_tel",
            "keydown #tel": "_on_change_tel",
            "change #tel": "_on_change_tel",
            "focusout #tel": "_on_change_tel",
            "keyup #name": "_on_change_name",
            "keydown #name": "_on_change_name",
            "change #name": "_on_change_name",
            "focusout #name": "_on_change_name",
            'click #evtc_payement_resume_button': '_onClickPaymentResumeButton',
        }),
        start: async function () {
            await this._super.apply(this, arguments);
            window.PartnerSelectedId = 0;
            this.get_user_info();
            this.check_label_string();
            this.mine_obj = 0;
        },
        _on_change_recuperation: function () {
            this.payment_resume.addClass("d-none");
            this.recuperation.removeClass("d-none");
        },
        _on_change_destination: function () {
            this.payment_resume.addClass("d-none");
            this.destination.removeClass("d-none");
        },
        _on_change_time: function () {
            this.payment_resume.addClass("d-none");
            this.appointment.removeClass("d-none");
        },
        _on_change_vehicle: function () {
            this.payment_resume.addClass("d-none");
            this.vehicle.removeClass("d-none");
        },
        _on_change_payment: function () {
            this.payment_resume.addClass("d-none");
            this.payment.removeClass("d-none");
        },
        get_user_info: function () {
            const inside = this;
            if (this.custom_yes.is(":checked")) {
                ajax.jsonRpc("/user/info/", "call", {}).then(function (data) {
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
                    this.tel.css("border-color", "red");
                } else if (!this.name.val()) {
                    this.small_name.show();
                    this.name.css("border-color", "red");
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
                this.tel.parents(".form-group").find("#for-tel").text("Mon numéro *");
                this.name.siblings("label").text("Mon nom et prénom *");
            } else if (this.custom_no.is(":checked")) {
                this.tel.parents().find("#for-tel").text("Son numéro *");
                this.name.siblings("label").text("Son nom et prénom *");
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
                    this.tel.css("border-color", "red");
                } else {
                    this.small_tel.hide();
                    // This.tel.css('border-color', 'black')
                }
            }
        },
        _on_change_name: function () {
            if (!this.name.val()) {
                this.small_name.show();
                this.name.css("border-color", "red");
            } else {
                this.small_name.hide();
                // This.name.css('border-color', 'black')
            }
        },

        prepareCrmData: function (partner, maps = false) {
            const note =
                "Voiture:" +
                this.choosing_vehicle() +
                "\nMéthode de payment:" +
                this.get_payment_method();
            const date_off_set = new Date();
            const off_set = date_off_set.getTimezoneOffset();
            const real_street = $("#real_address_recovery").val();
            const pickup_zone = real_street ? real_street : this.address_recuperation.val();
            const real_street_destination = $("#destination_address_destination").val();
            const destination_zone = real_street_destination ?
                real_street_destination :
                this.address_destination.val();
            let total_estimation = "";
            let to_estimate = $("#total_min_to_pay");
            if (to_estimate.length > 0) {
                total_estimation = to_estimate[0].innerHTML;
            }
            let model_id = $("input[name='vehicle_customRadio']:checked").data()["id"];
            const isNow = this.customRadioNow.is(":checked");
            return {
                partner_id: partner,
                pick_up_zone: pickup_zone,
                destination_zone: destination_zone,
                duration: $("#duration").text(),
                estimated_kilometers: parseFloat($("#length_target").text().replace(",", ".")),
                pick_up_datetime: this._getAppoitmentDatetime(isNow),
                off_set: off_set,
                expected_revenue: parseFloat(this.total_to_pay.text().replace(/\D/g, "")),
                dest_lat: $("#latitude_address_destination").val(),
                dest_long: $("#longitude_address_destination").val(),
                pick_up_lat: $("#latitude_address_recovery").val(),
                pick_up_long: $("#longitude_address_recovery").val(),
                client_note: note,
                vehicle_note: this.choosing_vehicle(),
                payment_method_note: this.get_payment_method(),
                phone_in_moment: this.tel.val(),
                type: "opportunity",
                maps_image: maps,
                by_website: true,
                estimated_price: total_estimation,
                model_category_id: model_id ? model_id : false,
            };
        },

        requestCrmObject: async function (crm = {}, method, models) {
            await rpc
                .query({
                    model: models,
                    method: method,
                    args: [crm],
                })
                .then((result) => {
                    $(".loading").hide();
                    sessionStorage.setItem("create_crm_lead", result);
                    if ($(window).width() <= 767) {
                        this.payment_resume.addClass("d-none");
                        this.here_we_go_resume.removeClass("d-none");
                        $("#evtc_aside").animate({scrollTop: 0});
                    }
                    if ($(window).width() > 767) {
                        $("#confirmationModal").modal("show");
                    }
                    return result;
                })
                .catch((error) => {
                    console.error(error.message);
                    this.show_errors();
                    return false;
                });
        },

        show_errors: function () {
            $(".loading").hide();
            $("#evtc_payement_resume_button").prop("disabled", false);
        },
        getListToCheck: function () {
            return ["pick_up_lat", "pick_up_long", "dest_lat", "dest_long"];
        },
        check_crm_value_data: function (data) {
            if (!data) {
                return false;
            }
            let toPassed = true;
            let values = this.getListToCheck();
            for (let i = 0; i < values.length; i++) {
                let value = values[i];
                if (value in data && data[value] === "") {
                    toPassed = false;
                    break;
                }
            }
            return toPassed;
        },

        _create_rpc_crm: async function (partner_id = false, maps_image = false) {
            let crm_values = await this.prepareCrmData(partner_id, maps_image);
            let isValidate = this.check_crm_value_data(crm_values);
            if (!isValidate) {
                return false;
            }
            let crm_lead_id = await this.requestCrmObject(
                crm_values,
                "create_crm_lead",
                "crm.lead"
            );
        },
        create_new_client: async function (maps_image) {
            let route_method = "/update/partner";
            const partner = {
                name: this.name.val(),
                phone: this.tel.val(),
            };
            if (window.PartnerSelectedId && window.PartnerSelectedId !== 0) {
                partner.partner_id = parseInt(window.PartnerSelectedId);
            }
            if (this.custom_no.is(":checked")) {
                route_method = "/new/partner";
                const country = $("#own_country").val();
                const email = $("#mail_no_partner").val();
                partner.country_id = country;
                partner.email = email;
            }
            const er = $(".small-constrains");
            er.empty();
            await ajax.jsonRpc(route_method, "call", partner).then(function (result) {
                if (!result.arch) {
                    er.append("<p>" + result.details + "</p>");
                    er.show();
                    return;
                }
                window.LcasCondition = result.id;
            });
        },
        middle_object: function (image) {
            this._create_rpc_crm(window.LcasCondition, image);
        },

        _prepare_screen_shot: function (element) {
            var userAgent = navigator.userAgent || navigator.vendor || window.opera;
            if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
                return new Promise(function (resolve, reject) {
                    resolve(false);
                });
            }
            $("#evtc_maps .gm-style .gm-style-iw-c").css({
                "box-shadow": "initial",
                transform: "initial",
            });
            $("#evtc_maps .gm-style .gm-style-iw-tc").css({transform: "initial"});
            return new Promise(function (resolve, reject) {
                html2canvas(document.getElementById(element), {
                    backgroundColor: null,
                    useCORS: true,
                })
                    .then((canvas) => {
                        resolve(canvas);
                    })
                    .catch((error) => {
                        reject(error);
                    });
            });
        },
        _onClickPaymentResumeButton: async function () {
            await this.record_user_log()
            const self = this;
            if (!self.tel.val()) {
                self.small_tel.show();
                self.tel.css("border-color", "red");
                self.tel
                    .parents(".form-group")
                    .find(".select-contact")
                    .css("border-color", "red");

                return;
            }
            if (!self.name.val()) {
                self.small_name.show();
                self.name.css("border-color", "red");
                return;
            }
            if (self.custom_no.is(":checked")) {
                const country = $("#own_country").val();
                const small_email = $(".small-email");
                const input_mail = $("#mail_no_partner");
                if (country !== "MG" && !input_mail.val()) {
                    small_email.show();
                    input_mail.css("border-color", "red");
                    return;
                }
                small_email.hide();
                // Input_mail.css('border-color', 'black');
            }
            $("#evtc_payement_resume_button").prop("disabled", true);
            $(".loading").show();
            await self.create_new_client();
            self._prepare_screen_shot("evtc_maps").then(function (canvas) {
                const maps_image = canvas ? canvas.toDataURL("image/jpeg", 0.3) : false;
                self.recuperation_adress_heading_payment_resume.contents().eq(4).remove();
                self.recuperation_adress_heading_payment_resume.find(".place_val")
                    .after(self.address_recuperation.val());
                self.destination_adress_heading_payment_resume.contents().eq(4).remove();
                self.destination_adress_heading_payment_resume
                    .find(".place_val")
                    .after(self.address_destination.val() || self.lastDestination);
                self.time_heading_payment_resume.contents().eq(2).remove();
                self.time_payment_resume.after(self.get_appointment_time());
                self.choise_vehicle_payment_resume_heading.contents().eq(2).remove();
                self.choise_vehicle_payment_resume_heading.find("span")
                    .after(self.choosing_vehicle());
                self.choose_payment_resume_method.text(self.get_payment_method());
                self.tel_payment_resume.text(self.tel.val());
                $(self.el).find(".oe_pickup_place_value").text("");
                $(self.el).find(".oe_dest_place_value").text("");
                $(self.el).find(".oe_pickup_place_value").append(self.address_recuperation.val());
                $(self.el).find(".oe_dest_place_value").append(self.address_destination.val());
                self.time_heading_payment_resume_modal.contents().eq(2).remove();
                self.time_payment_resume_modal.after(self.get_appointment_time());
                self.choise_vehicle_payment_resume_heading_modal.contents().eq(2).remove();
                self.choise_vehicle_payment_resume_heading_modal.find("span").after(self.choosing_vehicle());
                self.choose_payment_resume_method_modal.text(self.get_payment_method());
                self.tel_payment_resume_modal.text(self.tel.val());
                if (maps_image) {
                    self.middle_object(maps_image);
                } else {
                    self._create_rpc_crm(window.LcasCondition, false);
                }
                self.small_name.hide();
                // Self.name.css('border-color', 'black');
                self.small_tel.hide();
                // Self.tel.css('border-color', 'black');
            })
                .catch(function (error) {
                    $("#evtc_payement_resume_button").prop("disabled", false);
                    $(".loading").hide();
                });
        },
    });
});
