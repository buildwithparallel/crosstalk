<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Profile Icon</div>
                <div class="text-sm text-[var(--ct-dim)]">Personalise how you appear to other people on the network.</div>
            </div>

            <!-- info -->
            <div class="ct-card p-3 text-sm text-[var(--ct-dim)]">
                Your icon is sent with your outgoing messages, so people you chat with will see it. Without a custom icon, others see a unique auto-generated avatar based on your address.
                You can <span @click="removeProfileIcon" class="cursor-pointer text-[#7db0ff] underline hover:text-[var(--ct-text)]">remove your icon</span>, however it will still show for anyone that already received it.
            </div>

            <!-- colours -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Select your Colours</div>
                <div class="divide-y divide-[var(--ct-border)]">

                    <!-- background colour -->
                    <div class="flex space-x-2.5 p-2.5">
                        <div class="flex my-auto">
                            <ColourPickerDropdown v-model:colour="iconBackgroundColour"/>
                        </div>
                        <div class="my-auto">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Background Colour</div>
                            <div class="ct-hash text-xs text-[var(--ct-dim)]">{{ iconBackgroundColour }}</div>
                        </div>
                    </div>

                    <!-- icon colour -->
                    <div class="flex space-x-2.5 p-2.5">
                        <div class="flex my-auto">
                            <ColourPickerDropdown v-model:colour="iconForegroundColour"/>
                        </div>
                        <div class="my-auto">
                            <div class="text-sm font-medium text-[var(--ct-text)]">Icon Colour</div>
                            <div class="ct-hash text-xs text-[var(--ct-dim)]">{{ iconForegroundColour }}</div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- search icons -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Select your Icon</div>
                <div class="divide-y divide-[var(--ct-border)]">
                    <div class="flex p-2">
                        <input v-model="search" type="text" :placeholder="`Search ${iconNames.length} icons...`" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>
                    <div class="divide-y divide-[var(--ct-border)]">
                        <div @click="onIconClick(mdiIconName)" v-for="mdiIconName of searchedIconNames" class="flex cursor-pointer space-x-2.5 p-2 transition hover:bg-[rgba(255,255,255,0.05)]">
                            <div class="my-auto">
                                <LxmfUserIcon :icon-name="mdiIconName" :icon-foreground-colour="iconForegroundColour" :icon-background-colour="iconBackgroundColour"/>
                            </div>
                            <div class="my-auto text-sm text-[var(--ct-muted)]">{{ mdiIconName }}</div>
                        </div>
                        <div v-if="searchedIconNames.length === 0" class="p-2.5 text-sm text-[var(--ct-dim)]">No icons match your search.</div>
                        <div v-if="searchedIconNames.length === maxSearchResults" class="p-2.5 text-sm text-[var(--ct-dim)]">A maximum of {{ maxSearchResults }} icons are shown.</div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import * as mdi from "@mdi/js";
import LxmfUserIcon from "../LxmfUserIcon.vue";
import DialogUtils from "../../js/DialogUtils";
import ColourPickerDropdown from "../ColourPickerDropdown.vue";
import MaterialDesignIcon from "../MaterialDesignIcon.vue";

export default {
    name: 'ProfileIconPage',
    components: {
        ColourPickerDropdown,
        LxmfUserIcon,
        MaterialDesignIcon,
    },
    data() {
        return {

            config: null,
            iconForegroundColour: null,
            iconBackgroundColour: null,

            search: "",
            maxSearchResults: 100,
            iconNames: [],

        };
    },
    mounted() {

        this.getConfig();

        // load icon names
        this.iconNames = Object.keys(mdi).map((mdiIcon) => {
            return mdiIcon
                .replace(/^mdi/, '') // Remove the "mdi" prefix
                .replace(/([a-z])([A-Z])/g, '$1-$2') // Add a hyphen between lowercase and uppercase letters
                .toLowerCase(); // Convert the entire string to lowercase
        });

    },
    methods: {
        async getConfig() {
            try {
                const response = await window.axios.get("/api/v1/config");
                this.config = response.data.config;
            } catch(e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        async updateConfig(config) {
            try {
                const response = await window.axios.patch("/api/v1/config", config);
                this.config = response.data.config;
            } catch(e) {
                DialogUtils.toast("Failed to save profile icon", "error");
                console.log(e);
            }
        },
        async onIconClick(iconName) {

            // ensure foreground colour set
            if(this.iconForegroundColour == null){
                DialogUtils.toast("Select an icon colour first", "error");
                return;
            }

            // ensure background colour set
            if(this.iconBackgroundColour == null){
                DialogUtils.toast("Select a background colour first", "error");
                return;
            }

            // confirm user wants to update their icon
            if(!await DialogUtils.confirm("Set this as your profile icon? It will be sent with your outgoing messages.", { title: "Update Profile Icon", confirmLabel: "Set Icon" })){
                return;
            }

            // save icon appearance
            await this.updateConfig({
                "lxmf_user_icon_name": iconName,
                "lxmf_user_icon_foreground_colour": this.iconForegroundColour,
                "lxmf_user_icon_background_colour": this.iconBackgroundColour,
            });

            DialogUtils.toast("Profile icon updated", "success");

        },
        async removeProfileIcon() {

            // confirm user wants to remove their icon
            if(!await DialogUtils.confirm("Remove your profile icon? Anyone that has already received it will continue to see it until you send them a new icon.", { title: "Remove Profile Icon", confirmLabel: "Remove", danger: true })){
                return;
            }

            // remove profile icon
            await this.updateConfig({
                "lxmf_user_icon_name": null,
                "lxmf_user_icon_foreground_colour": null,
                "lxmf_user_icon_background_colour": null,
            });

        }
    },
    computed: {
        searchedIconNames() {
            return this.iconNames.filter((iconName) => {
                return iconName.includes(this.search);
            }).slice(0, this.maxSearchResults);
        },
    },
    watch: {
        config() {
            // update ui when config is updated
            this.iconName = this.config.lxmf_user_icon_name;
            this.iconForegroundColour = this.config.lxmf_user_icon_foreground_colour || "#6b7280";
            this.iconBackgroundColour = this.config.lxmf_user_icon_background_colour || "#e5e7eb";
        },
    },
}
</script>
