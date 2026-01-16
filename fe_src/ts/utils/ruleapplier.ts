/**
 * Declarative Rule Application System
 * Applies CSS-like selector rules with actions to DOM elements
 *
 * USAGE
 * =====
 *
 * Basic Usage:
 * ------------
 * <button onclick="applyRules('self: +active', event)">Click</button>
 *
 * Multiple Rules (separated by semicolon):
 * ----------------------------------------
 * applyRules('self: +active; siblings: -active', event)
 *
 * SELECTORS
 * =========
 *
 * Special Selectors:
 *   self              - The clicked element itself
 *   siblings          - All sibling elements
 *   parent            - Direct parent element
 *
 * Combined Selectors:
 *   self > a          - Direct child <a> elements of clicked element
 *   self .active      - Descendant elements with class 'active'
 *   parent > div      - Direct child divs of parent
 *
 * CSS Combinators:
 *   ~ selector        - Following siblings (general sibling combinator)
 *   + selector        - Next sibling (adjacent sibling combinator)
 *   > selector        - Direct children (child combinator)
 *   ^ selector        - Closest parent matching selector (traverse up)
 *
 * ACTIONS
 * =======
 *
 * Class Operations:
 *   +classname        - Add a single class
 *   -classname        - Remove a single class
 *   +[c1,c2,c3]       - Add multiple classes
 *   -[c1,c2,c3]       - Remove multiple classes
 *
 * Attribute Operations:
 *   attr=value        - Set attribute to value
 */

interface Rule {
    selector: string;
    actions: Action[];
}

interface Action {
    type: 'addClass' | 'removeClass' | 'setAttribute';
    classes?: string[];
    attribute?: string;
    value?: string;
}

interface ApplyRulesOptions {
    preventDefault?: boolean;
    stopPropagation?: boolean;
}

class RuleApplier {
    private debug = false;

    applyRules(rulesString: string, clickedElement: Element): void {
        try {
            const rules = this.parseRules(rulesString);
            this.executeRules(rules, clickedElement);
        } catch (error) {
            console.error('Rule application failed:', (error as Error).message);
            throw error;
        }
    }

    private parseRules(rulesString: string): Rule[] {
        const rules: Rule[] = [];
        const statements = this.tokenizeStatements(rulesString);

        for (const statement of statements) {
            const rule = this.parseStatement(statement);
            if (rule) rules.push(rule);
        }

        return rules;
    }

    private tokenizeStatements(rulesString: string): string[] {
        const cleaned = rulesString.trim();
        if (!cleaned) {
            throw new Error('Empty rules string provided');
        }

        const statements: string[] = [];
        let current = '';
        let inQuotes = false;
        let quoteChar: string | null = null;

        for (let i = 0; i < cleaned.length; i++) {
            const char = cleaned[i];

            if ((char === '"' || char === "'") && cleaned[i - 1] !== '\\') {
                if (!inQuotes) {
                    inQuotes = true;
                    quoteChar = char;
                } else if (char === quoteChar) {
                    inQuotes = false;
                    quoteChar = null;
                }
            }

            if (char === ';' && !inQuotes) {
                if (current.trim()) {
                    statements.push(current.trim());
                }
                current = '';
            } else {
                current += char;
            }
        }

        if (current.trim()) {
            statements.push(current.trim());
        }

        return statements;
    }

