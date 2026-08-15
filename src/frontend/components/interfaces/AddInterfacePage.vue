<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto p-3 space-y-3">

            <!-- page header -->
            <div class="flex items-center gap-x-2">
                <RouterLink :to="{ name: 'interfaces' }" class="flex rounded-md p-1.5 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.08)] hover:text-[var(--ct-text)]" title="Back to Network Interfaces">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                        <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
                    </svg>
                </RouterLink>
                <div>
                    <div class="text-lg font-bold text-[var(--ct-text)]">
                        <span v-if="isEditingInterface">Edit Interface</span>
                        <span v-else>Add Interface</span>
                    </div>
                    <div class="text-sm text-[var(--ct-dim)]">
                        <span v-if="isEditingInterface">Update how this device connects to the network.</span>
                        <span v-else-if="newInterfaceType == null">Choose how you want to connect to the Reticulum network.</span>
                        <span v-else>Fill in the details for this interface.</span>
                    </div>
                </div>
            </div>

            <!-- guided type picker -->
            <div v-if="!isEditingInterface && newInterfaceType == null" class="space-y-3">
                <div v-for="group of interfaceTypeGroups" :key="group.label">
                    <div class="ct-section-label mb-1.5">{{ group.label }}</div>
                    <div class="grid grid-cols-1 gap-2 md:grid-cols-2">
                        <button v-for="option of group.options" :key="option.type" @click="newInterfaceType = option.type" type="button" class="ct-card ct-card-hover flex items-start gap-x-3 p-3 text-left">
                            <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                                <PhosphorIcon :name="option.icon" weight="duotone" class="size-5"/>
                            </div>
                            <div class="min-w-0">
                                <div class="text-sm font-semibold text-[var(--ct-text)]">{{ option.name }}</div>
                                <div class="mt-0.5 text-xs leading-4 text-[var(--ct-dim)]">{{ option.description }}</div>
                                <div v-if="alreadyEnabledNoticeForType(option.type)" class="mt-1 text-xs font-medium text-[#7db0ff]">
                                    {{ alreadyEnabledNoticeForType(option.type) }}
                                </div>
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            <!-- community interfaces -->
            <div v-if="!isEditingInterface && newInterfaceType == null && config != null && config.show_suggested_community_interfaces" class="ct-elevated-surface rounded-lg divide-y divide-[var(--ct-border)]">
                <div class="flex p-2">
                    <div class="my-auto mr-auto">
                        <div class="font-bold text-[var(--ct-text)]">Suggested Public Backbone Node</div>
                        <div class="text-sm text-[var(--ct-muted)]">Miami Thunder Host is the recommended public backbone node for quickly testing Reticulum connectivity.</div>
                    </div>
                    <div class="my-auto ml-2">
                        <button @click="updateConfig({'show_suggested_community_interfaces': false})" type="button" class="ct-secondary-button p-2 rounded-full">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                                <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-text)]">

                    <div class="flex px-2 py-1">
                        <div class="my-auto mr-auto">
                            <div>Miami Thunder Host</div>
                            <div class="text-xs">mia.us.thunderhost.net:4242</div>
                        </div>
                        <div class="ml-2 my-auto">
                            <button
                                @click="usePublicBackboneInterface('Miami Thunder Host', 'mia.us.thunderhost.net', '4242')"
                                type="button"
                                class="inline-flex items-center gap-x-1 rounded-md ct-brand-button px-2 py-1 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                                <span>Use Backbone Node</span>
                            </button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- add interface form -->
            <div v-if="isEditingInterface || newInterfaceType != null" class="ct-elevated-surface rounded-lg divide-y divide-[var(--ct-border)]">
                <div class="flex items-center p-2.5">
                    <div class="flex min-w-0 items-center gap-x-2">
                        <div class="flex size-9 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                            <PhosphorIcon :name="selectedTypeOption?.icon ?? 'plugs-connected'" weight="duotone" class="size-5"/>
                        </div>
                        <div class="min-w-0">
                            <div class="truncate text-sm font-bold text-[var(--ct-text)]">{{ selectedTypeOption?.name ?? newInterfaceType }}</div>
                            <div class="truncate text-xs text-[var(--ct-dim)]">{{ selectedTypeOption?.description }}</div>
                        </div>
                    </div>
                    <button v-if="!isEditingInterface" @click="newInterfaceType = null" type="button" class="ct-secondary-button ml-auto shrink-0 rounded-lg px-2.5 py-1.5 text-xs font-semibold">Change Type</button>
                </div>
                <div class="p-2 space-y-3">

                    <!-- iGeneric interface settings -->
                    <!-- interface name -->
                    <div>
                        <FormLabel class="mb-1">Name</FormLabel>
                        <input type="text" :disabled="isEditingInterface" placeholder="New Interface Name"
                               v-model="newInterfaceName"
                               class="block w-full rounded-lg border p-2.5 text-sm"
                               :class="{ 'cursor-not-allowed opacity-60': isEditingInterface }">
                        <FormSubLabel>Interface names must be unique.</FormSubLabel>
                    </div>

                    <div v-if="!isEditingInterface && newInterfaceType === 'AutoInterface' && enabledAutoInterfaces.length > 0" class="rounded-lg border border-[rgba(110,168,255,0.34)] bg-[rgba(0,97,253,0.09)] p-3 text-sm text-[var(--ct-text)]">
                        <div class="font-bold">Local discovery is already on</div>
                        <div class="mt-1 text-[var(--ct-muted)]">
                            {{ enabledAutoInterfaceNames }} {{ enabledAutoInterfaces.length === 1 ? "is" : "are" }} already finding peers on this WiFi or Ethernet network. Another AutoInterface with the default group and ports will fail to start. Add a second one only if you need a separate mesh.
                        </div>
                        <button
                            v-if="enabledAutoInterfaces.length === 1"
                            @click="editExistingInterface(enabledAutoInterfaces[0]._name)"
                            type="button"
                            class="mt-2 inline-flex items-center rounded-md ct-secondary-button px-2.5 py-1.5 text-sm font-semibold">
                            Edit {{ enabledAutoInterfaces[0]._name }}
                        </button>
                    </div>

                    <div v-if="newInterfaceType === 'PublicBackboneInterface'" class="rounded-lg border border-[rgba(110,168,255,0.34)] bg-[rgba(0,97,253,0.09)] p-3 text-sm text-[var(--ct-text)] shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                        <div class="font-bold">Public Backbone Node Setup</div>
                        <div class="mt-1 text-[var(--ct-muted)]">Paste the rmap.world configuration block here, then fill the interface fields from it.</div>
                        <textarea
                            v-model="publicBackboneConfigText"
                            rows="7"
                            placeholder="[[____mia_us_thunderhost_net____]]
  type = BackboneInterface
  enabled = yes
  remote = mia.us.thunderhost.net
  target_port = 4242
  transport_identity = ..."
                            class="mt-2 font-mono border text-sm rounded-lg block w-full p-2.5 bg-[rgba(2,6,23,0.78)] border-[rgba(110,168,255,0.38)] text-[var(--ct-text)] placeholder:text-[var(--ct-dim)]"></textarea>
                        <div v-if="publicBackboneConfigError" class="mt-1 text-sm text-[var(--ct-red)]">{{ publicBackboneConfigError }}</div>
                        <div class="mt-2 grid grid-cols-1 xl:grid-cols-[auto_1fr] items-center gap-2">
                            <button
                                @click="usePublicBackboneConfig"
                                type="button"
                                class="inline-flex items-center justify-center gap-x-1 rounded-md ct-brand-button px-2 py-1 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                                Fill Interface Fields
                            </button>
                            <div class="min-w-0 text-[var(--ct-muted)] leading-5">
                                Crosstalk saves this as a TCP Client Interface. <code>remote</code> becomes Target Host, <code>target_port</code> becomes Target Port, and <code>transport_identity</code> is not required.
                            </div>
                        </div>
                    </div>

                    <!-- TCPClientInterface -->
                    <!-- interface target host -->
                    <div v-if="usesTCPClientFields" class="mb-2">
                        <FormLabel class="mb-1">Target Host</FormLabel>
                        <input type="text" placeholder="e.g: example.com" v-model="newInterfaceTargetHost" class="block w-full rounded-lg border p-2.5 text-sm">
                        <FormSubLabel>For rmap.world backbone configs, paste the <code>remote</code> value here.</FormSubLabel>
                    </div>

                    <!-- interface target port -->
                    <div v-if="usesTCPClientFields" class="mb-2">
                        <FormLabel class="mb-1">Target Port</FormLabel>
                        <input type="text" placeholder="e.g: 1234" v-model="newInterfaceTargetPort" class="block w-full rounded-lg border p-2.5 text-sm">
                        <FormSubLabel>For rmap.world backbone configs, paste the <code>target_port</code> value here.</FormSubLabel>
                    </div>

                    <div v-if="newInterfaceType === 'TCPClientInterface'" class="mb-2 rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.05)] p-2 text-sm text-[var(--ct-muted)]">
                        <div class="font-semibold">Using a public backbone node?</div>
                        <div class="mt-1 grid grid-cols-1 sm:grid-cols-2 gap-1">
                            <div>Choose Type</div>
                            <div>Public Backbone Node (rmap.world)</div>
                            <div><code>remote = host.example</code></div>
                            <div>Target Host</div>
                            <div><code>target_port = 4242</code></div>
                            <div>Target Port</div>
                        </div>
                        <div class="mt-2 text-[var(--ct-dim)]">Transport identity is used by Reticulum backbone nodes internally and is not required for this TCP client entry.</div>
                    </div>

                    <!-- TCPServerInterface -->
                    <!-- interface listen ip -->
                    <div v-if="newInterfaceType === 'TCPServerInterface' || newInterfaceType === 'UDPInterface'" class="mb-2">
                        <FormLabel class="mb-1">Listen IP</FormLabel>
                        <input type="text" placeholder="e.g: 0.0.0.0" v-model="newInterfaceListenIp" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <!-- interface listen port -->
                    <div v-if="newInterfaceType === 'TCPServerInterface' || newInterfaceType === 'UDPInterface'" class="mb-2">
                        <FormLabel class="mb-1">Listen Port</FormLabel>
                        <input type="text" placeholder="e.g: 1234" v-model="newInterfaceListenPort" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <!-- UDPInterface -->
                    <!-- interface forward ip -->
                    <div v-if="newInterfaceType === 'UDPInterface'" class="mb-2">
                        <FormLabel class="mb-1">Forward IP</FormLabel>
                        <input type="text" placeholder="e.g: 255.255.255.255" v-model="newInterfaceForwardIp" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <!-- interface listen port -->
                    <div v-if="newInterfaceType === 'UDPInterface'" class="mb-2">
                        <FormLabel class="mb-1">Forward Port</FormLabel>
                        <input type="text" placeholder="e.g: 1234" v-model="newInterfaceForwardPort" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <!-- I2PInterface -->
                    <!-- peers -->
                    <div v-if="newInterfaceType === 'I2PInterface'">
                        <div class="mb-2 text-sm text-[var(--ct-dim)]">ⓘ To use the I2P interface, you must have an I2P router running on your system. When the I2P Interface is added for the first time Reticulum will generate a new I2P address for the interface and begin listening for inbound traffic.</div>
                        <FormLabel class="mb-1">Peers</FormLabel>
                        <div class="space-y-2">
                            <div v-for="(peer, index) in I2PSettings.newInterfacePeers" :key="index" class="flex items-center space-x-2">
                                <input
                                    type="text"
                                    v-model="I2PSettings.newInterfacePeers[index]"
                                    placeholder="Enter peer address (e.g: 5urvjicpzi7q3ybztsef4i5ow2aq4soktfj7zedz53s47r54jnqq.b32.i2p)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                                <button @click="removeI2PPeer(index)" type="button" class="bg-red-500 hover:bg-red-400 text-white text-sm p-2 rounded-lg">Remove</button>
                            </div>
                            <button @click="addI2PPeer('')" type="button" class="bg-green-500 hover:bg-green-400 text-white text-sm px-4 py-2 rounded-lg">Add Peer</button>
                        </div>
                    </div>

                    <!-- RNode interface -->
                    <!-- interface port -->
                    <div v-if="newInterfaceType === 'RNodeInterface'" class="mb-2">
                        <FormLabel class="mb-1">Port</FormLabel>
                        <select v-model="newInterfacePort" class="block w-full rounded-lg border p-2.5 text-sm">
                            <option v-for="comport of comports" :value="comport.device">{{ comport.device }} (Product: {{ comport.product ?? '?' }}, Serial: {{ comport.serial ?? '?' }})</option>
                        </select>
                        <FormSubLabel>
                            <div @click="loadComports" class="text-blue-500 underline cursor-pointer">Reload Ports</div>
                        </FormSubLabel>
                    </div>

                    <!-- IridiumIMTInterface -->
                    <div v-if="newInterfaceType === 'IridiumIMTInterface'" class="space-y-3">
                        <div class="rounded-lg border border-[rgba(110,168,255,0.34)] bg-[rgba(0,97,253,0.09)] p-3 text-sm text-[var(--ct-text)]">
                            <div class="font-bold">Native Reticulum over Iridium IMT</div>
                            <div class="mt-1 text-[var(--ct-muted)]">
                                Carries complete encrypted Reticulum packets through a USB-connected RockBLOCK 9704. This optional interface requires Ground Control's <code>rockblock9704</code> Python package.
                            </div>
                        </div>

                        <div>
                            <FormLabel class="mb-1">RockBLOCK Serial Port</FormLabel>
                            <select v-model="newInterfacePort" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option v-for="comport of comports" :value="comport.device">{{ comport.device }} (Product: {{ comport.product ?? '?' }}, Serial: {{ comport.serial ?? '?' }})</option>
                            </select>
                            <FormSubLabel>
                                <div @click="loadComports" class="text-blue-500 underline cursor-pointer">Reload Ports</div>
                            </FormSubLabel>
                        </div>

                        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div>
                                <FormLabel class="mb-1">Cloudloop IMT Topic</FormLabel>
                                <input v-model.number="iridiumIMTSettings.topic" type="number" class="block w-full rounded-lg border p-2.5 text-sm">
                                <FormSubLabel>RAW messaging uses topic 244.</FormSubLabel>
                            </div>
                            <div>
                                <FormLabel class="mb-1">Maximum Queued Packets</FormLabel>
                                <input v-model.number="iridiumIMTSettings.maximumQueuedPackets" type="number" min="1" class="block w-full rounded-lg border p-2.5 text-sm">
                            </div>
                            <div>
                                <FormLabel class="mb-1">Modem Poll Interval (seconds)</FormLabel>
                                <input v-model.number="iridiumIMTSettings.pollInterval" type="number" min="0.01" step="0.01" class="block w-full rounded-lg border p-2.5 text-sm">
                            </div>
                            <div>
                                <FormLabel class="mb-1">Modem Failure Retry (seconds)</FormLabel>
                                <input v-model.number="iridiumIMTSettings.retryInterval" type="number" min="480" step="60" class="block w-full rounded-lg border p-2.5 text-sm">
                                <FormSubLabel>Minimum 480 seconds; applies only to a failed IMT submission.</FormSubLabel>
                            </div>
                            <div>
                                <FormLabel class="mb-1">Modem Attempts Per Packet</FormLabel>
                                <select v-model.number="iridiumIMTSettings.maximumModemAttempts" class="block w-full rounded-lg border p-2.5 text-sm">
                                    <option :value="1">1 — recommended</option>
                                    <option :value="2">2 — advanced</option>
                                </select>
                                <FormSubLabel>Keep this at one when LXMF retries are enabled.</FormSubLabel>
                            </div>
                            <div>
                                <FormLabel class="mb-1">LXMF Proof/Retry Window (seconds)</FormLabel>
                                <input v-model.number="iridiumIMTSettings.lxmfRetryInterval" type="number" min="480" step="60" class="block w-full rounded-lg border p-2.5 text-sm">
                                <FormSubLabel>Minimum 480 seconds; 600 seconds is recommended for Iridium.</FormSubLabel>
                            </div>
                            <div>
                                <FormLabel class="mb-1">Maximum Satellite Attempts</FormLabel>
                                <select v-model.number="iridiumIMTSettings.lxmfMaxAttempts" class="block w-full rounded-lg border p-2.5 text-sm">
                                    <option :value="1">1 — controlled testing</option>
                                    <option :value="2">2 — one delayed retry</option>
                                </select>
                                <FormSubLabel>A proof immediately cancels any remaining retry.</FormSubLabel>
                            </div>
                        </div>
                    </div>

                    <!-- interface Frequency -->
                    <div v-if="newInterfaceType === 'RNodeInterface'" class="mb-2">
                        <FormLabel class="mb-1">
                            <span>Frequency</span><span v-if="formattedFrequency">: {{ formattedFrequency }}</span>
                        </FormLabel>
                        <div class="flex items-center">
                            <div class="flex flex-col">
                                <input
                                    type="number"
                                    v-model.number="RNodeGHzValue"
                                    min="0"
                                    placeholder="GHz"
                                    class="w-full rounded-l-lg border p-2.5 text-sm"
                                />
                                <FormSubLabel class="text-center">GHz</FormSubLabel>
                            </div>
                            <div class="flex flex-col">
                                <input
                                    type="number"
                                    v-model.number="RNodeMHzValue"
                                    min="0"
                                    placeholder="MHz"
                                    class="w-full border-y p-2.5 text-sm"
                                />
                                <FormSubLabel class="text-center">MHz</FormSubLabel>
                            </div>
                            <div class="flex flex-col">
                                <input
                                    type="number"
                                    v-model.number="RNodekHzValue"
                                    min="0"
                                    placeholder="kHz"
                                    class="w-full rounded-r-lg border p-2.5 text-sm"
                                />
                                <FormSubLabel class="text-center">kHz</FormSubLabel>
                            </div>
                        </div>
                    </div>

                    <!-- interface bandwidth -->
                    <div v-if="newInterfaceType === 'RNodeInterface'" class="mb-2">
                        <FormLabel class="mb-1">Bandwidth</FormLabel>
                        <select v-model="newInterfaceBandwidth" class="block w-full rounded-lg border p-2.5 text-sm">
                            <option v-for="bandwidth in RNodeInterfaceDefaults.bandwidths" :value="bandwidth">{{ bandwidth / 1000 }} KHz</option>
                        </select>
                    </div>

                    <!-- interface txpower -->
                    <div v-if="newInterfaceType === 'RNodeInterface'" class="mb-2">
                        <FormLabel class="mb-1">Transmit Power (dBm)</FormLabel>
                        <input v-model="newInterfaceTxpower" type="number" class="block w-full rounded-lg border p-2.5 text-sm">
                    </div>

                    <div v-if="newInterfaceType === 'RNodeInterface'" class="mb-2 flex flex-wrap items-start gap-4">

                        <!-- interface spreading factor -->
                        <div class="flex-1">
                            <FormLabel class="mb-1">Spreading Factor</FormLabel>
                            <select v-model="newInterfaceSpreadingFactor" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option v-for="spreadingfactor in RNodeInterfaceDefaults.spreadingfactors" :value="spreadingfactor">{{ spreadingfactor }}</option>
                            </select>
                        </div>

                        <!-- interface coding rate -->
                        <div class="flex-1">
                            <FormLabel class="mb-1">Coding Rate</FormLabel>
                            <select v-model="newInterfaceCodingRate" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option v-for="codingrate in RNodeInterfaceDefaults.codingrates" :value="codingrate">{{ codingrate }} (LoRa 4/{{ codingrate }})</option>
                            </select>
                        </div>

                    </div>

                    <!-- RNodeMultiInterface -->
                    <div v-if="newInterfaceType === 'RNodeMultiInterface'" class="mb-2">
                        <p class="text-sm text-[var(--ct-dim)] mb-3">ⓘ The RNode Multi Interface is used for custom devices with multiple LoRa transceivers such as the openCom XL.</p>
                        <FormLabel class="mb-1">Port</FormLabel>
                        <select v-model="newInterfacePort" class="block w-full rounded-lg border p-2.5 text-sm">
                            <option v-for="comport of comports" :value="comport.device">{{ comport.device }} (Product: {{ comport.product ?? '?' }}, Serial: {{ comport.serial ?? '?' }})</option>
                        </select>
                        <FormSubLabel>
                            <div @click="loadComports" class="text-blue-500 underline cursor-pointer">Reload Ports</div>
                        </FormSubLabel>
                    </div>

                    <!-- RNodeMultiInterface: Sub Interfaces -->
                    <div v-if="newInterfaceType === 'RNodeMultiInterface'" class="mb-2">
                        <FormLabel class="mb-1">Sub-Interfaces</FormLabel>
                        <div class="space-y-3">
                            <div :key="idx" v-for="(sub, idx) in RNodeMultiInterface.subInterfaces" class="p-2 space-y-2 border border-[var(--ct-border)] rounded-lg">

                                <input
                                    v-model="sub.name"
                                    type="text"
                                    placeholder="Sub-Interface Name"
                                    class="w-full rounded-lg border p-2.5 text-sm">

                                <div class="flex gap-2">
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">Frequency (Hz)</FormLabel>
                                        <input
                                            v-model.number="sub.frequency"
                                            type="number"
                                            class="w-full rounded-lg border p-2.5 text-sm">
                                    </div>
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">Bandwidth</FormLabel>
                                        <select v-model="sub.bandwidth" class="block w-full rounded-lg border p-2.5 text-sm">
                                            <option v-for="bandwidth in RNodeInterfaceDefaults.bandwidths" :value="bandwidth">{{ bandwidth / 1000 }} KHz</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="flex gap-2">
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">Spreading Factor</FormLabel>
                                        <select v-model.number="sub.spreadingfactor" class="w-full rounded-lg border p-2.5 text-sm">
                                            <option :key="sf" v-for="sf in RNodeInterfaceDefaults.spreadingfactors" :value="sf">{{ sf }}</option>
                                        </select>
                                    </div>
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">Coding Rate</FormLabel>
                                        <select v-model.number="sub.codingrate" class="w-full rounded-lg border p-2.5 text-sm">
                                            <option :key="cr" v-for="cr in RNodeInterfaceDefaults.codingrates" :value="cr">{{ cr }} (LoRa 4/{{ cr }})</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="flex gap-2 items-center">
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">TX Power (dBm)</FormLabel>
                                        <input
                                            v-model.number="sub.txpower"
                                            type="number"
                                            class="w-full rounded-lg border p-2.5 text-sm">
                                    </div>
                                    <div class="flex-1">
                                        <FormLabel class="mb-1">Virtual Port</FormLabel>
                                        <input
                                            v-model.number="sub.vport"
                                            type="number"
                                            class="w-full rounded-lg border p-2.5 text-sm">
                                    </div>
                                </div>

                                <button @click="removeSubInterface(idx)" type="button" class="bg-red-500 hover:bg-red-400 text-white text-sm p-2 rounded-lg">Remove Sub-Interface</button>

                            </div>
                            <button @click="addSubInterface" type="button" class="bg-green-500 hover:bg-green-400 text-white text-sm px-4 py-2 rounded-lg">Add Sub-Interface</button>
                        </div>
                    </div>

                    <!-- Serial, KISS, and AX25Kiss -->
                    <div v-if="['SerialInterface', 'KISSInterface', 'AX25KISSInterface'].includes(newInterfaceType)" class="mb-4">

                        <div class="mb-2">
                            <FormLabel class="mb-1">Port</FormLabel>
                            <select v-model="newInterfacePort" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option v-for="comport of comports" :value="comport.device">{{ comport.device }} (Product: {{ comport.product ?? '?' }}, Serial: {{ comport.serial ?? '?' }})</option>
                            </select>
                            <FormSubLabel>
                                <div @click="loadComports" class="text-blue-500 underline cursor-pointer">Reload Ports</div>
                            </FormSubLabel>
                        </div>

                        <div class="mb-2">
                            <FormLabel class="mb-1">Serial connection baud rate (bps)</FormLabel>
                            <input v-model="newInterfaceSpeed" placeholder="9600" type="number" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                        <div class="mb-2">
                            <FormLabel class="mb-1">Databits</FormLabel>
                            <input v-model="newInterfaceDatabits" type="number" placeholder="8" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                        <div class="mb-2">
                            <FormLabel class="mb-1">Parity</FormLabel>
                            <select v-model="newInterfaceParity" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option :value="undefined">None</option>
                                <option value="even">Even</option>
                                <option value="odd">Odd</option>
                            </select>
                        </div>

                        <div>
                            <FormLabel class="mb-1">Stopbits</FormLabel>
                            <input v-model="newInterfaceStopbits" type="number" placeholder="1" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                    </div>

                    <!-- KISS and AX.25 KISS -->
                    <div v-if="['KISSInterface', 'AX25KISSInterface'].includes(newInterfaceType)" class="mb-4">

                        <div class="flex items-center mb-2">
                            <input
                                id="use-ax25"
                                type="checkbox"
                                :checked="newInterfaceType === 'AX25KISSInterface'"
                                @click="useKISSAX25"
                                class="size-5 rounded border text-blue-600"
                            />
                            <FormLabel for="use-ax25" class="ml-2">Enable AX.25 Framing</FormLabel>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <FormLabel class="mb-1">Preamble (milliseconds)</FormLabel>
                                <input
                                    v-model="this.newInterfacePreamble"
                                    type="number"
                                    placeholder="150"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div>
                                <FormLabel class="mb-1">TX Tail (milliseconds)</FormLabel>
                                <input
                                    v-model="this.newInterfaceTXTail"
                                    type="number"
                                    placeholder="10"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div>
                                <FormLabel class="mb-1">CDMA Persistence (milliseconds)</FormLabel>
                                <input
                                    v-model="this.newInterfacePersistence"
                                    type="number"
                                    placeholder="200"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div>
                                <FormLabel class="mb-1">CDMA Slot Time (milliseconds)</FormLabel>
                                <input
                                    v-model="this.newInterfaceSlotTime"
                                    type="number"
                                    placeholder="20"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 mt-4">
                            <div class="flex-1">
                                <FormLabel class="mb-1">SSID</FormLabel>
                                <input
                                    type="text"
                                    value="0"
                                    v-model="newInterfaceSSID"
                                    placeholder="Enter SSID"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Callsign</FormLabel>
                                <input
                                    type="text"
                                    v-model="newInterfaceCallsign"
                                    placeholder="Enter callsign"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Callsign ID Interval</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceIDInterval"
                                    placeholder="Enter interval (seconds)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                    </div>

                    <!-- Pipe Interface -->
                    <div v-if="newInterfaceType === 'PipeInterface'" class="mb-2">

                        <div class="text-sm text-[var(--ct-dim)] mb-3">ⓘ Using this interface, Reticulum can use any program as an interface via stdin and stdout. This can be usedto easily create virtual interfaces, or to interface with custom hardware or other systems.</div>

                        <div class="mb-2">
                            <FormLabel class="mb-1">Command</FormLabel>
                            <input type="text" placeholder="e.g: netcat -l 5757" v-model="newInterfaceCommand" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                        <div>
                            <FormLabel class="mb-1">Respawn Delay (seconds)</FormLabel>
                            <input type="number" placeholder="5" v-model="newInterfaceRespawnDelay" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                    </div>

                </div>
            </div>

            <!-- RNodeInterface bitrate & link budget -->
            <ExpandingSection v-if="newInterfaceType === 'RNodeInterface'">
                <template v-slot:title>Calculated RNode Bitrate & Link Budget</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div>
                            <FormLabel class="mb-1">Antenna Gain (dBi)</FormLabel>
                            <input
                                type="number"
                                v-model.number="RNodeInterfaceLoRaParameters.antennaGain"
                                placeholder="Enter gain"
                                class="block w-full rounded-lg border p-2.5 text-sm"
                            />
                            <p class="text-xs text-[var(--ct-dim)] mt-1">ⓘ A stub or PCB antenna might have around 1 dBi of gain, where a directional Yagi might have 5 dBi of gain.</p>
                        </div>

                        <div>
                            <FormLabel class="mb-1">On-Air Calculations</FormLabel>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-center">
                                <div class="ct-elevated-surface rounded-lg border border-[var(--ct-border)] p-3">
                                    <div class="text-sm font-medium text-[var(--ct-dim)]">Sensitivity</div>
                                    <div class="text-xl font-bold text-[var(--ct-text)]">{{ RNodeInterfaceLoRaParameters.sensitivity ?? "???" }}</div>
                                </div>
                                <div class="ct-elevated-surface rounded-lg border border-[var(--ct-border)] p-3">
                                    <div class="text-sm font-medium text-[var(--ct-dim)]">Data Rate</div>
                                    <div class="text-xl font-bold text-[var(--ct-text)]">{{ RNodeInterfaceLoRaParameters.dataRate ?? "???" }}</div>
                                </div>
                                <div class="ct-elevated-surface rounded-lg border border-[var(--ct-border)] p-3">
                                    <div class="text-sm font-medium text-[var(--ct-dim)]">Link Budget</div>
                                    <div class="text-xl font-bold text-[var(--ct-text)]">{{ RNodeInterfaceLoRaParameters.linkBudget ?? "???" }}</div>
                                </div>
                            </div>
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional AutoInterface settings -->
            <ExpandingSection v-if="newInterfaceType === 'AutoInterface'">
                <template v-slot:title>Optional AutoInterface Settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div class="flex-1">
                            <FormLabel class="mb-1">Group ID</FormLabel>
                            <input
                                type="text"
                                v-model="newInterfaceGroupID"
                                placeholder="reticulum"
                                class="block w-full rounded-lg border p-2.5 text-sm"
                            />
                        </div>

                        <div class="flex-1">
                            <FormLabel class="mb-1">Multicast Address Type</FormLabel>
                            <select v-model="newInterfaceMulticastAddressType" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option :value="undefined">(not set)</option>
                                <option value="permanent">Permanent</option>
                                <option value="temporary">Temporary</option>
                            </select>
                        </div>

                        <div class="flex items-center space-x-4 mt-4">
                            <div class="flex-1">
                                <FormLabel class="mb-1">Network devices</FormLabel>
                                <input
                                    type="text"
                                    v-model="newInterfaceDevices"
                                    placeholder="e.g: wlan0,eth1"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Ignored Devices</FormLabel>
                                <input
                                    type="text"
                                    v-model="newInterfaceIgnoredDevices"
                                    placeholder="e.g: tun0,eth0"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 mt-4">
                            <div class="flex-1">
                                <FormLabel class="mb-1">Discovery Scope</FormLabel>
                                <select v-model="newInterfaceDiscoveryScope" class="block w-full rounded-lg border p-2.5 text-sm">
                                    <option :value="undefined">(not set)</option>
                                    <option value="global">Global</option>
                                    <option value="admin">Admin</option>
                                    <option value="organisation">Organisation</option>
                                    <option value="site">Site</option>
                                    <option value="link">Link</option>
                                </select>
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Discovery Port</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceDiscoveryPort"
                                    placeholder="48555"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Data Port</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceDataPort"
                                    placeholder="49555"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional TCPClientInterface settings -->
            <ExpandingSection v-if="usesTCPClientFields">
                <template v-slot:title>Optional TCP Client Settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div class="flex">
                            <div class="flex flex-col mr-auto">
                                <FormLabel for="kiss-framing">Enable KISS Framing</FormLabel>
                                <span class="text-sm text-[var(--ct-dim)]">Enable this when connecting to software that uses KISS framing such as packet radio sound modems. For KISS connections through serial hardware select "KISS Interface" as the interface type.</span>
                            </div>
                            <input id="kiss-framing" type="checkbox" v-model="newInterfaceKISSFramingEnabled" class="my-auto mx-2 size-5 rounded border text-blue-600"/>
                        </div>

                        <div class="flex">
                            <div class="flex flex-col mr-auto">
                                <FormLabel for="i2p-tunneled">Enable I2P tunneling</FormLabel>
                                <span class="text-sm text-[var(--ct-dim)]">Enables tunnelling through an I2P Connection using the TCPClientInterface</span>
                            </div>
                            <input id="i2p-tunneled" type="checkbox" v-model="newInterfaceI2PTunnelingEnabled" class="my-auto mx-2 size-5 rounded border text-blue-600"/>
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional TCPClientInterface settings -->
            <ExpandingSection v-if="newInterfaceType === 'TCPServerInterface'">
                <template v-slot:title>Optional TCPServerInterface settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div>
                            <FormLabel>Network device</FormLabel>
                            <span class="text-sm text-[var(--ct-dim)]">Binds the interface to a specific network interface</span>
                            <input type="text" placeholder="e.g: eth0" v-model="newInterfaceNetworkDevice" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                        <div class="flex items-start">
                            <div class="flex flex-col mr-auto">
                                <FormLabel for="prefer-ipv6">Prefer IPv6</FormLabel>
                                <span class="text-sm text-[var(--ct-dim)]">Binds the TCP Server Interface to an IPv6 address</span>
                            </div>
                            <input
                                id="prefer-ipv6"
                                type="checkbox"
                                value="1"
                                v-model="newInterfacePreferIPV6"
                                class="my-auto mx-2 size-5 rounded border text-blue-600"
                            />
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional UDPInterface settings -->
            <ExpandingSection v-if="newInterfaceType === 'UDPInterface'">
                <template v-slot:title>Optional UDPInterface settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div>
                            <FormLabel>Network device</FormLabel>
                            <span class="text-sm text-[var(--ct-dim)]">Binds the interface to a specific network interface</span>
                            <input type="text" placeholder="e.g: eth0" v-model="newInterfaceNetworkDevice" class="block w-full rounded-lg border p-2.5 text-sm">
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional RNodeInterface settings -->
            <ExpandingSection v-if="newInterfaceType === 'RNodeInterface'">
                <template v-slot:title>Optional RNodeInterface Settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div class="flex items-center space-x-4">
                            <div class="flex-1">
                                <FormLabel class="mb-1">Callsign</FormLabel>
                                <input
                                    type="text"
                                    v-model="newInterfaceCallsign"
                                    placeholder="Enter callsign"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Callsign ID Interval</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceIDInterval"
                                    placeholder="Enter interval (seconds)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                        <div class="flex items-center space-x-4">
                            <div class="flex-1">
                                <FormLabel class="mb-1">Airtime Limit (Short)</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceAirtimeLimitShort"
                                    placeholder="Enter short airtime limit (% of a rolling 15 seconds window)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div class="flex-1">
                                <FormLabel class="mb-1">Airtime Limit (Long)</FormLabel>
                                <input
                                    type="number"
                                    v-model="newInterfaceAirtimeLimitLong"
                                    placeholder="Enter long airtime limit (% of a rolling 60 minutes window)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- optional interface settings -->
            <ExpandingSection v-if="isEditingInterface || newInterfaceType != null">
                <template v-slot:title>Optional Interface Settings</template>
                <template v-slot:content>
                    <div class="p-2 space-y-3">

                        <div>
                            <FormLabel class="mb-1">Interface Mode</FormLabel>
                            <select v-model="sharedInterfaceSettings.mode" class="block w-full rounded-lg border p-2.5 text-sm">
                                <option :value="undefined">(not set)</option>
                                <option value="full">Full</option>
                                <option value="gateway">Gateway</option>
                                <option value="access_point">Access Point</option>
                                <option value="roaming">Roaming</option>
                                <option value="boundary">Boundary</option>
                            </select>
                            <FormSubLabel>
                                This setting requires Transport Mode to be enabled. <a class="text-blue-500 underline" href="https://reticulum.network/manual/interfaces.html#interface-modes" target="_blank">Reticulum Docs: Interface Modes</a>
                            </FormSubLabel>
                        </div>

                        <div>
                            <FormLabel class="mb-1">Inferred Interface Bitrate</FormLabel>
                            <input
                                v-model="sharedInterfaceSettings.bitrate"
                                type="number"
                                placeholder="Enter inferred bitrate"
                                class="block w-full rounded-lg border p-2.5 text-sm"
                            />
                        </div>

                    </div>
                </template>
            </ExpandingSection>

            <!-- ifac settings -->
            <ExpandingSection v-if="isEditingInterface || newInterfaceType != null">
                <template v-slot:title>IFAC Settings</template>
                <template v-slot:content>
                    <div class="p-2">
                        <div class="text-sm text-[var(--ct-dim)] mb-2">ⓘ Interface Access Code settings are used for creating private networks and can be configured on the interface level.</div>
                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-y-2 lg:gap-x-2">
                            <div>
                                <FormLabel class="mb-1">Network Name</FormLabel>
                                <input
                                    v-model="sharedInterfaceSettings.network_name"
                                    type="text"
                                    placeholder="Enter network name"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div>
                                <FormLabel class="mb-1">Passphrase</FormLabel>
                                <input
                                    v-model="sharedInterfaceSettings.passphrase"
                                    type="text"
                                    placeholder="Enter passphrase"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                            <div>
                                <FormLabel class="mb-1">IFAC Size</FormLabel>
                                <input
                                    v-model="sharedInterfaceSettings.ifac_size"
                                    type="number"
                                    min="8"
                                    max="512"
                                    placeholder="Enter size (8-512)"
                                    class="block w-full rounded-lg border p-2.5 text-sm"
                                />
                            </div>
                        </div>
                    </div>
                </template>
            </ExpandingSection>

            <!-- add/save interface button -->
            <div v-if="isEditingInterface || newInterfaceType != null" class="flex justify-end pb-4">
                <button @click="addInterface" type="button" class="ct-brand-button inline-flex items-center gap-x-1.5 rounded-lg px-4 py-2 text-sm font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                    <span>Save Interface</span>
                </button>
            </div>

        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import AutoInterfaceUtils from "../../js/AutoInterfaceUtils";
