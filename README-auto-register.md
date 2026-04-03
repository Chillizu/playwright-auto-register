# 自动注册测试脚本使用说明

## 功能特性

✅ **已实现功能：**
- 随机用户名/密码生成
- 表单自动填写（用户名、密码、确认密码）
- 真实浏览器行为模拟（鼠标轨迹、随机延迟、逐字符输入）
- 速率限制（可配置间隔时间）
- 浏览器进程自动清理
- 详细的调试日志
- 反自动化检测（浏览器指纹伪装）

## 环境要求

- Node.js 14+
- Playwright 已安装
- **重要：** Cloudflare Turnstile 验证需要有头模式（非 headless）

## 使用方法

### 基础用法（默认配置）

```bash
node auto-register-test.js
```

默认配置：
- 测试次数：1 次
- 间隔时间：15 秒
- 浏览器模式：headless（无头模式）

### 高级用法（环境变量配置）

```bash
# 有头模式（推荐，可通过 CF 验证）
HEADLESS=false node auto-register-test.js

# 自定义测试次数
TEST_COUNT=5 node auto-register-test.js

# 自定义间隔时间（毫秒）
DELAY_MS=20000 node auto-register-test.js

# 组合使用
HEADLESS=false TEST_COUNT=10 DELAY_MS=30000 node auto-register-test.js
```

## Cloudflare Turnstile 问题

**问题：** Cloudflare Turnstile 在 headless 模式下检测到自动化，拒绝生成验证 token。

**解决方案：**

### 方案 1：有头模式（推荐）

在有图形界面的机器上运行：

```bash
HEADLESS=false node auto-register-test.js
```

### 方案 2：使用 xvfb（Linux 服务器）

安装 xvfb：
```bash
sudo apt-get install xvfb
```

运行脚本：
```bash
xvfb-run -a node auto-register-test.js
```

或者设置有头模式：
```bash
HEADLESS=false xvfb-run -a node auto-register-test.js
```

## 输出说明

脚本会生成：
- 控制台日志（详细的执行步骤）
- 截图文件（`register-*.png`）
- 最终统计结果（成功/失败次数，用户名和密码）

## 注意事项

1. **仅用于授权测试** - 确保你拥有该网站或有明确的测试授权
2. **遵守速率限制** - 避免过快的请求导致 IP 被封禁
3. **CF 验证** - 当前服务器环境（无 X Server）无法通过 CF Turnstile 验证
4. **建议在本地运行** - 在有图形界面的机器上使用有头模式效果最佳

## 故障排查

### Token 未生成

如果看到 `[Cloudflare] token 未生成，仍尝试提交`：
- 使用有头模式：`HEADLESS=false`
- 或使用 xvfb：`xvfb-run -a`

### 浏览器启动失败

如果看到 `Missing X server or $DISPLAY`：
- 安装 xvfb：`sudo apt-get install xvfb`
- 使用 xvfb 运行：`xvfb-run -a node auto-register-test.js`
