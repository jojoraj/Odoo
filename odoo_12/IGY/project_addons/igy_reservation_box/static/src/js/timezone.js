odoo.define('ingenosya_meeting.timezone_widget', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var basicFields = require('web.basic_fields');
    var FieldChar = basicFields.FieldChar;
    var ResultFieldChar = FieldChar.extend({
        start: function () {
            this._super.apply(this, arguments);
            this.$el.val(Intl.DateTimeFormat().resolvedOptions().timeZone);
            this.$el.prop('readonly', true);
        },
        commitChanges: function () {
            var self = this;
            this._setValue(Intl.DateTimeFormat().resolvedOptions().timeZone);
        },
        _setValue: function (value, options) {
            this._super.apply(this, arguments);
            var def = $.Deferred();
            var changes = {};
            value = Intl.DateTimeFormat().resolvedOptions().timeZone;
            changes[this.name] = value;
            this.trigger_up('field_changed', {
                dataPointID: this.dataPointID,
                changes: changes,
                viewType: this.viewType,
                doNotSetDirty: options && options.doNotSetDirty,
                notifyChange: !options || options.notifyChange !== false,
                allowWarning: options && options.allowWarning,
                onSuccess: def.resolve.bind(def),
                onFailure: def.reject.bind(def),
            });
        },
    });
    registry.add('timezone_widget', ResultFieldChar);
    return {
        ResultFieldChar: ResultFieldChar,
    };
});


