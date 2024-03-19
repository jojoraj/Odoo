odoo.define('evtc_location.evtc_final_resume_long', function (require) {

    const publicWidget = require('web.public.widget');

    publicWidget.registry.ConfirmationModalLongDuration = publicWidget.Widget.extend({
        selector: '.long-duration',
        start: function () {
            return Promise.all([this._super.apply(this, arguments), this._AddEventModal()]);
        },
        _AddEventModal: function () {
            $('#confirmationModalLongDuration').on('hidden.bs.modal', function () {
                window.location.replace("/my/home");;
            });
        }
    })
    return {
        ConfirmationModalLongDuration: publicWidget.registry.ConfirmationModalLongDuration
    }
});
