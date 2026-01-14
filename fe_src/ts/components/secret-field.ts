/**
 * Secret Field Component
 * Provides show/hide toggle and copy-to-clipboard functionality for sensitive values
 */

import type { Component } from '../utils/registry';

// Store component state per element
const elementState = new WeakMap<Element, {
    isVisible: boolean;
    showLabel: string;
    hideLabel: string;
    copyLabel: string;
    copiedLabel: string;
}>();

function showValue(element: HTMLElement): void {
    const state = elementState.get(element);
    if (!state) return;

    const mask = element.querySelector<HTMLElement>('.roos-secret-field__mask');
    const value = element.querySelector<HTMLElement>('.roos-secret-field__value');
    const toggleButton = element.querySelector<HTMLElement>('.roos-secret-field__toggle');
    const toggleText = element.querySelector<HTMLElement>('.roos-secret-field__toggle-text');

    if (mask) mask.style.display = 'none';
    if (value) value.style.display = 'inline';

    if (toggleButton) {
        toggleButton.setAttribute('aria-pressed', 'true');
        toggleButton.setAttribute('aria-label', state.hideLabel);
    }

    if (toggleText) toggleText.textContent = state.hideLabel;

    // Update icon
    const icon = toggleButton?.querySelector('.rvo-icon');
    if (icon) {
        icon.classList.remove('rvo-icon-oog');
        icon.classList.add('rvo-icon-oog-dicht');
    }

    state.isVisible = true;
}

function hideValue(element: HTMLElement): void {
    const state = elementState.get(element);
    if (!state) return;

    const mask = element.querySelector<HTMLElement>('.roos-secret-field__mask');
    const value = element.querySelector<HTMLElement>('.roos-secret-field__value');
    const toggleButton = element.querySelector<HTMLElement>('.roos-secret-field__toggle');
    const toggleText = element.querySelector<HTMLElement>('.roos-secret-field__toggle-text');

    if (mask) mask.style.display = 'inline';
    if (value) value.style.display = 'none';

    if (toggleButton) {
        toggleButton.setAttribute('aria-pressed', 'false');
        toggleButton.setAttribute('aria-label', state.showLabel);
    }

    if (toggleText) toggleText.textContent = state.showLabel;

    // Update icon
    const icon = toggleButton?.querySelector('.rvo-icon');
    if (icon) {
        icon.classList.remove('rvo-icon-oog-dicht');
        icon.classList.add('rvo-icon-oog');
    }

    state.isVisible = false;
}

function showCopySuccess(element: HTMLElement, copyButton: HTMLElement, copyText: HTMLElement): void {
    const state = elementState.get(element);
    if (!state) return;

    const originalText = copyText.textContent || state.copyLabel;
    copyText.textContent = state.copiedLabel;
    copyButton.classList.add('roos-secret-field__copy--success');

    // Update icon to checkmark
    const icon = copyButton.querySelector('.rvo-icon');
    if (icon) {
        icon.classList.remove('rvo-icon-document-blanco');
        icon.classList.add('rvo-icon-vinkje');
    }

    // Reset after delay
    setTimeout(() => {
        copyText.textContent = originalText;
        copyButton.classList.remove('roos-secret-field__copy--success');
        if (icon) {
            icon.classList.remove('rvo-icon-vinkje');
            icon.classList.add('rvo-icon-document-blanco');
        }
    }, 2000);
}

function fallbackCopy(text: string, element: HTMLElement, copyButton: HTMLElement, copyText: HTMLElement): void {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();

    try {
        document.execCommand('copy');
        showCopySuccess(element, copyButton, copyText);
    } catch (execErr) {
        console.error('Failed to copy text:', execErr);
    }

    document.body.removeChild(textArea);
}

export const SecretFieldComponent: Component = {
    selector: '[data-roos-component="secret-field"]',

    init(element: Element): void {
        const el = element as HTMLElement;

        // Get labels from data attributes
        const state = {
            isVisible: false,
            showLabel: el.dataset.showLabel || 'Tonen',
            hideLabel: el.dataset.hideLabel || 'Verbergen',
            copyLabel: el.dataset.copyLabel || 'Kopiëren',
            copiedLabel: el.dataset.copiedLabel || 'Gekopieerd!'
        };
        elementState.set(element, state);

        // Setup toggle button
        const toggleButton = el.querySelector<HTMLElement>('.roos-secret-field__toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => {
                const currentState = elementState.get(element);
                if (!currentState) return;

                if (currentState.isVisible) {
                    hideValue(el);
                } else {
                    showValue(el);
                }
            });
        }

        // Setup copy button
        const copyButton = el.querySelector<HTMLElement>('.roos-secret-field__copy');
        const copyText = el.querySelector<HTMLElement>('.roos-secret-field__copy-text');
        const valueEl = el.querySelector<HTMLElement>('.roos-secret-field__value');

        if (copyButton && copyText && valueEl) {
            copyButton.addEventListener('click', async () => {
                const secretValue = valueEl.textContent?.trim() || '';

                try {
                    await navigator.clipboard.writeText(secretValue);
                    showCopySuccess(el, copyButton, copyText);
                } catch (err) {
                    fallbackCopy(secretValue, el, copyButton, copyText);
                }
            });
        }
    },

    destroy(element: Element): void {
        elementState.delete(element);
        // Clone to remove event listeners
        const el = element as HTMLElement;
        const newEl = el.cloneNode(true);
        el.parentNode?.replaceChild(newEl, el);
    }
};
