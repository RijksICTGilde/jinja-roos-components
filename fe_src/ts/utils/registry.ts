/**
 * Component Registry - Manages component lifecycle and initialization
 */

export interface Component {
    selector: string;
    init(element: Element): void;
    destroy?(element: Element): void;
}

export class ComponentRegistry {
    private components: Map<string, Component> = new Map();
    private initializedElements: WeakSet<Element> = new WeakSet();

    /**
     * Register a component
     */
    register(name: string, component: Component): void {
        this.components.set(name, component);
    }

    /**
     * Initialize all registered components
     */
    initializeAll(): void {
        this.components.forEach((component, name) => {
            this.initializeComponent(name, component);
        });
    }

    /**
     * Initialize a specific component
     */
    initializeComponent(name: string, component: Component): void {
        const elements = document.querySelectorAll(component.selector);
        
        elements.forEach(element => {
            // Skip if already initialized
            if (this.initializedElements.has(element)) {
                return;
            }

            try {
                component.init(element);
                this.initializedElements.add(element);
            } catch (error) {
                console.error(`Error initializing ${name} component:`, error);
            }
        });
    }

    /**
     * Get a registered component
     */
    get(name: string): Component | undefined {
        return this.components.get(name);
    }

    /**
     * Destroy all components for a given element
     */
    destroyElement(element: Element): void {
        this.components.forEach((component) => {
            if (element.matches(component.selector) && component.destroy) {
                component.destroy(element);
                this.initializedElements.delete(element);
            }
        });
    }

    /**
     * List all registered component names
     */
    list(): string[] {
        return Array.from(this.components.keys());
    }
}