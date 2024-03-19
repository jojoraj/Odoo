odoo.define('evtc_publicity.media_video_play', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.ideaBox = publicWidget.Widget.extend({
        selector: '#section_idea_box',
        events: {
            'click #send_mail': '_sendMail',
            'click #close-modal': '_closeModal',
        },

        _closeModal: function () {
            $('#error-send-mail')[0].setAttribute("class", "alert alert-danger")
            $('#error-send-mail')[0].innerHTML = '';
            if ($('#error-send-mail')[0].getAttribute('value') === "1") {
                $('#error-send-mail')[0].removeAttribute("value");
                window.location.reload();
            } else {
                $('#error-send-mail')[0].removeAttribute("value");
            }

        },

        _sendMail: function () {
            var self = this;
            var mailFormat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
            var mailText = $('#email_from')[0];
            var ideas = $('#label2')[0];
            if (mailText.value.match(mailFormat)) {
                mailText.focus();
                self._rpc({
                    route: '/send/mail',
                    params: {
                        'mail': mailText.value,
                        'ideas': ideas.value,
                    },
                }).then((data) => {
                    if (data['data']) {
                        $('#error-send-mail').addClass('alert-success').removeClass('alert-danger')
                        $('#error-send-mail')[0].innerHTML += "Votre mail a été envoyé";
                        $('#error-send-mail')[0].setAttribute("value", 1)
                        $('#modal_idea').modal({
                            keyboard: false,
                            backdrop: 'static'
                        })
                        mailText.value = '';
                        ideas.value = '';
                    } else {
                        $('#error-send-mail')[0].innerHTML += 'Un problème est survenu ou votre texte était vide, veuillez renvoyer le mail';
                        $('#error-send-mail')[0].setAttribute("value", 0)
                        $('#modal_idea').modal({
                            keyboard: false,
                            backdrop: 'static'
                        })
                    };
                });
            } else {
                $('#error-send-mail')[0].innerHTML += 'Vous avez saisi une adresse électronique non valide ou vide !';
                $('#error-send-mail')[0].setAttribute("value", 0)
                $('#modal_idea').modal({
                    keyboard: false,
                    backdrop: 'static'
                })
                mailText.focus();
            }
        },

    });
});
