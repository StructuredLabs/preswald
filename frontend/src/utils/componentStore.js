class ComponentStore {
    constructor() {
        this.components = new Map();
        this.listeners = new Set();
        this.errors = new Map();  // Track errors by componentId
    }

    setComponents(components) {
        // Start fresh with new component list
        this.components = new Map();
        this.errors = new Map();
        
        components.forEach(component => {
            if (component.id) {
                // Keep existing value if we have it, otherwise use new value
                const existingState = this.components.get(component.id);
                this.components.set(component.id, 
                    existingState !== undefined ? existingState : component.value
                );
            }
        });
        this._notifyListeners();
    }

    updateComponent(componentId, value) {
        if (componentId) {
            this.components.set(componentId, value);
            // Clear any errors when we successfully update
            this.errors.delete(componentId);
            this._notifyListeners();
        }
    }

    setError(componentId, error) {
        if (componentId) {
            this.errors.set(componentId, error);
            this._notifyListeners();
        }
    }

    getComponent(componentId) {
        return {
            value: this.components.get(componentId),
            error: this.errors.get(componentId)
        };
    }

    getAllComponents() {
        return Array.from(this.components.entries()).map(([id, value]) => ({
            id,
            value,
            error: this.errors.get(id)
        }));
    }

    subscribe(listener) {
        this.listeners.add(listener);
        // Immediately notify with current state
        listener(this.getAllComponents());
        return () => this.listeners.delete(listener);
    }

    _notifyListeners() {
        const components = this.getAllComponents();
        this.listeners.forEach(listener => {
            try {
                listener(components);
            } catch (error) {
                console.error("[ComponentStore] Error in listener:", error);
            }
        });
    }
}

export const componentStore = new ComponentStore();