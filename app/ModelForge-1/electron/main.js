const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let workerProcess = null;

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('index.html');

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startWorker() {
  const pythonExe = process.platform === 'win32'
    ? path.join(process.cwd(), '..', '.venv', 'Scripts', 'python.exe')
    : 'python3';
  const appPy = path.join(process.cwd(), '..', 'app.py');
  const env = { ...process.env, FLASK_ENV: 'production', SESSION_SECRET: 'local-dev' };
  try {
    workerProcess = spawn(pythonExe, [appPy], { env, stdio: 'inherit' });
  } catch (e) {
    console.error('Failed to start worker', e);
  }
}

app.whenReady().then(() => {
  startWorker();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (workerProcess) {
    try { workerProcess.kill(); } catch {}
  }
});
