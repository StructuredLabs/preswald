// src/workers/PyodideWorker.ts
// This file will be used to create the web worker
let workerInstance = null;

// Create a worker factory function
export function createPyodideWorker() {
    console.log("Creating new worker instance");
    printMessage("Hello from workerJGJGJGJGJGJJG");
    if (workerInstance) {
        console.log("Reusing existing worker instance");
        return workerInstance;
    }

    // Define worker code as a string to be passed to Blob constructor
    const workerCode = `
      // Web Worker context
      console.log("Worker code loaded");
      self.window = self;
  
      // Import required Pyodide script
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js');
  
      // State variables
      let pyodide = null;
      let isInitialized = false;
      let isPreswaldInitialized = false;
      let activeScriptPath = null;
      let lastError = null;
  
      // Initialize Pyodide
      async function initializePyodide() {
        try {
          self.postMessage({ type: 'LOADING_STATUS', status: 'loading-pyodide' });
          
          // Load Pyodide
          pyodide = await loadPyodide({
            indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/',
          });
          
          self.postMessage({ type: 'LOADING_STATUS', status: 'setting-up-environment' });
          
          // Set browser mode flag
          pyodide.runPython(\`
            import js
            js.window.__PRESWALD_BROWSER_MODE = True
          \`);
          
          // Set up filesystem
          await pyodide.runPythonAsync(\`
            import os
            os.makedirs('/project', exist_ok=True)
            os.chdir('/project')
          \`);
          
          self.postMessage({ type: 'LOADING_STATUS', status: 'installing-packages' });
          
          // Install required packages
          await pyodide.loadPackage("micropip");
          await pyodide.runPythonAsync(\`
            import micropip
            await micropip.install('duckdb')
            await micropip.install('preswald==0.1.53')
            # await micropip.install("http://localhost:8000/preswald-0.1.52-py3-none-any.whl")
          \`);
          
          // Initialize Preswald - this will call expose_to_js() from your entrypoint.py
          await pyodide.runPythonAsync(\`
            import preswald.browser.entrypoint
          \`);
          
          // Now the self (worker's global scope) should have the preswaldInit, etc. functions
          isInitialized = true;
          self.postMessage({ type: 'READY' });
          
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
  
      // Load files to Pyodide filesystem
      async function loadFilesToFS(files) {
        try {
          if (!pyodide) throw new Error('Pyodide not initialized');
          
          self.postMessage({ type: 'LOADING_STATUS', status: 'loading-files' });
          
          // Process each file
          for (const [path, content] of Object.entries(files)) {
            // Ensure directory exists
            const dirPath = path.substring(0, path.lastIndexOf('/'));
            if (dirPath) {
              pyodide.runPython(\`
                import os
                os.makedirs('\${dirPath}', exist_ok=True)
              \`);
            }
            
            // Determine if it's binary or text content
            if (typeof content === 'string') {
              // Text file
              pyodide.FS.writeFile(path, content);
            } else if (content instanceof ArrayBuffer || ArrayBuffer.isView(content)) {
              // Binary file
              const uint8Array = new Uint8Array(content);
              pyodide.FS.writeFile(path, uint8Array);
            }
          }
          
          self.postMessage({ type: 'FILES_LOADED' });
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
  
      async function clearFilesystem() {
        try {
          if (!pyodide) throw new Error('Pyodide not initialized');
          
          self.postMessage({ type: 'LOADING_STATUS', status: 'clearing-filesystem' });
          
          await pyodide.runPythonAsync(\`
            import os
            import shutil
            
            os.makedirs('/project', exist_ok=True)
            
            for item in os.listdir('/project'):
                item_path = os.path.join('/project', item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
          \`);
          
          self.postMessage({ type: 'FILESYSTEM_CLEARED' });
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
  
      // Run a script using the preswaldRunScript function from your Python code
      async function runScript(scriptPath) {
        try {
          if (!pyodide || !isInitialized) throw new Error('Pyodide not initialized');
          
          self.postMessage({ type: 'LOADING_STATUS', status: 'running-script' });
          activeScriptPath = scriptPath;
          
          // Call the preswaldRunScript function that was exposed by your Python code
          const result = await self.preswaldRunScript(scriptPath);
          // Convert PyProxy to JS object
          const resultObj = result.toJs();
          
          if (resultObj.success === false) {
            self.postMessage({ 
              type: 'ERROR', 
              error: resultObj.error, 
              traceback: resultObj.traceback || ''
            });
            return false;
          }
          
          // Try to get components or any other needed data
          try {
            const componentsData = await pyodide.runPythonAsync(\`
              import json
              from preswald.browser.virtual_service import VirtualPreswaldService
              
              # Get the service instance
              service = VirtualPreswaldService.get_instance()
              
              # Get rendered components
              components = service.get_rendered_components()
              
              # Convert to JSON string
              json.dumps(components)
            \`);
            
            // Parse the components data
            const components = JSON.parse(componentsData);
            
            // Send result back to main thread
            self.postMessage({ 
              type: 'EXECUTION_RESULT', 
              components: components,
              scriptPath
            });
          } catch (error) {
            // If we can't get components, still report success but with empty components
            self.postMessage({ 
              type: 'EXECUTION_RESULT', 
              components: {},
              scriptPath
            });
          }
          
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
  
      // Update a component using the preswaldUpdateComponent function from your Python code
      async function updateComponent(componentId, value) {
        try {
          if (!pyodide || !isInitialized || !activeScriptPath) {
            throw new Error('Pyodide not initialized or no active script');
          }
          
          // Call the preswaldUpdateComponent function that was exposed by your Python code
          const result = await self.preswaldUpdateComponent(componentId, value);
          // Convert PyProxy to JS object
          const resultObj = result.toJs();
          
          if (resultObj.success === false) {
            self.postMessage({ type: 'ERROR', error: resultObj.error });
            return false;
          }
          
          // Try to get updated components
          try {
            const componentsData = await pyodide.runPythonAsync(\`
              import json
              from preswald.browser.virtual_service import VirtualPreswaldService
              
              # Get the service instance
              service = VirtualPreswaldService.get_instance()
              
              # Get rendered components
              components = service.get_rendered_components()
              
              # Convert to JSON string
              json.dumps(components)
            \`);
            
            // Parse the components data
            const components = JSON.parse(componentsData);
            
            // Send updated components back
            self.postMessage({ 
              type: 'COMPONENT_UPDATE', 
              components: components 
            });
          } catch (error) {
            // If we can't get components, still report success
            self.postMessage({ 
              type: 'COMPONENT_UPDATE', 
              components: {} 
            });
          }
          
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
      
      async function getBrandingInfo() {
        try {
          if (!pyodide || !isInitialized) throw new Error('Pyodide not initialized');

          // Get the PRESWALD_BRANDING object from the worker's window
          const brandingString = self.PRESWALD_BRANDING;

          let brandingObject = {};
          if (brandingString && typeof brandingString === 'string') {
            try {
              brandingObject = JSON.parse(brandingString);
            } catch (err) {
              console.error("Error parsing branding JSON:", err);
            }
          }

          // Send it back to the main thread
          self.postMessage({ 
            type: 'BRANDING_INFO', 
            data: brandingObject || {} // Send empty object if undefined
          });

          return true;
        } catch (error) {
          self.postMessage({ type: 'ERROR', error: error.message });
          return false;
        }
      }
  
      // Serialize the filesystem (extract files)
      async function serializeFilesystem() {
        try {
          if (!pyodide) throw new Error('Pyodide not initialized');
          
          const fsSnapshot = await pyodide.runPythonAsync(\`
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
                            # Handle binary files
                            with open(full_path, 'rb') as f:
                              binary_content = f.read()
                            encoded = base64.b64encode(binary_content).decode('ascii')
                            result[rel_path] = {'type': 'binary', 'content': encoded}
                        
                return result
            
            result_data = serialize_fs()
            json.dumps(result_data)
          \`);
          
          return JSON.parse(fsSnapshot);
        } catch (error) {
          lastError = error.message;
          self.postMessage({ type: 'ERROR', error: error.message });
          return null;
        }
      }
  
      async function listFilesInDirectory(directory) {
        try {
          if (!pyodide || !isInitialized) throw new Error('Pyodide not initialized');
          
          const filesListString = await pyodide.runPythonAsync(\`
            import os
            import json
            
            result = {}
            try:
                directory = "\${directory}"
                files = os.listdir(directory)
                result = files
            except Exception as e:
                result = {"error": str(e)}
            
            json.dumps(result)
          \`);
          
          const result = JSON.parse(filesListString);
          
          // Check if we got an error
          if (result && result.error) {
            throw new Error(result.error);
          }
          
          self.postMessage({ 
            type: 'DIRECTORY_LISTING', 
            directory: directory,
            files: result
          });
          
          return true;
        } catch (error) {
          lastError = error.message;
          self.postMessage({ 
            type: 'ERROR', 
            error: error.message,
            operation: 'listFilesInDirectory'
          });
          return false;
        }
      }
  
      async function generateAndApplyCode(scriptPath, openAIResponse) {
        try {
          if (!pyodide || !isInitialized) throw new Error('Pyodide not initialized');
          
          let currentContent;
          try {
            currentContent = pyodide.FS.readFile(scriptPath, { encoding: 'utf8' });
          } catch (error) {
            throw new Error(\`Could not read file at \${scriptPath}: \${error.message}\`);
          }
          
          const newContent = \`\${currentContent}\n\n# Generated plot\n\${openAIResponse}\n\n\`;
          
          try {
            pyodide.FS.writeFile(scriptPath, newContent);
            
            self.postMessage({ 
              type: 'CODE_GENERATION_RESULT', 
              success: true,
              scriptPath,
              content: newContent
            });
            
            return true;
          } catch (error) {
            throw new Error(\`Could not write to file at \${scriptPath}: \${error.message}\`);
          }
        } catch (error) {
          lastError = error.message;
          self.postMessage({ 
            type: 'ERROR', 
            error: error.message,
            operation: 'generateAndApplyCode'
          });
          return false;
        }
      }
  
      // Message handler
      self.onmessage = async function(event) {
        const { type, data } = event.data;

        self.postMessage({ type: 'RECEIVED_MESSAGE', data: event.data });

        switch (type) {
          case 'INITIALIZE':
            console.log("Initializing worker");
            await initializePyodide();
            break;
            
          case 'LOAD_FILES':
            await loadFilesToFS(data.files);
            break;
            
          case 'CLEAR_FILESYSTEM':
            await clearFilesystem();
            break;
            
          case 'RUN_SCRIPT':
            await runScript(data.scriptPath);
            break;
            
          case 'UPDATE_COMPONENT':
            await updateComponent(data.componentId, data.value);
            break;
            
          case 'SERIALIZE_FS':
            const fsSnapshot = await serializeFilesystem();
            self.postMessage({ 
              type: 'FS_SNAPSHOT', 
              snapshot: fsSnapshot 
            });
            break;
          
          case 'GET_BRANDING':
            await getBrandingInfo();
            break;
            
          case 'GENERATE_AND_APPLY_CODE':
            await generateAndApplyCode(data.scriptPath, data.generatedCode);
            break;
            
          case 'LIST_DIRECTORY':
            await listFilesInDirectory(data.directory);
            break;
            
          case 'SHUTDOWN':
            // Clean up resources
            if (pyodide && isInitialized) {
              try {
                // Call the shutdown function from your Python code
                await self.preswaldShutdown();
              } catch (e) {
                console.error('Error during shutdown:', e);
              }
            }
            
            self.postMessage({ type: 'TERMINATED' });
            // Close the worker
            self.close();
            break;
            
          default:
            self.postMessage({ 
              type: 'ERROR', 
              error: \`Unknown message type: \${type}\` 
            });
        }
      };
    `;

    // Create a blob from the worker code
    const blob = new Blob([workerCode], { type: "application/javascript" });
    const workerUrl = URL.createObjectURL(blob);

    // Create and return the worker
    const worker = new Worker(workerUrl);

    // Clean up the URL when no longer needed
    worker.addEventListener("message", (event) => {
        console.log("Worker message", event);
        if (event.data.type === "TERMINATED") {
            URL.revokeObjectURL(workerUrl);
            workerInstance = null;
        }
    });

    workerInstance = worker;

    return worker;
}

export function disposeWorker() {
    if (workerInstance) {
        workerInstance.postMessage({ type: "SHUTDOWN" });
        workerInstance = null;
    }
}
