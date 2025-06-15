const { app, BrowserWindow, Menu, dialog, shell, Tray, nativeImage, ipcMain, autoUpdater, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const isDev = process.env.NODE_ENV === 'development' || process.env.ELECTRON_IS_DEV === 'true';

let apiServer = null;

let tray = null;
let mainWindow = null;

// 启动内置API服务器
function startApiServer() {
  const serverPath = isDev 
    ? path.join(__dirname, '../../api_server.py')
    : path.join(process.resourcesPath, 'api_server.py');
    
  if (!fs.existsSync(serverPath)) {
    console.error('API服务器文件不存在:', serverPath);
    return;
  }
  
  console.log('启动内置API服务器:', serverPath);
  
  apiServer = spawn('python', [serverPath], {
    cwd: isDev ? path.join(__dirname, '../..') : process.resourcesPath,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  
  apiServer.stdout.on('data', (data) => {
    console.log('API服务器输出:', data.toString());
  });
  
  apiServer.stderr.on('data', (data) => {
    console.error('API服务器错误:', data.toString());
  });
  
  apiServer.on('close', (code) => {
    console.log('API服务器进程退出，代码:', code);
    apiServer = null;
  });
  
  // 等待服务器启动
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, 3000);
  });
}

// 停止API服务器
function stopApiServer() {
  if (apiServer) {
    apiServer.kill();
    apiServer = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    icon: path.join(__dirname, 'public/favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true
    },
    titleBarStyle: 'default',
    show: false
  });

  // 统一使用内置API服务器端口
  const startUrl = 'http://localhost:5000';
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Handle window close to minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!app.isQuiting && process.platform === 'win32') {
      event.preventDefault();
      mainWindow.hide();
      if (Notification.isSupported()) {
        new Notification({
          title: 'EMC知识图谱',
          body: '应用程序已最小化到系统托盘'
        }).show();
      }
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建项目',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-new-project');
          }
        },
        {
          label: '打开项目',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openDirectory'],
              title: '选择项目文件夹'
            });
            if (!result.canceled) {
              mainWindow.webContents.send('menu-open-project', result.filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' },
        { role: 'selectall', label: '全选' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新加载' },
        { role: 'forceReload', label: '强制重新加载' },
        { role: 'toggleDevTools', label: '开发者工具' },
        { type: 'separator' },
        { role: 'resetZoom', label: '实际大小' },
        { role: 'zoomIn', label: '放大' },
        { role: 'zoomOut', label: '缩小' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '全屏' }
      ]
    },
    {
      label: '工具',
      submenu: [
        {
          label: 'AI配置',
          click: () => {
            mainWindow.webContents.send('menu-ai-settings');
          }
        },
        {
          label: '导出数据',
          click: async () => {
            const result = await dialog.showSaveDialog(mainWindow, {
              title: '导出知识图谱数据',
              defaultPath: 'knowledge_graph_export.json',
              filters: [
                { name: 'JSON Files', extensions: ['json'] },
                { name: 'All Files', extensions: ['*'] }
              ]
            });
            if (!result.canceled) {
              mainWindow.webContents.send('menu-export-data', result.filePath);
            }
          }
        }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于EMC知识图谱',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '关于',
              message: 'EMC知识图谱系统',
              detail: '基于KAG-DeepSeek融合AI的专业级知识图谱构建系统\n版本: 1.0.0\n\n集成KAG知识增强生成框架，提供多跳推理和DIKW层次化知识提取能力。'
            });
          }
        },
        {
          label: '用户手册',
          click: () => {
            shell.openExternal('https://github.com/your-repo/emc-knowledge-graph/wiki');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  return mainWindow;
}

function createTray() {
  // Create tray icon (use favicon as tray icon)
  const trayIcon = nativeImage.createFromPath(path.join(__dirname, 'favicon.ico'));
  tray = new Tray(trayIcon.resize({ width: 16, height: 16 }));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createWindow();
        }
      }
    },
    {
      label: '新建项目',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('menu-new-project');
          mainWindow.show();
        }
      }
    },
    { type: 'separator' },
    {
      label: '关于',
      click: () => {
        dialog.showMessageBox({
          type: 'info',
          title: '关于EMC知识图谱',
          message: 'EMC知识图谱系统 v1.0.0',
          detail: '基于KAG-DeepSeek融合AI的专业级知识图谱构建系统'
        });
      }
    },
    {
      label: '退出',
      click: () => {
        app.isQuiting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('EMC知识图谱系统');
  tray.setContextMenu(contextMenu);
  
  // Double click to show window
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    } else {
      createWindow();
    }
  });
}

app.whenReady().then(async () => {
  // 先启动API服务器
  await startApiServer();
  
  // 再创建窗口
  createWindow();
  createTray();
  
  // Register global shortcut Ctrl+Shift+E to show/hide main window
  globalShortcut.register('CommandOrControl+Shift+E', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
  
  // Handle file associations (Windows)
  if (process.platform === 'win32') {
    app.setAsDefaultProtocolClient('emc-kg');
    
    // Handle opening files via file association
    app.on('open-file', (event, filePath) => {
      event.preventDefault();
      if (mainWindow) {
        mainWindow.webContents.send('open-file', filePath);
        mainWindow.show();
      }
    });
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopApiServer();
    app.quit();
  }
});

app.on('before-quit', () => {
  stopApiServer();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Handle file protocol for production
if (!isDev) {
  app.setAsDefaultProtocolClient('emc-knowledge-graph');
}

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (navigationEvent, url) => {
    navigationEvent.preventDefault();
    shell.openExternal(url);
  });
});

// Handle certificate errors in development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev && url.startsWith('https://localhost')) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

// IPC handlers for renderer process communication
ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-app-path', (event, name) => {
  return app.getPath(name);
});

// Auto-updater events (for production)
if (!isDev) {
  autoUpdater.checkForUpdatesAndNotify();
  
  autoUpdater.on('update-available', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: '更新可用',
      message: '发现新版本，将在后台下载更新。',
      buttons: ['确定']
    });
  });
  
  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: '更新就绪',
      message: '更新已下载完成，应用程序将重启以应用更新。',
      buttons: ['立即重启', '稍后']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });
}

// Global shortcut for showing/hiding window
const { globalShortcut } = require('electron');

app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// Windows-specific features
if (process.platform === 'win32') {
  // Handle protocol for Windows
  app.setAsDefaultProtocolClient('emc-knowledge-graph');
  
  // Handle squirrel events for Windows installer
  if (require('electron-squirrel-startup')) {
    app.quit();
  }
  
  // Handle app being launched with command line arguments
  const gotTheLock = app.requestSingleInstanceLock();
  
  if (!gotTheLock) {
    app.quit();
  } else {
    app.on('second-instance', (event, commandLine, workingDirectory) => {
      // Someone tried to run a second instance, focus our window instead
      if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.focus();
      }
    });
  }
}