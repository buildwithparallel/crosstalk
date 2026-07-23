<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto p-3 space-y-3">

            <!-- page header -->
            <div class="flex flex-wrap items-center gap-2">
                <div class="mr-auto">
                    <div class="text-lg font-bold text-[var(--ct-text)]">Connections</div>
                    <div class="text-sm text-[var(--ct-dim)]">Ways this device connects to the Reticulum network.</div>
                </div>

                <!-- Import button -->
                <button @click="showImportInterfacesModal" type="button" class="inline-flex items-center gap-x-1 rounded-lg ct-secondary-button px-2.5 py-1.5 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    <span>Import</span>
                </button>

                <!-- Export button -->
                <button @click="exportInterfaces" type="button" class="inline-flex items-center gap-x-1 rounded-lg ct-secondary-button px-2.5 py-1.5 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                    <span>Export</span>
                </button>

                <!-- Add Interface button -->
                <RouterLink :to="{ name: 'interfaces.add' }">
                    <button type="button" class="inline-flex items-center gap-x-1 rounded-lg ct-brand-button px-2.5 py-1.5 text-sm font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                        </svg>
                        <span>Add Connection</span>
                    </button>
                </RouterLink>

            </div>

            <!-- public internet nodes -->
            <div class="ct-elevated-surface rounded-lg overflow-hidden">
                <div class="grid grid-cols-1 gap-3 p-3 lg:grid-cols-[1fr_auto] lg:items-center">
                    <div class="min-w-0">
                        <div class="flex items-center gap-2">
                            <div class="flex size-10 shrink-0 items-center justify-center rounded-md border border-[rgba(110,168,255,0.34)] bg-[rgba(0,97,253,0.12)] text-[#7db0ff]">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0 0c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m-7.843 4.582A11.953 11.953 0 0 0 12 10.5c2.998 0 5.74-1.1 7.843-2.918M3.284 14.253A17.919 17.919 0 0 0 12 16.5c3.162 0 6.133-.815 8.716-2.247" />
                                </svg>
                            </div>
                            <div class="min-w-0">
                                <div class="font-bold text-[var(--ct-text)]">Need a public internet node?</div>
                                <div class="text-sm text-[var(--ct-muted)]">
                                    Find public Reticulum nodes on rmap.world, copy a node configuration, then add it here as a Public Backbone Node.
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="flex flex-wrap gap-2 lg:justify-end">
                        <a
                            href="https://rmap.world/"
                            target="_blank"
                            class="inline-flex items-center justify-center gap-x-1 rounded-md ct-secondary-button px-3 py-2 text-sm font-semibold">
                            <span>Open rmap.world</span>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                                <path fill-rule="evenodd" d="M4.25 5.5a.75.75 0 0 0-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 0 0 .75-.75v-4a.75.75 0 0 1 1.5 0v4A2.25 2.25 0 0 1 12.75 17h-8.5A2.25 2.25 0 0 1 2 14.75v-8.5A2.25 2.25 0 0 1 4.25 4h5a.75.75 0 0 1 0 1.5h-5Z" clip-rule="evenodd" />
                                <path fill-rule="evenodd" d="M6.194 12.753a.75.75 0 0 0 1.06.053L16.5 4.44v2.81a.75.75 0 0 0 1.5 0v-4.5A.75.75 0 0 0 17.25 2h-4.5a.75.75 0 0 0 0 1.5h2.553l-9.056 8.194a.75.75 0 0 0-.053 1.06Z" clip-rule="evenodd" />
                            </svg>
                        </a>
                        <RouterLink :to="{ name: 'interfaces.add', query: { interface_type: 'PublicBackboneInterface' } }">
                            <button type="button" class="inline-flex items-center justify-center gap-x-1 rounded-md ct-brand-button px-3 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                                Add Public Node
                            </button>
                        </RouterLink>
                    </div>
                </div>
            </div>

            <!-- enabled interfaces -->
            <Interface
                v-for="iface of enabledInterfaces"
                :iface="iface"
                @enable="enableInterface(iface._name)"
                @disable="disableInterface(iface._name)"
                @edit="editInterface(iface._name)"
                @export="exportInterface(iface._name)"
                @delete="deleteInterface(iface._name)"/>

            <!-- disabled interfaces -->
            <div v-if="disabledInterfaces.length > 0" class="ct-section-label pt-2">Turned Off</div>
            <Interface
                v-for="iface of disabledInterfaces"
                :iface="iface"
                @enable="enableInterface(iface._name)"
                @disable="disableInterface(iface._name)"
                @edit="editInterface(iface._name)"
                @export="exportInterface(iface._name)"
                @delete="deleteInterface(iface._name)"/>

        </div>
    </div>

    <!-- Import Dialog -->
    <ImportInterfacesModal ref="import-interfaces-modal" @dismissed="onImportInterfacesModalDismissed"/>

</template>

