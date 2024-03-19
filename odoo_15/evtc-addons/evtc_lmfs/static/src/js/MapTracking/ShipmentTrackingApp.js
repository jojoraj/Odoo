odoo.define("evtc_lmfs.ShipmentTrackingApp", function (require) {
    "use strict";

    const { ShipmentTrackingOptionsModal, OptionsModal } = require('evtc_lmfs.options');

    const BACKEND_HOST = "https://lastmile-preprod-api-bp3cgjjccq-ew.a.run.app";
    const PROJECT_ID = "esanandro-env-preprod-lastmile";

    const tracking = window.location.search.split("=");

    /**
     * Sets the tracking id input field and button to disabled or enabled
     *
     * @param {boolean} disabled Whether or not to disable the inputs
     */
    function setInputsDisabled(disabled) {
        if (disabled) {
            console.log("Input disable");
            // document.getElementById('tracking-id-input').setAttribute('disabled', true);
            // document.getElementById('tracking-button').setAttribute('disabled', true);
        } else {
            console.log("Input enable");
            // document.getElementById('tracking-id-input').removeAttribute('disabled');
            // document.getElementById('tracking-button').removeAttribute('disabled');
        }
    }



    /**
     * Shows or hides the DOM element with the given id
     *
     * @param {string} id
     * @param {boolean} show
     */
    function showHideElementById(id, show) {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = show ? 'block' : 'none';
        }
    }


    /**
     * Formats a Date object for display.
     * @param {!Date} date
     * @return {string} The formatted time string.
     */
    function getTimeString(date) {
        let hours = date.getHours();
        const ampm = hours >= 12 ? 'pm' : 'am';
        hours = (hours === 0 ? 12 : (hours > 12 ? hours - 12 : hours));
        let minutes = date.getMinutes();
        if (minutes < 10) {
            minutes = '0' + minutes;
        }
        return `${hours}:${minutes} ${ampm}`;
    }

    class ShipmentTrackingApp {
        /**
         * @param {!ShipmentTrackingOptionsModal} optionsModal
         */
        constructor(optionsModal) {
            this.isLoadingResults_ = false;

            this.trackingId_ = optionsModal.options.trackingId;
            this.optionsModal = optionsModal;
        }

        /**
         * Creates the singleton app instance
         *
         * @param {?ShipmentTrackingOptionsModal} optionsModal
         * @return {!ShipmentTrackingApp}
         */
        static createInstance(optionsModal) {
            this.instance = new ShipmentTrackingApp(optionsModal || {});
            return this.instance;
        }

        /**
         * Returns or creates the singleton app instance
         * @return {!ShipmentTrackingApp}
         */
        static getInstance() {
            if (!this.instance) {
                return ShipmentTrackingApp.createInstance();
            }

            return this.instance;
        }

        /**
         * Returns the tracking ID
         * @return {string} Tracking ID
         */
        get trackingId() {
            return this.trackingId_;
        }

        /**
         * Sets the tracking ID
         */
        set trackingId(newTrackingId) {
            if (this.trackingId_ === newTrackingId || !this.locationProvider) {
                return;
            }
            this.resetShipmentDetailsDisplay();
            this.isLoadingResults = !!newTrackingId;

            this.trackingId_ = newTrackingId;
            this.locationProvider.trackingId = newTrackingId;
        }

        /**
         * Disables inputs and shows a loading message depending on the value of
         * `newIsLoadingResults`
         */
        set isLoadingResults(newIsLoadingResults) {
            if (this.isLoadingResults_ === newIsLoadingResults) {
                return;
            }

            this.isLoadingResults_ = newIsLoadingResults;
            setInputsDisabled(newIsLoadingResults);
            showHideElementById('loading', newIsLoadingResults);
        }

        /**
         * Creates a FleetEngineLocationProvider and JourneySharingMapView. Also
         * sets LocationProvider event listeners.
         */
        start() {
            this.locationProvider = new google.maps.journeySharing.FleetEngineShipmentLocationProvider({
                    projectId: PROJECT_ID,
                    authTokenFetcher: this.authTokenFetcher,
                    trackingId: this.trackingId_,
                    pollingIntervalMillis: this.optionsModal.options.pollingIntervalMillis,
                });

            const mapViewOptions = {
                element: document.getElementById('map_canvas'),
                locationProvider: this.locationProvider,
                anticipatedRoutePolylineSetup:
                    { visible: this.optionsModal.options.showAnticipatedRoutePolyline },
                takenRoutePolylineSetup:
                    { visible: this.optionsModal.options.showTakenRoutePolyline },
            };

            if (this.optionsModal.options.vehicleIcon !== 'defaultVehicleIcon') {
                mapViewOptions.vehicleMarkerSetup = this.optionsModal.getMarkerSetup(
                    this.optionsModal.options.vehicleIcon);
            }

            if (this.optionsModal.options.destinationIcon !==
                'defaultDestinationIcon') {
                mapViewOptions.destinationMarkerSetup = this.optionsModal.getMarkerSetup(
                    this.optionsModal.options.destinationIcon);
            }

            this.mapView = new google.maps.journeySharing.JourneySharingMapView(mapViewOptions);

            this.mapView.map.setOptions({
                center: {
                    lat: -18.870728212062595,
                    lng: 47.5099079530499 },
                zoom: 13
            });

            google.maps.event.addListenerOnce(this.mapView.map, 'tilesloaded', () => {
                setInputsDisabled(false);
            });
            
            setTimeout(function() {
                const evtcMaps = document.getElementById('evtc_maps');
                
                // Vérifiez si l'élément existe
                if (evtcMaps) {
                    const parentElement = evtcMaps.parentElement;
                    
                    // Déplacez evtc_maps devant son parent (en tant que premier enfant direct)
                    parentElement.insertBefore(evtcMaps, parentElement.firstElementChild);
                }
            }, 3000); // 5000 millisecondes (5 secondes)
            let updateCount = 0
            this.locationProvider.addListener('update', e => {
                const task = e.task;
                this.isLoadingResults = false;
                if (e.taskTrackingInfo && e.taskTrackingInfo.estimatedArrivalTime != null) {
                    document.getElementById("estimated").innerHTML = "Heure d'arrivée estimée : " + e.taskTrackingInfo.estimatedArrivalTime;
                    e.taskTrackingInfo.plannedLocation
                    updateCount ++
                    if (updateCount === 1) {
                        this.mapView.map.setZoom(13)
                    }
                }
                else {
                    document.getElementById("estimated").innerHTML = "";
                }
                if (!task) {
                    if(document.getElementById('map_canvas').style.position == 'relative'){
                            location.reload()
                
                    }
                    return;
                }

                if (!task.hasOwnProperty('status')) {
                    document.getElementById('tracking-id-error').textContent =
                        `No shipment found for tracking id '${this.trackingId_}'`;
                    showHideElementById('tracking-id-error', true);
                    return;
                }

                document.getElementById('details-container').style.display = 'block';

                // Tracking ID
                document.getElementById('tracking-id-value').textContent =
                    this.trackingId_;

                // Task type
                document.getElementById('task-type-value').textContent = task.type;

                // Task status
                document.getElementById('task-status-value').textContent = task.status;

                // Task outcome
                document.getElementById('task-outcome-value').textContent = task.outcome;

                // # stops remaining
                const showStopsRemaining = !!task.remainingVehicleJourneySegments;
                const remainingVehicleJourneySegments =
                    task.remainingVehicleJourneySegments || [];
                const stopsRemaining =
                    showStopsRemaining ? remainingVehicleJourneySegments.length : -1;
                if (showStopsRemaining) {
                    document.getElementById('stops-remaining-value').textContent =
                        stopsRemaining;
                    if (stopsRemaining >= 2) {
                        document.getElementById('stops-count').innerText =
                            `${stopsRemaining} stops away`;
                    } else if (stopsRemaining === 1) {
                        document.getElementById('stops-remaining-value').textContent = '';
                        if (task.outcome === 'SUCCEEDED') {
                            document.getElementById('stops-count').innerText = 'Completed';
                        } else if (task.outcome === 'FAILED') {
                            document.getElementById('stops-count').innerText = 'Attempted';
                        } else {
                            document.getElementById('stops-count').innerText = `You are the next stop`;
                        }
                    }
                } else {
                    document.getElementById('stops-remaining-value').textContent = '';
                    if (task.status === 'CLOSED') {
                        document.getElementById('stops-remaining-value').textContent = '';
                        if (task.outcome === 'SUCCEEDED') {
                            document.getElementById('stops-count').innerText = 'Completed';
                        } else {
                            document.getElementById('stops-count').innerText = 'Attempted';
                        }
                    } else {
                        document.getElementById('stops-count').innerText = '';
                    }
                }

                // ETA
                document.getElementById('eta-value').textContent =
                    task.estimatedCompletionTime;

                // Fetch data from manifest
                const taskId = task.name.split('/').pop();
                fetch(`${BACKEND_HOST}/task/${taskId}?manifestDataRequested=true`)
                    .then((response) => response.json())
                    .then((d) => {
                        if (d == null || d['status'] === 404) {
                            document.getElementById('eta-time').innerText = 'n/a';
                            document.getElementById('address').innerText = 'n/a';
                            return;
                        }
                        if (d['planned_completion_time'] != '') {
                            const completionTime = new Date(d['planned_completion_time']);
                            let timeString = getTimeString(completionTime);
                            if (d['planned_completion_time_range_seconds'] > 0) {
                                timeString = timeString + ' - ' +
                                    getTimeString(new Date(
                                        completionTime.getTime() +
                                        d['planned_completion_time_range_seconds'] * 1000));
                            }
                            document.getElementById('eta-time').innerText = timeString;
                        } else {
                            document.getElementById('eta-time').innerText = 'n/a';
                        }
                        if (d['planned_waypoint']['description'] != null) {
                            document.getElementById('address').innerText =
                                d['planned_waypoint']['description'];
                        } else {
                            document.getElementById('address').innerText = 'n/a';
                        }
                    });
            });

            this.locationProvider.addListener('error', e => {
                const error = e.error;

                this.isLoadingResults = false;

                document.getElementById('tracking-id-error').textContent =
                    `Error: ${error.message}`;
                showHideElementById('tracking-id-error', true);
            });
        }

        /**
         * Resets DOM elements and restarts the shipment tracking demo app.
         */
        restart() {
            setInputsDisabled(true);
            this.resetErrorDisplay();
            this.resetShipmentDetailsDisplay();
            this.start();
        }

        /**
         * Resets the DOM elements that display shipment details.
         */
        resetShipmentDetailsDisplay() {
            this.resetErrorDisplay();

            // document.getElementById('tracking-id-value').textContent = '';
            // document.getElementById('task-type-value').textContent = '';
            // document.getElementById('task-status-value').textContent = '';
            // document.getElementById('task-outcome-value').textContent = '';
            // document.getElementById('stops-remaining-value').textContent = '';
            // document.getElementById('eta-value').textContent = '';
        }

        /**
         * Resets the error message display
         */
        resetErrorDisplay() {
            document.getElementById('tracking-id-error').textContent = '';
            showHideElementById('tracking-id-error', false);
        }

        /**
         * Fetcher to get auth tokens from backend.
         */
        async authTokenFetcher(options) {
            const url =
                `${BACKEND_HOST}/token/delivery_consumer/${options.context.trackingId}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            const data = await response.json();
            const expiresInSeconds =
                Math.floor((data.expiration_timestamp_ms - Date.now()) / 1000);
            if (expiresInSeconds < 0) {
                throw new Error('Auth token already expired');
            }
            return {
                token: data.token,
                expiresInSeconds: data.expiration_timestamp_ms - Date.now(),
            };
        }
    }

    return {
        ShipmentTrackingApp
    }
});
