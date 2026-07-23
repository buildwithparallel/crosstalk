<template>
    <div class="dark ct-shell ct-dot-grid h-screen w-full flex flex-col text-[var(--ct-text)]">

        <!-- overlay hosts -->
        <ModalHost/>
        <ToastHost/>

        <!-- header -->
        <div class="relative flex bg-[rgba(9,9,9,0.88)] backdrop-blur-xl px-3 py-2 border-b border-[var(--ct-border)] min-h-14 shadow-[0_12px_42px_rgba(0,0,0,0.28)]">
            <div class="pointer-events-none absolute inset-0 ct-vignette opacity-40"></div>
            <div class="flex w-full items-center">
                <div class="hidden sm:flex mr-2.5">
                    <img class="size-9 drop-shadow-[0_0_20px_rgba(0,97,253,0.45)]" src="/assets/images/crosstalk-mark.svg" />
                </div>
                <div @click="onAppNameClick" class="relative cursor-pointer">
                    <div class="font-bold leading-5 text-[var(--ct-text)]">Crosstalk</div>
                    <div class="text-xs text-[var(--ct-dim)]">Talk to the World</div>
                </div>

                <!-- contextual actions (messages) -->
                <div class="relative flex ml-auto items-center gap-x-2">
                    <button v-if="isOnMessagesRoute" @click="syncPropagationNode" type="button" class="ct-secondary-button flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-sm font-semibold transition">
                        <span :class="{ 'animate-spin': isSyncingPropagationNode }">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                            </svg>
                        </span>
                        <span class="hidden sm:inline-block">{{ isSyncingPropagationNode ? 'Syncing…' : 'Sync' }}</span>
                    </button>
                    <button @click="composeNewMessage" type="button" class="ct-brand-button flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-sm font-semibold text-white transition">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487 18.549 2.8a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                        </svg>
                        <span class="hidden sm:inline-block">Compose</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- middle -->
        <div ref="middle" class="flex h-full w-full overflow-auto">

            <!-- sidebar -->
            <div class="flex w-64 min-w-64 flex-col bg-[rgba(9,9,9,0.88)]">
                <div class="flex grow flex-col overflow-y-auto border-r border-[var(--ct-border)] bg-[rgba(9,9,9,0.72)] backdrop-blur-xl">

                    <!-- navigation -->
                    <div class="flex-1">

                        <!-- communicate group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Communicate</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'messages' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>
                                        <span>Messages</span>
                                        <span v-if="unreadConversationsCount > 0" class="ml-auto mr-2 inline-flex min-w-5 items-center justify-center rounded-full bg-[var(--ct-blue)] px-1.5 text-xs font-bold text-white">{{ unreadConversationsCount }}</span>
                                    </template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'nomadnetwork' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>Browse</template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- network group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Network</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'network-visualiser' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 256 256" class="size-5">
                                            <path d="M200,152a31.84,31.84,0,0,0-19.53,6.68l-23.11-18A31.65,31.65,0,0,0,160,128c0-.74,0-1.48-.08-2.21l13.23-4.41A32,32,0,1,0,168,104c0,.74,0,1.48.08,2.21l-13.23,4.41A32,32,0,0,0,128,96a32.59,32.59,0,0,0-5.27.44L115.89,81A32,32,0,1,0,96,88a32.59,32.59,0,0,0,5.27-.44l6.84,15.4a31.92,31.92,0,0,0-8.57,39.64L73.83,165.44a32.06,32.06,0,1,0,10.63,12l25.71-22.84a31.91,31.91,0,0,0,37.36-1.24l23.11,18A31.65,31.65,0,0,0,168,184a32,32,0,1,0,32-32Zm0-64a16,16,0,1,1-16,16A16,16,0,0,1,200,88ZM80,56A16,16,0,1,1,96,72,16,16,0,0,1,80,56ZM56,208a16,16,0,1,1,16-16A16,16,0,0,1,56,208Zm56-80a16,16,0,1,1,16,16A16,16,0,0,1,112,128Zm88,72a16,16,0,1,1,16-16A16,16,0,0,1,200,200Z"></path>
                                        </svg>
                                    </template>
                                    <template v-slot:text>Network Map</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'interfaces' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="currentColor" viewBox="0 0 256 256">
                                            <path d="M232,112H136V88h8a16,16,0,0,0,16-16V40a16,16,0,0,0-16-16H112A16,16,0,0,0,96,40V72a16,16,0,0,0,16,16h8v24H24a8,8,0,0,0,0,16H56v32H48a16,16,0,0,0-16,16v32a16,16,0,0,0,16,16H80a16,16,0,0,0,16-16V176a16,16,0,0,0-16-16H72V128H184v32h-8a16,16,0,0,0-16,16v32a16,16,0,0,0,16,16h32a16,16,0,0,0,16-16V176a16,16,0,0,0-16-16h-8V128h32a8,8,0,0,0,0-16ZM112,40h32V72H112ZM80,208H48V176H80Zm128,0H176V176h32Z"></path>
                                        </svg>
                                    </template>
                                    <template v-slot:text>Connections</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'infrastructure' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 0 1 7.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 0 1 1.06 0Z" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>Discovered Nodes</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'tools' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>Tools</template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- app group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">App</div>
                        <ul class="pr-2 space-y-0.5 pb-2">
                            <li>
                                <SidebarLink :to="{ name: 'settings' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>Settings</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'about' }">
                                    <template v-slot:icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
                                        </svg>
                                    </template>
                                    <template v-slot:text>About</template>
                                </SidebarLink>
                            </li>
                        </ul>

                    </div>

                    <!-- active calls banner -->
                    <div v-if="activeAudioCalls.length > 0" class="mx-2 mb-2 rounded-xl border border-[rgba(46,231,129,0.4)] bg-[rgba(46,231,129,0.08)] p-2">
                        <div class="flex items-center">
                            <div class="min-w-0">
                                <div class="text-sm font-semibold text-[var(--ct-text)]">
                                    <span v-if="activeInboundAudioCalls.length > 0">{{ activeInboundAudioCalls.length }} Incoming {{ activeInboundAudioCalls.length === 1 ? 'Call' : 'Calls' }}</span>
                                    <span v-else>{{ activeOutboundAudioCalls.length }} Outgoing {{ activeOutboundAudioCalls.length === 1 ? 'Call' : 'Calls' }}</span>
                                </div>
                            </div>
                            <div class="ml-auto flex items-center gap-x-1.5">
                                <a href="../call.html" target="_blank" title="View Calls" class="inline-flex items-center rounded-full bg-green-500 p-1.5 text-white hover:bg-green-400">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4">
                                        <path fill-rule="evenodd" d="M2 3.5A1.5 1.5 0 0 1 3.5 2h1.148a1.5 1.5 0 0 1 1.465 1.175l.716 3.223a1.5 1.5 0 0 1-1.052 1.767l-.933.267c-.41.117-.643.555-.48.95a11.542 11.542 0 0 0 6.254 6.254c.395.163.833-.07.95-.48l.267-.933a1.5 1.5 0 0 1 1.767-1.052l3.223.716A1.5 1.5 0 0 1 18 15.352V16.5a1.5 1.5 0 0 1-1.5 1.5H15c-1.149 0-2.263-.15-3.326-.43A13.022 13.022 0 0 1 2.43 8.326 13.019 13.019 0 0 1 2 5V3.5Z" clip-rule="evenodd" />
                                    </svg>
                                </a>
                                <button title="Hang up all calls" @click="hangupAllCalls" type="button" class="inline-flex items-center rounded-full bg-red-500 p-1.5 text-white hover:bg-red-400">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4 rotate-[135deg] translate-y-0.5">
                                        <path fill-rule="evenodd" d="M2 3.5A1.5 1.5 0 0 1 3.5 2h1.148a1.5 1.5 0 0 1 1.465 1.175l.716 3.223a1.5 1.5 0 0 1-1.052 1.767l-.933.267c-.41.117-.643.555-.48.95a11.542 11.542 0 0 0 6.254 6.254c.395.163.833-.07.95-.48l.267-.933a1.5 1.5 0 0 1 1.767-1.052l3.223.716A1.5 1.5 0 0 1 18 15.352V16.5a1.5 1.5 0 0 1-1.5 1.5H15c-1.149 0-2.263-.15-3.326-.43A13.022 13.022 0 0 1 2.43 8.326 13.019 13.019 0 0 1 2 5V3.5Z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- identity card -->
                    <div v-if="config" class="border-t border-[var(--ct-border)] bg-[rgba(13,13,18,0.9)]">

                        <!-- expanded identity settings -->
                        <div v-if="isShowingIdentitySettings" class="border-b border-[var(--ct-border)] p-3 space-y-3">
                            <div>
                                <div class="ct-section-label mb-1">Display Name</div>
                                <div class="flex gap-x-1.5">
                                    <input
                                        v-model="displayName"
                                        @keydown.enter="saveIdentitySettings"
                                        type="text"
                                        placeholder="Display Name"
                                        class="block w-full rounded-lg border p-2 text-sm"
                                    >
                                    <button @click="saveIdentitySettings" type="button" class="ct-brand-button rounded-lg px-3 text-sm font-semibold">Save</button>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">LXMF Address</div>
                                <div class="flex items-center gap-x-1">
                                    <div class="ct-hash break-all">{{ config.lxmf_address_hash }}</div>
                                    <CopyButton class="ml-auto" :value="config.lxmf_address_hash" label="LXMF Address"/>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">Identity Hash</div>
                                <div class="flex items-center gap-x-1">
                                    <div class="ct-hash break-all">{{ config.identity_hash }}</div>
                                    <CopyButton class="ml-auto" :value="config.identity_hash" label="Identity Hash"/>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">Auto Announce</div>
                                <select
                                    v-model="config.auto_announce_interval_seconds"
                                    @change="onAnnounceIntervalSecondsChange"
                                    class="block w-full rounded-lg border p-2 text-sm"
                                >
                                    <option value="0">Disabled</option>
                                    <option value="900">Every 15 Minutes</option>
                                    <option value="1800">Every 30 Minutes</option>
                                    <option value="3600">Every 1 Hour</option>
                                    <option value="10800">Every 3 Hours</option>
                                    <option value="21600">Every 6 Hours</option>
                                    <option value="43200">Every 12 Hours</option>
                                    <option value="86400">Every 24 Hours</option>
                                </select>
                                <div class="mt-1 text-xs text-[var(--ct-dim)]">
                                    <span v-if="config.last_announced_at">Last announced {{ formatSecondsAgo(config.last_announced_at) }}</span>
                                    <span v-else>Never announced</span>
                                </div>
                            </div>
                            <div class="flex gap-x-1.5">
                                <button @click="sendAnnounce" type="button" class="ct-secondary-button flex-1 rounded-lg px-3 py-1.5 text-sm font-semibold">Announce Now</button>
                                <a href="../call.html" target="_blank" class="ct-secondary-button flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                                    <span>Phone</span>
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-3.5">
                                        <path fill-rule="evenodd" d="M6.194 12.753a.75.75 0 0 0 1.06.053L16.5 4.44v2.81a.75.75 0 0 0 1.5 0v-4.5a.75.75 0 0 0-.75-.75h-4.5a.75.75 0 0 0 0 1.5h2.553l-9.056 8.194a.75.75 0 0 0-.053 1.06Z" clip-rule="evenodd" />
                                    </svg>
                                </a>
                            </div>
                        </div>

                        <!-- collapsed identity card row -->
                        <div @click="isShowingIdentitySettings = !isShowingIdentitySettings" class="flex cursor-pointer items-center gap-x-2.5 p-3 transition hover:bg-[rgba(255,255,255,0.04)]">
                            <RouterLink @click.stop :to="{ name: 'profile.icon' }" title="Change profile icon">
                                <LxmfUserIcon
                                    :icon-name="config?.lxmf_user_icon_name"
                                    :icon-foreground-colour="config?.lxmf_user_icon_foreground_colour"
                                    :icon-background-colour="config?.lxmf_user_icon_background_colour"
                                    :destination-hash="config?.lxmf_address_hash"/>
                            </RouterLink>
                            <div class="min-w-0 flex-1">
                                <div class="truncate text-sm font-semibold text-[var(--ct-text)]">{{ config.display_name || 'Anonymous Peer' }}</div>
                                <div class="ct-hash truncate">{{ truncatedAddress }}</div>
                            </div>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4 shrink-0 text-[var(--ct-dim)] transition" :class="{ 'rotate-180': isShowingIdentitySettings }">
                                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
                            </svg>
                        </div>

                    </div>

                </div>
            </div>

            <RouterView/>

        </div>
    </div>
