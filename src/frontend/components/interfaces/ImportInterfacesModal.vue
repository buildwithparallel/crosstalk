<template>
    <div v-if="isShowing" class="fixed inset-0 z-40 flex items-center justify-center bg-[rgba(0,0,0,0.6)] backdrop-blur-sm transition-opacity">
        <div class="flex w-full h-full p-4 overflow-y-auto">
            <div v-click-outside="dismiss" class="ct-panel my-auto mx-auto w-full max-w-2xl rounded-xl border border-[var(--ct-border)]">

                <!-- title -->
                <div class="border-b border-[var(--ct-border)] p-4">
                    <h3 class="text-lg font-semibold text-[var(--ct-text)]">Import Interfaces</h3>
                </div>

                <!-- content -->
                <div class="divide-y divide-[var(--ct-border)]">

                    <!-- file input -->
                    <div class="p-3">
                        <div>
                            <input ref="import-interfaces-file-input" type="file" @change="onFileSelected" accept="*" class="w-full text-sm text-[var(--ct-dim)]">
                        </div>
                        <div v-if="!selectedFile" class="mt-2 text-sm text-[var(--ct-dim)]">
                            <ul class="list-disc list-inside">
                                <li>You can import interfaces from a ~/.reticulum/config file.</li>
                                <li>You can import interfaces from an exported interfaces file.</li>
                            </ul>
                        </div>
                    </div>

                    <!-- select interfaces -->
                    <div v-if="importableInterfaces.length > 0" class="divide-y divide-[var(--ct-border)]">
                        <div class="flex p-3">
                            <div class="my-auto mr-auto text-sm font-medium text-[var(--ct-text)]">Select Interfaces to Import</div>
                            <div class="my-auto space-x-2">
                                <button @click="selectAllInterfaces" class="text-sm text-[#7db0ff] hover:underline">Select All</button>
                                <button @click="deselectAllInterfaces" class="text-sm text-[#7db0ff] hover:underline">Deselect All</button>
                            </div>
                        </div>
                        <div class="max-h-80 space-y-2 overflow-y-auto bg-[rgba(0,0,0,0.3)] p-2">
                            <div @click="toggleSelectedInterface(iface.name)" v-for="iface in importableInterfaces" :key="iface.name" class="ct-card ct-card-hover flex cursor-pointer items-center p-2.5">
                                <div class="mr-auto text-sm">
                                    <div class="font-semibold text-[var(--ct-text)]">{{ iface.name }}</div>
                                    <div class="text-sm text-[var(--ct-dim)]">

                                        <!-- auto interface -->
                                        <div v-if="iface.type === 'AutoInterface'">
                                            <div>{{ iface.type }}</div>
                                            <div>Ethernet and WiFi</div>
                                        </div>

                                        <!-- tcp client interface -->
                                        <div v-else-if="iface.type === 'TCPClientInterface'">
                                            <div>{{ iface.type }}</div>
                                            <div>{{ iface.target_host }}:{{ iface.target_port }}</div>
                                        </div>

                                        <!-- tcp server interface -->
                                        <div v-else-if="iface.type === 'TCPServerInterface'">
                                            <div>{{ iface.type }}</div>
                                            <div>{{ iface.listen_ip }}:{{ iface.listen_port }}</div>
                                        </div>

                                        <!-- udp interface -->
                                        <div v-else-if="iface.type === 'UDPInterface'">
                                            <div>{{ iface.type }}</div>
                                            <div>Listen: {{ iface.listen_ip }}:{{ iface.listen_port }}</div>
                                            <div>Forward: {{ iface.forward_ip }}:{{ iface.forward_port }}</div>
                                        </div>

                                        <!-- rnode interface details -->
                                        <div v-else-if="iface.type === 'RNodeInterface'">
                                            <div>{{ iface.type }}</div>
                                            <div>Port: {{ iface.port }}</div>
                                            <div>Frequency: {{ formatFrequency(iface.frequency) }}</div>
                                            <div>Bandwidth: {{ formatFrequency(iface.bandwidth) }}</div>
                                            <div>Spreading Factor: {{ iface.spreadingfactor }}</div>
                                            <div>Coding Rate: {{ iface.codingrate }}</div>
                                            <div>Transmit Power: {{ iface.txpower }}dBm</div>
                                        </div>

                                        <!-- other interface types -->
                                        <div v-else>{{ iface.type }}</div>

                                    </div>
                                </div>
                                <input @click.stop type="checkbox" v-model="selectedInterfaces" :value="iface.name" class="mx-2 size-4 rounded border text-blue-600">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- actions -->
                <div class="flex justify-end space-x-2 border-t border-[var(--ct-border)] p-4">
                    <button @click="dismiss" class="ct-secondary-button rounded-lg px-4 py-2 text-sm font-semibold">
                        Cancel
                    </button>
                    <button @click="importSelectedInterfaces" class="ct-brand-button rounded-lg px-4 py-2 text-sm font-semibold">
                        Import Selected
                    </button>
                </div>

            </div>
        </div>
    </div>
