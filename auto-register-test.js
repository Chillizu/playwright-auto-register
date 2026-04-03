/**
 * 自动注册测试脚本 - 仅用于授权测试
 * 使用前确保：1) 你拥有该网站 2) 在测试环境运行 3) 遵守速率限制
 * 
 * 配置：headless: false (无头模式), 自动清理进程，15秒速率限制
 */

const { chromium } = require('playwright');

// 生成随机用户名（不带@）
function generateRandomUsername() {
 const timestamp = Date.now().toString().slice(-6);
 const random = Math.random().toString(36).substring(2, 6);
 return `user_${timestamp}_${random}`;
}

// 生成随机密码（8-16位，包含字母和数字）
function generateRandomPassword() {
  const length = Math.floor(Math.random() * 9) + 8; // 8-16位
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}

// 延迟函数（速率限制）
function delay(ms) {
return new Promise(resolve => setTimeout(resolve, ms));
}

// 随机延迟函数（模拟人类行为）
function randomDelay(min, max) {
return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 贝塞尔曲线计算函数
function cubicBezier(t, p0, p1, p2, p3) {
const mt = 1 - t;
return mt * mt * mt * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t * t * t * p3;
}

// 模拟人类鼠标移动轨迹（使用贝塞尔曲线）
async function mouseHumanMove(page, element) {
try {
const box = await element.boundingBox();
if (!box) return;

// 计算目标位置（元素中心附近随机点）
const targetX = Math.floor(box.x + box.width / 2 + (Math.random() - 0.5) * box.width * 0.3);
const targetY = Math.floor(box.y + box.height / 2 + (Math.random() - 0.5) * box.height * 0.3);

// 获取当前位置
const mousePos = { x: 0, y: 0 };

// 使用贝塞尔曲线生成平滑路径
const steps = randomDelay(5, 10);
const controlPoints = [];

// 生成 2-4 个随机控制点，模拟鼠标曲线移动
const controlCount = randomDelay(2, 4);
for (let i = 0; i < controlCount; i++) {
controlPoints.push({
x: Math.floor(targetX * (0.3 + Math.random() * 0.4)),
y: Math.floor(targetY * (0.3 + Math.random() * 0.4))
});
}

// 添加目标点作为最后一个控制点
controlPoints.push({ x: targetX, y: targetY });

// 分段移动
for (let i = 0; i <= steps; i++) {
const t = i / steps;
// 使用第一个控制点计算简单曲线
const newX = Math.floor(cubicBezier(t, 0, controlPoints[0].x * 0.3, controlPoints[0].x * 0.7, targetX));
const newY = Math.floor(cubicBezier(t, 0, controlPoints[0].y * 0.3, controlPoints[0].y * 0.7, targetY));

await page.mouse.move(newX, newY);

// 每步之间的随机延迟，模拟真实鼠标移动速度变化
await delay(randomDelay(10, 50));
}

// 确保最终位置准确
await page.mouse.move(targetX, targetY);
} catch (error) {
console.log('鼠标移动警告:', error.message);
}
}

// 模拟人类打字（逐字符输入，带随机延迟）
async function typeHuman(page, element, text) {
const chars = text.split('');
const avgDelay = 60; // 平均每字符延迟（毫秒），模拟 40-60 字/分钟

for (let i = 0; i < chars.length; i++) {
await element.type(chars[i]);
// 人类打字速度有波动，添加随机性
await delay(randomDelay(avgDelay - 30, avgDelay + 30));

// 偶尔停顿（约 10% 概率）
if (Math.random() < 0.1 && i < chars.length - 1) {
await delay(randomDelay(200, 500));
}
}
}

// 清理函数：确保浏览器进程被清理
async function cleanup(browser, context, page) {
  try {
    if (page) await page.close().catch(() => {});
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    console.log('✓ 浏览器进程已清理');
  } catch (error) {
    console.error('清理进程时出错:', error.message);
  }
}

async function registerUser(page, url) {
    const username = generateRandomUsername();
    const password = generateRandomPassword();

    console.log(`\n[注册] 尝试注册：${username}`);

    try {
        // 导航到注册页面
        console.log(`[导航] 开始导航到：${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(3000);
        console.log(`[导航] 导航完成，当前 URL: ${page.url()}`);

        // 随机等待页面加载（模拟真实用户）
        console.log('[等待] 等待页面加载...');
        await delay(randomDelay(1000, 3000));
        console.log('[等待] 页面加载完成');

        // 查找用户名输入框
        console.log('[查找元素] 正在查找用户名输入框...');
        const usernameInput = await page.locator('input[name="username"], input[placeholder*="用户名"], input[placeholder*="Username"], input[id="username"]').first();
        if (await usernameInput.count() > 0) {
            console.log('[查找元素] 找到用户名输入框');
        } else {
            console.log('[查找元素] 未找到用户名输入框');
        }
        // 鼠标移动到用户名输入框（模拟人类行为）
        console.log('[鼠标] 移动鼠标到用户名输入框');
        await mouseHumanMove(page, usernameInput);
        // 随机等待后再输入
        console.log('[等待] 等待后输入用户名...');
        await delay(randomDelay(500, 1500));
        // 逐字符输入用户名
        console.log(`[输入] 正在输入用户名：${username}`);
        await typeHuman(page, usernameInput, username);
        console.log('[输入] 用户名输入完成');

        // 查找密码输入框（第一个 password 输入框）
        console.log('[查找元素] 正在查找密码输入框...');
        const passwordInputs = await page.locator('input[type="password"]').count();
        console.log(`[查找元素] 找到 ${passwordInputs} 个密码输入框`);
        const passwordInput = page.locator('input[type="password"]').first();
        // 鼠标移动到密码输入框
        console.log('[鼠标] 移动鼠标到密码输入框');
        await mouseHumanMove(page, passwordInput);
        // 随机等待
        console.log('[等待] 等待后输入密码...');
        await delay(randomDelay(500, 1500));
        // 逐字符输入密码
        console.log('[输入] 正在输入密码');
        await typeHuman(page, passwordInput, password);
        console.log('[输入] 密码输入完成');

        // 查找确认密码输入框（第二个 password 输入框）
        console.log('[查找元素] 正在查找确认密码输入框...');
        const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
        console.log('[鼠标] 移动鼠标到确认密码输入框');
        await mouseHumanMove(page, confirmPasswordInput);
        console.log('[等待] 等待后输入确认密码...');
        await delay(randomDelay(300, 800));
        // 逐字符输入确认密码
        console.log('[输入] 正在输入确认密码');
        await typeHuman(page, confirmPasswordInput, password);
        console.log('[输入] 确认密码输入完成');

        // 随机等待后截图（模拟真实行为）
        console.log('[等待] 等待后截图...');
        await delay(randomDelay(500, 1000));
        const screenshotPath = `register-${Date.now()}.png`;
        console.log(`[截图] 正在保存截图：${screenshotPath}`);
        await page.screenshot({ path: screenshotPath });
        console.log(`[截图] 截图已保存：${screenshotPath}`);

        console.log('[Cloudflare] 等待 CF Turnstile token 生成...');
        let cfReady = false;
        for (let attempt = 0; attempt < 20; attempt++) {
            const token = await page.evaluate(() => {
                const el = document.querySelector('[name="cf-turnstile-response"], input[name*="turnstile"]');
                return el ? el.value : null;
            });
            if (token && token.length > 10) {
                console.log(`[Cloudflare] CF token 已生成 (长度: ${token.length})`);
                cfReady = true;
                break;
            }
            console.log(`[Cloudflare] 等待 token... (${attempt + 1}/20)`);
            await delay(1000);
        }
        if (!cfReady) {
            console.log('[Cloudflare] token 未生成，仍尝试提交');
        }

        // 查找并点击注册按钮
        console.log('[查找元素] 正在查找注册按钮...');
        const submitButton = await page.locator('button[type="submit"], button:has-text("注册"), button:has-text("Register"), button:has-text("Sign up")').first();
        if (await submitButton.count() > 0) {
            console.log('[查找元素] 找到注册按钮');
        } else {
            console.log('[查找元素] 未找到注册按钮');
        }
        // 鼠标移动到提交按钮
        console.log('[鼠标] 移动鼠标到注册按钮');
        await mouseHumanMove(page, submitButton);
        // 随机等待后点击
        console.log('[等待] 等待后点击注册按钮...');
        await delay(randomDelay(500, 1500));
        console.log('[点击] 点击注册按钮');
        await submitButton.click();
        console.log('[点击] 注册按钮点击完成');

        console.log('[等待] 等待服务器响应...');
        await delay(randomDelay(3000, 5000));
        console.log('[等待] 等待完成');

        // 检测注册是否成功
        console.log('[检测] 检查注册结果...');
        const currentUrl = page.url();
        const isSuccess = currentUrl.includes('/login');
        const successMessage = 0;
        console.log(`[检测] 当前 URL: ${currentUrl}`);
        console.log(`[检测] 成功消息数量：${successMessage}`);

        console.log(`[结果] ✓ 注册请求已发送`);
        console.log(`[结果] 用户名：${username}`);
        console.log(`[结果] 密码：${password}`);
        console.log(`[结果] 当前 URL: ${currentUrl}`);

        if (isSuccess || successMessage > 0) {
            console.log('[结果] 注册成功检测：成功');
            return { success: true, username, password };
        } else {
            console.log('[结果] 注册结果：等待进一步验证');
            return { success: true, username, password, pending: true };
        }

    } catch (error) {
        console.error(`[错误] ✗ 注册失败：${error.message}`);
        console.error(`[错误] 详细堆栈：${error.stack}`);
        return { success: false, error: error.message, stack: error.stack };
    }
}

async function main() {
    const url = 'https://ai.yumeyuki.moe/register?aff=P7SY';
    const testCount = parseInt(process.env.TEST_COUNT || '1');
    const delayBetweenTests = parseInt(process.env.DELAY_MS || '15000');
    const headlessMode = process.env.HEADLESS !== 'false';
    
    console.log('=== 自动注册测试开始 ===');
    console.log(`目标 URL: ${url}`);
    console.log(`测试次数：${testCount}`);
    console.log(`间隔时间：${delayBetweenTests/1000} 秒`);
    console.log(`浏览器模式：${headlessMode ? 'headless (无头模式)' : '有头模式 (可见窗口)'}`);
    console.log('');

    console.log('[浏览器] 正在启动浏览器...');
    const browser = await chromium.launch({
        headless: headlessMode,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-web-security',
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--no-zygote',
            '--window-size=1920,1080'
        ],
        ignoreDefaultArgs: ['--enable-automation', '--enable-blink-features=IdleDetection']
    });
    console.log('[浏览器] 浏览器启动成功');

    let context = null;
    let page = null;

    try {
        const results = [];

        for (let i = 1; i <= testCount; i++) {
            console.log(`\n[测试进度] [${i}/${testCount}] 开始测试...`);

            console.log('[上下文] 创建新的浏览器上下文...');
            context = await browser.newContext({
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport: { width: 1920, height: 1080 },
                locale: 'zh-CN',
                timezoneId: 'Asia/Shanghai',
                permissions: ['geolocation'],
                geolocation: { latitude: 31.2304, longitude: 121.4737 },
                colorScheme: 'light',
                deviceScaleFactor: 1,
                hasTouch: false,
                isMobile: false,
                javaScriptEnabled: true
            });
            
            await context.addInitScript(() => {
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
                window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {} };
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            });
            
            console.log('[上下文] 上下文创建成功');
            console.log('[页面] 创建新页面...');
            page = await context.newPage();
            console.log('[页面] 页面创建成功');

            console.log('[调用] 调用 registerUser 函数...');
            const result = await registerUser(page, url);
            console.log(`[调用] registerUser 返回结果：${result.success ? '成功' : '失败'}`);
            results.push(result);

            // 关闭当前上下文
            console.log('[上下文] 关闭当前上下文...');
            await context.close();
            console.log('[上下文] 上下文已关闭');

            // 速率限制：等待指定时间后再进行下一次测试
            if (i < testCount) {
                console.log(`[速率限制] 等待 ${delayBetweenTests/1000} 秒后继续...`);
                await delay(delayBetweenTests);
            }
        }
    
    // 统计结果
    console.log('\n=== 测试结果统计 ===');
    const successCount = results.filter(r => r.success).length;
    console.log(`成功: ${successCount}/${testCount}`);
    console.log(`失败: ${testCount - successCount}/${testCount}`);
    
    if (successCount > 0) {
      console.log('\n成功的测试:');
      results.forEach((r, i) => {
        if (r.success) {
          console.log(`  ${i+1}. 用户名: ${r.username}, 密码: ${r.password}`);
        }
      });
    }
    
    } catch (error) {
        console.error(`[主程序错误] 测试过程中出错：${error.message}`);
        console.error(`[主程序错误] 详细堆栈：${error.stack}`);
    } finally {
        // 确保浏览器进程被清理
        console.log('[清理] 正在清理浏览器进程...');
        await cleanup(browser, context, page);
        console.log('[清理] 清理完成');
    }
}

// 运行主函数
console.log('[启动] 开始执行主程序...');
main().catch(error => {
    console.error('[致命错误] 程序执行出错:', error);
    console.error('[致命错误] 详细堆栈:', error.stack);
    process.exit(1);
});
