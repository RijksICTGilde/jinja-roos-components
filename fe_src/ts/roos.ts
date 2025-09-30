/**
 * ROOS Components - Main Entry Point
 * 
 * This file initializes the ROOS component library and provides
 * utilities for component interaction and HTMX integration.
 */

// Import styles
import '../scss/roos.scss';

import { ButtonComponent } from './components/button';
import { CardComponent } from './components/card';
import { ComponentRegistry } from './utils/registry';

// Create global registry
const registry = new ComponentRegistry();

// Register default components
registry.register('button', ButtonComponent);
registry.register('card', CardComponent);

// Form components use basic interaction enhancement
registry.register('checkbox', { selector: '[data-roos-component="checkbox"]', init: () => {} });
registry.register('select', { selector: '[data-roos-component="select"]', init: () => {} });
registry.register('radio', { selector: '[data-roos-component="radio"]', init: () => {} });
registry.register('textarea', { selector: '[data-roos-component="textarea"]', init: () => {} });
registry.register('input', { selector: '[data-roos-component="input"]', init: () => {} });

// Layout components don't need JavaScript enhancement
registry.register('layout-flow', { selector: '[data-roos-component="layout-flow"]', init: () => {} });
registry.register('grid', { selector: '[data-roos-component="grid"]', init: () => {} });
registry.register('tag', { selector: '[data-roos-component="tag"]', init: () => {} });

// Page component manages the entire page structure
registry.register('page', { selector: '[data-roos-page="true"]', init: () => {} });

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initializeComponents();
});

// Also initialize for dynamically loaded content (HTMX)
if (typeof window !== 'undefined' && (window as any).htmx) {
    document.body.addEventListener('htmx:afterSwap', () => {
        initializeComponents();
    });
}

/**
 * Initialize all ROOS components in the document
 */
function initializeComponents(): void {
    registry.initializeAll();
}

/**
 * Get the global component registry
 */
export function getRegistry(): ComponentRegistry {
    return registry;
}

/**
 * Initialize components manually (useful for dynamically added content)
 */
export function init(): void {
    initializeComponents();
}

// Make available globally for browser usage
if (typeof window !== 'undefined') {
    (window as any).roos = {
        init,
        getRegistry,
        registry
    };
}

export { ButtonComponent, CardComponent, ComponentRegistry };