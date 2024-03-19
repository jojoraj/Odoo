odoo.define('evtc_lmfs.EvtcFinalResume', function (require) {
    "use strict";

    const FinalResumeTemplate = require('evtc_front.final_resume_template');
    const widgets = require('web.public.widget');
    widgets.registry.EvtcLmfsFinalResume = FinalResumeTemplate.ConfirmationModal.extend({
        _AddEventModal: function () {
            $('#confirmationModal').on('show.bs.modal', (event) => {
                const {create_crm_lead} = sessionStorage
                const opportunity_data = JSON.parse(create_crm_lead)
                sessionStorage.removeItem('create_crm_lead')
                if (opportunity_data && opportunity_data.mo_lmfs_status === 'active' && opportunity_data.id !== undefined && opportunity_data.is_trip_now) {
                    event.preventDefault();
                    window.location.replace('/trip-reservation/' + opportunity_data.id)
                } else if (opportunity_data.id) {
                    sessionStorage.setItem('create_crm_lead', opportunity_data.id)
                }
            });
            this._super.apply(this, arguments);
        }
    })
    return widgets.registry.EvtcLmfsFinalResume
})
