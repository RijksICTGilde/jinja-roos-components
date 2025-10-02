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

/***/ "./src/scss/roos.scss":
/*!****************************!*\
  !*** ./src/scss/roos.scss ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ "./fe_src/ts/components/button.ts":
/*!*************************************!*\
  !*** ./fe_src/ts/components/button.ts ***!
  \*************************************/
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
/*!***********************************!*\
  !*** ./fe_src/ts/components/card.ts ***!
  \***********************************/
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

/***/ "./fe_src/ts/utils/registry.ts":
/*!**********************************!*\
  !*** ./fe_src/ts/utils/registry.ts ***!
  \**********************************/
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
/*!************************!*\
  !*** ./fe_src/ts/roos.ts ***!
  \************************/
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonComponent: () => (/* reexport safe */ _components_button__WEBPACK_IMPORTED_MODULE_1__.ButtonComponent),
/* harmony export */   CardComponent: () => (/* reexport safe */ _components_card__WEBPACK_IMPORTED_MODULE_2__.CardComponent),
/* harmony export */   ComponentRegistry: () => (/* reexport safe */ _utils_registry__WEBPACK_IMPORTED_MODULE_3__.ComponentRegistry),
/* harmony export */   getRegistry: () => (/* binding */ getRegistry),
/* harmony export */   init: () => (/* binding */ init)
/* harmony export */ });
/* harmony import */ var _scss_roos_scss__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../scss/roos.scss */ "./src/scss/roos.scss");
/* harmony import */ var _components_button__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/button */ "./fe_src/ts/components/button.ts");
/* harmony import */ var _components_card__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/card */ "./fe_src/ts/components/card.ts");
/* harmony import */ var _utils_registry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./utils/registry */ "./fe_src/ts/utils/registry.ts");




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
}


})();

/******/ 	return __webpack_exports__;
/******/ })()
;
});
//# sourceMappingURL=roos.js.map