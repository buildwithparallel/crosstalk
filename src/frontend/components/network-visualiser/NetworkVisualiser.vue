<template>
    <div class="network-map relative h-full min-w-full flex-1 overflow-hidden sm:min-w-[500px]">
        <div class="network-map-grid pointer-events-none absolute inset-0"></div>

        <!-- network -->
        <div id="network" class="relative z-0 h-full w-full"></div>

        <!-- title, status and controls -->
        <div class="pointer-events-none absolute inset-x-0 top-0 z-10 p-3">
            <div class="network-toolbar pointer-events-auto mx-auto flex max-w-6xl flex-wrap items-center gap-3 rounded-2xl border border-white/10 px-3 py-2.5 shadow-2xl">
                <div class="flex min-w-52 items-center gap-2.5">
                    <div class="flex size-9 shrink-0 items-center justify-center rounded-xl border border-blue-400/25 bg-blue-500/10 text-[#7db0ff] shadow-[0_0_24px_rgba(0,97,253,0.16)]">
                        <PhosphorIcon name="graph" weight="duotone" class="size-5"/>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 class="text-sm font-bold tracking-wide text-[var(--ct-text)]">Network Map</h1>
                            <span class="inline-flex items-center gap-1 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em] text-emerald-300">
                                <span class="size-1.5 rounded-full bg-emerald-300 shadow-[0_0_8px_rgba(110,231,183,0.8)]"></span>
                                Live
                            </span>
                        </div>
                        <div class="text-xs text-[var(--ct-dim)]">Reticulum topology visible to this device</div>
                    </div>
                </div>

                <div class="flex flex-1 flex-wrap items-center gap-1.5 md:justify-center">
                    <div class="network-stat">
                        <span class="size-1.5 rounded-full bg-[#2ee781]"></span>
                        <strong>{{ onlineInterfaces.length }}</strong>
                        <span>online</span>
                    </div>
                    <div v-if="offlineInterfaces.length > 0" class="network-stat">
                        <span class="size-1.5 rounded-full bg-[#ff5c72]"></span>
                        <strong>{{ offlineInterfaces.length }}</strong>
                        <span>offline</span>
                    </div>
                    <div class="network-stat">
                        <strong>{{ peopleCount }}</strong>
                        <span>people</span>
                    </div>
                    <div class="network-stat">
                        <strong>{{ nomadNodeCount }}</strong>
                        <span>pages</span>
                    </div>
                    <div v-if="infrastructureCount > 0" class="network-stat">
                        <strong>{{ infrastructureCount }}</strong>
                        <span>infrastructure</span>
                    </div>
                </div>

                <div class="ml-auto flex items-center gap-1.5">
                    <button
                        @click="autoReload = !autoReload"
                        type="button"
                        class="network-control gap-1.5 px-2.5"
                        :class="autoReload ? 'border-blue-400/35 bg-blue-500/15 text-[#9cc2ff]' : ''"
                        :title="autoReload ? 'Turn off automatic refresh' : 'Refresh automatically every 5 seconds'">
                        <span class="relative flex h-2 w-2">
                            <span v-if="autoReload" class="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-300 opacity-50"></span>
                            <span class="relative inline-flex h-2 w-2 rounded-full" :class="autoReload ? 'bg-blue-300' : 'bg-[var(--ct-dim)]'"></span>
                        </span>
                        <span class="hidden text-xs font-semibold lg:inline">Auto</span>
                    </button>
                    <button @click="zoomOut" type="button" class="network-control" title="Zoom out" aria-label="Zoom out">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" d="M5 12h14"/>
                        </svg>
                    </button>
                    <button @click="fitNetwork" type="button" class="network-control" title="Fit network to view" aria-label="Fit network to view">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3.75h-3a1.5 1.5 0 0 0-1.5 1.5v3m16.5 0v-3a1.5 1.5 0 0 0-1.5-1.5h-3m0 16.5h3a1.5 1.5 0 0 0 1.5-1.5v-3m-16.5 0v3a1.5 1.5 0 0 0 1.5 1.5h3"/>
                        </svg>
                    </button>
                    <button @click="zoomIn" type="button" class="network-control" title="Zoom in" aria-label="Zoom in">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" d="M12 5v14M5 12h14"/>
                        </svg>
                    </button>
                    <button @click="refresh" type="button" class="network-control ml-1 border-blue-400/30 bg-blue-500/10 text-[#9cc2ff]" title="Refresh network" aria-label="Refresh network">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4" :class="{ 'animate-spin': isUpdating }">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <div class="pointer-events-none absolute bottom-0 right-0 z-10 hidden p-3 text-[10px] text-[var(--ct-dim)] md:block">
            Drag to pan · Scroll to zoom · Double-click people or pages to open
        </div>

        <div v-if="isUpdating && nodes.length === 0" class="pointer-events-none absolute inset-0 z-20 flex items-center justify-center">
            <div class="network-toolbar flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-xs text-[var(--ct-muted)] shadow-xl">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="size-4 animate-spin text-[#7db0ff]">
                    <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" opacity=".25"/>
                    <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                Mapping the network…
            </div>
        </div>
    </div>
