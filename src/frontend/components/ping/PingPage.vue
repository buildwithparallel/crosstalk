<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="flex flex-col h-full space-y-3 p-3 overflow-y-auto">

            <!-- page header -->
            <div class="flex items-center gap-2">
                <RouterLink :to="{ name: 'tools' }" class="flex rounded-md p-1.5 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.08)] hover:text-[var(--ct-text)]" title="Back to Diagnostics">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                        <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
                    </svg>
                </RouterLink>
                <div>
                    <div class="text-lg font-bold text-[var(--ct-text)]">Ping</div>
                    <div class="text-sm text-[var(--ct-dim)]">Check if a peer is reachable. Only LXMF delivery destinations can be pinged.</div>
                </div>
            </div>

            <!-- inputs -->
            <div class="ct-card">
                <div class="divide-y divide-[var(--ct-border)]">

                    <div class="p-2.5">
                        <div class="mb-1 text-sm font-medium text-[var(--ct-text)]">Destination Hash</div>
                        <input v-model="destinationHash" type="text" placeholder="e.g: 7b746057a7294469799cd8d7d429676a" class="ct-hash block w-full rounded-lg border p-2.5">
                    </div>

                    <div class="p-2.5">
                        <div class="mb-1 text-sm font-medium text-[var(--ct-text)]">Ping Timeout (seconds)</div>
                        <input v-model="timeout" type="number" placeholder="Timeout" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <div class="flex flex-wrap gap-2 p-2.5">
                        <button v-if="!isRunning" @click="start" type="button" class="ct-brand-button inline-flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                            Start
                        </button>
                        <button v-if="isRunning" @click="stop" type="button" class="ct-secondary-button inline-flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                            Stop
                        </button>
                        <button @click="clear" type="button" class="ct-secondary-button inline-flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                            Clear Results
                        </button>
                        <button @click="dropPath" type="button" class="ct-danger-button ml-auto inline-flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                            Drop Path
                        </button>
                    </div>

                </div>
            </div>

            <!-- results -->
            <div class="ct-card flex flex-col h-full overflow-hidden min-h-52">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Results</div>
                <div id="results" class="flex h-full flex-col overflow-y-auto overflow-x-auto whitespace-nowrap bg-[rgba(0,0,0,0.45)] p-2.5 font-mono text-sm text-[var(--ct-muted)]">
                    <div v-if="pingResults.length === 0" class="text-[var(--ct-dim)]">Ping results will appear here.</div>
                    <div v-for="pingResult of pingResults" class="w-fit">{{ pingResult }}</div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import {CanceledError} from "axios";
import DialogUtils from "../../js/DialogUtils";

export default {
    name: 'PingPage',
    data() {
        return {
            isRunning: false,
            destinationHash: null,
            timeout: 10,
            seq: 0,
            pingResults: [],
            abortController: null,
        };
    },
    beforeUnmount() {
        this.stop();
    },
    methods: {
        async start() {

            // do nothing if already running
            if(this.isRunning){
                return;
            }

            // simple check to ensure destination hash is valid
            if(this.destinationHash == null || this.destinationHash.length !== 32){
                DialogUtils.toast("Enter a valid 32 character destination hash", "error");
                return;
            }

            // simple check to ensure destination hash is valid
            if(this.timeout == null || this.timeout < 0){
                DialogUtils.toast("Timeout must be a positive number", "error");
                return;
            }

            // we are now running ping
            this.seq = 0;
            this.isRunning = true;
            this.abortController = new AbortController();

            // run ping until stopped
            while(this.isRunning){

                // run ping
                await this.ping();

                // wait a bit before running next ping
                await this.sleep(1000);

            }

        },
        async stop() {
            this.isRunning = false;
            this.abortController.abort();
        },
        async clear() {
            this.pingResults = [];
        },
        async sleep(millis) {
            return new Promise((resolve, reject) => setTimeout(resolve, millis));
        },
        async ping() {
            try {

                this.seq++;

                // ping destination
                const response = await window.axios.get(`/api/v1/ping/${this.destinationHash}/lxmf.delivery`, {
                    signal: this.abortController.signal,
                    params: {
                        timeout: this.timeout,
                    },
                });

                const pingResult = response.data.ping_result;
                const rttMilliseconds = (pingResult.rtt * 1000).toFixed(3);
                const rttDurationString = `${rttMilliseconds}ms`;

                const info = [
                    `seq=${this.seq}`,
                    `duration=${rttDurationString}`,
                    `hops_there=${pingResult.hops_there}`,
                    `hops_back=${pingResult.hops_back}`,
                ];

                // add rssi if available
                if(pingResult.rssi != null){
                    info.push(`rssi=${pingResult.rssi}dBm`);
                }

                // add snr if available
                if(pingResult.snr != null){
                    info.push(`snr=${pingResult.snr}dB`);
                }

                // add signal quality if available
                if(pingResult.quality != null){
                    info.push(`quality=${pingResult.quality}%`);
                }

                // add receiving interface
                info.push(`via=${pingResult.receiving_interface}`);

                // update ui
                this.addPingResult(info.join(" "));

            } catch(e) {

                // ignore cancelled error
                if(e instanceof CanceledError){
                    return;
                }

                console.log(e);

                // add ping error to results
                const message = e.response?.data?.message ?? e;
                this.addPingResult(`seq=${this.seq} error=${message}`);

            }
        },
        async dropPath() {

            // simple check to ensure destination hash is valid
            if(this.destinationHash == null || this.destinationHash.length !== 32){
                DialogUtils.toast("Enter a valid 32 character destination hash", "error");
                return;
            }

            try {
                const response = await window.axios.post(`/api/v1/destination/${this.destinationHash}/drop-path`);
                DialogUtils.toast(response.data.message, "success");
            } catch(e) {
                console.log(e);
                const message = e.response?.data?.message ?? `Failed to drop path: ${e}`;
                DialogUtils.toast(message, "error");
            }

        },
        addPingResult(result) {
            this.pingResults.push(result);
            this.scrollPingResultsToBottom();
        },
        scrollPingResultsToBottom: function() {
            // next tick waits for the ui to have the new elements added
            this.$nextTick(() => {
                // set timeout with zero millis seems to fix issue where it doesn't scroll all the way to the bottom...
                setTimeout(() => {
                    const container = document.getElementById("results");
                    if(container){
                        container.scrollTop = container.scrollHeight;
                    }
                }, 0);
            });
        },
    },
}
</script>
