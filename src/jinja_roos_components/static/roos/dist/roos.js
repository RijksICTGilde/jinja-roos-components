(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["roos"] = factory();
	else
		root["roos"] = factory();
})(self, () => {
return /******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./fe_src/scss/roos.scss":
/*!*******************************!*\
  !*** ./fe_src/scss/roos.scss ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ "./fe_src/ts/components/button.ts":
/*!****************************************!*\
  !*** ./fe_src/ts/components/button.ts ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonComponent: () => (/* binding */ ButtonComponent)
/* harmony export */ });
function createRipple(button, event) {
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
    const computedStyle = getComputedStyle(button);
    if (computedStyle.position === 'static') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    setTimeout(() => {
        ripple.remove();
    }, 600);
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
const ButtonComponent = {
    selector: '[data-roos-component="button"]',
    init(element) {
        const button = element;
        button.addEventListener('click', (event) => {
            if (button.disabled)
                return;
            createRipple(button, event);
            const isLoading = button.hasAttribute('aria-label') &&
                button.getAttribute('aria-label') === 'Loading...';
            if (isLoading) {
                event.preventDefault();
                return false;
            }
        });
        button.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                button.click();
            }
        });
    },
    destroy(element) {
        const button = element;
        const newButton = button.cloneNode(true);
        button.parentNode?.replaceChild(newButton, button);
    }
};


/***/ }),

/***/ "./fe_src/ts/components/card.ts":
/*!**************************************!*\
  !*** ./fe_src/ts/components/card.ts ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CardComponent: () => (/* binding */ CardComponent)
/* harmony export */ });
function enhanceElevatedCard(card) {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-2px)';
        card.style.transition = 'transform 0.2s ease-out';
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
    });
}
function makeCardInteractive(card) {
    card.style.cursor = 'pointer';
    card.addEventListener('focus', () => {
        card.style.outline = '2px solid var(--rvo-color-focus, #0070f3)';
        card.style.outlineOffset = '2px';
    });
    card.addEventListener('blur', () => {
        card.style.outline = 'none';
    });
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
const CardComponent = {
    selector: '[data-roos-component="card"]',
    init(element) {
        const card = element;
        const isElevated = card.dataset.roosElevated === 'true';
        if (isElevated) {
            enhanceElevatedCard(card);
        }
        const hasClickHandler = card.hasAttribute('onclick') ||
            card.hasAttribute('hx-get') ||
            card.hasAttribute('hx-post');
        if (hasClickHandler) {
            makeCardInteractive(card);
        }
        if (hasClickHandler) {
            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    card.click();
                }
            });
            if (!card.hasAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
            }
        }
    },
    destroy(element) {
        const card = element;
        const newCard = card.cloneNode(true);
        card.parentNode?.replaceChild(newCard, card);
    }
};


/***/ }),

/***/ "./fe_src/ts/utils/clipboard.ts":
/*!**************************************!*\
  !*** ./fe_src/ts/utils/clipboard.ts ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   copyToClipboard: () => (/* binding */ copyToClipboard)
/* harmony export */ });
function copyToClipboard(targetSelector, event, parentOrOptions = {}) {
    const options = typeof parentOrOptions === 'string'
        ? { searchFromParent: parentOrOptions }
        : parentOrOptions;
    const { feedbackDuration = 2000, feedbackClass = 'is-copied', searchFromParent = '[data-copy-scope]' } = options;
    const button = (event?.currentTarget || event?.target);
    if (!button) {
        console.error('copyToClipboard: No button element found');
        return;
    }
    const container = button.closest(searchFromParent);
    if (!container) {
        console.error(`copyToClipboard: Could not find parent "${searchFromParent}"`);
        return;
    }
    const targetElement = container.querySelector(targetSelector);
    if (!targetElement) {
        console.error(`copyToClipboard: Could not find target "${targetSelector}"`);
        return;
    }
    const textToCopy = targetElement.textContent?.trim() || '';
    if (!textToCopy) {
        console.warn('copyToClipboard: No text content to copy');
        return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textToCopy)
            .then(() => showCopyFeedback(button, feedbackClass, feedbackDuration))
            .catch(() => fallbackCopy(textToCopy, button, feedbackClass, feedbackDuration));
    }
    else {
        fallbackCopy(textToCopy, button, feedbackClass, feedbackDuration);
    }
}
function fallbackCopy(text, button, feedbackClass, feedbackDuration) {
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
    }
    catch (err) {
        console.error('copyToClipboard: Failed to copy text:', err);
    }
    finally {
        document.body.removeChild(textArea);
    }
}
function showCopyFeedback(button, feedbackClass, duration) {
    button.classList.add(feedbackClass);
    setTimeout(() => {
        button.classList.remove(feedbackClass);
    }, duration);
}


