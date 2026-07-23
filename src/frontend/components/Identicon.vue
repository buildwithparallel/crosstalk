<template>
    <svg :viewBox="`0 0 ${gridSize} ${gridSize}`" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" :style="{ background: backgroundColour }">
        <rect
            v-for="(cell, index) in cells"
            :key="index"
            :x="cell.x"
            :y="cell.y"
            width="1"
            height="1"
            :fill="cell.colour"
        />
    </svg>
</template>

<script>
// Deterministic geometric avatar derived from a destination hash.
// Same idea as crypto "blockies", but constrained to the Parallel palette
// so every generated avatar sits comfortably on the dark UI.
const PALETTES = [
    // [primary, accent, background]
    ["#0061fd", "#7db0ff", "#0c1220"], // parallel blue
    ["#2ee781", "#9ff5c6", "#0b1a13"], // green
    ["#ff9900", "#ffc266", "#1d1408"], // amber
    ["#b779ff", "#dcbcff", "#160f22"], // violet
    ["#22d3ee", "#a5f3fc", "#082026"], // cyan
    ["#ff5c8a", "#ffadc4", "#220d14"], // magenta
    ["#8da2fb", "#c7d2fe", "#10142a"], // indigo
    ["#f4e04d", "#faf0a0", "#1e1b08"], // yellow
];

// simple deterministic PRNG seeded from the hash string (mulberry32)
function createRandom(seedString) {
    let seed = 0;
    const value = String(seedString ?? "");
    for(let i = 0; i < value.length; i++){
        seed = Math.imul(seed ^ value.charCodeAt(i), 2654435761);
    }
    seed = seed >>> 0;
    return function() {
        seed |= 0;
        seed = (seed + 0x6D2B79F5) | 0;
        let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

export default {
    name: "Identicon",
    props: {
        // the value the avatar is derived from, e.g. a destination hash
        hash: {
            type: String,
            default: "",
        },
        size: {
            type: Number,
            default: 5, // grid cells per side
        },
    },
    computed: {
        gridSize() {
            return this.size;
        },
        generated() {
            const random = createRandom(this.hash);
            const palette = PALETTES[Math.floor(random() * PALETTES.length)];
            const [primary, accent, background] = palette;

            // build a horizontally mirrored cell grid
            const cells = [];
            const half = Math.ceil(this.size / 2);
            for(let y = 0; y < this.size; y++){
                for(let x = 0; x < half; x++){
                    const roll = random();
                    let colour = null;
                    if(roll < 0.44){
                        colour = primary;
                    } else if(roll < 0.58){
                        colour = accent;
                    }
                    if(colour){
                        cells.push({ x, y, colour });
                        const mirrorX = this.size - 1 - x;
                        if(mirrorX !== x){
                            cells.push({ x: mirrorX, y, colour });
                        }
                    }
                }
            }
            return { cells, background };
        },
        cells() {
            return this.generated.cells;
        },
        backgroundColour() {
            return this.generated.background;
        },
    },
};
</script>
