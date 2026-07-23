<template>
    <div class="flex cursor-pointer space-x-2 p-3 text-sm text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.06)] hover:text-[var(--ct-text)]">
        <slot/>
    </div>
</template>

<script>
export default {
    name: 'DropDownMenuItem',
}
</script>
