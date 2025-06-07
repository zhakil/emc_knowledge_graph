// desktop/main.js - Electron主进程
const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class EMCDesktopApp {
    constructor() {
        this.mainWindow = null;
        this.backendProcess = null;
        this.frontendProcess = null;
        this.isReady = false;
    }

    async createWindow() {
        // 创建主窗口
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                webSecurity: false,
                preload: path.join(__dirname, 'preload.js')
            },
            icon: path.join(__dirname, 'assets', 'icon.ico'),
            title: 'EMC知识图谱系统',
            show: false
        });

        // 设置菜单
        this.createMenu();

        // 启动后端服务
        await this.startBackendService();

        // 等待服务就绪后加载前端
        await this.waitForBackend();
        
        // 加载应用
        if (process.env.NODE_ENV === 'development') {
            await this.mainWindow.loadURL('http://localhost:3000');
            this.mainWindow.webContents.openDevTools();
        } else {
            await this.mainWindow.loadFile('build/index.html');
        }

        this.mainWindow.show();
        this.mainWindow.focus();
    }

    async startBackendService() {
        try {
            // 检查是否为打包后的应用
            const isDev = process.env.NODE_ENV === 'development';
            const backendPath = isDev 
                ? path.join(__dirname, '..', 'start_gateway.py')
                : path.join(process.resourcesPath, 'backend', 'emc_backend.exe');

            if (isDev) {
                // 开发环境：启动Python脚本
                this.backendProcess = spawn('python', [backendPath], {
                    cwd: path.dirname(backendPath),
                    stdio: ['pipe', 'pipe', 'pipe']
                });
            } else {
                // 生产环境：启动打包的exe
                this.backendProcess = spawn(backendPath, [], {
                    cwd: path.dirname(backendPath),
                    stdio: ['pipe', 'pipe', 'pipe']
                });
            }

            this.backendProcess.stdout.on('data', (data) => {
                console.log(`Backend: ${data}`);
            });

            this.backendProcess.stderr.on('data', (data) => {
                console.error(`Backend Error: ${data}`);
            });

            console.log('后端服务启动中...');
        } catch (error) {
            console.error('启动后端服务失败:', error);
            this.showErrorDialog('启动失败', '无法启动后端服务，请检查安装是否完整。');
        }
    }

    async waitForBackend() {
        const maxAttempts = 30;
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                const response = await fetch('http://localhost:8000/health');
                if (response.ok) {
                    console.log('后端服务就绪');
                    return;
                }
            } catch (error) {
                // 继续等待
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
        }

        this.showErrorDialog('启动超时', '后端服务启动超时，请重新启动应用。');
    }

    createMenu() {
        const template = [
            {
                label: '文件',
                submenu: [
                    {
                        label: '导入文档',
                        accelerator: 'CmdOrCtrl+O',
                        click: () => this.openFileDialog()
                    },
                    {
                        label: '导出数据',
                        accelerator: 'CmdOrCtrl+E',
                        click: () => this.exportData()
                    },
                    { type: 'separator' },
                    {
                        label: '退出',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => app.quit()
                    }
                ]
            },
            {
                label: '工具',
                submenu: [
                    {
                        label: 'Neo4j浏览器',
                        click: () => shell.openExternal('http://localhost:7474')
                    },
                    {
                        label: 'API文档',
                        click: () => shell.openExternal('http://localhost:8000/docs')
                    },
                    { type: 'separator' },
                    {
                        label: '开发者工具',
                        accelerator: 'F12',
                        click: () => this.mainWindow.webContents.toggleDevTools()
                    }
                ]
            },
            {
                label: '帮助',
                submenu: [
                    {
                        label: '用户手册',
                        click: () => shell.openExternal('https://github.com/zhakil/emc_knowledge_graph')
                    },
                    {
                        label: '关于',
                        click: () => this.showAboutDialog()
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    async openFileDialog() {
        const result = await dialog.showOpenDialog(this.mainWindow, {
            properties: ['openFile', 'multiSelections'],
            filters: [
                { name: 'EMC文档', extensions: ['pdf', 'docx', 'xlsx', 'csv'] },
                { name: '所有文件', extensions: ['*'] }
            ]
        });

        if (!result.canceled && result.filePaths.length > 0) {
            // 通过IPC通知渲染进程处理文件
            this.mainWindow.webContents.send('files-selected', result.filePaths);
        }
    }

    async exportData() {
        const result = await dialog.showSaveDialog(this.mainWindow, {
            defaultPath: `emc_data_${new Date().toISOString().split('T')[0]}.json`,
            filters: [
                { name: 'JSON文件', extensions: ['json'] },
                { name: '所有文件', extensions: ['*'] }
            ]
        });

        if (!result.canceled) {
            // 通知渲染进程导出数据
            this.mainWindow.webContents.send('export-data', result.filePath);
        }
    }

    showAboutDialog() {
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: '关于EMC知识图谱系统',
            message: 'EMC知识图谱系统',
            detail: `版本: 1.0.0\n集成DeepSeek AI和Neo4j的专业EMC知识管理平台\n\n© 2025 EMC Knowledge Graph Team`
        });
    }

    showErrorDialog(title, message) {
        dialog.showErrorBox(title, message);
    }

    cleanup() {
        if (this.backendProcess) {
            this.backendProcess.kill();
        }
        if (this.frontendProcess) {
            this.frontendProcess.kill();
        }
    }
}

// 应用生命周期管理
const emcApp = new EMCDesktopApp();

app.whenReady().then(() => {
    emcApp.createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            emcApp.createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    emcApp.cleanup();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    emcApp.cleanup();
});