    private parseStatement(statement: string): Rule | null {
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

    private parseActions(actionsString: string): Action[] {
        const actions: Action[] = [];
        const tokens = this.tokenizeActions(actionsString);

        for (const token of tokens) {
            const action = this.parseActionToken(token);
            if (action) actions.push(action);
        }

        return actions;
    }

    private tokenizeActions(actionsString: string): string[] {
        const tokens: string[] = [];
        let current = '';
        let inBrackets = false;

        for (let i = 0; i < actionsString.length; i++) {
            const char = actionsString[i];

            if (char === '[') {
                inBrackets = true;
                current += char;
            } else if (char === ']') {
                inBrackets = false;
                current += char;
            } else if (char === ' ' && !inBrackets) {
                if (current.trim()) {
                    tokens.push(current.trim());
                }
                current = '';
            } else {
                current += char;
            }
        }

        if (current.trim()) {
            tokens.push(current.trim());
        }

        return tokens;
    }

    private parseActionToken(token: string): Action | null {
        if (token.startsWith('+')) {
            const value = token.substring(1);

            if (value.startsWith('[') && value.endsWith(']')) {
                const classList = value.slice(1, -1).split(',').map(c => c.trim());
                return { type: 'addClass', classes: classList };
            } else {
                return { type: 'addClass', classes: [value] };
            }
        }

        if (token.startsWith('-')) {
            const value = token.substring(1);

            if (value.startsWith('[') && value.endsWith(']')) {
                const classList = value.slice(1, -1).split(',').map(c => c.trim());
                return { type: 'removeClass', classes: classList };
            } else {
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

    private resolveSelector(selector: string, clickedElement: Element): Element[] {
        const interpolated = this.interpolateVariables(selector, clickedElement);

        if (interpolated === 'self' || interpolated.startsWith('self ') || interpolated.startsWith('self>')) {
            const baseElements = [clickedElement];
            const remainder = interpolated.substring(4).trim();
            if (!remainder) return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }

        if (interpolated === 'siblings' || interpolated.startsWith('siblings ') || interpolated.startsWith('siblings>')) {
            const parent = clickedElement.parentElement;
            if (!parent) return [];
            const baseElements = Array.from(parent.children).filter(el => el !== clickedElement);
            const remainder = interpolated.substring(8).trim();
            if (!remainder) return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }

        if (interpolated === 'parent' || interpolated.startsWith('parent ') || interpolated.startsWith('parent>')) {
            const baseElements = clickedElement.parentElement ? [clickedElement.parentElement] : [];
            const remainder = interpolated.substring(6).trim();
            if (!remainder) return baseElements;
            return this.queryFromElements(baseElements, remainder);
        }

        if (interpolated.startsWith('~')) {
            const selectorPart = interpolated.substring(1).trim();
            const siblings: Element[] = [];
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
        } catch {
            throw new Error(`Invalid selector: "${selector}"`);
        }
    }

    private queryFromElements(elements: Element[], selectorPart: string): Element[] {
        const results: Element[] = [];
        for (const element of elements) {
            if (selectorPart.startsWith('>')) {
                const childSelector = selectorPart.substring(1).trim();
                if (!childSelector) {
                    results.push(...Array.from(element.children));
                } else {
                    results.push(...Array.from(element.querySelectorAll(':scope > ' + childSelector)));
                }
            } else if (selectorPart) {
                results.push(...Array.from(element.querySelectorAll(selectorPart)));
            }
        }
        return results;
    }

    private interpolateVariables(selector: string, element: Element): string {
        return selector.replace(/\{([^}]+)\}/g, (match, varName) => {
            if (varName.startsWith('data-')) {
                return (element as HTMLElement).dataset[varName.substring(5)] || '';
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

    private executeRules(rules: Rule[], clickedElement: Element): void {
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

    private applyActions(element: Element, actions: Action[]): void {
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

export function applyRules(rulesString: string, event: Event | null, options: ApplyRulesOptions = {}): void {
    if (options.preventDefault && event?.preventDefault) {
        event.preventDefault();
    }
    if (options.stopPropagation && event?.stopPropagation) {
        event.stopPropagation();
    }

    const clickedElement = (event?.currentTarget || event?.target) as Element;

    if (!clickedElement) {
        console.error('No element found for rule application');
        return;
    }

    try {
        ruleApplier.applyRules(rulesString, clickedElement);
    } catch (error) {
        console.error('Rule Application Error:', error);
    }
}

export { RuleApplier };
