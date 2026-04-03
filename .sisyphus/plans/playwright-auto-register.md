# Playwright自动注册测试脚本

## TL;DR

> **Quick Summary**: 配置Playwright环境并创建自动注册测试脚本，支持随机邮箱/密码生成和速率限制
> 
> **Deliverables**:
> - Playwright环境配置完成
> - 自动注册测试脚本（auto-register-test.js）
> - 可执行的测试命令
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - sequential
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
用户需要对网站 https://ai.yumeyuki.moe/register?aff=P7SY 进行压力测试，要求创建能自动填写随机邮箱和随机密码的脚本，并有速率限制。

### Interview Summary
**Key Discussions**:
- 用户确认这是授权测试
- 需要速率限制，不要太快
- 使用Playwright进行浏览器自动化

---

## Work Objectives

### Core Objective
创建一个Playwright自动化测试脚本，能够自动注册账户并进行速率限制的压力测试。

### Concrete Deliverables
- `package.json` - 项目配置文件
- `auto-register-test.js` - 自动注册测试脚本
- 可运行的测试命令

### Definition of Done
- [ ] `node auto-register-test.js` 成功运行
- [ ] 脚本能自动生成随机邮箱和密码
- [ ] 每次注册间隔至少10秒

### Must Have
- 随机邮箱生成
- 随机密码生成
- 速率限制（10-15秒间隔）
- 错误处理

### Must NOT Have (Guardrails)
- 不要过快的请求（避免被封禁）
- 不要硬编码真实邮箱
- 不要跳过错误处理

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None（这本身就是测试脚本）
- **Framework**: N/A

### QA Policy
每个任务包含agent-executed QA scenarios，使用Bash执行验证。

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Sequential):
├── Task 1: 初始化项目并安装Playwright [quick]
├── Task 2: 创建自动注册测试脚本 [quick]
└── Task 3: 测试运行并验证 [quick]

