# CastMind Agent

## 概述

基于 Anthropic 文章 "Effective Harnesses for Long-Running Agents" 设计的代码优化 Agent 框架，专注于 UX 优化。

## 核心理念

1. **增量开发**: 每次只做一个功能点
2. **状态管理**: 通过文件记录进度
3. **UX 优先**: 优先修复严重交互问题
4. **清洁提交**: 确保代码可合并

## 目录结构

```
castmind-optimizer/
├── SKILL.md
├── README.md
├── scripts/
│   └── agent_loop.sh
├── references/
│   ├── ux_audit.md          # UX 审核报告
│   ├── project_structure.md
│   ├── api_endpoints.md
│   ├── database_models.md
│   ├── frontend_pages.md
│   ├── coding_standards.md
│   └── workflow.md
└── artifacts/
    ├── CLAUDE_PROGRESS.md  # 进度记录
    ├── feature_list.json    # 功能列表 (含 UX)
    └── init.sh
```

## 任务优先级

### P0 - 立即修复 (用户体验严重问题)
- 创建 Articles 页面
- 播客内置播放器
- Toast 通知

### P1 - 交互优化 (操作流程问题)
- 快速添加 Modal
- 一键处理按钮
- 导航统一命名

### P2 - 体验提升 (建议改进)
- 骨架屏
- 批量操作
- 移动端优化

## 工作流程

```bash
# 1. 查看当前任务
cat artifacts/CLAUDE_PROGRESS.md

# 2. 查看功能列表
cat artifacts/feature_list.json

# 3. 选择一个任务
# 选择 priority=1 且 passes=false 的任务

# 4. 执行任务
# ... 修改代码 ...

# 5. 提交并更新
# git commit + 更新 feature_list.json
```

## UX 审核清单

修改代码前检查:
- [ ] 是否有 Toast 反馈?
- [ ] 加载状态是否友好?
- [ ] 操作步骤是否最少?
- [ ] 移动端是否可用?
- [ ] 错误处理是否明确?
