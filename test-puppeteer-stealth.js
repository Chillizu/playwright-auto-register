const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

function generateRandomUsername() {
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.random().toString(36).substring(2, 6);
  return `user_${timestamp}_${random}`;
}

function generateRandomPassword() {
  const length = Math.floor(Math.random() * 9) + 8;
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const url = 'https://ai.yumeyuki.moe/register?aff=P7SY';
  
  console.log('=== Puppeteer Stealth 测试 ===');
  console.log('启动浏览器...');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  console.log('导航到注册页面...');
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await delay(3000);
  
  const username = generateRandomUsername();
  const password = generateRandomPassword();
  
  console.log(`用户名: ${username}`);
  console.log(`密码: ${password}`);
  
  console.log('填写表单...');
  await page.type('input[name="username"], input[placeholder*="用户名"]', username, { delay: 50 });
  await delay(500);
  
  const passwordInputs = await page.$$('input[type="password"]');
  await passwordInputs[0].type(password, { delay: 50 });
  await delay(500);
  await passwordInputs[1].type(password, { delay: 50 });
  await delay(1000);
  
  await page.screenshot({ path: 'puppeteer-before-submit.png' });
  console.log('截图已保存');
  
  console.log('等待 CF token...');
  let tokenFound = false;
  for (let i = 0; i < 20; i++) {
    const token = await page.evaluate(() => {
      const el = document.querySelector('[name="cf-turnstile-response"]');
      return el ? el.value : null;
    });
    if (token && token.length > 10) {
      console.log(`✓ CF token 已生成 (长度: ${token.length})`);
      tokenFound = true;
      break;
    }
    console.log(`等待 token... (${i + 1}/20)`);
    await delay(1000);
  }
  
  if (!tokenFound) {
    console.log('✗ CF token 未生成');
  }
  
  console.log('点击注册按钮...');
  await page.click('button[type="submit"]');
  await delay(5000);
  
  const finalUrl = page.url();
  console.log(`最终 URL: ${finalUrl}`);
  
  if (finalUrl.includes('/login')) {
    console.log('✓ 注册成功！跳转到登录页面');
  } else {
    console.log('✗ 未跳转到登录页面');
  }
  
  await page.screenshot({ path: 'puppeteer-after-submit.png' });
  await browser.close();
  console.log('完成');
}

main().catch(console.error);
