# CastMind 开发进度

## 系统目标

**CastMind** - 可私有化部署的播客 AI 辅助系统

- 播客订阅管理 (RSS/Atom/RSSHub)
- 音频下载与本地存储
- 语音转文字 (Whisper)
- AI 内容分析 (DeepSeek/OpenAI)
- 定时自动抓取与处理

---

## UX 审核结果 (2025-02-23)

### 🔴 严重问题 (P0 - 立即修复)

| # | 问题 | 影响 | 位置 |
|---|------|------|------|
| 1 | 缺少 Articles 页面 | 内容消费流程不完整 | App.tsx |
| 2 | 播客无内置播放器 | 需跳转到外部播放 | Podcasts.tsx |
| 3 | 无 Toast 通知 | 用户不知操作结果 | 所有页面 |

### 🟠 交互问题 (P1 - 需要优化)

| # | 问题 | 建议方案 |
|---|------|----------|
| 4 | 添加订阅源流程长 | 快速添加 Modal |
| 5 | 播客处理需3步 | 一键处理按钮 |
| 6 | 导航语义不清 | 统一命名 |

### 🟡 体验提升 (P2 - 建议改进)

| # | 问题 | 建议方案 |
|---|------|----------|
| 7 | 加载体验差 | 骨架屏 |
| 8 | 无批量操作 | 批量选择 |
| 9 | 移动端体验差 | 响应式优化 |

---

## 当前状态

### ✅ 已完成功能

- FastAPI 后端 + React 前端
- 订阅源管理 (CRUD)
- 播客下载/转录/分析流程
- 定时任务调度
- Skills/Agent Loop 框架

### 🚨 待完成任务

**P0 (立即修复):**
1. 创建 Articles.tsx 页面
2. Podcasts 添加内置播放器
3. 添加 Toast 通知组件

**P1 (交互优化):**
4. 订阅源快速添加 Modal
5. 播客一键处理按钮
6. 统一导航命名

**P2 (体验提升):**
7. 骨架屏加载
8. 批量操作
9. 移动端优化

---

## Feature List

详见 `artifacts/feature_list.json` (12 个任务)

---

## 下一步 (需要 OpenCode 执行)

### 立即执行 P0 任务:

1. **创建 Articles.tsx 页面**
   - 参考 Excerpts.tsx 结构
   - 实现列表、分页、筛选

2. **Podcasts 添加内置播放器**
   - 使用 `<audio>` 标签
   - 添加播放控制 UI

3. **添加 Toast 通知**
   - 安装 react-hot-toast
   - 在所有 mutation 中使用

---

## 常用命令

```bash
# 启动开发服务器
./skills/castmind-optimizer/artifacts/init.sh

# 运行 lint
cd backend && ruff check .
cd frontend && pnpm lint

# 测试
pytest
```

---

## 进度更新

- 2025-02-23: 完成 UX 审核，发布 P0-P2 任务列表

### 2026-02-23 16:04 - Coding Agent
- 任务: 修复 RSSHub SSL 证书验证失败问题
  - 测试: 通过
  - Lint: 通过
  - 提交: 否

### 2026-02-23 17:12 - Coding Agent
- 任务: 添加 Toast 通知组件
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 17:31 - Coding Agent
- 任务: 创建订阅源快速添加 Modal
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 19:53 - Coding Agent
- 任务: 播客页面添加一键处理按钮
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 19:57 - Coding Agent
- 任务: 统一导航命名
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 20:09 - Coding Agent
- 任务: 添加骨架屏加载状态
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 20:22 - Coding Agent
- 任务: 添加批量操作功能
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 21:12 - Coding Agent
- 任务: 移动端响应式优化
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-23 21:19 - Coding Agent
- 任务: 添加搜索快捷键 (Cmd+K)
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-24 09:15 - Coding Agent
- 任务: 提取公共 hooks 减少重复代码
  - 测试: 通过
  - Lint: 通过
  - 提交: 是

### 2026-02-24 09:15 - Coding Agent
- 任务: 完善 TypeScript 类型定义
  - 测试: 通过
  - Lint: 通过
  - 提交: 是
