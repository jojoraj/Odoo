odoo.define('entrivis_kanban_many2many_tags.kanban_field_registry', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var registry = require('web.field_registry');
var _field_registry = require('web._field_registry');

delete registry.get('kanban.many2many_tags');
registry.add('kanban.many2many_tags', relational_fields.FieldMany2ManyTags);

});
