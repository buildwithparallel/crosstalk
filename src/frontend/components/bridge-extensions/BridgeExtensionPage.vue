<template>
    <HfBridgesPage
        v-if="role && extension?.id === lastResortHopId"
        :extension="extension"
        :role="role"/>
    <BridgeExtensionRolesPage
        v-else-if="extension && !roleId"
        :extension="extension"/>
    <div v-else class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <EmptyState
            :title="emptyTitle"
            :description="emptyDescription">
            <template v-slot:icon>
                <PhosphorIcon name="plugs-connected" weight="duotone" class="size-7"/>
            </template>
            <template v-slot:action>
                <RouterLink :to="emptyBackTo" class="ct-secondary-button rounded-lg px-4 py-2 text-sm font-semibold">
                    {{ emptyBackLabel }}
                </RouterLink>
            </template>
        </EmptyState>
    </div>
</template>

<script>
import EmptyState from "../base/EmptyState.vue";
import HfBridgesPage from "../hf/HfBridgesPage.vue";
import PhosphorIcon from "../PhosphorIcon.vue";
import BridgeExtensionRolesPage from "./BridgeExtensionRolesPage.vue";
import { LAST_RESORT_HOP_ID, getBridgeExtension, getBridgeExtensionRole } from "../../js/bridgeExtensions";

export default {
    name: "BridgeExtensionPage",
    components: {
        BridgeExtensionRolesPage,
        EmptyState,
        HfBridgesPage,
        PhosphorIcon,
    },
    props: {
        id: {
            type: String,
            required: true,
        },
        roleId: {
            type: String,
            default: null,
        },
    },
    data() {
        return {
            lastResortHopId: LAST_RESORT_HOP_ID,
        };
    },
    computed: {
        extension() {
            return getBridgeExtension(this.id);
        },
        role() {
            if (!this.roleId) {
                return null;
            }
            return getBridgeExtensionRole(this.id, this.roleId);
        },
        emptyTitle() {
            if (!this.extension) {
                return "Unknown bridge extension";
            }
            if (this.roleId && !this.role) {
                return "Unknown radio";
            }
            return "This radio has no page yet";
        },
        emptyDescription() {
            if (!this.extension) {
                return `No implementation is registered for ${this.id}.`;
            }
            if (this.roleId && !this.role) {
                return `No radio named ${this.roleId} on ${this.extension.name}.`;
            }
            return `${this.role?.hardware || "This radio"} is not set up in Crosstalk yet.`;
        },
        emptyBackTo() {
            if (this.extension) {
                return { name: "bridge-extensions.show", params: { id: this.extension.id } };
            }
            return { name: "bridge-extensions" };
        },
        emptyBackLabel() {
            return this.extension ? this.extension.name : "Bridge Extensions";
        },
    },
};
</script>
