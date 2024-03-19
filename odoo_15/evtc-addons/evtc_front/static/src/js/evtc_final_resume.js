odoo.define('evtc_front.final_resume_template', function (require) {

    const publicWidget = require('web.public.widget');

    publicWidget.registry.ConfirmationModal = publicWidget.Widget.extend({
        selector: '.reservation_evtc',
        start: function () {
            return Promise.all([this._super.apply(this, arguments), this._AddEventModal()]);
        },
        _AddEventModal: function () {
            $('#confirmationModal').on('hidden.bs.modal', function () {
                window.location.replace("/my/home");;
            });
        }
    })
    return {
        ConfirmationModal: publicWidget.registry.ConfirmationModal
    }
});
