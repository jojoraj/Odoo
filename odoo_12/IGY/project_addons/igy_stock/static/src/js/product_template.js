odoo.define('igy_stock.product_template_js', function(require) {
   'use strict';
    var KanbanRecord = require('web.KanbanRecord');
    KanbanRecord.include({
        _openRecord: function(){
            if (this.modelName == 'product.template' && this.$('.o_kanban_footer a').length) {
                this.$('.o_kanban_footer a').first().click();
            }
            else {
                this._super.apply(this, arguments);
            }
        }
    })
})