import DialogUtils from "../../js/DialogUtils";
import ExpandingSection from "./ExpandingSection.vue";
import FormLabel from "../forms/FormLabel.vue";
import FormSubLabel from "../forms/FormSubLabel.vue";
import ElectronUtils from "../../js/ElectronUtils";
import PhosphorIcon from "../PhosphorIcon.vue";

export default {
    name: 'AddInterfacePage',
    components: {
        FormSubLabel,
        FormLabel,
        ExpandingSection,
        PhosphorIcon,
    },
    data() {
        return {

            isEditingInterface: false,

            config: null,
            existingInterfaces: {},

            comports: [],

            // guided picker: plain-language connection types
                        interfaceTypeGroups: [
                            {
                                label: "Recommended",
                                options: [
                                    { type: "PublicBackboneInterface", name: "Public Internet Node", icon: "globe-hemisphere-west", description: "Connect over the internet to a public Reticulum node from rmap.world. The easiest way to get connected." },
                                    { type: "AutoInterface", name: "Local Network (Auto)", icon: "house", description: "Automatically find and connect to other Reticulum peers on your WiFi or Ethernet network." },
                                ],
                            },
                            {
                                label: "Radio Hardware",
                                options: [
                                    { type: "RNodeInterface", name: "RNode (LoRa Radio)", icon: "broadcast", description: "Long-range, off-grid communication using an RNode LoRa radio device." },
                                    { type: "RNodeMultiInterface", name: "RNode Multi", icon: "cell-tower", description: "For devices with multiple LoRa transceivers, such as the openCom XL." },
                                    { type: "IridiumIMTInterface", name: "RockBLOCK 9704 (Iridium)", icon: "planet", description: "Carry native Reticulum packets through Iridium Messaging Transport." },
                                    { type: "SerialInterface", name: "Serial Port", icon: "usb", description: "Connect through a raw serial port to custom hardware." },
                                    { type: "KISSInterface", name: "KISS / Packet Radio", icon: "wifi-high", description: "Connect through KISS-compatible TNCs and packet radio modems." },
                                ],
                            },
                            {
                                label: "Advanced Networking",
                                options: [
                                    { type: "TCPClientInterface", name: "TCP Client", icon: "plugs-connected", description: "Connect to a specific Reticulum TCP server by host and port." },
                                    { type: "TCPServerInterface", name: "TCP Server", icon: "hard-drives", description: "Let other Reticulum peers connect to this device over TCP." },
                                    { type: "UDPInterface", name: "UDP", icon: "share-network", description: "Send and receive Reticulum traffic over UDP broadcast." },
                                    { type: "I2PInterface", name: "I2P", icon: "detective", description: "Route traffic anonymously through the I2P network. Requires a local I2P router." },
                                    { type: "PipeInterface", name: "Program Pipe", icon: "terminal-window", description: "Use any program as an interface via stdin and stdout." },
                                ],
                            },
                        ],

            newInterfaceName: null,
            newInterfaceType: null,
            publicBackboneConfigText: "",
            publicBackboneConfigError: null,

            newInterfaceGroupID: null,
            newInterfaceMulticastAddressType: null,
            newInterfaceDevices: null,
            newInterfaceIgnoredDevices: null,
            newInterfaceDiscoveryScope: null,
            newInterfaceDiscoveryPort: null,
            newInterfaceDataPort: null,

            newInterfaceTargetHost: null,
            newInterfaceTargetPort: null,

            newInterfaceListenIp: null,
            newInterfaceListenPort: null,
            newInterfaceNetworkDevice: null,
            newInterfacePreferIPV6: null,
            newInterfaceKISSFramingEnabled: null,
            newInterfaceI2PTunnelingEnabled: null,

            sharedInterfaceSettings: {
                "mode": null,
                "network_name": null,
                "passphrase": null,
                "ifac_size": null,
            },

            newInterfaceForwardIp: null,
            newInterfaceForwardPort: null,

            I2PSettings: {
                newInterfacePeers: [],
            },

            RNodeMultiInterface: {
                port: null,
                subInterfaces: [],
            },

            iridiumIMTSettings: {
                topic: 244,
                pollInterval: 0.01,
                retryInterval: 600,
                maximumQueuedPackets: 512,
                maximumModemAttempts: 1,
                lxmfRetryInterval: 600,
                lxmfMaxAttempts: 1,
            },

            newInterfacePort: null,
            RNodeGHzValue: 0,
            RNodeMHzValue: 0,
            RNodekHzValue: 0,
            newInterfaceFrequency: null,
            newInterfaceBandwidth: null,
            newInterfaceTxpower: null,
            newInterfaceSpreadingFactor: null,
            newInterfaceCodingRate: null,

            // Serial, KISS, and AX25KISS options
            newInterfaceSpeed: null,
            newInterfaceDatabits: null,
            newInterfaceParity: null,
            newInterfaceStopbits: null,

            // KISS and AX25KISS
            newInterfacePreamble: null,
            newInterfaceTXTail: null,
            newInterfacePersistence: null,
            newInterfaceSlotTime: null,

            // RNode and KISS
            newInterfaceCallsign: null,
            newInterfaceIDInterval: null,
            newInterfaceFlowControl: null,
            newInterfaceAirtimeLimitLong: null,
            newInterfaceAirtimeLimitShort: null,

            // Pipe interface
            newInterfaceCommand: null,
            newInterfaceRespawnDelay: null,

            RNodeInterfaceDefaults: {
                // bandwidth in hz
                bandwidths: [
                    7800, // 7.8 kHz
                    10400, // 10.4 kHz
                    15600, // 15.6 kHz
                    20800, // 20.8 kHz
                    31250, // 31.25 kHz
                    41700, // 41.7 kHz
                    62500, // 62.5 kHz
                    125000, // 125 kHz
                    250000, // 250 kHz
                    500000, // 500 kHz
                    1625000, // 1625 kHz (for 2.4 GHz SX1280)
                ],
                codingrates: [
                    5, // 4:5
                    6, // 4:6
                    7, // 4:7
                    8, // 4:8
                ],
                spreadingfactors: [
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                ],
            },

            RNodeInterfaceLoRaParameters: {
                antennaGain: 0,
                noiseFloor: 5,
                sensitivity: null,
                dataRate: null,
                linkBudget: null,
            },

        };
    },
    computed: {
        formattedFrequency() {
            const totalHz = this.calculateFrequencyInHz();
            if(totalHz >= 1e9){
                return `${(totalHz / 1e9).toFixed(3)} GHz`;
            } else if(totalHz >= 1e6) {
                return `${(totalHz / 1e6).toFixed(3)} MHz`;
            } else if(totalHz >= 1e3) {
                return `${(totalHz / 1e3).toFixed(3)} kHz`;
            }
            return `${totalHz} Hz`;
        },
        interfaceTypeForSave() {
            if(this.newInterfaceType === 'PublicBackboneInterface'){
                return 'TCPClientInterface';
            }
            return this.newInterfaceType;
        },
        usesTCPClientFields() {
            return this.interfaceTypeForSave === 'TCPClientInterface';
        },
        selectedTypeOption() {
            for(const group of this.interfaceTypeGroups){
                const option = group.options.find((option) => option.type === this.newInterfaceType);
                if(option){
                    return option;
                }
            }
            // AX25KISSInterface is toggled from the KISS form, show it as KISS
            if(this.newInterfaceType === "AX25KISSInterface"){
                return { type: "AX25KISSInterface", name: "AX.25 KISS / Packet Radio", icon: "wifi-high", description: "Connect through KISS-compatible TNCs with AX.25 framing." };
            }
            return null;
        },
        enabledAutoInterfaces() {
            const excludeName = this.isEditingInterface ? this.newInterfaceName : null;
            return AutoInterfaceUtils.enabledAutoInterfaces(this.existingInterfaces, excludeName);
        },
        enabledAutoInterfaceNames() {
            return this.enabledAutoInterfaces.map((iface) => `"${iface._name}"`).join(", ");
        },
    },
    watch: {
        newInterfaceBandwidth: "updateRNodeCalculations",
        newInterfaceSpreadingFactor: "updateRNodeCalculations",
        newInterfaceCodingRate: "updateRNodeCalculations",
        newInterfaceTxpower: "updateRNodeCalculations",
        'RNodeInterfaceLoRaParameters.antennaGain': "updateRNodeCalculations",
    },
    mounted() {

        this.getConfig();
        this.loadComports();
        this.loadExistingInterfaces();

        // check if we are editing an interface
        const interfaceName = this.$route.query.interface_name;
        if(interfaceName != null){
            this.isEditingInterface = true;
            this.loadInterfaceToEdit(interfaceName);
            return;
        }

        const interfaceType = this.$route.query.interface_type;
        if(typeof interfaceType === "string" && interfaceType !== ""){
            this.newInterfaceType = interfaceType;
        }

    },
    methods: {
        async getConfig() {
            try {
                const response = await window.axios.get(`/api/v1/config`);
                this.config = response.data.config;
            } catch (e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        async updateConfig(config) {
            try {
                const response = await window.axios.patch("/api/v1/config", config);
                this.config = response.data.config;
            } catch (e) {
                DialogUtils.toast("Failed to save config", "error");
                console.log(e);
            }
        },
        alreadyEnabledNoticeForType(interfaceType) {
            if(interfaceType !== "AutoInterface" || this.enabledAutoInterfaces.length === 0){
                return null;
            }
            if(this.enabledAutoInterfaces.length === 1){
                return `Already on as ${this.enabledAutoInterfaces[0]._name}`;
            }
            return `Already on as ${this.enabledAutoInterfaces.map((iface) => iface._name).join(", ")}`;
        },
        editExistingInterface(interfaceName) {
            this.$router.push({
                name: "interfaces.edit",
                query: {
                    interface_name: interfaceName,
                },
            });
        },
        async loadExistingInterfaces() {
            try {
                const response = await window.axios.get(`/api/v1/reticulum/interfaces`);
                this.existingInterfaces = response.data.interfaces ?? {};
            } catch(e) {
                console.log(e);
            }
        },
        async loadComports() {
            try {
                const response = await window.axios.get(`/api/v1/comports`);
                this.comports = response.data.comports;
            } catch (e) {
                // do nothing if failed to load interfaces
            }
        },
        async loadInterfaceToEdit(interfaceName) {
            try {

                // fetch interfaces
                const response = await window.axios.get(`/api/v1/reticulum/interfaces`);
                const interfaces = response.data.interfaces;
                this.existingInterfaces = interfaces ?? {};

                // find interface, else show error and redirect to interfaces
                const iface = interfaces[interfaceName];
                if (!iface) {
                    DialogUtils.alert("The selected interface for editing could not be found.");
                    this.$router.push({
                        "name": "interfaces",
                    });
                    return;
                }

                // set form values
                this.newInterfaceName = interfaceName;
                this.newInterfaceType = iface.type;

                // AutoInterface additional settings
                this.newInterfaceGroupID = iface.group_id;
                this.newInterfaceMulticastAddressType = iface.multicast_address_type;
                this.newInterfaceDevices = iface.devices;
                this.newInterfaceIgnoredDevices = iface.ignored_devices;
                this.newInterfaceDiscoveryScope = iface.discovery_scope;
                this.newInterfaceDiscoveryPort = iface.discovery_port;
                this.newInterfaceDataPort = iface.data_port;

                // tcp client interface
                this.newInterfaceTargetHost = iface.target_host;
                this.newInterfaceTargetPort = iface.target_port;

                if (iface.kiss_framing) {
                    this.newInterfaceKISSFramingEnabled = true;
                }
                if (iface.i2p_tunneled) {
                    this.newInterfaceI2PTunnelingEnabled = true;
                }
                if (iface.prefer_ipv6) {
                    this.newInterfacePreferIPV6 = true;
                }


                // tcp server interface & udp interface
                this.newInterfaceNetworkDevice = iface.device;
                this.newInterfaceListenIp = iface.listen_ip;
                this.newInterfaceListenPort = iface.listen_port;

                // I2P Interface
                if(iface.peers){
                    const peersToAdd = iface.peers.split(',');
                    for(const address of peersToAdd){
                        this.addI2PPeer(address);
                    }
                }

                // udp interface
                this.newInterfaceForwardIp = iface.forward_ip;
                this.newInterfaceForwardPort = iface.forward_port;

                // Port (For RNode, Serial, and KISS)
                this.newInterfacePort = iface.port;

                // RockBLOCK 9704 / Iridium IMT
                this.iridiumIMTSettings.topic = iface.topic ?? 244;
                this.iridiumIMTSettings.pollInterval = iface.poll_interval ?? 0.01;
                this.iridiumIMTSettings.retryInterval = iface.retry_interval ?? 600;
                this.iridiumIMTSettings.maximumQueuedPackets = iface.maximum_queued_packets ?? 512;
                this.iridiumIMTSettings.maximumModemAttempts = iface.maximum_modem_attempts ?? 1;
                this.iridiumIMTSettings.lxmfRetryInterval = iface.lxmf_retry_interval ?? 600;
                this.iridiumIMTSettings.lxmfMaxAttempts = iface.lxmf_max_attempts ?? 1;

                // RNode Interface
                this.newInterfaceFrequency = iface.frequency;
                this.RNodeGHzValue = Math.floor(iface.frequency / 1e9);
                this.RNodeMHzValue = Math.floor((iface.frequency % 1e9) / 1e6);
                this.RNodekHzValue = Math.floor((iface.frequency % 1e6) / 1e3);
                this.newInterfaceBandwidth = iface.bandwidth;
                this.newInterfaceTxpower = iface.txpower;
                this.newInterfaceSpreadingFactor = iface.spreadingfactor;
                this.newInterfaceCodingRate = iface.codingrate;

                // RNode Multi Interface
                this.RNodeMultiInterface.subInterfaces = iface.sub_interfaces;

                // Serial, KISS, and AX25KISS
                this.newInterfaceSpeed = iface.speed;
                this.newInterfaceDatabits = iface.databits;
                this.newInterfaceParity = iface.parity;
                this.newInterfaceStopbits = iface.stopbits;

                this.newInterfacePreamble = iface.preamble;
                this.newInterfaceTXTail = iface.txtail;
                this.newInterfacePersistence = iface.persistence;
                this.newInterfaceSlotTime = iface.slottime;

                this.newInterfaceCallsign = iface.callsign;
                this.newInterfaceIDInterval = iface.id_interval;
                this.newInterfaceSSID = iface.ssid;

                // Airtime limit
                this.newInterfaceAirtimeLimitLong = iface.airtime_limit_long;
                this.newInterfaceAirtimeLimitShort = iface.airtime_limit_short;

                // Pipe Interface
                this.newInterfaceCommand = iface.command;
                this.newInterfaceRespawnDelay = iface.respawn_delay;

                // Shared interface settings
                this.sharedInterfaceSettings.mode = iface.mode;
                this.sharedInterfaceSettings.bitrate = iface.bitrate;
                this.sharedInterfaceSettings.network_name = iface.network_name;
                this.sharedInterfaceSettings.passphrase = iface.passphrase;
                this.sharedInterfaceSettings.ifac_size = iface.ifac_size;

            } catch (e) {
                // do nothing if failed to load interfaces
            }
        },
        async addInterface() {
            try {

                if(this.newInterfaceType === "AutoInterface"){
                    const conflicting = AutoInterfaceUtils.conflictingEnabledAutoInterface(
                        this.existingInterfaces,
                        {
                            group_id: this.newInterfaceGroupID,
                            discovery_port: this.newInterfaceDiscoveryPort,
                            data_port: this.newInterfaceDataPort,
                        },
                        this.isEditingInterface ? this.newInterfaceName : null,
                    );
                    if(conflicting){
                        const shouldSave = await DialogUtils.confirm(
                            `"${conflicting._name}" is already providing local discovery on the same group and ports. Saving another copy will likely fail until one of them is turned off. Save anyway?`,
                            { title: "Local discovery already enabled", confirmLabel: "Save anyway" },
                        );
                        if(!shouldSave){
                            return;
                        }
                    }
                }

                // process sub interfaces for RNodeMultiInterface
                let subInterfacesData = null;
                if(this.newInterfaceType === 'RNodeMultiInterface'){
                    subInterfacesData = this.RNodeMultiInterface.subInterfaces.map((subInterface) => {
                        return {
                            name: subInterface.name,
                            frequency: subInterface.frequency,
                            bandwidth: subInterface.bandwidth,
                            txpower: subInterface.txpower,
                            spreadingfactor: subInterface.spreadingfactor,
                            codingrate: subInterface.codingrate,
                            vport: subInterface.vport,
                        };
                    });
                }

                // add interface
                const response = await window.axios.post(`/api/v1/reticulum/interfaces/add`, {

                    allow_overwriting_interface: this.isEditingInterface,

                    // required values
                    name: this.newInterfaceName,
                    type: this.interfaceTypeForSave,

                    // AutoInterface
                    group_id: this.newInterfaceGroupID,
                    multicast_address_type: this.newInterfaceMulticastAddressType,
                    devices: this.newInterfaceDevices,
                    ignored_devices: this.newInterfaceIgnoredDevices,
                    discovery_scope: this.newInterfaceDiscoveryScope,
                    discovery_port: this.newInterfaceDiscoveryPort,
                    data_port: this.newInterfaceDataPort,

                    // tcp client interface
                    target_host: this.newInterfaceTargetHost,
                    target_port: this.newInterfaceTargetPort,

                    // TCP Client & Server interface
                    kiss_framing: this.newInterfaceKISSFramingEnabled,
                    i2p_tunneled: this.newInterfaceI2PTunnelingEnabled,

                    // tcp server interface & udp interface
                    listen_ip: this.newInterfaceListenIp,
                    listen_port: this.newInterfaceListenPort,
                    device: this.newInterfaceNetworkDevice,
                    prefer_ipv6: this.newInterfacePreferIPV6,

                    // udp interface
                    forward_ip: this.newInterfaceForwardIp,
                    forward_port: this.newInterfaceForwardPort,

                    //  I2P Interface
                    peers: this.I2PSettings.newInterfacePeers.join(','),

                    // rnode interface
                    port: this.newInterfacePort,
                    frequency: this.calculateFrequencyInHz(),
                    bandwidth: this.newInterfaceBandwidth,
                    txpower: this.newInterfaceTxpower,
                    spreadingfactor: this.newInterfaceSpreadingFactor,
                    codingrate: this.newInterfaceCodingRate,

                    // RockBLOCK 9704 / Iridium IMT
                    topic: this.iridiumIMTSettings.topic,
                    poll_interval: this.iridiumIMTSettings.pollInterval,
                    retry_interval: this.iridiumIMTSettings.retryInterval,
                    maximum_queued_packets: this.iridiumIMTSettings.maximumQueuedPackets,
                    maximum_modem_attempts: this.iridiumIMTSettings.maximumModemAttempts,
                    lxmf_retry_interval: this.iridiumIMTSettings.lxmfRetryInterval,
                    lxmf_max_attempts: this.iridiumIMTSettings.lxmfMaxAttempts,

                    // RNode Multi Interface
                    sub_interfaces: subInterfacesData,

                    // Seiral, KISS, and AX25KISS
                    speed: this.newInterfaceSpeed,
                    databits: this.newInterfaceDatabits,
                    parity: this.newInterfaceParity,
                    stopbits: this.newInterfaceStopbits,

                    // KISS and AX25KISS
                    preamble: this.newInterfacePreamble,
                    txtail: this.newInterfaceTXTail,
                    persistence: this.newInterfacePersistence,
                    slottime: this.newInterfaceSlotTime,

                    callsign: this.newInterfaceCallsign,
                    id_interval: this.newInterfaceIDInterval,
                    ssid: this.newInterfaceSSID,

                    // Pipe interface
                    command: this.newInterfaceCommand,
                    respawn_delay: this.newInterfaceRespawnDelay,

                    // Airtime limit
                    airtime_limit_long: this.newInterfaceAirtimeLimitLong,
                    airtime_limit_short: this.newInterfaceAirtimeLimitShort,

                    // settings that can be added to any interface type
                    mode: this.sharedInterfaceSettings.mode,
                    bitrate: this.sharedInterfaceSettings.bitrate,
                    network_name: this.sharedInterfaceSettings.network_name,
                    passphrase: this.sharedInterfaceSettings.passphrase,
                    ifac_size: this.sharedInterfaceSettings.ifac_size,

                });

                await ElectronUtils.restartBackend("#/interfaces");
                return;

            } catch (e) {
                const message = e.response?.data?.message ?? "Failed to save interface.";
                DialogUtils.alert(message, { title: "Could Not Save" });
                console.log(e);
            }

        },
        formatFrequency(hz) {
            return Utils.formatFrequency(hz);
        },
        calculateFrequencyInHz() {
            const ghzToHz = this.RNodeGHzValue * 1e9;
            const mhzToHz = this.RNodeMHzValue * 1e6;
            const khzToHz = this.RNodekHzValue * 1e3;
            return ghzToHz + mhzToHz + khzToHz;
        },
        updateRNodeCalculations() {
            this.calculateRNodeParameters(
                this.newInterfaceBandwidth,
                this.newInterfaceSpreadingFactor,
                this.newInterfaceCodingRate,
                this.RNodeInterfaceLoRaParameters.noiseFloor,
                this.RNodeInterfaceLoRaParameters.antennaGain,
                this.newInterfaceTxpower
            );
        },
        calculateRNodeParameters(bandwidth, spreadingFactor, codingRate, noiseFloor, antennaGain, transmitPower) {

            // https://unsigned.io/understanding-lora-parameters/
            // "SX1272/3/6/7/8 LoRa Modem Design Guide" https://www.openhacks.com/uploadsproductos/loradesignguide_std.pdf
            // 4:5 - 4:8
            const crn = {
                5: 1,
                6: 2,
                7: 3,
                8: 4,
            };

            codingRate = crn[codingRate];

            const sfn = {
                5: -2.5,
                6: -5,
                7: -7.5,
                8: -10,
                9: -12.5,
                10: -15,
                11: -17.5,
                12: -20
            };

            let dataRate = spreadingFactor * ((4 / (4 + codingRate)) / (Math.pow(2, spreadingFactor) / (bandwidth / 1000))) * 1000;

            let sensitivity = -174 + 10 * Math.log10(bandwidth) + noiseFloor + (sfn[spreadingFactor] || 0);

            if(bandwidth === 203125 || bandwidth === 406250 || bandwidth > 500000){
                sensitivity = -165.6 + 10 * Math.log10(bandwidth) + noiseFloor + (sfn[spreadingFactor] || 0);
            }

            let linkBudget = (transmitPower - sensitivity) + antennaGain;
            this.RNodeInterfaceLoRaParameters.dataRate = dataRate < 1000
                ? `${dataRate.toFixed(0)} bps`
                : `${(dataRate / 1000).toFixed(2)} kbps`;
            this.RNodeInterfaceLoRaParameters.linkBudget = `${linkBudget.toFixed(1)} dB`;
            this.RNodeInterfaceLoRaParameters.sensitivity = `${sensitivity.toFixed(1)} dBm`;

        },
        addI2PPeer(address = "") {
            this.I2PSettings.newInterfacePeers.push(address);
        },
        removeI2PPeer(index) {
            this.I2PSettings.newInterfacePeers.splice(index, 1);
        },
        usePublicBackboneInterface(name, host, port) {
            this.newInterfaceName = name;
            this.newInterfaceType = 'PublicBackboneInterface';
            this.newInterfaceTargetHost = host;
            this.newInterfaceTargetPort = port;
            this.newInterfaceKISSFramingEnabled = null;
            this.newInterfaceI2PTunnelingEnabled = null;
        },
        usePublicBackboneConfig() {
            this.publicBackboneConfigError = null;

            const config = this.publicBackboneConfigText ?? "";
            const sectionName = config.match(/\[\[([^\]]+)\]\]/)?.[1];
            const type = config.match(/^\s*type\s*=\s*(.+?)\s*$/mi)?.[1]?.trim();
            const remote = config.match(/^\s*remote\s*=\s*(.+?)\s*$/mi)?.[1]?.trim();
            const targetPort = config.match(/^\s*target_port\s*=\s*(.+?)\s*$/mi)?.[1]?.trim();

            if(type !== "BackboneInterface"){
                this.publicBackboneConfigError = "Paste a BackboneInterface block from rmap.world.";
                return;
            }

            if(!remote || !targetPort){
                this.publicBackboneConfigError = "The block must include remote and target_port values.";
                return;
            }

            const fallbackName = remote
                .replace(/[^a-z0-9]+/gi, " ")
                .trim()
                .replace(/\s+/g, " ");

            const name = (sectionName ?? fallbackName)
                .replace(/^_+|_+$/g, "")
                .replace(/_+/g, " ")
                .trim() || fallbackName;

            this.usePublicBackboneInterface(name, remote, targetPort);
        },
        addSubInterface() {
            this.RNodeMultiInterface.subInterfaces.push({
                name: '',
                frequency: null,
                bandwidth: null,
                txpower: null,
                spreadingfactor: null,
                codingrate: null,
                vport: null,
            });
        },
        useKISSAX25() {
            if(this.newInterfaceType === 'AX25KISSInterface'){
                this.newInterfaceType = "KISSInterface";
            } else {
                this.newInterfaceType = 'AX25KISSInterface';
            }
        },
        removeSubInterface(idx) {
            this.RNodeMultiInterface.subInterfaces.splice(idx, 1);
        },
    },
}
</script>
