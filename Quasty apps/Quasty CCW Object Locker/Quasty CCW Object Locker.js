// ==UserScript==
// @name         Quasty CCW Object Locker
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Enhanced object locking tool with draggable window and dynamic tracking
// @author       Developer
// @match        https://www.ccw.site/*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// ==/UserScript==

(function() {
    'use strict';

    // 保存当前主题
    let currentTheme = GM_getValue('theme', 'light');
    let isLocking = false;
    let isPaused = false;
    let redBoxes = [];
    let centerX = 0;
    let centerY = 0;
    let trackedElements = new Map(); // 存储被追踪的元素和对应的红框
    let animationFrameId = null;

    // 添加自定义样式
    GM_addStyle(`
        /* 小球样式 */
        #floatingBall {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: #3498db;
            border-radius: 50%;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: bold;
            font-size: 20px;
            transition: all 0.3s ease;
        }

        #floatingBall:hover {
            transform: scale(1.1);
            background: #2980b9;
        }

        /* 主窗口样式 */
        #toolkitWindow {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 350px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 10001;
            display: none;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }

        .window-header {
            background: #2c3e50;
            color: white;
            padding: 12px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            user-select: none;
        }

        .window-title {
            font-weight: bold;
        }

        .position-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }

        .window-body {
            padding: 20px;
        }

        .theme-selector {
            display: flex;
            justify-content: center;
            margin-bottom: 15px;
            gap: 10px;
        }

        .theme-btn {
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }

        .light-theme {
            background: #f0f0f0;
            color: #333;
        }

        .dark-theme {
            background: #333;
            color: #fff;
        }

        .hacker-theme {
            background: #000;
            color: #0f0;
            font-family: 'Courier New', monospace;
        }

        .lock-controls {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }

        .lock-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }

        .start-lock {
            background: #27ae60;
            color: white;
        }

        .stop-lock {
            background: #e74c3c;
            color: white;
        }

        .pause-lock {
            background: #f39c12;
            color: white;
        }

        .red-box {
            position: absolute;
            border: 2px solid red;
            z-index: 9999;
            pointer-events: none;
            box-shadow: 0 0 8px rgba(255, 0, 0, 0.6);
        }

        /* 暗色主题 */
        .theme-dark #toolkitWindow {
            background: #2c3e50;
            color: #ecf0f1;
        }

        .theme-dark .window-header {
            background: #1a2530;
        }

        .theme-dark .position-btn {
            background: #16a085;
        }

        /* 黑客主题 */
        .theme-hacker #toolkitWindow {
            background: #0c0c0c;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            border: 1px solid #00ff00;
        }

        .theme-hacker .window-header {
            background: #000;
            border-bottom: 1px solid #00ff00;
        }

        .theme-hacker .position-btn {
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
        }

        .theme-hacker .lock-btn {
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
            font-family: 'Courier New', monospace;
        }

        .theme-hacker .lock-btn:hover {
            background: #003300;
        }
    `);

    // 创建浮动小球
    function createFloatingBall() {
        const ball = document.createElement('div');
        ball.id = 'floatingBall';
        ball.innerHTML = '𝑄';
        ball.title = 'Object Locker';

        // 添加拖动功能
        let isDragging = false;
        let dragOffsetX, dragOffsetY;

        ball.addEventListener('mousedown', function(e) {
            isDragging = true;
            dragOffsetX = e.clientX - ball.offsetLeft;
            dragOffsetY = e.clientY - ball.offsetTop;
            ball.style.cursor = 'grabbing';
            e.stopPropagation();
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                ball.style.left = (e.clientX - dragOffsetX) + 'px';
                ball.style.top = (e.clientY - dragOffsetY) + 'px';
                ball.style.right = 'auto';
                ball.style.bottom = 'auto';
            }
        });

        document.addEventListener('mouseup', function() {
            isDragging = false;
            ball.style.cursor = 'pointer';
        });

        ball.addEventListener('click', function(e) {
            if (e.target === ball) {
                toggleToolkitWindow();
            }
        });

        document.body.appendChild(ball);
        return ball;
    }

    // 创建主窗口
    function createToolkitWindow() {
        const window = document.createElement('div');
        window.id = 'toolkitWindow';

        window.innerHTML = `
            <div class="window-header">
                <div class="window-title">Object Locker</div>
                <button class="position-btn" id="positionBtn">Select Position</button>
            </div>
            <div class="window-body">
                <div class="theme-selector">
                    <button class="theme-btn light-theme" data-theme="light">Light</button>
                    <button class="theme-btn dark-theme" data-theme="dark">Dark</button>
                    <button class="theme-btn hacker-theme" data-theme="hacker">Hacker</button>
                </div>
                <div class="lock-controls">
                    <button class="lock-btn start-lock" id="startLock">Start Lock</button>
                    <button class="lock-btn stop-lock" id="stopLock">Stop Lock</button>
                    <button class="lock-btn pause-lock" id="pauseLock">Pause Lock</button>
                </div>
                <div id="status">Status: Ready</div>
            </div>
        `;

        document.body.appendChild(window);

        // 添加窗口拖动功能
        makeWindowDraggable(window);

        return window;
    }

    // 使窗口可拖动
    function makeWindowDraggable(window) {
        const header = window.querySelector('.window-header');
        let isDragging = false;
        let dragOffsetX, dragOffsetY;

        header.addEventListener('mousedown', function(e) {
            if (e.target.tagName !== 'BUTTON') {
                isDragging = true;
                dragOffsetX = e.clientX - window.offsetLeft;
                dragOffsetY = e.clientY - window.offsetTop;
                window.style.cursor = 'grabbing';
            }
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                window.style.left = `${e.clientX - dragOffsetX}px`;
                window.style.top = `${e.clientY - dragOffsetY}px`;
                window.style.transform = 'none';
            }
        });

        document.addEventListener('mouseup', function() {
            isDragging = false;
            window.style.cursor = 'default';
        });
    }

    // 切换工具窗口显示/隐藏
    function toggleToolkitWindow() {
        const window = document.getElementById('toolkitWindow');
        if (window.style.display === 'block') {
            window.style.display = 'none';
        } else {
            window.style.display = 'block';
            applyTheme(currentTheme);
        }
    }

    // 应用主题
    function applyTheme(theme) {
        const window = document.getElementById('toolkitWindow');
        window.className = '';
        if (theme !== 'light') {
            window.classList.add(`theme-${theme}`);
        }
        currentTheme = theme;
        GM_setValue('theme', theme);
    }

    // 位置选择功能
    function setupPositionSelection() {
        const positionBtn = document.getElementById('positionBtn');
        positionBtn.addEventListener('click', function() {
            const window = document.getElementById('toolkitWindow');
            window.style.display = 'none';

            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            overlay.style.zIndex = '10000';
            overlay.style.cursor = 'crosshair';

            const instruction = document.createElement('div');
            instruction.style.position = 'fixed';
            instruction.style.top = '50%';
            instruction.style.left = '50%';
            instruction.style.transform = 'translate(-50%, -50%)';
            instruction.style.color = 'white';
            instruction.style.fontSize = '24px';
            instruction.style.textShadow = '1px 1px 2px black';
            instruction.textContent = 'Click to set center position';

            document.body.appendChild(overlay);
            document.body.appendChild(instruction);

            overlay.addEventListener('click', function(e) {
                centerX = e.clientX;
                centerY = e.clientY;

                document.body.removeChild(overlay);
                document.body.removeChild(instruction);

                const window = document.getElementById('toolkitWindow');
                window.style.display = 'block';

                updateStatus(`Center set to: ${centerX}, ${centerY}`);
            });
        });
    }

    // 更新状态信息
    function updateStatus(message) {
        const status = document.getElementById('status');
        status.textContent = `Status: ${message}`;
    }

    // 设置锁定控制
    function setupLockControls() {
        const startBtn = document.getElementById('startLock');
        const stopBtn = document.getElementById('stopLock');
        const pauseBtn = document.getElementById('pauseLock');

        startBtn.addEventListener('click', function() {
            isLocking = true;
            isPaused = false;
            updateStatus("Locking active");
            startLocking();
        });

        stopBtn.addEventListener('click', function() {
            isLocking = false;
            isPaused = false;
            updateStatus("Locking stopped");
            stopLocking();
        });

        pauseBtn.addEventListener('click', function() {
            isPaused = !isPaused;
            updateStatus(isPaused ? "Locking paused" : "Locking resumed");

            // 暂停时隐藏红框，恢复时显示
            const display = isPaused ? 'none' : 'block';
            trackedElements.forEach((redBox, element) => {
                redBox.style.display = display;
            });
        });
    }

    // 开始锁定
    function startLocking() {
        // 清除之前的追踪
        stopLocking();

        // 查找移动的元素并添加红框
        const movingElements = findMovingElements();
        movingElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const redBox = document.createElement('div');
            redBox.className = 'red-box';
            redBox.style.left = `${rect.left}px`;
            redBox.style.top = `${rect.top}px`;
            redBox.style.width = `${rect.width}px`;
            redBox.style.height = `${rect.height}px`;
            document.body.appendChild(redBox);

            // 存储元素和对应的红框
            trackedElements.set(element, redBox);
        });

        updateStatus(`Tracking ${trackedElements.size} objects`);

        // 启动位置追踪
        startTracking();
    }

    // 开始追踪元素位置
    function startTracking() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }

        function track() {
            if (!isLocking || isPaused) {
                animationFrameId = null;
                return;
            }

            trackedElements.forEach((redBox, element) => {
                if (document.body.contains(element)) {
                    const rect = element.getBoundingClientRect();
                    redBox.style.left = `${rect.left}px`;
                    redBox.style.top = `${rect.top}px`;
                    redBox.style.width = `${rect.width}px`;
                    redBox.style.height = `${rect.height}px`;
                } else {
                    // 如果元素已从DOM中移除，移除对应的红框
                    if (redBox.parentNode) {
                        redBox.parentNode.removeChild(redBox);
                    }
                    trackedElements.delete(element);
                }
            });

            animationFrameId = requestAnimationFrame(track);
        }

        animationFrameId = requestAnimationFrame(track);
    }

    // 停止锁定
    function stopLocking() {
        // 移除所有红框
        trackedElements.forEach((redBox, element) => {
            if (redBox.parentNode) {
                redBox.parentNode.removeChild(redBox);
            }
        });
        trackedElements.clear();

        // 停止动画帧
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    }

    // 查找移动的元素（增强版）
    function findMovingElements() {
        const possibleMovingElements = [];

        // 查找动画元素
        const animatedElements = document.querySelectorAll('*');
        animatedElements.forEach(element => {
            const style = window.getComputedStyle(element);
            if (style.animationName !== 'none' || style.transitionProperty !== 'none') {
                possibleMovingElements.push(element);
            }
        });

        // 查找视频元素
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            possibleMovingElements.push(video);
        });

        // 查找Canvas元素
        const canvases = document.querySelectorAll('canvas');
        canvases.forEach(canvas => {
            possibleMovingElements.push(canvas);
        });

        // 查找iframe元素
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            possibleMovingElements.push(iframe);
        });

        // 查找具有特定类的元素（可根据网站调整）
        const movingCandidates = document.querySelectorAll('[class*="move"], [class*="slide"], [class*="anim"]');
        movingCandidates.forEach(element => {
            possibleMovingElements.push(element);
        });

        return possibleMovingElements;
    }

    // 设置主题选择
    function setupThemeSelection() {
        const themeButtons = document.querySelectorAll('.theme-btn');
        themeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const theme = this.getAttribute('data-theme');
                applyTheme(theme);
            });
        });
    }

    // 初始化函数
    function init() {
        createFloatingBall();
        createToolkitWindow();
        setupPositionSelection();
        setupLockControls();
        setupThemeSelection();
        applyTheme(currentTheme);
    }

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();