/***/ }),

/***/ "./fe_src/ts/utils/registry.ts":
/*!*************************************!*\
  !*** ./fe_src/ts/utils/registry.ts ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ComponentRegistry: () => (/* binding */ ComponentRegistry)
/* harmony export */ });
class ComponentRegistry {
    constructor() {
        this.components = new Map();
        this.initializedElements = new WeakSet();
    }
    register(name, component) {
        this.components.set(name, component);
    }
    initializeAll() {
        this.components.forEach((component, name) => {
            this.initializeComponent(name, component);
        });
    }
    initializeComponent(name, component) {
        const elements = document.querySelectorAll(component.selector);
        elements.forEach(element => {
            if (this.initializedElements.has(element)) {
                return;
            }
            try {
                component.init(element);
                this.initializedElements.add(element);
            }
            catch (error) {
                console.error(`Error initializing ${name} component:`, error);
            }
        });
    }
    get(name) {
        return this.components.get(name);
    }
    destroyElement(element) {
        this.components.forEach((component) => {
            if (element.matches(component.selector) && component.destroy) {
                component.destroy(element);
                this.initializedElements.delete(element);
            }
        });
    }
    list() {
        return Array.from(this.components.keys());
    }
}


/***/ }),

/***/ "./fe_src/ts/utils/ruleapplier.ts":
/*!****************************************!*\
  !*** ./fe_src/ts/utils/ruleapplier.ts ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RuleApplier: () => (/* binding */ RuleApplier),
