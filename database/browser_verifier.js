/**
 * Browser Verification Script for Music App
 * Controls headless Chrome via Chrome DevTools Protocol (CDP) using native Node.js fetch and WebSocket.
 * Captures genuine PNG browser screenshots for all required pages and tests user flows.
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const BASE_URL = "http://127.0.0.1:8000";
const SCREENSHOT_DIR = path.resolve(__dirname, '..', 'screenshots', 'ui');
const USER_DATA_DIR = path.resolve(__dirname, '..', 'temp_chrome_profile');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

class CDPClient {
    constructor(wsUrl) {
        this.wsUrl = wsUrl;
        this.id = 1;
        this.callbacks = new Map();
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.wsUrl);
            this.ws.onopen = () => resolve();
            this.ws.onerror = (err) => reject(err);
            this.ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.id && this.callbacks.has(msg.id)) {
                    const cb = this.callbacks.get(msg.id);
                    this.callbacks.delete(msg.id);
                    if (msg.error) cb.reject(new Error(msg.error.message));
                    else cb.resolve(msg.result);
                }
            };
        });
    }

    send(method, params = {}) {
        return new Promise((resolve, reject) => {
            const id = this.id++;
            this.callbacks.set(id, { resolve, reject });
            this.ws.send(JSON.stringify({ id, method, params }));
        });
    }

    async navigate(url) {
        await this.send('Page.navigate', { url });
        await sleep(1500); // Wait for render
    }

    async evaluate(expression) {
        const res = await this.send('Runtime.evaluate', { expression, returnByValue: true });
        return res.result?.value;
    }

    async screenshot(filePath) {
        const res = await this.send('Page.captureScreenshot', { format: 'png' });
        fs.writeFileSync(filePath, Buffer.from(res.data, 'base64'));
        console.log(`[CAPTURED] ${path.basename(filePath)}`);
    }

    close() {
        if (this.ws) this.ws.close();
    }
}

async function main() {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    fs.mkdirSync(USER_DATA_DIR, { recursive: true });

    console.log("Launching headless Google Chrome...");
    const chrome = spawn(CHROME_PATH, [
        '--headless=new',
        '--remote-debugging-port=9222',
        '--window-size=1280,900',
        `--user-data-dir=${USER_DATA_DIR}`,
        '--disable-gpu',
        '--no-first-run',
        '--no-default-browser-check',
        'about:blank'
    ]);

    await sleep(2500);

    try {
        const versionRes = await fetch('http://127.0.0.1:9222/json/version');
        const versionData = await versionRes.json();
        console.log("Connected to Chrome:", versionData['Browser']);

        const listRes = await fetch('http://127.0.0.1:9222/json/list');
        const listData = await listRes.json();
        const wsUrl = listData[0].webSocketDebuggerUrl;

        const cdp = new CDPClient(wsUrl);
        await cdp.connect();
        await cdp.send('Page.enable');
        await cdp.send('DOM.enable');

        // 1. HOME PAGE
        console.log("\n1. Inspecting Home Page...");
        await cdp.navigate(`${BASE_URL}/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '01_home_page.png'));

        // 2. LOGIN PAGE
        console.log("\n2. Inspecting Login Page...");
        await cdp.navigate(`${BASE_URL}/login/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '02_login_page.png'));

        // 3. REGISTRATION PAGE
        console.log("\n3. Inspecting Registration Page...");
        await cdp.navigate(`${BASE_URL}/register/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '03_register_page.png'));

        // 4. MEMBER LOGIN & MEMBER DASHBOARD
        console.log("\n4. Performing Member Login ('alex_rhythm')...");
        await cdp.navigate(`${BASE_URL}/login/`);
        await cdp.evaluate(`
            document.querySelector('#id_username').value = 'alex_rhythm';
            document.querySelector('#id_password').value = 'MemberDemo2026!';
            document.querySelector('form').submit();
        `);
        await sleep(2000);
        console.log("Current URL after login:", await cdp.evaluate('window.location.href'));
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '04_member_dashboard.png'));

        // 5. MEMBER PROFILE
        console.log("\n5. Inspecting Member Profile...");
        await cdp.navigate(`${BASE_URL}/profile/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '05_member_profile.png'));

        // 8. MEMBER ACCESS-DENIED PAGE (Member attempting admin-dashboard)
        console.log("\n6. Testing Member Access to Admin Dashboard (Expecting 403 Access Denied)...");
        await cdp.navigate(`${BASE_URL}/admin-dashboard/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '08_access_denied_page.png'));

        // LOGOUT MEMBER via POST form in nav
        console.log("\n7. Logging out Member via POST...");
        await cdp.navigate(`${BASE_URL}/dashboard/`);
        await cdp.evaluate(`
            const form = document.querySelector('form[action="/accounts/logout/"]') || document.querySelector('form[action="/logout/"]');
            if (form) form.submit();
        `);
        await sleep(2000);

        // 6. ADMIN LOGIN & ADMIN DASHBOARD
        console.log("\n8. Performing Administrator Login ('admin_demo')...");
        await cdp.navigate(`${BASE_URL}/login/`);
        await cdp.evaluate(`
            document.querySelector('#id_username').value = 'admin_demo';
            document.querySelector('#id_password').value = 'AdminDemo2026!';
            document.querySelector('form').submit();
        `);
        await sleep(2000);
        console.log("Current URL after admin login:", await cdp.evaluate('window.location.href'));
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '06_admin_dashboard.png'));

        // 7. CATALOGUE MANAGEMENT PAGE
        console.log("\n9. Inspecting Catalogue Management Page...");
        await cdp.navigate(`${BASE_URL}/catalog/manage/`);
        await cdp.screenshot(path.join(SCREENSHOT_DIR, '07_catalogue_management.png'));

        // Clean logout
        await cdp.evaluate(`
            const form = document.querySelector('form[action="/accounts/logout/"]') || document.querySelector('form[action="/logout/"]');
            if (form) form.submit();
        `);
        await sleep(1500);

        cdp.close();
        console.log("\n[SUCCESS] All 8 required browser PNG screenshots captured successfully!");
    } finally {
        chrome.kill();
        // Clean temp user data dir
        try { fs.rmSync(USER_DATA_DIR, { recursive: true, force: true }); } catch (_) {}
    }
}

main().catch(err => {
    console.error("Browser verification error:", err);
    process.exit(1);
});