</template>

<script>
import "vis-network/styles/vis-network.css";
import { Network } from "vis-network";
import { DataSet } from "vis-data";
import Utils from "../../js/Utils";
import { infrastructureIconDataUri } from "../../js/InfrastructureIcons";
import { getPhosphorPath } from "../../js/PhosphorIcons";
import PhosphorIcon from "../PhosphorIcon.vue";
export default {
    name: 'NetworkVisualiser',
    components: {
        PhosphorIcon,
    },
    data() {
        return {
            config: null,
            autoReload: false,
            reloadInterval: null,
            isUpdating: false,
            interfaces: [],
            discoveredInterfaces: [],
            pathTable: [],
            announces: {},
            network: null,
            nodes: new DataSet(),
            edges: new DataSet(),
        };
    },
    beforeUnmount() {
        clearInterval(this.reloadInterval);
    },
    mounted() {
        this.init();
    },
    methods: {
        // deterministic identicon svg data-uri, same algorithm as Identicon.vue
        identiconDataUri(hash) {

            // cached per hash so vis-network doesn't re-decode on every update
            this._identiconCache = this._identiconCache ?? {};
            if(this._identiconCache[hash]){
                return this._identiconCache[hash];
            }

            const palettes = [
                ["#0061fd", "#7db0ff", "#0c1220"],
                ["#2ee781", "#9ff5c6", "#0b1a13"],
                ["#ff9900", "#ffc266", "#1d1408"],
                ["#b779ff", "#dcbcff", "#160f22"],
                ["#22d3ee", "#a5f3fc", "#082026"],
                ["#ff5c8a", "#ffadc4", "#220d14"],
                ["#8da2fb", "#c7d2fe", "#10142a"],
                ["#f4e04d", "#faf0a0", "#1e1b08"],
            ];

            // mulberry32 prng seeded from the hash string
            let seed = 0;
            const value = String(hash ?? "");
            for(let i = 0; i < value.length; i++){
                seed = Math.imul(seed ^ value.charCodeAt(i), 2654435761);
            }
            seed = seed >>> 0;
            const random = function() {
                seed |= 0;
                seed = (seed + 0x6D2B79F5) | 0;
                let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
                t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
                return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
            };

            // draw into a real pixel canvas rather than a 5x5 one. an svg sized only by
            // its grid has a 5px intrinsic size, so the canvas scaled it up to the node
            // size and it rendered blurry.
            const grid = 5;
            const cell = 64;
            const size = grid * cell;

            const [primary, accent, background] = palettes[Math.floor(random() * palettes.length)];
            let rects = "";
            const half = Math.ceil(grid / 2);
            for(let y = 0; y < grid; y++){
                for(let x = 0; x < half; x++){
                    const roll = random();
                    let colour = null;
                    if(roll < 0.44) colour = primary;
                    else if(roll < 0.58) colour = accent;
                    if(colour){
                        rects += `<rect x="${x * cell}" y="${y * cell}" width="${cell}" height="${cell}" fill="${colour}"/>`;
                        const mirrorX = grid - 1 - x;
                        if(mirrorX !== x){
                            rects += `<rect x="${mirrorX * cell}" y="${y * cell}" width="${cell}" height="${cell}" fill="${colour}"/>`;
                        }
                    }
                }
            }

            const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" shape-rendering="crispEdges"><rect width="${size}" height="${size}" fill="${background}"/>${rects}</svg>`;
            const dataUri = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
            this._identiconCache[hash] = dataUri;
            return dataUri;

        },
        // crisp vector badge for an interface node, so it stays sharp at any zoom level
        interfaceIconDataUri(isOnline) {

            this._interfaceIconCache = this._interfaceIconCache ?? {};
            const key = isOnline ? "online" : "offline";
            if(this._interfaceIconCache[key]){
                return this._interfaceIconCache[key];
            }

            const background = isOnline ? "#22c55e" : "#ef4444";
            const glyph = getPhosphorPath("tree-structure", "bold");

            const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">`
                + `<circle cx="128" cy="128" r="128" fill="${background}"/>`
                + `<path d="${glyph}" fill="#ffffff" transform="translate(48 48) scale(0.625)"/>`
                + `</svg>`;

            const dataUri = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
            this._interfaceIconCache[key] = dataUri;
            return dataUri;

        },
        graphLabelFont(size = 13) {
            return {
                color: "#e8eaf4",
                background: "rgba(5, 6, 10, 0.78)",
                strokeWidth: 0,
                size,
                face: "CrosstalkRoboto",
                vadjust: -1,
            };
        },
        async getInterfaceStats() {
            try {
                const response = await axios.get(`/api/v1/interface-stats`);
                this.interfaces = response.data.interface_stats?.interfaces ?? [];
            } catch(e) {
                console.log(e);
            }
        },
        async getPathTable() {
            try {
                const response = await axios.get(`/api/v1/path-table`);
                this.pathTable = response.data.path_table;
            } catch(e) {
                console.log(e);
            }
        },
        async getDiscoveredInterfaces() {
            try {
                const response = await axios.get(`/api/v1/discovered-interfaces`);
                this.discoveredInterfaces = response.data.discovered_interfaces ?? [];
            } catch(e) {
                console.log(e);
            }
        },
        async getConfig() {
            try {
                const response = await axios.get("/api/v1/config");
                this.config = response.data.config;
            } catch(e) {
                console.error(e);
            }
        },
        async resolveAnnouncePaths() {

            // reticulum learns routes lazily, so ask the network to resolve paths for
            // everyone we know about. this is what makes known peers appear on the map
            // even when the network is quiet and no fresh announces are arriving.
            // throttle so we don't spam path requests on every 5s auto-reload.
            const now = Date.now();
            if(this._lastPathResolveAt != null && (now - this._lastPathResolveAt) < 45000){
                return;
            }
            this._lastPathResolveAt = now;

            try {
                await window.axios.post(`/api/v1/path-table/resolve-announces`);
            } catch(e) {
                // best-effort: the map still works from whatever paths already exist
                console.log(e);
            }
        },
        async getAnnounces() {
            try {

                // fetch announces
                const response = await window.axios.get(`/api/v1/announces`);

                // cache announces
                this.announces = {};
                for(const announce of response.data.announces){
                    this.announces[announce.destination_hash] = announce;
                }

            } catch(e) {
                // do nothing if failed to load announces
                console.log(e);
            }
        },
        async init() {

            // create network ui
            const container = document.getElementById("network");
            this.network = new Network(container, {
                nodes: this.nodes,
                edges: this.edges,
            }, {
                interaction: {
                    tooltipDelay: 0, // show tooltip instantly on hover
                    hover: true,
                    hoverConnectedEdges: true,
                    keyboard: {
                        enabled: false,
                    },
                    zoomSpeed: 0.65,
                },
                edges: {
                    color: {
                        color: "rgba(148, 163, 184, 0.34)",
                        highlight: "rgba(125, 176, 255, 0.9)",
                        hover: "rgba(125, 176, 255, 0.75)",
                    },
                    smooth: {
                        enabled: true,
                        type: "continuous",
                        roundness: 0.12,
                    },
                    width: 1,
                    hoverWidth: 0.6,
                    selectionWidth: 1,
                },
                layout: {
                    // always layout nodes the same way across reloads if nothing changed
                    randomSeed: 1,
                },
                nodes: {
                    color: {
                        border: "#363856",
                        highlight: {
                            border: "#6ea8ff",
                        },
                        hover: {
                            border: "#7db0ff",
                        },
                    },
                    font: this.graphLabelFont(),
                    borderWidth: 1.5,
                    borderWidthSelected: 2,
                    shapeProperties: {
                        // vis-network otherwise downsamples node images into a mipmap and
                        // scales a quarter-size tile back up, which makes every icon soft.
                        // drawing straight from the full-resolution source keeps them sharp.
                        interpolation: false,
                    },
                },
                physics: {
                    barnesHut: {
                        gravitationalConstant: -3400,
                        centralGravity: 0.08,
                        springLength: 165,
                        springConstant: 0.035,
                        damping: 0.28,
                        avoidOverlap: 0.55,
                    },
                    maxVelocity: 70,
                    minVelocity: 0.35,
                    stabilization: {
                        enabled: true,
                        iterations: 320,
                        updateInterval: 40,
                        fit: true,
                    },
                },
                groups: {
                    "me": {
                        // circularImage clips to a circle like every other node on the
                        // map. plain "image" renders the artwork's bounding box, which
                        // showed up as a hard-edged box around the mark.
                        shape: "circularImage",
                        image: "/assets/images/network-visualiser/me-node.svg",
                        color: {
                            background: "#080b14",
                            border: "#0061fd",
                            highlight: { background: "#080b14", border: "#6ea8ff" },
                            hover: { background: "#080b14", border: "#7db0ff" },
                        },
                        borderWidth: 2,
                    },
                    "interface": {

                    },
                    "announce": {

                    },
                },
            });

            // handle double click on a node
            this.network.on("doubleClick", (params) => {

                // get clicked node id
                const clickedNodeId = params.nodes[0];
                if(!clickedNodeId){
                    return;
                }

                // find node by id
                const node = this.network.body.nodes[clickedNodeId];
                if(!node){
                    return;
                }

                // handle double click on an announce node
                if(node.options.group === "announce"){

                    // get announce
                    const announce = node.options._announce;
                    if(!announce) {
                        return;
                    }

                    // handle double click on lxmf.delivery node
                    if(announce.aspect === "lxmf.delivery"){

                        // go to messages page for this destination hash
                        this.$router.push({
                            name: "messages",
                            params: {
                                destinationHash: announce.destination_hash,
                            },
                        });

                    }

                    // handle double click on nomadnetwork.node node
                    if(announce.aspect === "nomadnetwork.node"){

                        // go to nomadnetwork page for this destination hash
                        this.$router.push({
                            name: "nomadnetwork",
                            params: {
                                destinationHash: announce.destination_hash,
                            },
                        });

                    }

                }

                if(node.options.group === "infrastructure"){
                    this.$router.push({ name: "infrastructure" });
                }

            });

            // update network
            await this.refresh();

            // fit network after initial load
            setTimeout(() => {
                this.fitNetwork();
            }, 2000);

            // auto reload
            this.reloadInterval = setInterval(this.onAutoReload, 5000);

        },
        async onAutoReload() {

            // do nothing if auto reload disabled
            if(!this.autoReload){
                return;
            }

            // do nothing if already updating
            if(this.isUpdating){
                return;
            }

            await this.refresh();

        },
        async refresh() {
            if(this.isUpdating){
                return;
            }

            try {
                this.isUpdating = true;
                await this.update();
            } finally {
                this.isUpdating = false;
            }
        },
        fitNetwork() {
            if(!this.network){
                return;
            }
            this.network.fit({
                animation: {
                    duration: 450,
                    easingFunction: "easeInOutQuad",
                },
            });
        },
        zoomIn() {
            this.zoomNetworkBy(1.2);
        },
        zoomOut() {
            this.zoomNetworkBy(1 / 1.2);
        },
        zoomNetworkBy(multiplier) {
            if(!this.network){
                return;
            }
            this.network.moveTo({
                scale: this.network.getScale() * multiplier,
                animation: {
                    duration: 180,
                    easingFunction: "easeInOutQuad",
                },
            });
        },
        async update() {

            await this.getConfig();
            await this.getInterfaceStats();
            await this.getDiscoveredInterfaces();

            // ask the network to resolve routes to known peers so they show up on the
            // map. path responses arrive asynchronously and are picked up by the next
            // auto-reload, so we don't block the current refresh on them.
            this.resolveAnnouncePaths();

            await this.getPathTable();
            await this.getAnnounces();

            const nodes = [];
            const edges = [];

            // add me
            nodes.push({
                id: "me",
                group: "me",
                size: 44,
                label: this.config?.display_name ?? "This Device",
                title: [
                    `${this.config?.display_name ?? 'This Device'}`,
                    `Identity: ${this.config?.identity_hash ?? 'Unknown'}`,
                ].join("\n"),
                font: this.graphLabelFont(14),
                shadow: {
                    enabled: true,
                    color: "rgba(0, 97, 253, 0.3)",
                    size: 24,
                    x: 0,
                    y: 0,
                },
            });

            // add interfaces
            for(const entry of this.interfaces){

                // determine label
                var label = entry.interface_name ?? entry.name;

                // we want to show the full info for LocalServerInterface
                // we also want to show the full info instead of just "Client on Name" for TCPServerInterface clients
                if(entry.type === "LocalServerInterface" || entry.parent_interface_name != null){
                    label = entry.name;
                }

                const node = {
                    id: entry.name,
                    group: "interface",
                    label: label,
                    title: [
                        entry.name,
                        `State: ${entry.status ? 'Online' : 'Offline'}`,
                        `Bitrate: ${this.formatBitsPerSecond(entry.bitrate)}`,
                        `TX: ${this.formatBytes(entry.txb)}`,
                        `RX: ${this.formatBytes(entry.rxb)}`,
                    ].join("\n"),
                    size: 23,
                    font: this.graphLabelFont(13),
                    shape: "circularImage",
                    image: this.interfaceIconDataUri(entry.status),
                    shadow: entry.status ? { enabled: true, color: "rgba(46, 231, 129, 0.3)", size: 16, x: 0, y: 0 } : { enabled: false },
                };

                // add interface node
                nodes.push(node);

                // add edge to interface
                if(entry.parent_interface_name){
                    // add edge from parent interface to interface
                    edges.push({
                        id: `${entry.parent_interface_name}~${entry.name}`,
                        from: entry.parent_interface_name,
                        to: entry.name,
                        color: {
                            color: entry.status ? "rgba(46, 231, 129, 0.72)" : "rgba(255, 92, 114, 0.62)",
                            highlight: entry.status ? "#6ef0a9" : "#ff8298",
                        },
                        dashes: !entry.status,
                        width: entry.status ? 2.4 : 1.5,
                        length: 180,
                    });
                } else {
                    // add edge from me to interface
                    edges.push({
                        id: `me~${entry.name}`,
                        from: "me",
                        to: entry.name,
                        color: {
                            color: entry.status ? "rgba(46, 231, 129, 0.72)" : "rgba(255, 92, 114, 0.62)",
                            highlight: entry.status ? "#6ef0a9" : "#ff8298",
                        },
                        dashes: !entry.status,
                        width: entry.status ? 2.4 : 1.5,
                        length: 180,
                    });
                }

            }

            // add signed Reticulum infrastructure advertisements with friendly names
            for(const infrastructure of this.discoveredInterfaces){
                const path = this.pathTable.find((entry) => entry.hash === infrastructure.destination_hash);
                if(!infrastructure.destination_hash){
                    continue;
                }
                const hops = path?.hops ?? infrastructure.hops;
                const pathDescription = path
                    ? `${path.hops} ${path.hops === 1 ? 'Hop' : 'Hops'} via ${path.interface}`
                    : `${hops ?? 'Unknown'} ${hops === 1 ? 'Hop' : 'Hops'} when advertised; current route not loaded`;

                const radio = [
                    infrastructure.frequency ? `Frequency: ${this.formatFrequency(infrastructure.frequency)}` : null,
                    infrastructure.bandwidth ? `Bandwidth: ${this.formatFrequency(infrastructure.bandwidth)}` : null,
                    infrastructure.sf ? `Spreading Factor: SF${infrastructure.sf}` : null,
                    infrastructure.cr ? `Coding Rate: 4/${infrastructure.cr}` : null,
                ].filter((line) => line != null);

                nodes.push({
                    id: infrastructure.destination_hash,
                    group: "infrastructure",
                    label: infrastructure.name ?? "Discovered Infrastructure",
                    title: [
                        `Name: ${infrastructure.name ?? 'Unknown'}`,
                        `Type: ${infrastructure.type ?? 'Unknown'}`,
                        `State: ${infrastructure.status ?? 'Unknown'}`,
                        `Transport: ${infrastructure.transport ? 'Enabled' : 'Disabled'}`,
                        `Transport Identity: ${infrastructure.transport_id ?? 'Unknown'}`,
                        `Path: ${pathDescription}`,
                        ...radio,
                    ].join("\n"),
                    size: 20,
                    shape: "circularImage",
                    image: infrastructureIconDataUri(infrastructure),
                    color: {
                        border: infrastructure.status === "available"
                            ? (infrastructure.transport ? "#93c5fd" : "#60a5fa")
                            : infrastructure.status === "unknown" ? "#fbbf24" : "#71717a",
                        highlight: { border: "#dbeafe" },
                    },
                    borderWidth: infrastructure.status === "available" ? 2 : 1.5,
                    shadow: path && infrastructure.status === "available"
                        ? { enabled: true, color: "rgba(96, 165, 250, 0.24)", size: 12, x: 0, y: 0 }
                        : false,
                    font: this.graphLabelFont(12),
                    _infrastructure: infrastructure,
                });

                edges.push({
                    id: `${path?.interface ?? 'me'}~${infrastructure.destination_hash}`,
                    from: path?.interface ?? "me",
                    to: infrastructure.destination_hash,
                    dashes: !path,
                    color: {
                        color: path ? "rgba(96, 165, 250, 0.42)" : "rgba(96, 165, 250, 0.28)",
                        highlight: "#93c5fd",
                        hover: "#93c5fd",
                    },
                    width: path ? 1.1 : 0.8,
                });
            }

            // add paths for announces
            for(const entry of this.pathTable){

                // skip this path if hops are unknown
                if(entry.hops == null){
                    continue;
                }

                // find what announced this path, or skip showing it for now
                const announce = this.announces[entry.hash];
                if(!announce){
                    continue;
                }

                // skip announces if we don't want to show them
                const aspectsToShow = ["lxmf.delivery", "nomadnetwork.node"];
                if(!aspectsToShow.includes(announce.aspect)){
                    continue;
                }

                const node = {
                    id: entry.hash,
                    group: "announce",
                    size: 17,
                    font: this.graphLabelFont(12),
                };

                if(announce.aspect === "lxmf.delivery"){

                    const name = announce.custom_display_name ?? announce.display_name;

                    node.shape = "circularImage";
                    node.image = this.identiconDataUri(announce.destination_hash);
                    node.color = { border: entry.hops === 1 ? "#2ee781" : "#363856", highlight: { border: "#6ea8ff" } };
                    node.borderWidth = 1.5;
                    if(entry.hops === 1){
                        node.shadow = { enabled: true, color: "rgba(0, 97, 253, 0.32)", size: 14, x: 0, y: 0 };
                    }

                    node.label = name;
                    node.title = [
                        `Name: ${announce.display_name}`,
                        announce.custom_display_name != null ? `Custom Name: ${announce.custom_display_name}` : null,
                        `Aspect: ${announce.aspect}`,
                        `Identity: ${announce.identity_hash}`,
                        `Destination: ${announce.destination_hash}`,
                        `Path: ${entry.hops} ${entry.hops === 1 ? 'Hop' : 'Hops'} via ${entry.interface}`,
                        `Announced At: ${announce.updated_at}`,
                    ].filter((line) => line != null).join("\n");

                }

                if(announce.aspect === "nomadnetwork.node"){

                    const name = announce.custom_display_name ?? announce.display_name;

                    node.shape = "circularImage";
                    node.image = this.identiconDataUri(announce.destination_hash);
                    node.color = { border: entry.hops === 1 ? "#b779ff" : "#363856", highlight: { border: "#6ea8ff" } };
                    node.borderWidth = 1.5;
                    if(entry.hops === 1){
                        node.shadow = { enabled: true, color: "rgba(183, 121, 255, 0.3)", size: 14, x: 0, y: 0 };
                    }

                    node.label = name;
                    node.title = [
                        `Name: ${announce.display_name}`,
                        announce.custom_display_name != null ? `Custom Name: ${announce.custom_display_name}` : null,
                        `Aspect: ${announce.aspect}`,
                        `Identity: ${announce.identity_hash}`,
                        `Destination: ${announce.destination_hash}`,
                        `Path: ${entry.hops} ${entry.hops === 1 ? 'Hop' : 'Hops'} via ${entry.interface}`,
                        `Announced At: ${announce.updated_at}`,
                    ].filter((line) => line != null).join("\n");

                }

                // attach announce to this node
                node._announce = announce;

                // add node
                nodes.push(node);

                // add edge from interface to announced aspect
                edges.push({
                    id: `${entry.interface}~${entry.hash}`,
                    from: entry.interface,
                    to: entry.hash,
                    color: {
                        color: "rgba(148, 163, 184, 0.32)",
                        highlight: "#6ea8ff",
                        hover: "#6ea8ff",
                    },
                    width: 0.9,
                });

            }

            // process nodes and edges
            this.processNewNodes(nodes);
            this.processNewEdges(edges);

        },
        processNewNodes(newNodes) {

            // determine old and new nodes
            const oldNodeIds = this.nodes.map((node) => node.id);
            const newNodeIds = newNodes.map((node) => node.id);

            // log new nodes
            for(const newNodeId of newNodeIds){
                if(!oldNodeIds.includes(newNodeId)){
                    console.log("Added Node: " + newNodeId);
                }
            }

            // remove old nodes that no longer exist
            for(const oldNodeId of oldNodeIds){
                if(!newNodeIds.includes(oldNodeId)){
                    console.log("Removed Node: " + oldNodeId);
                    this.nodes.remove(oldNodeId);
                }
            }

            // update nodes
            this.nodes.update(newNodes);

        },
        processNewEdges(newEdges) {

            // determine old and new edges
            const oldEdgeIds = this.edges.map((edge) => edge.id);
            const newEdgeIds = newEdges.map((edge) => edge.id);

            // log new edges
            for(const newEdgeId of newEdgeIds){
                if(!oldEdgeIds.includes(newEdgeId)){
                    console.log("Added Edge: " + newEdgeId);
                }
            }

            // remove old edges that no longer exist
            for(const oldEdgeId of oldEdgeIds){
                if(!newEdgeIds.includes(oldEdgeId)){
                    console.log("Removed Edge: " + oldEdgeId);
                    this.edges.remove(oldEdgeId);
                }
            }

            // update edges
            this.edges.update(newEdges);

        },
        formatBytes: function(bytes) {
            return Utils.formatBytes(bytes);
        },
        formatBitsPerSecond: function(bits) {
            return Utils.formatBitsPerSecond(bits);
        },
        formatFrequency: function(hz) {
            return Utils.formatFrequency(hz);
        },
    },
    computed: {
        onlineInterfaces() {
            return this.interfaces.filter((iface) => {
                return iface.status;
            });
        },
        offlineInterfaces() {
            return this.interfaces.filter((iface) => {
                return !iface.status;
            });
        },
        // reachable destinations of a given aspect, i.e. the ones we actually draw on
        // the map (a path table entry with a known hop count and a matching announce).
        // counting the whole announce history here overstated things badly, e.g. every
        // lxmf user ever heard, when the map only shows peers we currently have a route to.
        reachableCountByAspect() {
            const counts = {};
            for(const entry of this.pathTable){
                if(entry.hops == null){
                    continue;
                }
                const announce = this.announces[entry.hash];
                if(!announce){
                    continue;
                }
                counts[announce.aspect] = (counts[announce.aspect] ?? 0) + 1;
            }
            return counts;
        },
        peopleCount() {
            return this.reachableCountByAspect["lxmf.delivery"] ?? 0;
        },
        nomadNodeCount() {
            return this.reachableCountByAspect["nomadnetwork.node"] ?? 0;
        },
        // infrastructure nodes actually drawn (advertisements with a destination hash)
        infrastructureCount() {
            return this.discoveredInterfaces.filter((infrastructure) => {
                return infrastructure.destination_hash != null;
            }).length;
        },
    },
}
</script>

