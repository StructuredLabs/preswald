import * as Comlink from 'comlink';
// importScripts('https://unpkg.com/comlink/dist/umd/comlink.js');
// importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js');
import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.mjs';

self.window = self;

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
pw.text("Hello from Preswald!")
val = pw.slider("Slider", 0, 100, 0)
pw.text(f"Slider value: {val}")`
      );

      // Install required packages
      console.log('[Worker] Installing required packages');
      await this.pyodide.loadPackage('micropip');
      await this.pyodide.runPythonAsync(`
                import micropip
                await micropip.install('duckdb')
                # await micropip.install('preswald==0.1.53')
                await micropip.install("http://localhost:8000/preswald-0.1.53-py3-none-any.whl")
            `);

      // Initialize Preswald
      console.log('[Worker] Initializing Preswald');
      await this.pyodide.runPythonAsync(`
                import preswald.browser.entrypoint
            `);

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

  async generateAndApplyCode(scriptPath, openAIResponse) {
    try {
      if (!this.pyodide || !this.isInitialized) {
        throw new Error('Pyodide not initialized');
      }

      let currentContent;
      try {
        currentContent = this.pyodide.FS.readFile(scriptPath, { encoding: 'utf8' });
      } catch (error) {
        throw new Error(`Could not read file at ${scriptPath}: ${error.message}`);
      }

      const newContent = `${currentContent}\n\n# Generated plot\n${openAIResponse}\n\n`;

      try {
        this.pyodide.FS.writeFile(scriptPath, newContent);
        return { success: true, scriptPath, content: newContent };
      } catch (error) {
        throw new Error(`Could not write to file at ${scriptPath}: ${error.message}`);
      }
    } catch (error) {
      console.error('[Worker] Code generation error:', error);
      throw error;
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

// Create and expose the worker instance - this is all we need
const worker = new PreswaldWorker();
Comlink.expose(worker);
