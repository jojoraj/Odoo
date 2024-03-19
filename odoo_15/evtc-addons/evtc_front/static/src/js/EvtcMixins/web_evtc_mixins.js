odoo.define("evtc_front.web_evtc_mixins", function (require) {
    "use strict";

    const events = require("evtc_front.reservations");
    const core = require('web.core');
    const _t = core._t;
    events.evtcArkeupMap.include({
        events: _.extend({}, events.evtcArkeupMap.prototype.events, {
            "click .oe_event_web_change": "_onClickModifyEvents",
        }),

        start: async function () {
            await this._super.apply(this, arguments);
            this._initEvtcSelector();
            this.evtcParentNode = await this._getParents();
        },
        /**
         * this function calculates the day and date from the reservation made by the user
         *
         * @user
         * @extends evtc_front.reservations
         * @param {isCurrentMoment} boolean - the type of user choice.
         * @param {calendar} selector - the date on which the user selected the date.
         * @param {time} selector - the time on which the user selected the date.
         * @return {date} string - format Y-m-d H:M
         */

        _getAppoitmentDatetime: function (isCurrentMoment) {
            let calendar = $("#date");
            let time = $("#time");
            if (isCurrentMoment) {
                let date = new Date();
                date = new Date(date.getTime() + 30 * 60 * 1000);
                return (
                    date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " + date.getHours() + ":" +
                    date.getMinutes() + ":" + date.getSeconds()
                );
            }
            const vals = calendar.val();
            if (vals === "Aujourd'hui") {
                const today = new Date();
                return (
                    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate() + " " + time.val() + ":00"
                );
            } else if (vals === "Demain") {
                let tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                tomorrow = new Date(tomorrow);
                return (
                    tomorrow.getFullYear() + "-" + (tomorrow.getMonth() + 1) + "-" + tomorrow.getDate() +
                    " " + time.val() + ":" + "00"
                );
            } else if (vals === "Après demain") {
                let afterTomorrow = new Date();
                afterTomorrow.setDate(afterTomorrow.getDate() + 2);
                afterTomorrow = new Date(afterTomorrow);
                return (
                    afterTomorrow.getFullYear() + "-" + (afterTomorrow.getMonth() + 1) + "-" + afterTomorrow.getDate() +
                    " " + time.val() + ":" + "00"
                );
            }
            const xsplited = vals.split("/");
            const date = new Date(xsplited[2] + "/" + xsplited[1] + "/" + xsplited[0]);
            return (
                date.getFullYear() +
                "-" +
                (date.getMonth() + 1) +
                "-" +
                date.getDate() +
                " " +
                time.val() +
                ":00"
            );
        },

        /**
         *
         * defined all selector in the current selector
         * make all variable in global
         */
        _initEvtcSelector: function () {
            this.recuperation_adress_heading_appointment = $(
                "#recuperation_adress_heading_appointment"
            );
            this.recuperation_adress_appointment = $("#recuperation_adress_appointment");
            this.destination_adress_appointment = $("#destination_adress_appointment");
            this.time_heading_appointment = $("#time_heading_appointment");
            this.time_appointment = $("#time_appointment");
            this.destination_adress_heading_appointment = $(
                "#destination_adress_heading_appointment"
            );
            this.time_selection = $("#time_selection");
            this.waiting = $("#waiting");
            this.waiting_label = $("#waiting_label");
            this.destination = $("#evtc_destination");
            this.div_destination = $("#evtc-form-destination");
            this.recuperation_adress_heading_destination = $(
                "#recuperation_adress_heading_destination"
            );
            this.recuperation_adress_destination = $("#recuperation_adress_destination");
            this.destination_adress_heading = $("#destination_adress_heading");
            this.destination_adress = $("#destination_adress");
            this.destination_address_destination = $("#destination_address_destination");
            this.address_recuperation = $("#address_recuperation");
            this.div_recuperation = $("#evtc-form-recuperation");
            this.recuperation_adress_heading = $("#recuperation_adress_heading");
            this.recuperation_adress = $("#recuperation_adress");
            this.real_address_recovery = $("#real_address_recovery");
            this.small_tel = $(".small-tel");
            this.small_name = $(".small-name");
            this.payment_resume = $("#evtc_payement_resume");
            this.appointment = $("#evtc_appointment");
            this.payment = $("#evtc_payement");
            this.custom_yes = $("#customRadio10");
            this.custom_no = $("#customRadio11");
            this.tel = $("#tel");
            this.name = $("#name");
            this.here_we_go_resume = $("#evtc_here_we_go_resume");
            this.address_destination = $("#address_destination");
            this.customRadioNow = $("#customRadio1");
            this.customRadioSet = $("#customRadio2");
            this.total_to_pay = $("#total_to_pay");
            this.recuperation_adress_heading_payment_resume = $(
                "#recuperation_adress_heading_payment_resume"
            );
            this.recuperation_adress_heading_payment_resume_modal = $(
                "#recuperation_adress_heading_payment_resume_modal"
            );
            this.recuperation_adress_payment_resume = $(
                "#recuperation_adress_payment_resume"
            );
            this.destination_adress_heading_payment_resume = $(
                "#destination_adress_heading_payment_resume"
            );
            this.destination_adress_heading_payment_resume_modal = $(
                "#destination_adress_heading_payment_resume_modal"
            );
            this.destination_adress_payment_resume = $("#destination_adress_payment_resume");
            this.time_heading_payment_resume = $("#time_heading_payment_resume");
            this.time_heading_payment_resume_modal = $("#time_heading_payment_resume_modal");
            this.time_payment_resume = $("#time_payment_resume");
            this.time_payment_resume_modal = $("#time_payment_resume_modal");
            this.choise_vehicle_payment_resume_heading = $(
                "#choise_vehicle_payment_resume_heading"
            );
            this.choise_vehicle_payment_resume_heading_modal = $(
                "#choise_vehicle_payment_resume_heading_modal"
            );
            this.choose_payment_resume_method = $("#choose_payment_resume_method");
            this.choose_payment_resume_method_modal = $(
                "#choose_payment_resume_method_modal"
            );
            this.tel_payment_resume = $("#tel_payment_resume");
            this.tel_payment_resume_modal = $("#tel_payment_resume_modal");
            this.div_choose = $("#choose_vehicle");
            this.choose_payment = $("#choose_payment");
            this.small_name.hide();
            this.small_tel.hide();
            this.errosHtmlMessage =
                '<small class="text-danger">Veuillez remplir le champs</small>';
            this.recuperation = $("#evtc_recuperation");
            this.vehicle = $("#evtc_vehicle");
            this.recuperation_adress_heading_vehicle_resume = $(
                "#recuperation_adress_heading_vehicle_resume"
            );
            this.recuperation_adress_vehicle_resume = $(
                "#recuperation_adress_vehicle_resume"
            );
            this.destination_adress_heading_vehicle_resume = $(
                "#destination_adress_heading_vehicle_resume"
            );
            this.destination_adress_vehicule_resume = $(
                "#destination_adress_vehicule_resume"
            );
            this.time_heading_vehicle_resume = $("#time_heading_vehicle_resume");
            this.time_vehicle_resume = $("#time_vehicle_resume");
            this.choise_vehicle_resume_heading = $("#choise_vehicle_resume_heading");
            this.choise_vehicle_resume = $("#choise_vehicle_resume");
            this.recuperation_adress_heading_vehicle = $(
                "#recuperation_adress_heading_vehicle"
            );
            this.recuperation_adress_vehicle = $("#recuperation_adress_vehicle");
            this.destination_adress_heading_vehicle = $(
                "#destination_adress_heading_vehicle"
            );
            this.destination_adress_vehicule = $("#destination_adress_vehicule");
            this.time_heading_vehicle = $("#time_heading_vehicle");
            this.time_vehicle = $("#time_vehicle");
            this.choise_vehicle_heading = $("#choise_vehicle_heading");
            this.vehicle_resume = $("#evtc_vehicle_resume");
            this.recuperation_adress_heading_payment = $(
                "#recuperation_adress_heading_payment"
            );
            this.recuperation_adress_payment = $("#recuperation_adress_payment");
            this.destination_adress_heading_payment = $(
                "#destination_adress_heading_payment"
            );
            this.destination_adress_payment = $("#destination_adress_payment");
            this.time_heading_payment = $("#time_heading_payment");
            this.time_payment = $("#time_payment");
            this.choise_vehicle_payment_heading = $("#choise_vehicle_payment_heading");
            this.choise_vehicle_payment = $("#choise_vehicle_payment");
            this.choose_payment_method = $("#choose_payment_method");
        },

        _getParents: function () {
            return {
                evtc_recuperation_button: "evtc_recuperation",
                evtc_destination_button: "evtc_destination",
                evtc_appointment_button: "evtc_appointment",
                evtc_vehicle_button: "evtc_vehicle",
                evtc_vehicle_resume_button: "evtc_vehicle_resume",
                evtc_payement_button: "evtc_payement",
                evtc_payement_resume_button: "evtc_payement_resume",
                evtc_here_we_go_resume_button: "evtc_here_we_go_resume",
            };
        },

        /**
        * @param { undefined }
        * @return { dict } headerTemplate: list of the header in the template
        */
        _getHeaderTemplate: function () {
            return {
                evtc_recuperation: [
                    "recuperation_adress_heading",
                    'recuperation_adress_heading_destination',
                    'recuperation_adress_heading_appointment',
                    'recuperation_adress_heading_vehicle',
                    'recuperation_adress_heading_vehicle_resume',
                    'recuperation_adress_heading_payment',
                ],
                evtc_destination: [
                    'destination_adress_heading',
                    'destination_adress_heading_appointment',
                    'destination_adress_heading_vehicle',
                    'destination_adress_heading_vehicle_resume',
                    'destination_adress_heading_payment',
                ],
                evtc_appointment: [
                    'time_heading_appointment',
                    'time_heading_vehicle',
                    'time_heading_vehicle_resume',
                    'time_heading_payment',
                ],
                evtc_vehicle: [
                    'choise_vehicle_heading',
                    'choise_vehicle_resume_heading',
                    'choise_vehicle_payment_heading',
                ],
                evtc_vehicle_resume: [],
                evtc_payement: [
                    'choose_payment_method'
                ],
                evtc_payement_resume: [],
                evtc_here_we_go_resume: []
            }
        },

        _getHeaderItalic: function () {
            return {
                evtc_recuperation: [
                    "recuperation_adress",
                    'recuperation_adress_destination',
                    'recuperation_adress_appointment',
                    'recuperation_adress_vehicle',
                    'recuperation_adress_vehicle_resume',
                    'recuperation_adress_payment'
                ],
                evtc_destination: [
                    'destination_adress',
                    'destination_adress_heading_appointment',
                    'destination_adress_vehicule',
                    'destination_adress_vehicule_resume',
                    'destination_adress_payment'
                ],
                evtc_appointment: [
                    'time_appointment',
                    'time_vehicle',
                    'time_vehicle_resume',
                    'time_payment',
                ],
                evtc_vehicle: [
                    'choise_vehicle',
                    'choise_vehicle_resume',
                    'choise_vehicle_payment',
                ],
                evtc_vehicle_resume: [],
                evtc_payement: [
                    'choose_payment_method',
                ],
                evtc_payement_resume: [],
                evtc_here_we_go_resume: []
            }
        },
        /**
         * @overload
         * @param { string } templateId: the id of the template
         * @return { list } the list of the header to update
         */
        _getHeaderList: function (templateId) {
            let templates = this._getHeaderTemplate();
            return templates[templateId]
        },

        _getHeaders: function (template) {
            return this._getHeaderItalic()[template]
        },

        _getHeadHTML: function (type, text, oeClass) {
            const myCustomHtml =
                `
                <span>
                    <span> `+ type + ` </span> <i class="` + oeClass + `" id="destination_adress"/>
                        ` + text + ` </span>
            `;
            return myCustomHtml
        },

        _setValueByEdit: function (template) {

            const head = this._getHeaders(template)
            const tmplHead = this._getHeaderList(template)
            let key = this._getStepByXmlID(template);
            let params = this._ObjectsParams[key]
            for (let index = 0; index < tmplHead.length; index++) {
                if (params.escape && tmplHead[index] && tmplHead[index]) {
                    $('#' + tmplHead[index]).empty()
                    $('#' + tmplHead[index]).append(this._getHeadHTML(params.type, params.value, params.oeClass))
                }
            }
        },

        convertHMS: function (d) {
            d = Number(d);
            var h = Math.floor(d / 3600);
            var m = Math.floor((d % 3600) / 60);
            var hDisplay = h > 0 ? h + (h === 1 ? " h " : " h") : "";
            var mDisplay = m > 0 ? m + (m === 1 ? " mn " : " mn") : "";
            return hDisplay + mDisplay;
        },

        _ShowObjectParamsLog: function () {
            /**
             * show log for debugging
             * console.log(this._ObjectsParams)
             */
        },
        _nextStep: (currentId) => {
            let $el = $("#" + currentId)
            if ($el.length > 0 && !$el.hasClass('d-none')) {
                $el.addClass('d-none')
            }
        },
        _hideStep: ($el) => {
            if ($el && $('#' + $el).length > 0 && !$('#' + $el).hasClass('d-none')) {
                $('#' + $el).addClass('d-none')
            }
        },

        _showStep: (currentId) => {
            if (currentId && $('#' + currentId).length > 0 && $('#' + currentId).hasClass('d-none')) {
                $("#" + currentId).removeClass("d-none")
            }
        },

        _onClickModified: function (events) {
            let step = this.evtcParentNode[events.target.id];
            this._autoPassStep(step, events.target.id);
        },
        _onClickModifyEvents: function (events) {
            let step = events.currentTarget.getAttribute('target');
            if ('evtc_recuperation' === step){
                $('#' + step).find('.save-recently-wrap').attr('style','')
            }
            this._autoHideAllStepWithoutSelected(step);
        },

        _stepByAppoitment: function () {
            let step = this._getStepByXmlID('evtc_vehicle_resume');
            if (step) {
                this._ObjectsParams[step].escape = false
            }
            this._addClassByStep("evtc_appointment_button");
        },

        /**
         * add class oe_auto_passed to listen events click
         * @param {string} el: button action id
         * */
        _addClassByStep: (el) => {
            if (el && $("#" + el).length > 0) {
                $("#" + el).addClass("oe_auto_passed")
            }
        },

        /**
         *
         * save value of input[@id='evtc_recuperation'] for all template
         * @param {string} $className: button action
         * @param {string} $inputId: input value
         * */
        _registerInputValues: function ($className, $inputId) {
            for (const [key, value] of Object.entries($('.' + $className))) {
                if (!isNaN(parseInt(key)) && $(value).length > 0) {
                    let postMessage = _t('From : ')
                    value.innerText = postMessage + $('#' + $inputId).val()
                }
            }
        },
        /**
         * close current step and show next step
         * @param {string} current: current template id
         * */
        _showNextStep: function (currentElement) {
            let steps = this._getStep()
            const stepIndex = steps.indexOf(currentElement);
            if (stepIndex + 1 < steps.length && steps[stepIndex + 1]) {
                $('#' + steps[stepIndex + 1]).removeClass('d-none')
            }
            this._hideStep(steps[stepIndex])
        },

        /**
         * Remove class oe_auto_passed to break auto-call events
         * @param {string} el: button action id
         * */
        _removeClassByStep: function (el) {
            if (el && $('#' + el).length > 0) {
                $("#" + el).removeClass("oe_auto_passed")
            }
        },

        /**
         * hide template when his value is complete and show the latest not complete information
         * @param {string, string} [currentStep, stepButton]: template and button  selection id of current action
         * update vehicle_resume_template when step pass in
         * */
        _autoPassStep: async function (currentStep, stepButton) {
            this._removeClassByStep(stepButton);
            let steps = this._getStep();
            const stepIndex = steps.indexOf(currentStep);
            for (let i = stepIndex; i < steps.length; i++) {
                let values = steps[i];
                if (values) {
                    let step = this._getStepByXmlID(values);
                    this._setValueByEdit(values)
                    if (values === "evtc_vehicle_resume") {
                        //    vehicle_resume_template
                        await this._bindClickVehicle()
                    }
                    if (this._ObjectsParams[step].escape) {
                        await this._nextStep(values);
                    } else {
                        return this._showStep(values);
                    }
                }
            }
        },

        /**
         * auto-hide all template and show the only one present in events
         * @param {string} currentStep: parent of the event
         * */
        _autoHideAllStepWithoutSelected: function (currentStep) {
            let steps = this._getStep();
            for (let i = 0; i < steps.length; i++) {
                this._hideStep(steps[i]);
            }
            if (currentStep) {
                this._showStep(currentStep)
                // find button inside events
                let buttonValidate = $('#' + currentStep).find('button').filter(function (x, v) { if (v.id) { return v } })[0]
                if (this._getParents()[buttonValidate.id]) {
                    this._addClassByStep(buttonValidate.id);
                }
            }
        },

        _computeAutoClass: async function (events, templatesId, buttonId, values, lat, lng) {
            let ObjectKey = this._getStepByXmlID(templatesId);
            let validationNumber = ++this._ObjectsParams[ObjectKey].validationNumber;
            this._setStep(ObjectKey, true, true, values, lat, lng, validationNumber);
            this._ShowObjectParamsLog()
            this._showNextStep(templatesId)
            if ($('#' + buttonId).hasClass('oe_auto_passed')) {
                await this._onClickModified(events)
            }
        }
    });
});
