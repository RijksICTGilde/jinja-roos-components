/**
 * Clipboard Utility
 * Provides copy-to-clipboard functionality with visual feedback
 *
 * USAGE
 * =====
 *
 * Copy text from a target element:
 * --------------------------------
 * <button onclick="copyToClipboard('.my-value', event)">Copy</button>
 *
 * The function will:
 * 1. Find the target element relative to the clicked button
 * 2. Copy its text content to clipboard
 * 3. Add 'is-copied' class to the button for visual feedback
 * 4. Remove the class after 2 seconds
 */

export interface CopyOptions {
    feedbackDuration?: number;
    feedbackClass?: string;
    searchFromParent?: string;
}

/**
 * Copy text content from a target element to clipboard
 * @param targetSelector - CSS selector for the element containing text to copy
 * @param event - The click event (used to find context element)
 * @param parentOrOptions - Parent selector string OR options object
 */
export function copyToClipboard(
    targetSelector: string,
    event: Event | null,
    parentOrOptions: string | CopyOptions = {}
): void {
    // Allow passing parent selector as string for convenience
    const options: CopyOptions = typeof parentOrOptions === 'string'
        ? { searchFromParent: parentOrOptions }
        : parentOrOptions;

    const {
        feedbackDuration = 2000,
        feedbackClass = 'is-copied',
        searchFromParent = '[data-copy-scope]'  // Generic default, falls back to closest scoped element
    } = options;

    const button = (event?.currentTarget || event?.target) as HTMLElement;
    if (!button) {
        console.error('copyToClipboard: No button element found');
        return;
    }

    // Find the parent container to scope the search
    const container = button.closest(searchFromParent);
    if (!container) {
        console.error(`copyToClipboard: Could not find parent "${searchFromParent}"`);
        return;
    }

    // Find the target element within the container
    const targetElement = container.querySelector(targetSelector);
    if (!targetElement) {
        console.error(`copyToClipboard: Could not find target "${targetSelector}"`);
        return;
    }

    // Get the text content
    const textToCopy = targetElement.textContent?.trim() || '';

    if (!textToCopy) {
        console.warn('copyToClipboard: No text content to copy');
        return;
    }

    // Try modern clipboard API first, fall back to execCommand
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textToCopy)
            .then(() => showCopyFeedback(button, feedbackClass, feedbackDuration))
            .catch(() => fallbackCopy(textToCopy, button, feedbackClass, feedbackDuration));
    } else {
        fallbackCopy(textToCopy, button, feedbackClass, feedbackDuration);
    }
}

/**
 * Fallback copy method using execCommand (for older browsers)
 */
function fallbackCopy(
    text: string,
    button: HTMLElement,
    feedbackClass: string,
    feedbackDuration: number
): void {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '0';
    textArea.setAttribute('readonly', '');
    document.body.appendChild(textArea);

    try {
        textArea.select();
        textArea.setSelectionRange(0, text.length);
        document.execCommand('copy');
        showCopyFeedback(button, feedbackClass, feedbackDuration);
    } catch (err) {
        console.error('copyToClipboard: Failed to copy text:', err);
    } finally {
        document.body.removeChild(textArea);
    }
}

/**
 * Show visual feedback on the button after successful copy
 */
function showCopyFeedback(
    button: HTMLElement,
    feedbackClass: string,
    duration: number
): void {
    button.classList.add(feedbackClass);

    setTimeout(() => {
        button.classList.remove(feedbackClass);
    }, duration);
}
