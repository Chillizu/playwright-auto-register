# Repository Agent Guide

This document explains how to build, test, lint, and maintain the Puppeteer/Playwright automation suite stored in this repository. It is written for agentic tools that may make changes, run experiments, or debug failures. Any agent working here should read the sections below before making edits.

***

## 1. Commands & Automation

### 1.1 Standard setup
- `npm install` — install dependencies from `package-lock.json`. Run this before touching any automation scripts or tests.
- `node auto-register-test.js` — execute the primary automation scenario described in `README-auto-register.md`. This script drives Chromium through Playwright with stealth tweaks and is the de facto smoke test for the repo.
- `npm test` — currently wired to `echo "Error: no test specified" && exit 1`. Do not rely on it unless the package becomes more fully featured.

### 1.2 Running a single test scenario
The repository has no conventional test harness, so a "single test" means launching the automation once using `auto-register-test.js`. Recommended workflow:
1. Set the desired environment variables on the CLI: `TEST_COUNT=1 DELAY_MS=15000 HEADLESS=false`
2. Run `node auto-register-test.js` to perform one registration attempt.
3. Observe console output for `[结果]` log lines and screenshot files generated in the repo root (`register-*.png`).

### 1.3 Build & lint status
- There is no build step beyond installing Node dependencies; the scripts are plain CommonJS files. Keep `package-lock.json` in sync if dependencies change.
- No linting framework currently configured; format and style expectations are handled manually through the guidelines in Section 2.

### 1.4 Environment & execution notes
- The primary script assumes Node.js 14+ and Playwright packages from npm (`playwright`, `puppeteer`, `puppeteer-extra`).
- For Cloudflare turnstile validation, prefer running with a visible browser (`HEADLESS=false`). If running headless, expect `token 未生成` warnings and treat failures as expected.
- When running on Linux servers without a display, wrap the command with `xvfb-run -a`.
- `HEADLESS`, `TEST_COUNT`, and `DELAY_MS` are the only supported overrides; avoid injecting additional env variables unless you understand how `auto-register-test.js` uses them.

***

## 2. Repository Culture & Style Guidelines

These conventions keep the automation script readable, predictable, and easy to reason about. Treat them as binding when touching existing files or adding new helpers. If you need an exception, note it explicitly in your change description or PR comments.

### 2.1 Imports & module structure
- Stick with CommonJS: `const { chromium } = require('playwright');` as used in `auto-register-test.js`. Do not migrate to ESM unless the repo is converted wholesale.
- Keep auxiliary utilities close to the consuming file. There is currently only `auto-register-test.js`; adding new modules should follow the single-file pattern unless the helper grows significantly.
- Avoid nested or conditional requires; load dependencies at the top level for visibility.

### 2.2 Formatting & formatting
- Use 2 spaces for indentation to match the existing script. Align braces and control structures with consistent indentation.
- Prefer `const` for functions and values that do not change. Use `let` only for loop counters or variables that are reassigned within a block.
- Keep blank lines around logical sections (helper definitions, try/catch blocks, logging sections) to improve scanability.
- Strings should be wrapped in single quotes `'` unless interpolating with template literals or when a string contains an apostrophe.
- Use trailing commas sparingly (none in current code). Only add them when modifying a multiline list for easier diffing.

### 2.3 Types & JavaScript idioms
- Avoid mixing type systems; this repo is plain JavaScript without TypeScript or JSDoc types. Any type validation should remain in-code (e.g., `parseInt`, `typeof` checks) or rely on bound runtime behavior.
- Prefer descriptive helper names (`generateRandomUsername`, `mouseHumanMove`, `cleanup`). Keep helper logic focused and single-purpose.
- When introducing new data structures, default to plain objects and arrays. Do not bring in external schema libraries unless required for new features.

### 2.4 Naming & naming conventions
- Function names follow camelCase and describe the action performed (e.g., `typeHuman`, `registerUser`). Continue this pattern for new functions.
- Constants that represent configuration (such as `avgDelay` or environment variable keys) should be declared near the top of the relevant scope.
- Log prefixes (e.g., `[输入]`, `[等待]`, `[Cloudflare]`) should be preserved when expanding logging, to maintain the readable timeline in console output.

### 2.5 Logging & error handling
- Logs should remain human-friendly and informative. Use `console.log` for status messages and `console.error` for errors/stack traces.
- Wrap async operations in `try/catch` blocks when failure recovery or cleanup is necessary. Always log both the message and stack trace when catching unexpected errors (as seen in `registerUser` and `main`).
- When failing gracefully, return structured objects (`{ success: false, error: message }`) so callers can reason about status without rethrowing.
- Avoid swallowing errors silently; at minimum, log the error message even if you cannot recover.

### 2.6 Modularization & concurrency
- The repo currently runs sequential tests inside a `for` loop with rate limiting via `delay`. If you add parallelism, guard Chromium contexts carefully so multiple pages do not reuse the same browser or context handles.
- Keep shared utilities small and synchronous where possible to preserve deterministic timing.

### 2.7 Comments & documentation
- Maintain bilingual (Chinese/English) comments when they explain domain-specific behavior or non-obvious mitigations (e.g., `HEADLESS=false` required for CF turnstile). New comments should follow the tone of the existing ones: short, actionable, and ideally duplicated in both languages if the comment precedes a technical section.
- Avoid excessive comments for straightforward logic; let clean naming and structure explain intent.

### 2.8 Error & exception patterns
- When interacting with Playwright, guard DOM operations with `try/catch` and fallback logging (`console.log` for warnings). Document what happens when an element is not found (like logging `[查找元素] 未找到`).
- When calling `element.boundingBox()` or other APIs that may return `null`, add defensive checks before using the result.
- Always close Playwright artifacts (`page`, `context`, `browser`) in `finally` blocks or dedicated cleanup helpers. Log success/failure of cleanup explicitly.

### 2.9 Environment & security
- Do not commit real credentials or secrets. The repo stores only automation logic; keep any sensitive data in environment variables when needed.
- Respect Cloudflare rate limits and do not script loops without `delay` (15000ms default). If you reduce `DELAY_MS`, include a comment explaining why the safety margin was changed.

### 2.10 Contribution flow
- Before pushing changes, run `npm install` and the relevant automation command locally to verify there are no syntax/time issues.
- Add new screenshots or artifacts (like `register-*.png`) only if they are part of a regression capture; otherwise, keep the repo clean.
- Document any new environment variables or configuration toggles inside `README-auto-register.md` and refer back to this AGENTS guide if behavior impacts other agents.

***

## 3. Cursor / Copilot rules
- Cursor: none detected (no `.cursor/` directory or `.cursorrules`).
- GitHub Copilot: no `.github/copilot-instructions.md` file. No additional guidance.
  If such rules arrive in the future, replicate their sections here and reference the official file locations.

***

## 4. Verification / Next steps
- Run `node auto-register-test.js` locally to ensure new helpers do not break the automation workflow.
- When opening PRs, reference this AGENTS guide so reviewers know the command & style expectations.
