odoo.define("news_letter.basic_field",function(require){
"use strict";
    var basicFields = require('web.basic_fields');

    basicFields.FieldBinaryFile.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            this.max_upload_size = 2500000000 * 1024 * 1024;
        },
    });

    basicFields.FieldBinaryImage.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            this.max_upload_size = 2500000000 * 1024 * 1024;
        },
    });

})
