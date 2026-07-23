import formsPlugin from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'selector',
    content: [
        "./src/frontend/index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx,html}",
    ],
    theme: {
        extend: {
            colors: {
                // Parallel brand tokens, defined as CSS variables in style.css
                'ct-bg': 'var(--ct-bg)',
                'ct-bg-2': 'var(--ct-bg-2)',
                'ct-surface': 'var(--ct-surface)',
                'ct-surface-2': 'var(--ct-surface-2)',
                'ct-raised': 'var(--ct-raised)',
                'ct-overlay': 'var(--ct-overlay)',
                'ct-border': 'var(--ct-border)',
                'ct-border-strong': 'var(--ct-border-strong)',
                'ct-text': 'var(--ct-text)',
                'ct-muted': 'var(--ct-muted)',
                'ct-dim': 'var(--ct-dim)',
                'ct-blue': 'var(--ct-blue)',
                'ct-blue-hover': 'var(--ct-blue-hover)',
                'ct-amber': 'var(--ct-amber)',
                'ct-red': 'var(--ct-red)',
                'ct-green': 'var(--ct-green)',
            },
            borderRadius: {
                'ct-sm': 'var(--ct-radius-sm)',
                'ct': 'var(--ct-radius)',
                'ct-lg': 'var(--ct-radius-lg)',
            },
            fontFamily: {
                'brand': ['CrosstalkRoboto', 'Roboto', 'system-ui', 'sans-serif'],
                'display': ['CrosstalkCode', 'ui-monospace', 'monospace'],
                'hash': ['"Roboto Mono"', 'ui-monospace', 'monospace'],
            },
        },
    },
    plugins: [
        formsPlugin,
    ],
}
