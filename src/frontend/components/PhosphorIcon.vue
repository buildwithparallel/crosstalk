<template>
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 256 256"
        role="img"
        :aria-label="name"
        fill="currentColor"
        style="display:inline-block;vertical-align:middle;flex-shrink:0;">
        <!-- duotone icons carry a background layer, so render their full inner markup -->
        <g v-if="isMarkup" v-html="innerMarkup"></g>
        <path v-else :d="pathD"/>
    </svg>
</template>

<script>
import { getPhosphorPath, getPhosphorSvg } from "../js/PhosphorIcons";

export default {
    name: "PhosphorIcon",
    props: {
        // kebab-case Phosphor name, e.g. "house", "chat-circle", "tree-structure"
        name: {
            type: String,
            required: true,
        },
        // regular | bold | fill | duotone | light | thin
        weight: {
            type: String,
            default: "regular",
        },
    },
    computed: {
        svg() {
            return getPhosphorSvg(this.name, this.weight) ?? "";
        },
        pathD() {
            return getPhosphorPath(this.name, this.weight);
        },
        isMarkup() {
            // duotone (and rare multi-path) icons need more than the single path
            return (this.svg.match(/<path\b/g) || []).length > 1;
        },
        innerMarkup() {
            return this.svg
                .replace(/^<svg[^>]*>/i, "")
                .replace(/<\/svg>\s*$/i, "");
        },
    },
};
</script>