/* harmony export */   applyRules: () => (/* binding */ applyRules)
/* harmony export */ });
class RuleApplier {
    constructor() {
        this.debug = false;
    }
    applyRules(rulesString, clickedElement) {
        try {
            const rules = this.parseRules(rulesString);
            this.executeRules(rules, clickedElement);
        }
        catch (error) {
            console.error('Rule application failed:', error.message);
            throw error;
        }
    }
    parseRules(rulesString) {
        const rules = [];
        const statements = this.tokenizeStatements(rulesString);
        for (const statement of statements) {
            const rule = this.parseStatement(statement);
            if (rule)
                rules.push(rule);
        }
        return rules;
    }
    tokenizeStatements(rulesString) {
        const cleaned = rulesString.trim();
        if (!cleaned) {
            throw new Error('Empty rules string provided');
        }
        const statements = [];
        let current = '';
        let inQuotes = false;
        let quoteChar = null;
        for (let i = 0; i < cleaned.length; i++) {
            const char = cleaned[i];
            if ((char === '"' || char === "'") && cleaned[i - 1] !== '\\') {
                if (!inQuotes) {
                    inQuotes = true;
                    quoteChar = char;
                }
                else if (char === quoteChar) {
                    inQuotes = false;
                    quoteChar = null;
                }
            }
            if (char === ';' && !inQuotes) {
                if (current.trim()) {
                    statements.push(current.trim());
                }
                current = '';
            }
            else {
                current += char;
            }
        }
        if (current.trim()) {
            statements.push(current.trim());
        }
        return statements;
    }
    parseStatement(statement) {
        const colonIndex = statement.indexOf(':');
        if (colonIndex === -1) {
            throw new Error(`Invalid statement format: "${statement}". Expected: "selector: actions"`);
        }
        const selector = statement.substring(0, colonIndex).trim();
        const actionsString = statement.substring(colonIndex + 1).trim();
        if (!selector) {
            throw new Error(`Empty selector in statement: "${statement}"`);
        }
        if (!actionsString) {
            throw new Error(`No actions specified for selector "${selector}"`);
        }
        const actions = this.parseActions(actionsString);
        return { selector, actions };
    }
    parseActions(actionsString) {
        const actions = [];
        const tokens = this.tokenizeActions(actionsString);
        for (const token of tokens) {
            const action = this.parseActionToken(token);
            if (action)
                actions.push(action);
        }
        return actions;
    }
    tokenizeActions(actionsString) {
        const tokens = [];
        let current = '';
        let inBrackets = false;
        for (let i = 0; i < actionsString.length; i++) {
            const char = actionsString[i];
            if (char === '[') {
                inBrackets = true;
                current += char;
            }
            else if (char === ']') {
                inBrackets = false;
                current += char;
            }
            else if (char === ' ' && !inBrackets) {
                if (current.trim()) {
                    tokens.push(current.trim());
                }
                current = '';
            }
            else {
                current += char;
            }
        }
        if (current.trim()) {
            tokens.push(current.trim());
        }
        return tokens;
    }
    parseActionToken(token) {
        if (token.startsWith('+')) {
            const value = token.substring(1);
            if (value.startsWith('[') && value.endsWith(']')) {
                const classList = value.slice(1, -1).split(',').map(c => c.trim());
                return { type: 'addClass', classes: classList };
            }
            else {
                return { type: 'addClass', classes: [value] };
            }
        }
        if (token.startsWith('-')) {
            const value = token.substring(1);
            if (value.startsWith('[') && value.endsWith(']')) {
                const classList = value.slice(1, -1).split(',').map(c => c.trim());
                return { type: 'removeClass', classes: classList };
            }
            else {
                return { type: 'removeClass', classes: [value] };
            }
        }
        if (token.includes('=')) {
            const [key, ...valueParts] = token.split('=');
            const value = valueParts.join('=');
            if (!key.trim()) {
                throw new Error(`Invalid attribute assignment: "${token}"`);
            }
            return {
                type: 'setAttribute',
                attribute: key.trim(),
                value: value.trim().replace(/^["']|["']$/g, '')
            };
        }
        throw new Error(`Unknown action format: "${token}"`);
    }
    resolveSelector(selector, clickedElement) {
        const interpolated = this.interpolateVariables(selector, clickedElement);
        if (interpolated === 'self' || interpolated.startsWith('self ') || interpolated.startsWith('self>')) {
            const baseElements = [clickedElement];
            const remainder = interpolated.substring(4).trim();
            if (!remainder)
                return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }
        if (interpolated === 'siblings' || interpolated.startsWith('siblings ') || interpolated.startsWith('siblings>')) {
            const parent = clickedElement.parentElement;
            if (!parent)
                return [];
            const baseElements = Array.from(parent.children).filter(el => el !== clickedElement);
            const remainder = interpolated.substring(8).trim();
            if (!remainder)
                return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }
        if (interpolated === 'parent' || interpolated.startsWith('parent ') || interpolated.startsWith('parent>')) {
            const baseElements = clickedElement.parentElement ? [clickedElement.parentElement] : [];
            const remainder = interpolated.substring(6).trim();
            if (!remainder)
                return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }
        if (interpolated.startsWith('~')) {
            const selectorPart = interpolated.substring(1).trim();
            const siblings = [];
            let sibling = clickedElement.nextElementSibling;
            while (sibling) {
                if (!selectorPart || sibling.matches(selectorPart)) {
                    siblings.push(sibling);
                }
                sibling = sibling.nextElementSibling;
            }
            return siblings;
        }
        if (interpolated.startsWith('+')) {
            const selectorPart = interpolated.substring(1).trim();
            const next = clickedElement.nextElementSibling;
            if (next && (!selectorPart || next.matches(selectorPart))) {
                return [next];
            }
            return [];
        }
        if (interpolated.startsWith('>')) {
            const selectorPart = interpolated.substring(1).trim();
            if (!selectorPart) {
                return Array.from(clickedElement.children);
            }
            return Array.from(clickedElement.querySelectorAll(':scope > ' + selectorPart));
        }
        if (interpolated.startsWith('^')) {
            const selectorPart = interpolated.substring(1).trim();
            const parent = clickedElement.closest(selectorPart);
            return parent ? [parent] : [];
        }
        try {
            if (interpolated.startsWith('#')) {
                return Array.from(document.querySelectorAll(interpolated));
            }
            return Array.from(clickedElement.querySelectorAll(interpolated));
        }
        catch {
            throw new Error(`Invalid selector: "${selector}"`);
        }
    }
    queryFromElements(elements, selectorPart) {
        const results = [];
        for (const element of elements) {
            if (selectorPart.startsWith('>')) {
                const childSelector = selectorPart.substring(1).trim();
                if (!childSelector) {
                    results.push(...Array.from(element.children));
                }
                else {
                    results.push(...Array.from(element.querySelectorAll(':scope > ' + childSelector)));
                }
            }
            else if (selectorPart) {
                results.push(...Array.from(element.querySelectorAll(selectorPart)));
            }
        }
        return results;
    }
    interpolateVariables(selector, element) {
        return selector.replace(/\{([^}]+)\}/g, (match, varName) => {
            if (varName.startsWith('data-')) {
                return element.dataset[varName.substring(5)] || '';
            }
            if (varName === 'id') {
                return element.id || '';
            }
            if (varName.startsWith('attr:')) {
                const attrName = varName.substring(5);
                return element.getAttribute(attrName) || '';
            }
            return element.getAttribute(varName) || '';
        });
    }
    executeRules(rules, clickedElement) {
        for (const rule of rules) {
            const elements = this.resolveSelector(rule.selector, clickedElement);
            if (elements.length === 0 && this.debug) {
                console.warn(`No elements found for selector: "${rule.selector}"`);
                continue;
            }
            for (const element of elements) {
                this.applyActions(element, rule.actions);
            }
        }
    }
    applyActions(element, actions) {
        for (const action of actions) {
            switch (action.type) {
                case 'addClass':
                    element.classList.add(...(action.classes || []));
                    break;
                case 'removeClass':
                    element.classList.remove(...(action.classes || []));
                    break;
                case 'setAttribute':
                    if (action.attribute && action.value !== undefined) {
                        element.setAttribute(action.attribute, action.value);
                    }
                    break;
            }
        }
    }
}
const ruleApplier = new RuleApplier();
function applyRules(rulesString, event, options = {}) {
    if (options.preventDefault && event?.preventDefault) {
        event.preventDefault();
    }
    if (options.stopPropagation && event?.stopPropagation) {
        event.stopPropagation();
    }
    const clickedElement = (event?.currentTarget || event?.target);
    if (!clickedElement) {
        console.error('No element found for rule application');
        return;
    }
    try {
        ruleApplier.applyRules(rulesString, clickedElement);
    }
    catch (error) {
        console.error('Rule Application Error:', error);
    }
}



/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry needs to be wrapped in an IIFE because it needs to be isolated against other modules in the chunk.
(() => {
/*!***************************!*\
  !*** ./fe_src/ts/roos.ts ***!
  \***************************/
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonComponent: () => (/* reexport safe */ _components_button__WEBPACK_IMPORTED_MODULE_1__.ButtonComponent),
/* harmony export */   CardComponent: () => (/* reexport safe */ _components_card__WEBPACK_IMPORTED_MODULE_2__.CardComponent),
/* harmony export */   ComponentRegistry: () => (/* reexport safe */ _utils_registry__WEBPACK_IMPORTED_MODULE_3__.ComponentRegistry),
/* harmony export */   applyRules: () => (/* reexport safe */ _utils_ruleapplier__WEBPACK_IMPORTED_MODULE_4__.applyRules),
/* harmony export */   copyToClipboard: () => (/* reexport safe */ _utils_clipboard__WEBPACK_IMPORTED_MODULE_5__.copyToClipboard),
/* harmony export */   getRegistry: () => (/* binding */ getRegistry),
/* harmony export */   init: () => (/* binding */ init)
/* harmony export */ });
/* harmony import */ var _scss_roos_scss__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../scss/roos.scss */ "./fe_src/scss/roos.scss");
/* harmony import */ var _components_button__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/button */ "./fe_src/ts/components/button.ts");
/* harmony import */ var _components_card__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/card */ "./fe_src/ts/components/card.ts");
/* harmony import */ var _utils_registry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./utils/registry */ "./fe_src/ts/utils/registry.ts");
/* harmony import */ var _utils_ruleapplier__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./utils/ruleapplier */ "./fe_src/ts/utils/ruleapplier.ts");
/* harmony import */ var _utils_clipboard__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./utils/clipboard */ "./fe_src/ts/utils/clipboard.ts");