<script>
import DialogUtils from "../../js/DialogUtils";
import ElectronUtils from "../../js/ElectronUtils";
import Interface from "./Interface.vue";
import Utils from "../../js/Utils";
import ImportInterfacesModal from "./ImportInterfacesModal.vue";
import DownloadUtils from "../../js/DownloadUtils";

export default {
    name: 'InterfacesPage',
    components: {
        ImportInterfacesModal,
        Interface,
    },
    data() {
        return {
            interfaces: {},
            interfaceStats: {},
            reloadInterval: null,
        };
    },
    beforeUnmount() {
        clearInterval(this.reloadInterval);
    },
    mounted() {

        this.loadInterfaces();
        this.updateInterfaceStats();

        // update info every few seconds
        this.reloadInterval = setInterval(() => {
            this.updateInterfaceStats();
        }, 1000);

    },
    methods: {
        isInterfaceEnabled: function(iface) {
            return Utils.isInterfaceEnabled(iface);
        },
        async loadInterfaces() {
            try {
                const response = await window.axios.get(`/api/v1/reticulum/interfaces`);
                this.interfaces = response.data.interfaces;
            } catch(e) {
                // do nothing if failed to load interfaces
            }
        },
        async updateInterfaceStats() {
            try {

                // fetch interface stats
                const response = await window.axios.get(`/api/v1/interface-stats`);

                // update data
                const interfaces = response.data.interface_stats?.interfaces ?? [];
                for(const iface of interfaces){
                    this.interfaceStats[iface.short_name] = iface;
                }

            } catch(e) {
                // do nothing if failed to load interfaces
            }
        },
        async enableInterface(interfaceName) {

            // enable interface
            try {
                await window.axios.post(`/api/v1/reticulum/interfaces/enable`, {
                    name: interfaceName,
                });
                await this.applyInterfaceChanges();
            } catch(e) {
                DialogUtils.toast("Failed to enable interface", "error");
                console.log(e);
            }

            // reload interfaces
            await this.loadInterfaces();

        },
        async disableInterface(interfaceName) {

            // disable interface
            try {
                await window.axios.post(`/api/v1/reticulum/interfaces/disable`, {
                    name: interfaceName,
                });
                await this.applyInterfaceChanges();
            } catch(e) {
                DialogUtils.toast("Failed to disable interface", "error");
                console.log(e);
            }

            // reload interfaces
            await this.loadInterfaces();

        },
        async editInterface(interfaceName) {
            this.$router.push({
                name: "interfaces.edit",
                query: {
                    interface_name: interfaceName,
                },
            });
        },
        async deleteInterface(interfaceName) {

            // ask user to confirm deleting conversation history
            if(!await DialogUtils.confirm("Are you sure you want to delete this interface? This can not be undone!", { title: "Delete Interface", danger: true, confirmLabel: "Delete" })){
                return;
            }

            // delete interface
            try {
                await window.axios.post(`/api/v1/reticulum/interfaces/delete`, {
                    name: interfaceName,
                });
                await this.applyInterfaceChanges();
            } catch(e) {
                DialogUtils.toast("Failed to delete interface", "error");
                console.log(e);
            }

            // reload interfaces
            await this.loadInterfaces();

        },
        async exportInterfaces() {
            try {

                // fetch exported interfaces
                const response = await window.axios.post('/api/v1/reticulum/interfaces/export');

                // download file to browser
                DownloadUtils.downloadFile("crosstalk_interfaces.txt", new Blob([response.data]));

            } catch(e) {
                DialogUtils.toast("Failed to export interfaces", "error");
                console.error(e);
            }
        },
        async exportInterface(interfaceName) {
            try {

                // fetch exported interfaces
                const response = await window.axios.post('/api/v1/reticulum/interfaces/export', {
                    selected_interface_names: [
                        interfaceName,
                    ],
                });

                // download file to browser
                DownloadUtils.downloadFile(`${interfaceName}.txt`, new Blob([response.data]));

            } catch(e) {
                DialogUtils.toast("Failed to export interface", "error");
                console.error(e);
            }
        },
        showImportInterfacesModal() {
            this.$refs["import-interfaces-modal"].show();
        },
        onImportInterfacesModalDismissed() {
            // reload interfaces as something may have been imported
            this.loadInterfaces();
        },
        async applyInterfaceChanges() {
            await ElectronUtils.restartBackend("#/interfaces");
        },
    },
    computed: {
        interfacesWithStats() {
            const results = [];
            for(const [interfaceName, iface] of Object.entries(this.interfaces)){
                iface._name = interfaceName;
                iface._stats = this.interfaceStats[interfaceName];
                results.push(iface);
            }
            return results;
        },
        enabledInterfaces() {
            return this.interfacesWithStats.filter((iface) => this.isInterfaceEnabled(iface));
        },
        disabledInterfaces() {
            return this.interfacesWithStats.filter((iface) => !this.isInterfaceEnabled(iface));
        },
    },
}
</script>
