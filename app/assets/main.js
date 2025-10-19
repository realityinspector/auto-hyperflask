// Main JavaScript entry point for AutoHyperFlask
// This file is bundled by esbuild and includes all frontend dependencies

// Import Alpine.js for reactive components
import Alpine from 'alpinejs'

// Import HTMX for dynamic HTML
import 'htmx.org'

// Import HTMX SSE extension for server-sent events
import 'htmx.org/dist/ext/sse.js'

// Initialize Alpine.js
window.Alpine = Alpine
Alpine.start()

// Log successful initialization
console.log('AutoHyperFlask frontend initialized')
console.log('- Alpine.js:', typeof Alpine !== 'undefined' ? '✓' : '✗')
console.log('- HTMX:', typeof htmx !== 'undefined' ? '✓' : '✗')
