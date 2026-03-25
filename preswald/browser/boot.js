/**
 * Boot script for Preswald HTML export
 * This gets appended to index.html during export
 */
async function boot() {
    console.log('[Boot] Starting boot process...');

    // Wait for the communication layer to be initialized
    let comm = window.__PRESWALD_COMM;
    let retryCount = 0;
    const maxRetries = 50; // 5 seconds with 100ms intervals

    while (!comm && retryCount < maxRetries) {
        console.log(`[Boot] Waiting for PRESWALD_COMM... (${retryCount + 1}/${maxRetries})`);
        await new Promise(resolve => setTimeout(resolve, 100));
        comm = window.__PRESWALD_COMM;
        retryCount++;
    }

    if (!comm) {
        console.error('[Boot] Error: window.__PRESWALD_COMM is not initialized after timeout');
        console.error('[Boot] Make sure the communication layer is properly set up for HTML export');
        return;
    }

    console.log('[Boot] PRESWALD_COMM found, proceeding with initialization');

    // Wait until the worker finished initialising
    await new Promise((resolve) => {
        const unsub = comm.subscribe((msg) => {
            if (msg.type === 'connection_status' && msg.connected) {
                unsub();
                resolve();
            }
        });
    });

    // Use embedded project FS if available (single-file export), otherwise fetch
    let raw;
    if (window.__PRESWALD_PROJECT_FS) {
        console.log('[Boot] Using embedded project filesystem data');
        raw = window.__PRESWALD_PROJECT_FS;
    } else {
        const resp = await fetch('project_fs.json');
        raw = await resp.json();
    }

    // Convert it to the shape loadFilesToFS expects
    const files = {};
    for (const [path, entry] of Object.entries(raw)) {
        if (entry.type === 'text') {
            files[path] = entry.content;
        } else if (entry.type === 'binary') {
            files[path] = Uint8Array.from(atob(entry.content), (c) => c.charCodeAt(0));
        }
    }

    await comm.loadFilesToFS(files);
    console.log('[HTML-export] Project copied into /project');

    // Run the entrypoint script
    console.log('[Client] Running initial script');
    comm.runScript('/project/' + (raw.__entrypoint__ || 'hello.py'));
}

window.addEventListener('load', boot);
