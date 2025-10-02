/**
 * Card Component - Enhanced card functionality
 */

import type { Component } from '../utils/registry';

function enhanceElevatedCard(card: HTMLElement): void {
    // Add subtle animation on hover
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-2px)';
        card.style.transition = 'transform 0.2s ease-out';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
    });
}

function makeCardInteractive(card: HTMLElement): void {
    // Add visual feedback for interactive cards
    card.style.cursor = 'pointer';
    
    // Add focus styling
    card.addEventListener('focus', () => {
        card.style.outline = '2px solid var(--rvo-color-focus, #0070f3)';
        card.style.outlineOffset = '2px';
    });

    card.addEventListener('blur', () => {
        card.style.outline = 'none';
    });

    // Add active state
    card.addEventListener('mousedown', () => {
        card.style.transform = 'scale(0.98)';
    });

    card.addEventListener('mouseup', () => {
        card.style.transform = 'scale(1)';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'scale(1)';
    });
}

export const CardComponent: Component = {
    selector: '[data-roos-component="card"]',

    init(element: Element): void {
        const card = element as HTMLElement;
        
        // Add hover effects for elevated cards
        const isElevated = card.dataset.roosElevated === 'true';
        if (isElevated) {
            enhanceElevatedCard(card);
        }

        // Add click handling if the card has click handlers
        const hasClickHandler = card.hasAttribute('onclick') || 
                               card.hasAttribute('hx-get') || 
                               card.hasAttribute('hx-post');
        
        if (hasClickHandler) {
            makeCardInteractive(card);
        }

        // Handle keyboard navigation for interactive cards
        if (hasClickHandler) {
            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    card.click();
                }
            });
            
            // Make it focusable
            if (!card.hasAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
            }
        }
    },

    destroy(element: Element): void {
        // Clean up event listeners
        const card = element as HTMLElement;
        const newCard = card.cloneNode(true);
        card.parentNode?.replaceChild(newCard, card);
    }
};