</template>

<script>
import DialogUtils from "../../js/DialogUtils";
import Utils from "../../js/Utils";
import ElectronUtils from "../../js/ElectronUtils";

export default {
    name: "ImportInterfacesModal",
    emits: [
        "dismissed",
    ],
    data() {
        return {
            isShowing: false,
            selectedFile: null,
            importableInterfaces: [],
            selectedInterfaces: [],
        };
    },
    methods: {
        show() {
            this.isShowing = true;
            this.selectedFile = null;
            this.importableInterfaces = [];
            this.selectedInterfaces = [];
        },
        dismiss() {
            this.isShowing = false;
            this.$emit("dismissed");
        },
        clearSelectedFile() {
            this.selectedFile = null;
            this.$refs["import-interfaces-file-input"].value = null;
        },
        async onFileSelected(event) {

            // get selected file
            const file = event.target.files[0];
            if(!file){
                return;
            }

            // update ui
            this.selectedFile = file;
            this.importableInterfaces = [];
            this.selectedInterfaces = [];

            try {

                // fetch preview of interfaces to import
                const response = await window.axios.post('/api/v1/reticulum/interfaces/import-preview', {
                    config: await file.text(),
                });

                // ensure there are some interfaces available to import
                if(!response.data.interfaces || response.data.interfaces.length === 0){
                    this.clearSelectedFile();
                    DialogUtils.toast("No interfaces were found in the selected configuration file", "error");
                    return;
                }

                // update ui
                this.importableInterfaces = response.data.interfaces;

                // auto select all interfaces
                this.selectAllInterfaces();

            } catch(e) {
                this.clearSelectedFile();
                DialogUtils.toast("Failed to parse configuration file", "error");
                console.error(e);
            }
        },
        isInterfaceSelected(name) {
            return this.selectedInterfaces.includes(name);
        },
        selectInterface(name) {
            if(!this.isInterfaceSelected(name)){
                this.selectedInterfaces.push(name);
            }
        },
        deselectInterface(name) {
            this.selectedInterfaces = this.selectedInterfaces.filter((selectedInterfaceName) => {
                return selectedInterfaceName !== name;
            });
        },
        toggleSelectedInterface(name) {
            if(this.isInterfaceSelected(name)){
                this.deselectInterface(name);
            } else {
                this.selectInterface(name);
            }
        },
        selectAllInterfaces() {
            this.selectedInterfaces = this.importableInterfaces.map(i => i.name);
        },
        deselectAllInterfaces() {
            this.selectedInterfaces = [];
        },
        async importSelectedInterfaces() {

            // ensure user selected a file to import from
            if(!this.selectedFile){
                DialogUtils.toast("Select a configuration file first", "error");
                return;
            }

            // ensure user selected some interfaces
            if(this.selectedInterfaces.length === 0){
                DialogUtils.toast("Select at least one interface to import", "error");
                return;
            }

            try {

                // import interfaces
                await window.axios.post('/api/v1/reticulum/interfaces/import', {
                    config: await this.selectedFile.text(),
                    selected_interface_names: this.selectedInterfaces,
                });

                // dismiss modal
                this.dismiss();

                await ElectronUtils.restartBackend("#/interfaces");
                return;

            } catch(e) {
                const message = e.response?.data?.message || "Failed to import interfaces";
                DialogUtils.toast(message, "error");
                console.error(e);
            }
        },
        formatFrequency(hz) {
            return Utils.formatFrequency(hz);
        },
    },
}
</script>
