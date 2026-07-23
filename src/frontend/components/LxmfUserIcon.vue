<template>
    <div v-if="iconName" class="flex items-center justify-center rounded-lg p-2" :style="{ 'color': iconForegroundColour, 'background-color': iconBackgroundColour }">
        <MaterialDesignIcon :icon-name="iconName" class="size-6"/>
    </div>
    <div v-else-if="destinationHash" class="overflow-hidden rounded-lg">
        <Identicon :hash="destinationHash" class="size-10"/>
    </div>
    <div v-else class="rounded-lg bg-[var(--ct-raised)] p-2 text-[var(--ct-dim)]">
        <MaterialDesignIcon icon-name="account-outline" class="size-6"/>
    </div>
</template>

<script>
import MaterialDesignIcon from "./MaterialDesignIcon.vue";
import Identicon from "./Identicon.vue";

export default {
    name: "LxmfUserIcon",
    components: {
        MaterialDesignIcon,
        Identicon,
    },
    props: {
        iconName: String,
        iconForegroundColour: String,
        iconBackgroundColour: String,
        // used to auto-generate an identicon when no custom icon is set
        destinationHash: String,
    },
}
</script>
