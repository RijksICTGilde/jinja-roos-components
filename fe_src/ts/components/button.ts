/**
 * Button Component - Enhanced button functionality
 */

import type { Component } from '../utils/registry';

function createRipple(button: HTMLButtonElement, event: MouseEvent): void {
    // Simple ripple effect for better UX
    const rect = button.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: roos-ripple 0.6s linear;
        pointer-events: none;
    `;

    // Ensure button has relative positioning for ripple
    const computedStyle = getComputedStyle(button);
    if (computedStyle.position === 'static') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';

    button.appendChild(ripple);

    // Remove ripple after animation
    setTimeout(() => {
        ripple.remove();
    }, 600);

    // Add CSS animation if not already added
    if (!document.querySelector('#roos-ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'roos-ripple-styles';
        style.textContent = `
            @keyframes roos-ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

export const ButtonComponent: Component = {
    selector: '[data-roos-component="button"]',

    init(element: Element): void {
        const button = element as HTMLButtonElement;
        
        // Add click ripple effect
        button.addEventListener('click', (event) => {
            if (button.disabled) return;
            
            // Create ripple effect
            createRipple(button, event);
            
            // Handle loading state
            const isLoading = button.hasAttribute('aria-label') && 
                             button.getAttribute('aria-label') === 'Loading...';
            
            if (isLoading) {
                event.preventDefault();
                return false;
            }
        });

        // Handle keyboard navigation
        button.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                button.click();
            }
        });
    },

    destroy(element: Element): void {
        // Clean up event listeners if needed
        const button = element as HTMLButtonElement;
        const newButton = button.cloneNode(true);
        button.parentNode?.replaceChild(newButton, button);
    }
};