import express from 'express';
import { createServer as createViteServer } from 'vite';
import { spawn, ChildProcess } from 'child_process';
import http from 'http';
import path from 'path';

const app = express();
const PORT = 3000;
const PYTHON_PORT = process.env.PYTHON_PORT || 8001;
const PYTHON_BASE_URL = `http://127.0.0.1:${PYTHON_PORT}`;

let pythonProcess: ChildProcess | null = null;

// Start Python FastAPI backend in background if not already running
function startPythonBackend() {
  console.log(`[MY PC REMEMBERS] Checking Python FastAPI backend on port ${PYTHON_PORT}...`);
  
  // Test if already running
  const req = http.get(`${PYTHON_BASE_URL}/api/health`, (res) => {
    if (res.statusCode === 200) {
      console.log(`[MY PC REMEMBERS] Python backend already active on ${PYTHON_BASE_URL}`);
    }
  });

  req.on('error', () => {
    console.log(`[MY PC REMEMBERS] Launching Python backend process...`);
    const env = { ...process.env, PYTHONPATH: process.cwd() };
    
    pythonProcess = spawn('python3', [
      '-m', 'uvicorn',
      'backend.app.main:app',
      '--host', '127.0.0.1',
      '--port', String(PYTHON_PORT)
    ], {
      cwd: process.cwd(),
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    pythonProcess.stdout?.on('data', (data) => {
      const msg = data.toString().trim();
      if (msg) console.log(`[Python] ${msg}`);
    });

    pythonProcess.stderr?.on('data', (data) => {
      const msg = data.toString().trim();
      if (msg) console.error(`[Python Err] ${msg}`);
    });

    pythonProcess.on('exit', (code) => {
      console.log(`[Python] Process exited with code ${code}`);
    });
  });
}

// Clean up child process on shutdown
process.on('SIGINT', () => {
  if (pythonProcess) pythonProcess.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  if (pythonProcess) pythonProcess.kill();
  process.exit(0);
});

// Proxy /api/* requests to FastAPI backend on port 8000
app.use('/api', (req, res) => {
  const targetUrl = `${PYTHON_BASE_URL}/api${req.url}`;
  
  const headers = { ...req.headers };
  delete headers.host;

  const proxyReq = http.request(targetUrl, {
    method: req.method,
    headers: headers,
    timeout: 15000,
  }, (proxyRes) => {
    res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    // If Python backend is still starting up
    if (req.url === '/health') {
      res.json({
        status: 'starting',
        app: 'MY PC REMEMBERS',
        version: '0.1.0',
        indexed_files: 0,
        device: 'Initializing local Python runtime...',
        local_mode: true
      });
      return;
    }
    res.status(503).json({
      error: 'Backend initializing or temporarily unavailable',
      detail: err.message
    });
  });

  req.pipe(proxyReq, { end: true });
});

async function main() {
  startPythonBackend();

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.resolve(process.cwd(), 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(process.cwd(), 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[MY PC REMEMBERS] Server listening at http://localhost:${PORT}`);
  });
}

main().catch((err) => {
  console.error('Failed to start server:', err);
});
