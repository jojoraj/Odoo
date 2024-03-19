odoo.define('evtc_taxi.final_resume_template', function (require) {
    "use strict";

    const FinalResumeTemplate = require('evtc_front.final_resume_template');
    const widgets = require('web.public.widget');
    widgets.registry.FinalResumeTemplate = FinalResumeTemplate.ConfirmationModal.extend({
        events: _.extend({}, FinalResumeTemplate.ConfirmationModal.prototype.events, {
            'click .click': '_onPlaceService',
        }),
        _AddEventModal: function () {
            $('#confirmationModal').on('show.bs.modal', function (event) {
                const { taxi, create_crm_lead } = sessionStorage;
                if (taxi === 'true' && create_crm_lead !== undefined) {
                    event.preventDefault();
                    window.location = '/taxi-reservation/' + create_crm_lead
                }
            });
            this._super.apply(this, arguments);
        }
    })
    return widgets.registry.FinalResumeTemplate
})
