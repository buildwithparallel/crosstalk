<template>
    <button type="button" class="rounded-full bg-[rgba(255,255,255,0.08)] p-2 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.14)] hover:text-[var(--ct-text)]">
        <slot/>
    </button>
</template>

<script>
export default {
    name: 'IconButton',
}
</script>