</template>


<script>
import SidebarLink from "./SidebarLink.vue";
import DialogUtils from "../js/DialogUtils";
import WebSocketConnection from "../js/WebSocketConnection";
import GlobalState from "../js/GlobalState";
import Utils from "../js/Utils";
import GlobalEmitter from "../js/GlobalEmitter";
import NotificationUtils from "../js/NotificationUtils";
import LxmfUserIcon from "./LxmfUserIcon.vue";
import CopyButton from "./CopyButton.vue";
import ModalHost from "./overlays/ModalHost.vue";
import ToastHost from "./overlays/ToastHost.vue";

export default {
    name: 'App',
    components: {
        CopyButton,
        LxmfUserIcon,
        SidebarLink,
        ModalHost,
        ToastHost,
    },
    data() {
        return {

            reloadInterval: null,

            isShowingIdentitySettings: false,

            displayName: "Anonymous Peer",
            config: null,
            appInfo: null,

            audioCalls: [],
            propagationNodeStatus: null,

        };
    },
    beforeUnmount() {

        clearInterval(this.reloadInterval);

        // stop listening for websocket messages
        WebSocketConnection.off("message", this.onWebsocketMessage);

    },
    mounted() {

        // listen for websocket messages
        WebSocketConnection.on("message", this.onWebsocketMessage);

        this.getAppInfo();
        this.updateCallsList();
        this.updatePropagationNodeStatus();

        // update info every few seconds
        this.reloadInterval = setInterval(() => {
            this.updateCallsList();
            this.updatePropagationNodeStatus();
        }, 3000);

    },
    methods: {
        async onWebsocketMessage(message) {
            const json = JSON.parse(message.data);
            switch(json.type){
                case 'config': {
                    this.config = json.config;
                    this.displayName = json.config.display_name;
                    break;
                }
                case 'announced': {
                    // we just announced, update config so we can show the new last updated at
                    this.getConfig();
                    break;
                }
                case 'incoming_audio_call': {
                    NotificationUtils.showIncomingCallNotification();
                    break;
                }
            }
        },
        async getAppInfo() {
            try {
                const response = await window.axios.get(`/api/v1/app/info`);
                this.appInfo = response.data.app_info;
            } catch(e) {
                // do nothing if failed to load app info
                console.log(e);
            }
        },
        async getConfig() {
            try {
                const response = await window.axios.get(`/api/v1/config`);
                this.config = response.data.config;
            } catch(e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        async sendAnnounce() {

            try {
                await window.axios.get(`/api/v1/announce`);
                DialogUtils.toast("Announce sent to the network", "success");
            } catch(e) {
                DialogUtils.toast("Failed to announce", "error");
                console.log(e);
            }

            // fetch config so it updates last announced timestamp
            await this.getConfig();

        },
        async updateConfig(config) {
            try {
                WebSocketConnection.send(JSON.stringify({
                    "type": "config.set",
                    "config": config,
                }));
            } catch(e) {
                console.error(e);
            }
        },
        async saveIdentitySettings() {
            await this.updateConfig({
                "display_name": this.displayName,
            });
            DialogUtils.toast("Display name saved", "success");
        },
        async onAnnounceIntervalSecondsChange() {
            await this.updateConfig({
                "auto_announce_interval_seconds": this.config.auto_announce_interval_seconds,
            });
        },
        async composeNewMessage() {

            // go to messages route
            await this.$router.push({ name: "messages" });

            // emit global event handled by MessagesPage
            GlobalEmitter.emit("compose-new-message");

        },
        async syncPropagationNode() {

            // ask to stop syncing if already syncing
            if(this.isSyncingPropagationNode){
                if(await DialogUtils.confirm("Are you sure you want to stop syncing?")){
                    await this.stopSyncingPropagationNode();
                }
                return;
            }

            // request sync
            try {
                await axios.get("/api/v1/lxmf/propagation-node/sync");
            } catch(e) {
                const errorMessage = e.response?.data?.message ?? "Something went wrong. Try again later.";
                DialogUtils.toast(errorMessage, "error");
                return;
            }

            // update propagation status
            await this.updatePropagationNodeStatus();

            // wait until sync has finished
            const syncFinishedInterval = setInterval(() => {

                // do nothing if still syncing
                if(this.isSyncingPropagationNode){
                    return;
                }

                // finished syncing, stop checking
                clearInterval(syncFinishedInterval);

                // show result
                const status = this.propagationNodeStatus?.state;
                const messagesReceived = this.propagationNodeStatus?.messages_received ?? 0;
                if(status === "complete" || status === "idle"){
                    DialogUtils.toast(`Sync complete. ${messagesReceived} ${messagesReceived === 1 ? 'message' : 'messages'} received.`, "success");
                } else {
                    DialogUtils.toast(`Sync error: ${status}`, "error");
                }

            }, 500);

        },
        async stopSyncingPropagationNode() {

            // stop sync
            try {
                await axios.get("/api/v1/lxmf/propagation-node/stop-sync");
            } catch(e) {
                // do nothing on error
            }

            // update propagation status
            await this.updatePropagationNodeStatus();

        },
        async updatePropagationNodeStatus() {
            try {
                const response = await axios.get("/api/v1/lxmf/propagation-node/status");
                this.propagationNodeStatus = response.data.propagation_node_status;
            } catch(e) {
                // do nothing on error
            }
        },
        formatSecondsAgo: function(seconds) {
            return Utils.formatSecondsAgo(seconds);
        },
        async updateCallsList() {
            try {

                // fetch calls
                const response = await axios.get("/api/v1/calls");

                // update ui
                this.audioCalls = response.data.audio_calls;

            } catch(e) {
                // do nothing on error
            }
        },
        async hangupAllCalls() {

            // confirm user wants to hang up calls
            if(!await DialogUtils.confirm("Are you sure you want to hang up all incoming and outgoing calls?", { danger: true, confirmLabel: "Hang Up All" })){
                return;
            }

            try {

                // hangup all calls
                await axios.get(`/api/v1/calls/hangup-all`);

                // reload calls list
                await this.updateCallsList();

            } catch(e) {
                // ignore error hanging up call
            }

        },
        onAppNameClick() {
            // user may be on mobile, and is unable to scroll back to sidebar, so let them tap app name to do it
            this.$refs["middle"].scrollTo({
                top: 0,
                left: 0,
                behavior: "smooth",
            });
        },
    },
    computed: {
        unreadConversationsCount() {
            return GlobalState.unreadConversationsCount;
        },
        isOnMessagesRoute() {
            return this.$route.name === "messages";
        },
        truncatedAddress() {
            const hash = this.config?.lxmf_address_hash ?? "";
            if(hash.length > 16){
                return `${hash.slice(0, 8)}…${hash.slice(-8)}`;
            }
            return hash;
        },
        activeAudioCalls() {
            return this.audioCalls.filter(function(audioCall) {
                return audioCall.is_active;
            });
        },
        activeInboundAudioCalls() {
            return this.activeAudioCalls.filter(function(audioCall) {
                return !audioCall.is_outbound;
            });
        },
        activeOutboundAudioCalls() {
            return this.activeAudioCalls.filter(function(audioCall) {
                return audioCall.is_outbound;
            });
        },
        isSyncingPropagationNode() {
            return [
                "path_requested",
                "link_establishing",
                "link_established",
                "request_sent",
                "receiving",
                "response_received",
            ].includes(this.propagationNodeStatus?.state);
        },
    },
}
</script>
