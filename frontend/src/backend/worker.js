import * as Comlink from 'comlink';

self.window = self;

let _loadPyodidePromise = null;
async function _getLoadPyodide() {
  if (!_loadPyodidePromise) {
    _loadPyodidePromise = import(
      /* @vite-ignore */ 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.mjs'
    ).then((mod) => mod.loadPyodide);
  }
  return _loadPyodidePromise;
}

class PreswaldWorker {
  constructor() {
    console.log('[Worker] Initializing PreswaldWorker');
    this.pyodide = null;
    this.isInitialized = false;
    this.activeScriptPath = null;
    this.components = {};
  }

  async initializePyodide() {
    console.log('[Worker] Starting Pyodide initialization');
    try {
      const loadPyodide = await _getLoadPyodide();
      // Load Pyodide
      console.log('[Worker] About to call loadPyodide');
      this.pyodide = await loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/',
      });
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

      // Inject matplotlibrc file to set backend
      console.log('[Worker] Configuring matplotlib');
      await this.pyodide.loadPackage('matplotlib');
      await this.pyodide.runPythonAsync(`
        with open("/matplotlibrc", "w") as f:
          f.write("backend: agg\\n")
        import matplotlib
        matplotlib.use("agg")`);

      // Install required packages
      console.log('[Worker] Installing required packages');
      await this.pyodide.loadPackage('micropip');
      await this.pyodide.runPythonAsync(`
                import micropip
                await micropip.install('duckdb')
                await micropip.install('preswald')
                # await micropip.install("http://localhost:8000/preswald-0.1.54-py3-none-any.whl")
            `);

      // Initialize Preswald
      console.log('[Worker] Initializing Preswald');
      await this.pyodide.runPythonAsync(`
                import preswald.browser.entrypoint
            `);

