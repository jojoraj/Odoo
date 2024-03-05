odoo.define('igy_document_inherit.document_inherit', function(require){
    "use strict";
    var KanbanController = require('documents.DocumentsKanbanController');
    var DocumentInspector = require('documents.DocumentsInspector');
    var DocumentViewer = require('mail.DocumentViewer');
    var session = require('web.session');


    var core = require('web.core');
    var qweb = core.qweb;
    var selected ;
    KanbanController.include({

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function(){
            this._super.apply(this, arguments);
            var self = this;
            var def = self.get_folder_id().then(function(folder_id){
                    if (folder_id.length > 0){
                         self.folder_id = folder_id[0].id;
                    }
                    else{
                        self.folder_id = null;
                    }

                })
        },
        get_folder_id: function(){
            return this._rpc({
                    model: 'documents.folder',
                    method: 'search_read',
                    domain: [['name', 'ilike', 'formation']],
                    fields: ['id'],
                    limit: 1
                })
        },
        renderButtons: function (){
            this._super.apply(this, arguments);
            var self = this;
            session.user_has_group('documents.group_documents_manager').then(function(has_group){
                if (!has_group) {
                    var buttons_url = self.$buttons.find('button.o_documents_kanban_url').hide();
                    var buttons_url = self.$buttons.find('button.o_documents_kanban_upload').hide();
                    var buttons_url = self.$buttons.find('button.o_documents_kanban_request').hide();
                }
            });
        },
        _renderFolders: function (folders) {
            var self = this;
            var $folders = $('<ul>', {class: 'list-group d-block'});
            _.each(folders, function (folder) {
                var $folder = $(qweb.render('documents.DocumentsSelectorFolder', {
                    activeFolderID: self.selectedFolderID,
                    folder: folder,
                }));
                if (self.selectedFolderID == self.folder_id){
                    selected = true;
                }else{
                    selected = false;
                }

                if (folder.children.length) {
                    var $children =  self._renderFolders(folder.children);
                    $children.appendTo($folder);
                }
                $folder.appendTo($folders);
            });
            return $folders;
        },
    });

    DocumentInspector.include({
        _renderField: function(fieldName, options){
            this._super.apply(this, arguments);
            var self = this;
            session.user_has_group('documents.group_documents_manager').then(function(has_group){
                if (!has_group){
                    self.$el.find('.o_inspector_fields').hide();
                    self.$el.find('.o_inspector_replace').hide();
                    self.$el.find('.o_inspector_lock').hide();
                    self.$el.find('.o_inspector_archive').hide();
                    self.$el.find('.o_inspector_section_rules').hide();
                    if (selected===true){
                          self.$el.find('.o_inspector_download').hide();
                    }  
                    
                }
            });
        }
    }) ;

    DocumentViewer.include({
        start: function () {
              var self = this;
            this._super.apply(this, arguments);
            session.user_has_group('documents.group_documents_manager').then(function(has_group){
                if (!has_group && selected == true){
                     self.$el.find('.o_download_btn').hide();
                     self.$el.find('.o_viewer_img').addClass('not-downloadable')
                }
            })
        }
    })
});