<style scoped>
.network-map {
    background:
        radial-gradient(circle at 50% 42%, rgba(0, 97, 253, 0.1), transparent 34%),
        radial-gradient(circle at 78% 70%, rgba(46, 231, 129, 0.045), transparent 26%),
        linear-gradient(180deg, #08090e 0%, #05060a 100%);
}

.network-map-grid {
    background-image:
        linear-gradient(rgba(125, 176, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125, 176, 255, 0.035) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: radial-gradient(circle at center, black 0%, rgba(0, 0, 0, 0.55) 48%, transparent 88%);
    opacity: 0.55;
}

.network-toolbar {
    background: linear-gradient(180deg, rgba(24, 25, 36, 0.9), rgba(13, 14, 21, 0.88));
    box-shadow:
        0 18px 60px rgba(0, 0, 0, 0.34),
        inset 0 1px 0 rgba(255, 255, 255, 0.045);
    backdrop-filter: blur(22px) saturate(135%);
}

.network-stat {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    min-height: 1.75rem;
    border: 1px solid rgba(255, 255, 255, 0.075);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.035);
    padding: 0.25rem 0.55rem;
    color: var(--ct-dim);
    font-size: 0.6875rem;
    line-height: 1;
}

.network-stat strong {
    color: var(--ct-text);
    font-size: 0.75rem;
}

.network-control {
    display: inline-flex;
    height: 2rem;
    min-width: 2rem;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 0.65rem;
    background: rgba(255, 255, 255, 0.045);
    color: var(--ct-muted);
    transition: 140ms ease;
}

.network-control:hover {
    border-color: rgba(125, 176, 255, 0.32);
    background: rgba(125, 176, 255, 0.1);
    color: var(--ct-text);
}

.network-control:focus-visible {
    outline: 2px solid rgba(110, 168, 255, 0.75);
    outline-offset: 2px;
}

:deep(.vis-network:focus) {
    outline: none;
}
</style>
