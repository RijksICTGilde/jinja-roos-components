/**
 * Dialog Component - Manages dialog open/close behavior
 *
 * Handles:
 * - Close button (×) click
 * - ESC key (respects closedby attribute)
 * - Backdrop click (respects closedby attribute)
 * - Opening via showModal() for proper backdrop + focus trap
 */

import type { Component } from '../utils/registry';

function getClosedBy(dialog: HTMLDialogElement): string {
    return dialog.getAttribute('closedby') || 'any';
}

function closeDialog(dialog: HTMLDialogElement): void {
    dialog.close();
    dialog.dispatchEvent(new CustomEvent('roos:dialog:close'));
}

function openDialog(dialog: HTMLDialogElement): void {
    if (!dialog.open) {
        dialog.showModal();
        dialog.dispatchEvent(new CustomEvent('roos:dialog:open'));
    }
}

export const DialogComponent: Component = {
    selector: '[data-roos-component="dialog"]',

    init(element: Element): void {
        const dialog = element as HTMLDialogElement;

        // Close button (×)
        const closeBtn = dialog.querySelector('.rvo-dialog__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                closeDialog(dialog);
            });
        }

        // Backdrop click (only when closedby="any")
        dialog.addEventListener('click', (event) => {
            if (event.target !== dialog) return;
            if (getClosedBy(dialog) !== 'any') return;

            // Click on backdrop (the dialog element itself, outside inner content)
            const rect = dialog.getBoundingClientRect();
            const clickedInside =
                event.clientX >= rect.left &&
                event.clientX <= rect.right &&
                event.clientY >= rect.top &&
                event.clientY <= rect.bottom;

            if (!clickedInside) {
                closeDialog(dialog);
            }
        });

        // ESC key (closedby="any" or "closerequest")
        dialog.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;
            const closedby = getClosedBy(dialog);
            if (closedby === 'none') {
                event.preventDefault();
            }
            // "any" and "closerequest" allow ESC (native behavior)
        });

        // If dialog has open attribute, upgrade to showModal() for proper backdrop
        if (dialog.hasAttribute('open')) {
            dialog.close();
            dialog.showModal();
        }
    }
};