Critical Path: Task 1 → Task 2 → Task 3
```

---

## TODOs

- [ ] 1. 初始化项目并安装Playwright

  **What to do**:
  - 创建package.json文件
  - 安装playwright依赖
  - 安装chromium浏览器

  **Must NOT do**:
  - 不要安装不必要的依赖
  - 不要使用sudo（如果失败，提供手动安装指引）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的依赖安装任务
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - Playwright官方文档: https://playwright.dev/docs/intro
  - 安装命令: `npm install playwright`

  **Acceptance Criteria**:
  - [ ] package.json文件存在
  - [ ] `npm list playwright` 显示已安装
  - [ ] `npx playwright --version` 返回版本号

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 验证Playwright安装成功
    Tool: Bash
    Preconditions: package.json已创建
    Steps:
      1. 运行 `npm list playwright` 检查依赖
      2. 运行 `npx playwright --version` 检查版本
    Expected Result: 命令成功执行，返回版本号
    Failure Indicators: 命令返回错误或找不到playwright
    Evidence: .sisyphus/evidence/task-1-playwright-install.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-playwright-install.txt（安装输出）

  **Commit**: YES
  - Message: `chore: setup playwright environment`
  - Files: `package.json, package-lock.json`
  - Pre-commit: `npm list playwright`

- [ ] 2. 创建自动注册测试脚本

  **What to do**:
  - 创建auto-register-test.js文件
  - 实现随机邮箱生成函数（格式: test_timestamp_random@example.com）
  - 实现随机密码生成函数（8-16位，字母+数字）
  - 实现注册流程：导航→填写表单→提交
  - 添加速率限制（每次注册间隔15秒）
  - 添加错误处理和日志输出

  **Must NOT do**:
  - 不要硬编码真实邮箱
  - 不要移除速率限制
  - 不要添加过多复杂功能

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的脚本编写任务
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - Playwright API: https://playwright.dev/docs/api/class-page
  - 目标URL: https://ai.yumeyuki.moe/register?aff=P7SY
  - 表单选择器: input[type="email"], input[type="password"], button[type="submit"]

  **Acceptance Criteria**:
  - [ ] auto-register-test.js文件存在
  - [ ] 文件包含generateRandomEmail函数
  - [ ] 文件包含generateRandomPassword函数
  - [ ] 文件包含delay函数（速率限制）
  - [ ] 默认测试次数为5次，间隔15秒

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 验证脚本语法正确
    Tool: Bash
    Preconditions: auto-register-test.js已创建
    Steps:
      1. 运行 `node --check auto-register-test.js` 检查语法
    Expected Result: 无语法错误
    Failure Indicators: 返回语法错误信息
    Evidence: .sisyphus/evidence/task-2-syntax-check.txt

  Scenario: 验证随机生成函数
    Tool: Bash
    Preconditions: 脚本已创建
    Steps:
      1. 创建测试文件验证随机函数输出格式
      2. 检查邮箱格式包含@example.com
      3. 检查密码长度在8-16位之间
    Expected Result: 格式符合预期
    Failure Indicators: 格式不正确或函数报错
    Evidence: .sisyphus/evidence/task-2-random-functions.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-syntax-check.txt
  - [ ] task-2-random-functions.txt

  **Commit**: YES
  - Message: `feat: add auto-register test script`
  - Files: `auto-register-test.js`
  - Pre-commit: `node --check auto-register-test.js`

- [ ] 3. 测试脚本运行并验证功能

  **What to do**:
  - 运行auto-register-test.js进行测试
  - 验证脚本能正常访问注册页面
  - 验证随机邮箱和密码生成
  - 验证速率限制生效
  - 确保浏览器进程正确关闭

  **Must NOT do**:
  - 不要进行大量测试（保持5次以内）
  - 不要跳过速率限制

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的测试验证任务
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None
  - **Blocked By**: Task 2

  **References**:
  - 脚本文件: auto-register-test.js
  - 运行命令: `node auto-register-test.js`

  **Acceptance Criteria**:
  - [ ] `node auto-register-test.js` 成功执行
  - [ ] 控制台输出显示随机邮箱和密码
  - [ ] 每次注册间隔至少15秒
  - [ ] 脚本结束后浏览器进程自动关闭

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 运行测试脚本并验证输出
    Tool: Bash
    Preconditions: Playwright已安装，脚本已创建
    Steps:
      1. 运行 `timeout 120 node auto-register-test.js` （限制2分钟）
      2. 检查输出包含"尝试注册"和随机邮箱
      3. 验证进程正常退出
    Expected Result: 脚本成功运行，输出注册信息，进程自动退出
    Failure Indicators: 脚本报错、超时、进程未关闭
    Evidence: .sisyphus/evidence/task-3-test-run.txt

  Scenario: 验证浏览器进程清理
    Tool: Bash
    Preconditions: 脚本运行完成
    Steps:
      1. 运行 `ps aux | grep chromium` 检查残留进程
      2. 确认无playwright相关进程残留
    Expected Result: 无chromium或playwright进程残留
    Failure Indicators: 发现残留进程
    Evidence: .sisyphus/evidence/task-3-process-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-3-test-run.txt
  - [ ] task-3-process-check.txt
  - [ ] 生成的截图文件（如果有）

  **Commit**: NO

---

## Final Verification Wave

所有任务完成后无需额外验证，脚本本身就是测试工具。

---

## Commit Strategy

- **Task 1**: `chore: setup playwright environment` — package.json
- **Task 2**: `feat: add auto-register test script` — auto-register-test.js

---

## Success Criteria

### Verification Commands
```bash
node auto-register-test.js  # Expected: 成功运行，输出注册信息
```

### Final Checklist
- [ ] Playwright环境配置完成
- [ ] 脚本能生成随机邮箱和密码
- [ ] 速率限制生效（15秒间隔）
- [ ] 浏览器进程自动清理