const registry = new _utils_registry__WEBPACK_IMPORTED_MODULE_3__.ComponentRegistry();
registry.register('button', _components_button__WEBPACK_IMPORTED_MODULE_1__.ButtonComponent);
registry.register('card', _components_card__WEBPACK_IMPORTED_MODULE_2__.CardComponent);
registry.register('checkbox', { selector: '[data-roos-component="checkbox"]', init: () => { } });
registry.register('select', { selector: '[data-roos-component="select"]', init: () => { } });
registry.register('radio', { selector: '[data-roos-component="radio"]', init: () => { } });
registry.register('textarea', { selector: '[data-roos-component="textarea"]', init: () => { } });
registry.register('input', { selector: '[data-roos-component="input"]', init: () => { } });
registry.register('layout-flow', { selector: '[data-roos-component="layout-flow"]', init: () => { } });
registry.register('grid', { selector: '[data-roos-component="grid"]', init: () => { } });
registry.register('tag', { selector: '[data-roos-component="tag"]', init: () => { } });
registry.register('page', { selector: '[data-roos-page="true"]', init: () => { } });
document.addEventListener('DOMContentLoaded', () => {
    initializeComponents();
});
if (typeof window !== 'undefined' && window.htmx) {
    document.body.addEventListener('htmx:afterSwap', () => {
        initializeComponents();
    });
}
function initializeComponents() {
    registry.initializeAll();
}
function getRegistry() {
    return registry;
}
function init() {
    initializeComponents();
}
if (typeof window !== 'undefined') {
    window.roos = {
        init,
        getRegistry,
        registry
    };
    window.applyRules = _utils_ruleapplier__WEBPACK_IMPORTED_MODULE_4__.applyRules;
    window.copyToClipboard = _utils_clipboard__WEBPACK_IMPORTED_MODULE_5__.copyToClipboard;
}


})();

/******/ 	return __webpack_exports__;
/******/ })()
;
});
//# sourceMappingURL=roos.js.map