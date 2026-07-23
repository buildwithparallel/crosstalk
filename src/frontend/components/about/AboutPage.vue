<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">About</div>
                <div class="text-sm text-[var(--ct-dim)]">App versions, file locations and your network addresses.</div>
            </div>

            <!-- app info -->
            <div v-if="appInfo" class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">App Info</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <!-- version -->
                    <div class="flex p-2.5">
                        <div class="mr-auto">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Versions</div>
                            <div class="text-sm text-[var(--ct-dim)]">
                                Crosstalk v{{ appInfo.version }} • RNS v{{ appInfo.rns_version }} • LXMF v{{ appInfo.lxmf_version }} • Python v{{ appInfo.python_version }}
                            </div>
                        </div>
                        <div class="hidden sm:block mx-2 my-auto">
                            <a target="_blank"
                                href="https://github.com/buildwithparallel/crosstalk/releases"
                                class="ct-secondary-button my-auto inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                                Check for Updates
                            </a>
                        </div>
                    </div>

                    <!-- reticulum config path -->
                    <div class="flex p-2.5">
                        <div class="mr-auto min-w-0">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Reticulum Config Path</div>
                            <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ appInfo.reticulum_config_path }}</div>
                        </div>
                        <div class="mx-2 my-auto flex shrink-0 items-center gap-2">
                            <CopyButton :value="appInfo.reticulum_config_path" label="Reticulum Config Path"/>
                            <button @click="showReticulumConfigFile"
                                v-if="isElectron"
                                type="button"
                                class="ct-secondary-button my-auto inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                                Show in Folder
                            </button>
                        </div>
                    </div>

                    <!-- database path -->
                    <div class="flex p-2.5">
                        <div class="mr-auto min-w-0">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Database Path</div>
                            <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ appInfo.database_path }}</div>
                        </div>
                        <div class="mx-2 my-auto flex shrink-0 items-center gap-2">
                            <CopyButton :value="appInfo.database_path" label="Database Path"/>
                            <button @click="showDatabaseFile"
                                v-if="isElectron"
                                type="button"
                                class="ct-secondary-button my-auto inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                                Show in Folder
                            </button>
                        </div>
                    </div>

                    <!-- database file size -->
                    <div class="p-2.5">
                        <div class="text-sm font-medium text-[var(--ct-text)]">Database File Size</div>
                        <div class="text-sm text-[var(--ct-dim)]">{{ formatBytes(appInfo.database_file_size) }}</div>
                    </div>

                </div>
            </div>

            <!-- reticulum status -->
            <div v-if="appInfo" class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Reticulum Status</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <!-- instance mode -->
                    <div class="flex items-center justify-between p-2.5">
                        <div class="text-sm font-medium text-[var(--ct-text)]">Instance Mode</div>
                        <Badge v-if="appInfo.is_connected_to_shared_instance" variant="amber" dot>Shared Instance</Badge>
                        <Badge v-else variant="green" dot>Standalone Instance</Badge>
                    </div>

                    <!-- transport mode -->
                    <div class="flex items-center justify-between p-2.5">
                        <div class="text-sm font-medium text-[var(--ct-text)]">Transport Mode</div>
                        <Badge v-if="appInfo.is_transport_enabled" variant="green" dot>Enabled</Badge>
                        <Badge v-else variant="neutral">Disabled</Badge>
                    </div>

                </div>
            </div>

            <!-- my addresses -->
            <div v-if="config" class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">My Addresses</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">
                    <div class="p-2.5">
                        <div class="flex items-center gap-1">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Identity Hash</div>
                            <CopyButton class="ml-auto" :value="config.identity_hash" label="Identity Hash"/>
                        </div>
                        <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ config.identity_hash }}</div>
                    </div>
                    <div class="p-2.5">
                        <div class="flex items-center gap-1">
                            <div class="text-sm font-medium text-[var(--ct-text)]">LXMF Address</div>
                            <CopyButton class="ml-auto" :value="config.lxmf_address_hash" label="LXMF Address"/>
                        </div>
                        <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ config.lxmf_address_hash }}</div>
                    </div>
                    <div class="p-2.5">
                        <div class="flex items-center gap-1">
                            <div class="text-sm font-medium text-[var(--ct-text)]">LXMF Propagation Node Address</div>
                            <CopyButton class="ml-auto" :value="config.lxmf_local_propagation_node_address_hash" label="LXMF Propagation Node Address"/>
                        </div>
                        <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ config.lxmf_local_propagation_node_address_hash }}</div>
                    </div>
                    <div class="p-2.5">
                        <div class="flex items-center gap-1">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Audio Call Address</div>
                            <CopyButton class="ml-auto" :value="config.audio_call_address_hash" label="Audio Call Address"/>
                        </div>
                        <div class="ct-hash break-all text-xs text-[var(--ct-dim)]">{{ config.audio_call_address_hash }}</div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import ElectronUtils from "../../js/ElectronUtils";
import CopyButton from "../CopyButton.vue";
import Badge from "../base/Badge.vue";
export default {
    name: 'AboutPage',
    components: {
        CopyButton,
        Badge,
    },
    data() {
        return {
            appInfo: null,
            config: null,
        };
    },
    mounted() {
        this.getAppInfo();
        this.getConfig();
    },
    methods: {
        async getAppInfo() {
            try {
                const response = await window.axios.get("/api/v1/app/info");
                this.appInfo = response.data.app_info;
            } catch(e) {
                // do nothing if failed to load app info
                console.log(e);
            }
        },
        async getConfig() {
            try {
                const response = await window.axios.get("/api/v1/config");
                this.config = response.data.config;
            } catch(e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        showReticulumConfigFile() {
            const reticulumConfigPath = this.appInfo.reticulum_config_path;
            if(reticulumConfigPath){
                ElectronUtils.showPathInFolder(reticulumConfigPath);
            }
        },
        showDatabaseFile() {
            const databasePath = this.appInfo.database_path;
            if(databasePath){
                ElectronUtils.showPathInFolder(databasePath);
            }
        },
        formatBytes: function(bytes) {
            return Utils.formatBytes(bytes);
        },
    },
    computed: {
        isElectron() {
            return ElectronUtils.isElectron();
        },
    },
}
</script>
