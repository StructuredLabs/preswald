importScripts('https://unpkg.com/comlink/dist/umd/comlink.js');
console.log('[Worker] Loading Comlink...');

console.log('[Worker] About to load Pyodide...');
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js');
console.log(
  '[Worker] Pyodide script loaded, loadPyodide exists?',
  typeof loadPyodide === 'function'
);

// Web Worker context
console.log('[Worker] Worker code loaded');
self.window = self;

class PreswaldWorker {
  constructor() {
    console.log('[Worker] Initializing PreswaldWorker');
    this.pyodide = null;
    this.isInitialized = false;
    this.activeScriptPath = null;
    this.components = {};
    this.stateChangeCallbacks = new Set();
  }

  async initializePyodide() {
    console.log('[Worker] Starting Pyodide initialization');
    try {
      // Load Pyodide
      console.log('[Worker] About to call loadPyodide');
      //this.pyodide = await loadPyodide({
      //    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/',
      //});
      console.log('[Worker] loadPyodide resolved');

      // Set browser mode flag
      console.log('[Worker] Setting browser mode flag');
      this.pyodide.runPython(`
                import js
                js.window.__PRESWALD_BROWSER_MODE = True
            `);

      // Set up filesystem
      console.log('[Worker] Setting up filesystem');
      await this.pyodide.runPythonAsync(`
                import os
                os.makedirs('/project', exist_ok=True)
                os.chdir('/project')
            `);

      // Write initial files
      console.log('[Worker] Writing initial configuration files');
      this.pyodide.FS.writeFile(
        'preswald.toml',
        `[project]
title = "Preswald Tutorial"
version = "0.1.0"
port = 8501
entrypoint = "hello.py"
slug = "preswald-test"

[branding]
name = "Preswald Tutorial"
logo = "images/logo.png"
favicon = "images/favicon.ico"
primaryColor = "#000000"`
      );

      this.pyodide.FS.writeFile(
        'hello.py',
        `import preswald as pw
pw.text("Hello from Preswald!")`
      );

      // Install required packages
      console.log('[Worker] Installing required packages');
      await this.pyodide.runPythonAsync(`
                import micropip
                await micropip.install('duckdb')
                await micropip.install("http://localhost:8000/preswald-0.1.53-py3-none-any.whl")
            `);
      console.log('[Worker] Packages installed successfully');

      // Initialize Preswald
      console.log('[Worker] Initializing Preswald');
      await this.pyodide.runPythonAsync(`
                import preswald.browser.entrypoint
            `);

      this.isInitialized = true;
      console.log('[Worker] Pyodide initialization complete');
      return true;
    } catch (error) {
      console.error('[Worker] Initialization error:', error);
      throw error;
    }
  }

  async runScript(scriptPath) {
    console.log('[Worker] Running script:', scriptPath);
    if (!this.isInitialized) {
      console.error('[Worker] Cannot run script - Pyodide not initialized');
      throw new Error('Pyodide not initialized');
    }

    try {
      this.activeScriptPath = scriptPath;

      // Run the script
      console.log('[Worker] Executing script through preswaldRunScript');
      const result = await self.preswaldRunScript(scriptPath);
      const resultObj = result.toJs();
      console.log('[Worker] Script execution result:', resultObj);

      if (!resultObj.success) {
        console.error('[Worker] Script execution failed:', resultObj.error);
        throw new Error(resultObj.error || 'Script execution failed');
      }

      // Get updated components
      console.log('[Worker] Fetching updated components');
      await this._updateComponents();
      console.log('[Worker] Current components:', this.components);

      return {
        success: true,
        components: this.components,
      };
    } catch (error) {
      console.error('[Worker] Script execution error:', error);
      throw new Error(`Script execution error: ${error.message}`);
    }
  }

  async updateComponent(componentId, value) {
    console.log('[Worker] Updating component:', componentId, 'with value:', value);
    if (!this.isInitialized || !this.activeScriptPath) {
      console.error('[Worker] Cannot update component - not initialized or no active script');
      throw new Error('Not initialized or no active script');
    }

    try {
      console.log('[Worker] Calling preswaldUpdateComponent');
      const result = await self.preswaldUpdateComponent(componentId, value);
      const resultObj = result.toJs();
      console.log('[Worker] Update result:', resultObj);

      if (!resultObj.success) {
        console.error('[Worker] Component update failed:', resultObj.error);
        throw new Error(resultObj.error || 'Component update failed');
      }

      // Get updated components
      console.log('[Worker] Fetching updated components after update');
      await this._updateComponents();
      console.log('[Worker] Updated components:', this.components);

      return {
        success: true,
        components: this.components,
      };
    } catch (error) {
      console.error('[Worker] Component update error:', error);
      throw new Error(`Component update error: ${error.message}`);
    }
  }

  async _updateComponents() {
    console.log('[Worker] Updating internal components state');
    const componentsData = await this.pyodide.runPythonAsync(`
            import json
            from preswald.browser.virtual_service import VirtualPreswaldService
            
            service = VirtualPreswaldService.get_instance()
            components = service.get_rendered_components()
            json.dumps(components)
        `);

    this.components = JSON.parse(componentsData);
    console.log('[Worker] Components updated:', this.components);
    return this.components;
  }

  async getComponents() {
    return this.components;
  }

  async loadFilesToFS(files) {
    if (!this.pyodide) throw new Error('Pyodide not initialized');

    try {
      for (const [path, content] of Object.entries(files)) {
        const dirPath = path.substring(0, path.lastIndexOf('/'));
        if (dirPath) {
          this.pyodide.runPython(`
                        import os
                        os.makedirs('${dirPath}', exist_ok=True)
                    `);
        }

        if (typeof content === 'string') {
          this.pyodide.FS.writeFile(path, content);
        } else if (content instanceof ArrayBuffer || ArrayBuffer.isView(content)) {
          this.pyodide.FS.writeFile(path, new Uint8Array(content));
        }
      }
      return true;
    } catch (error) {
      throw new Error(`File loading error: ${error.message}`);
    }
  }

  async clearFilesystem() {
    if (!this.pyodide) throw new Error('Pyodide not initialized');

    try {
      await this.pyodide.runPythonAsync(`
                import os
                import shutil
                
                for item in os.listdir('/project'):
                    item_path = os.path.join('/project', item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            `);
      return true;
    } catch (error) {
      throw new Error(`Filesystem clear error: ${error.message}`);
    }
  }

  async shutdown() {
    if (this.pyodide && this.isInitialized) {
      try {
        await self.preswaldShutdown?.();
      } catch (e) {
        console.error('Shutdown error:', e);
      }
    }
    self.close();
  }
}

// Create and expose the worker instance
const worker = new PreswaldWorker();
Comlink.expose(worker);
