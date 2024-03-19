odoo.define('website_esavtc_front.website_event_many2many_tags', function (require) {
    'use strict';

    // Noinspection JSAnnotator
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    let searchtimer;


    publicWidget.registry.websiteMany2manyTags = publicWidget.Widget.extend({
        selector: '.o_wevent_many2many_tags',
        events: {
            'input #oe_wevent_many': 'reload_tiping',
            "click .oe_partner_select": '_onClickInput',
            "click #new_save_": 'save_adress',
            'click .oe_add_partner': 'permute_value',
            'change #oe_country_selected': '_OnchangeItem',
        },
        _partner: async function () {
            let partner_name = {};
            await ajax.jsonRpc(
                '/web/partners',
                'call',
                {}
            ).then((res) => {
                partner_name = res;
            })
            this.options = partner_name;
        },
        start: async function () {
            await this._partner()
            this.create_views = this.options[0]
            this.partner_ids = this.options[1]
        },
        reload_tiping: function (e) {
            clearTimeout(searchtimer);
            searchtimer = setTimeout(() => {
                var mySearchInput = e.target.value;
                if (mySearchInput.length > 3) {
                    this._onInputAutosuggestion();
                } else {
                    this.removeInputSuggestion()
                }
            }, 500);
        },

        removeInputSuggestion: function () {
            $(this.templateInputSearchResult()).empty()
        },

        noSearchFound: function (searchWord) {
            return `<li class="list-group-item" style="text-align: center;"> <p>
                Aucun résultat trouvé pour `+ searchWord + `
            </p> </li>`
        },


        templateInputSearchResult: function () {
            let tmpl = $('.oe_partner_research_by_name')
            tmpl.removeAttr('style')
            return tmpl[0]
        },

        _onInputAutosuggestion: function () {
            const word = $('#oe_wevent_many').val()
            const resultFound = this.partner_ids.filter(res => res.nameLower.includes(word.toLowerCase()))
            this.removeInputSuggestion()
            if (resultFound.length == 0) {
                let templates = $(this.templateInputSearchResult());
                templates.append(this.noSearchFound(word));
                templates.append(this.create_views.create_views)
                return
            }
            this._render(resultFound)
        },
        _render: function (searchFound) {
            var templates = $(this.templateInputSearchResult())
            searchFound.length > 5 ? templates.attr('style', 'max-height: 250px; overflow-y: scroll;') : templates.removeAttr('style')
            searchFound.forEach(searching => { templates.append(searching.html_viewer) });
            templates.append(this.create_views.create_views)
        },
        _onRemove: function (e) {
            e.preventDefault();
            $('.oe_partner_research_by_name').empty();
        },
        _onClickInput: async function ($item) {
            const id = $item.currentTarget.attributes.partner_id.value;
            await ajax.jsonRpc('/web/partners/phone', 'call', { partner_id: id })
                .then((result) => {
                    $('#oe_wevent_many').val(result.name);
                    $('#oe_phone').val(result.phone);
                    $('#oe_data_id').val(result.id);
                    $('#res_id').val(result.id);
                    window.PartnerSelectedId = result.id;
                })
            $('.oe_partner_research_by_name').empty();
            this._onValidate();
        },
        save_adress: function () {
            const lodEnd = $('.loading');
            lodEnd.show();
            const errors = $('.oe_errors');
            errors.empty();
            const name = $('#newNameContact').val();
            const tel = $('#newPhoneContact').val();
            const country = $('#oe_country_selected').val();
            const email = $('#newEmail').val();
            if (!name || !tel) {
                const loadError = !name ? 'Le champ Nom est obligatoire' : 'Le champ téléphone est obligatoire';
                errors.append("<p> " + loadError + " </p>");
                errors.show();
                lodEnd.hide();
                return;
            }
            if (country !== 'MG') {
                if (!email) {
                    errors.append("<p> L' email est obligatoire </p>");
                    errors.show();
                    return;
                }
            }
            ajax.jsonRpc('/web/partners/new', 'call', { name: name, tel: tel, country_code: country, email: email })
                .then((res) => {
                    if (res.stat === 'success') {
                        $('#oe_wevent_many').val(res.details.name);
                        $('#oe_phone').val(res.details.phone);
                        $('#create_new_contact').hide();
                        $('.oe_partner_research_by_name').empty();
                        $('#oe_data_id').val(res.details.id);
                        window.PartnerSelectedId = res.details.id
                        this._onValidate();
                    } else {
                        const string = res.details.name;
                        errors.append("<p>" + string + "</p>");
                        errors.show();
                    }
                })
            lodEnd.hide();
        },
        permute_value: function () {
            const str = $('#oe_wevent_many').val();
            $('#newNameContact').val(str);
        },
        _onValidate: function () {
            const widget_name = $('#oe_wevent_many').val();
            const widget_phone = $('#oe_phone').val();
            const widget_id = $('#oe_data_id').val();
            $('#res_id').val(widget_id);
            $('#name').val(widget_name);
            $('#tel').val(widget_phone);
        },
        _OnchangeItem: function (e) {
            const value = e.currentTarget.value;
            const email_ = $('.oe_email_show');
            if (value !== 'MG') {
                email_.show();
            } else {
                email_.hide();
            }
            $('.oe_errors').empty();
        }
    });

    return publicWidget.registry.websiteMany2manyTags;

});
