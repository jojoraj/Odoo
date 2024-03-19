odoo.define('evtc_publicity.evtc_pub', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const userSession = require('web.session');
    const SnippetsMixin = publicWidget.Widget.extend({
        disabledInEditableMode: false,
        /**
         *
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.data = [];
        },
        /**
         *
         * @override
         */
        willStart: function () {
            return this._super.apply(this, arguments).then(
                () => Promise.all([
                    this._fetchData(),
                ])
            );
        },
        /**
         *
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments)
                .then(() => {
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
                    this._render();
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
                });
        },
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            /* Calling RPC to get datas from database */
            this.data = '';
        },
        /**
         *
         * @private
         */
        _render: function () {
            this.$el.html(this.data);
        },

        destroy: function () {
            this._super.apply(this, arguments);
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
            this.$el.html('');
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
        },

    });

    publicWidget.registry.MediaPub = SnippetsMixin.extend({
        selector: '.evtc_pub_media',
        start: async function () {
            let res = await this._super.apply(this, arguments)
            await this._load_video()
            new Promise((s, r) => setTimeout(() => {
                this.autoPlayVideo();
                s();
            }, 2000));
            return res
        },
        willStart: function () {
            let res = this._super.apply(this, arguments)
            let serviceWorker = navigator.serviceWorker
            if (serviceWorker) {
                serviceWorker.register('/evtc_publicity/static/src/js/app.js').then(function (res) {
                    console.log('Registration succeeded. Scope is ' + res.scope)
                }).catch(function (e) {
                    console.log('Registration failed with ' + e)
                });
            }
            return res
        },
        _load_video: async function () {
            let videos = [];
            Object.entries($(this.el).find('.video-source')).map(([k, v]) => (v))
                .filter(r => r.dataset).forEach(target => {
                    videos.push(target.dataset.src)
                })
            await this._playVideo(videos, { 'is_public': !userSession.user_id })
            $(".button_content").click(function () {
                $(".link_container").toggleClass("d-none");
                $(".text-pub").toggleClass("d-none");
                $(this).toggleClass("collapse-button");
            });
        },
        _log_apps: function (message) {
            console.log(message)
        },
        run_video: function (times) {
            times = times + 1.2
            new Promise((s, r) => setTimeout(() => {
                document.getElementById("play-video").play().then(() => {
                    console.log('Ok', times)
                    s()
                }).catch(() => {
                    console.log('not Ok', times)
                    return this.run_video()
                })
            }, times * 1000));
        },
        autoPlayVideo: function (timeLaps = 2) {
            const elementQueryVideo = $(this.el).find('video')[0];
            const vVolume = document.getElementById("vVolume");
            const video = document.getElementById("play-video");
            const vVolIco = document.getElementById("vVolIco");
            vVolume.value = '0'
            video.setAttribute('palyingAuto', 1)
            elementQueryVideo.muted = true;
            vVolIco.innerHTML = "volume_mute"
            this.run_video(2)
        },

        // render main template
        async _fetchData(e) {
            const res = await this._rpc({ route: '/render/view/publicity' });
            this.data = res;
        },

        _render: function () {
            this.$el.html(this.data);
        },

        _initialize_modal_values: function () {
            let opinions = '';
            $(this.el).find('#client-rate')[0].value = opinions;
            for (let i = 0; i < document.getElementsByName('rating').length; i++) {
                document.getElementsByName('rating')[i].checked == false
            }
        },
        _playVideo: function (result, user) {
            let playlist = result;
            // (A2) VIDEO PLAYER & GET HTML CONTROLS
            const video = document.getElementById("play-video");
            const vPlay = document.getElementById("vPlay");
            const vPlayIco = document.getElementById("vPlayIco");
            const vNow = document.getElementById("vNow");
            const vTime = document.getElementById("vTime");
            const vSeek = document.getElementById("vSeek");
            const vVolume = document.getElementById("vVolume");
            const vVolIco = document.getElementById("vVolIco");
            // (B) PLAY MECHANISM
            // (B1) FLAGS
            let vidNow = 0; // current video
            let vidStart = false; // auto start next video

            let vidPlay = function (idx, nostart) {
                vidNow = idx;
                vidStart = nostart ? false : true;

                const videoRequest = fetch(playlist[idx]).then((response) => {
                    if (!response.ok) {
                        console.error('Bad response status')
                    } else {
                        try {
                            response.blob().then(blob => {
                                video.src = window.URL.createObjectURL(blob)
                            })
                            caches.open('v1').then(function (cache) {
                                return cache.add(response.url);
                            }).catch(function (error) {
                                console.log('caching failed with ' + error);
                            });
                        } catch (error) {
                            console.error(error)
                        }
                    }
                });
            };

            // (B3) AUTO START WHEN SUFFICIENTLY BUFFERED
            video.addEventListener("canplay", () => {
                if (vidStart) {
                    video.play();
                    vidStart = false;
                }
            });

            // (B4) AUTOPLAY NEXT VIDEO IN THE PLAYLIST
            video.addEventListener("ended", () => {
                vidNow++;
                if (vidNow === Math.floor(playlist.length / 2) && user.is_public) {
                    this._initialize_modal_values();
                    $('#modal_rating').modal()
                }
                if (vidNow >= playlist.length) {
                    vidNow = 0;
                    if (user.is_public) {
                        this._initialize_modal_values();
                        $('#modal_rating').modal()
                    }
                }
                vidPlay(vidNow);
            });

            // (B5) INIT SET FIRST VIDEO
            vidPlay(0, true);

            // (C) PLAY/PAUSE BUTTON
            // (C1) AUTO SET PLAY/PAUSE TEXT
            video.addEventListener("play", () => {
                vPlayIco.innerHTML = "pause";
            });
            video.addEventListener("pause", () => {
                vPlayIco.innerHTML = "play_arrow";
            });

            // (C2) CLICK TO PLAY/PAUSE
            vPlay.addEventListener("click", () => {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            });

            // (D) TRACK PROGRESS
            // (D1) SUPPORT FUNCTION - FORMAT HH:MM:SS
            let timeString = (secs) => {
                // HOURS, MINUTES, SECONDS
                let ss = Math.floor(secs),
                    hh = Math.floor(ss / 3600),
                    mm = Math.floor((ss - (hh * 3600)) / 60);
                ss = ss - (hh * 3600) - (mm * 60);

                // RETURN FORMATTED TIME
                if (hh > 0) {
                    mm = mm < 10 ? "0" + mm : mm;
                }
                ss = ss < 10 ? "0" + ss : ss;
                return hh > 0 ? `${hh}:${mm}:${ss}` : `${mm}:${ss}`;
            };

            // (D2) INIT SET TRACK TIME
            video.addEventListener("loadedmetadata", () => {
                vNow.innerHTML = timeString(0);
                vTime.innerHTML = timeString(video.duration);
            });

            // (D3) UPDATE TIME ON PLAYING
            video.addEventListener("timeupdate", () => {
                vNow.innerHTML = timeString(video.currentTime);
            });

            // (E) SEEK BAR
            video.addEventListener("loadedmetadata", () => {
                // (E1) SET SEEK BAR MAX TIME
                vSeek.max = Math.floor(video.duration);

                // (E2) USER CHANGE SEEK BAR TIME
                let vSeeking = false; // USER IS NOW CHANGING TIME
                vSeek.addEventListener("input", () => {
                    vSeeking = true; // PREVENTS CLASH WITH (E3)
                });
                vSeek.addEventListener("change", () => {
                    video.currentTime = vSeek.value;
                    if (!video.paused) {
                        video.play();
                    }
                    vSeeking = false;
                });

                // (E3) UPDATE SEEK BAR ON PLAYING
                video.addEventListener("timeupdate", () => {
                    if (!vSeeking) {
                        vSeek.value = Math.floor(video.currentTime);
                    }
                });
            });

            // (F) VOLUME
            vVolume.addEventListener("change", () => {
                video.volume = vVolume.value;
                vVolIco.innerHTML = (vVolume.value === 0 ? "volume_mute" : "volume_up");
                if (!video.paused && video.getAttribute('palyingAuto') === '1') {
                    video.pause()
                    video.setAttribute('palyingAuto', 0);
                    $(this.el).find('video')[0].muted = false;
                    video.play()
                }
            });

            // (G) ENABLE/DISABLE CONTROLS
            video.addEventListener("canplay", () => {
                vPlay.disabled = false;
                vVolume.disabled = false;
                vSeek.disabled = false;
            });
            video.addEventListener("waiting", () => {
                vPlay.disabled = true;
                vVolume.disabled = true;
                vSeek.disabled = true;
            });

        },
    });
});
