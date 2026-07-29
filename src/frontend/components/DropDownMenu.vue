<template>
    <div v-click-outside="{ handler: onClickOutsideMenu, capture: true }" class="cursor-default relative inline-block text-left">

        <!-- menu button -->
        <div ref="dropdown-button" @click.stop="toggleMenu">
            <slot name="button"/>
        </div>

        <!-- Render the menu at the document level so cards and scrolling panes cannot clip it. -->
        <Teleport to="body">
            <Transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <div
                    v-if="isShowingMenu"
                    ref="dropdown-menu"
                    @click.stop="hideMenu"
                    class="ct-panel fixed z-50 w-56 overflow-hidden rounded-lg border border-[var(--ct-border)] focus:outline-none"
                    :style="dropdownStyle">
                    <slot name="items"/>
                </div>
            </Transition>
        </Teleport>

    </div>
</template>

<script>
export default {
    name: 'DropDownMenu',
    data() {
        return {
            isShowingMenu: false,
            dropdownStyle: {
                visibility: "hidden",
            },
        };
    },
    beforeUnmount() {
        this.removeViewportListeners();
    },
    methods: {
        toggleMenu() {
            if(this.isShowingMenu){
                this.hideMenu();
            } else {
                this.showMenu();
            }
        },
        showMenu() {
            this.dropdownStyle = {
                visibility: "hidden",
            };
            this.isShowingMenu = true;
            this.adjustDropdownPosition();
            this.addViewportListeners();
        },
        hideMenu() {
            this.isShowingMenu = false;
            this.removeViewportListeners();
        },
        onClickOutsideMenu(event) {
            if(this.isShowingMenu){
                const dropdown = this.$refs["dropdown-menu"];
                if(dropdown && dropdown.contains(event.target)){
                    return;
                }
                event.preventDefault();
                this.hideMenu();
            }
        },
        addViewportListeners() {
            window.addEventListener("resize", this.adjustDropdownPosition);
            window.addEventListener("scroll", this.adjustDropdownPosition, true);
        },
        removeViewportListeners() {
            window.removeEventListener("resize", this.adjustDropdownPosition);
            window.removeEventListener("scroll", this.adjustDropdownPosition, true);
        },
        adjustDropdownPosition() {
            this.$nextTick(() => {

                // find button and dropdown
                const button = this.$refs["dropdown-button"];
                const dropdown = this.$refs["dropdown-menu"];

                // do nothing if not found
                if(!button || !dropdown){
                    return;
                }

                // get bounding box of button and dropdown
                const buttonRect = button.getBoundingClientRect();
                const dropdownRect = dropdown.getBoundingClientRect();

                // calculate how much space is under and above the button
                const spaceBelowButton = window.innerHeight - buttonRect.bottom;
                const spaceAboveButton = buttonRect.top;

                const gap = 8;
                const viewportPadding = 8;
                const requiredHeight = dropdownRect.height + gap;
                const openAbove = spaceAboveButton >= requiredHeight
                    && spaceBelowButton < requiredHeight;

                // Prefer below the button, then flip above when the lower viewport is too short.
                const desiredTop = openAbove
                    ? buttonRect.top - dropdownRect.height - gap
                    : buttonRect.bottom + gap;
                const maxTop = Math.max(viewportPadding, window.innerHeight - dropdownRect.height - viewportPadding);
                const top = Math.min(Math.max(desiredTop, viewportPadding), maxTop);

                // Align the right edges and keep the menu inside the viewport.
                const desiredLeft = buttonRect.right - dropdownRect.width;
                const maxLeft = Math.max(viewportPadding, window.innerWidth - dropdownRect.width - viewportPadding);
                const left = Math.min(Math.max(desiredLeft, viewportPadding), maxLeft);

                this.dropdownStyle = {
                    left: `${Math.round(left)}px`,
                    top: `${Math.round(top)}px`,
                    visibility: "visible",
                };
            });
        },
    },
}
</script>