      // TODO: Do we need to call preswaldInit() here? if not, we can remove it from the entrypoint.py
      this.isInitialized = true;
      console.log('[Worker] Initialization complete');
      return { success: true };
    } catch (error) {
      console.error('[Worker] Initialization error:', error);
      throw error;
    }
  }

  async runScript(scriptPath) {
    console.log('[Worker] Running script:', scriptPath);
    if (!this.isInitialized) {
      throw new Error('Pyodide not initialized');
    }

    try {
      this.activeScriptPath = scriptPath;
      const result = await self.preswaldRunScript(scriptPath);
      const resultObj = result.toJs();

      if (!resultObj.success) {
        throw new Error(resultObj.error || 'Script execution failed');
      }

      // Get components
      const componentsData = await this.pyodide.runPythonAsync(`
                import json
                from preswald.browser.virtual_service import VirtualPreswaldService
                service = VirtualPreswaldService.get_instance()
                components = service.get_rendered_components()
                json.dumps(components)
            `);

      this.components = JSON.parse(componentsData);
      return { success: true, components: this.components };
    } catch (error) {
      console.error('[Worker] Script execution error:', error);
      throw error;
    }
  }

  async updateComponent(componentId, value) {
    console.log('[Worker] Updating component:', componentId, value);
    if (!this.isInitialized || !this.activeScriptPath) {
      throw new Error('Not initialized or no active script');
    }

    try {
      const result = await self.preswaldUpdateComponent(componentId, value);
      const resultObj = result.toJs();

      if (!resultObj.success) {
        throw new Error(resultObj.error || 'Component update failed');
      }

      // Get updated components
      const componentsData = await this.pyodide.runPythonAsync(`
                import json
                from preswald.browser.virtual_service import VirtualPreswaldService
                service = VirtualPreswaldService.get_instance()
                components = service.get_rendered_components()
                json.dumps(components)
            `);

      this.components = JSON.parse(componentsData);
      return { success: true, components: this.components };
    } catch (error) {
      console.error('[Worker] Component update error:', error);
      throw error;
    }
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
      return { success: true };
    } catch (error) {
      console.error('[Worker] File loading error:', error);
      throw error;
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
      return { success: true };
    } catch (error) {
      console.error('[Worker] Filesystem clear error:', error);
      throw error;
    }
  }

  async serializeFilesystem() {
    try {
      if (!this.pyodide) throw new Error('Pyodide not initialized');

      const fsSnapshot = await this.pyodide.runPythonAsync(`
                import os
                import json
                import base64
                
                def serialize_fs(root_dir='/project'):
                    result = {}
                    for root, dirs, files in os.walk(root_dir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, root_dir)
                            
                            try:
                                with open(full_path, 'r') as f:
                                  content = f.read()
                                result[rel_path] = {'type': 'text', 'content': content}
                            except UnicodeDecodeError:
                                with open(full_path, 'rb') as f:
                                  binary_content = f.read()
                                encoded = base64.b64encode(binary_content).decode('ascii')
                                result[rel_path] = {'type': 'binary', 'content': encoded}
                            
                    return result
                
                result_data = serialize_fs()
                json.dumps(result_data)
            `);

      return { success: true, snapshot: JSON.parse(fsSnapshot) };
    } catch (error) {
      console.error('[Worker] Filesystem serialization error:', error);
      throw error;
    }
  }

  async getBrandingInfo() {
    try {
      if (!this.pyodide || !this.isInitialized) {
        throw new Error('Pyodide not initialized');
      }

      const brandingString = self.PRESWALD_BRANDING;
      let brandingObject = {};

      if (brandingString && typeof brandingString === 'string') {
        try {
          brandingObject = JSON.parse(brandingString);
        } catch (err) {
          console.error('Error parsing branding JSON:', err);
        }
      }

      return { success: true, data: brandingObject };
    } catch (error) {
      console.error('[Worker] Branding info error:', error);
      throw error;
    }
  }

  // TODO: DELETE
  async listFilesInDirectory(directory) {
    try {
      if (!this.pyodide || !this.isInitialized) {
        throw new Error('Pyodide not initialized');
      }

      const filesListString = await this.pyodide.runPythonAsync(`
                import os
                import json
                
                result = {}
                try:
                    directory = "${directory}"
                    files = os.listdir(directory)
                    result = files
                except Exception as e:
                    result = {"error": str(e)}
                
                json.dumps(result)
            `);

      const result = JSON.parse(filesListString);
      if (result && result.error) {
        throw new Error(result.error);
      }

      return { success: true, files: result };
    } catch (error) {
      console.error('[Worker] Directory listing error:', error);
      throw error;
    }
  }

  async exportHtml(scriptPath) {
    console.log('[Worker] Exporting HTML for script:', scriptPath);
    if (!this.isInitialized) {
      throw new Error('Pyodide not initialized');
    }
    if (!this.activeScriptPath && !scriptPath) {
      throw new Error('No active script path provided for export.');
    }

    // Use provided scriptPath or the active one
    const pathToExport = scriptPath || this.activeScriptPath;

    try {
      // Call the Python function exposed on self (window)
      const result = await self.preswaldExportHtml(pathToExport);
      // Ensure correct conversion for the nested 'files' dictionary,
      // which contains Uint8Array values that should be preserved.
      const resultObj = result.toJs({
        dict_converter: Object.fromEntries,
        create_pyproxies: false, // Avoid creating PyProxies for values in the files dict
      });
      result.destroy(); // Clean up the PyProxy

      if (!resultObj.success) {
        throw new Error(resultObj.error || 'HTML export failed');
      }

      // resultObj.files will be a JS object like:
      // {
      //   "index.html": Uint8Array(...),
      //   "project_fs.json": Uint8Array(...),
      //   "assets/logo.png": Uint8Array(...),
      //   "_assets/some_file_component_asset.csv": Uint8Array(...)
      // }
      // The keys are relative paths, values are Uint8Arrays (binary content)
      console.log(
        '[Worker] HTML export successful, files received:',
        Object.keys(resultObj.files || {})
      );
      return { success: true, files: resultObj.files, message: resultObj.message };
    } catch (error) {
      console.error('[Worker] HTML export error:', error);
      throw error; // Re-throw to be caught by Comlink/caller
    }
  }

  async shutdown() {
    if (this.pyodide && this.isInitialized) {
      try {
        await self.preswaldShutdown();
      } catch (e) {
        console.error('Shutdown error:', e);
      }
    }
    self.close();
  }
}

// Create and expose the worker instance - this is all we need
const worker = new PreswaldWorker();
Comlink.expose(worker);
