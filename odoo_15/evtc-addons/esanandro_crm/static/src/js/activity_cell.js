/** @odoo-module **/


import ActivityCell from '@mail/js/views/activity/activity_cell';
import {patch} from 'web.utils';
import session from 'web.session';

patch(ActivityCell.prototype, 'esanandro_crm/static/src/js/activity_cell.js', {
    /**
     * @override
     * @private
     */
    _render() {
        // replace clock by closest deadline
        const $date = $('<div class="o_closest_deadline">');
        // change by Tokill
        var d = new Date();
        var tz = - d.getTimezoneOffset();
        const date = moment(this.record.data.closest_deadline);
        // To remove year only if current year
        if (moment().year() === moment(date).year()) {
            $date.text(moment(date).add(tz, 'm').format('lll'));
        } else {
            $date.text(moment(date).format('ll'));
        }
        this.$('a').html($date);
        if (this.record.data.activity_ids.res_ids.length > 1) {
            this.$('a').append($('<span>', {
                class: 'badge badge-light badge-pill border-0 ' + this.record.data.activity_state,
                text: this.record.data.activity_ids.res_ids.length,
            }));
        }
        if (this.$el.hasClass('show')) {
            // note: this part of the rendering might be asynchronous
            this._renderDropdown();
        }
    }

});
