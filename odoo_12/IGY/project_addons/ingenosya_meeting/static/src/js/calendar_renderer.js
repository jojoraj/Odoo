odoo.define('ingenosya_meeting.CalendarRenderer', function (require) {
"use strict";

var CalendarRenderer = require('web.CalendarRenderer');
//meeting.reservation
return CalendarRenderer.include({
    _render: function () {
        var res = this._super.apply(this, arguments);

        this.$calendar.find('.fc-resizer').removeClass('fc-resizer');
        return res;
    },
});

});
