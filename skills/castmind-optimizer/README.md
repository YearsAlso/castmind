# Agent Loop 使用指南

## 快速开始

### 1. 初始化项目 (第一次)

```bash
# 创建 artifacts 目录结构
mkdir -p skills/castmind-optimizer/artifacts

# 查看现有功能列表
cat skills/castmind-optimizer/artifacts/feature_list.json
```

### 2. 开始开发

每次开发时：

```bash
# 1. 查看当前状态
cat skills/castmind-optimizer/artifacts/CLAUDE_PROGRESS.md
git log --oneline -10

# 2. 验证环境
cd backend && ruff check .   # Python lint
cd ../frontend && pnpm lint   # JS lint

# 3. 选择一个功能
# 打开 feature_list.json，选择 passes=false 的第一个

# 4. 实现功能
# ... 修改代码 ...

# 5. 测试
pytest  # 或 pnpm test

# 6. 提交
git add -A && git commit -m "feat: 描述"

# 7. 更新进度
# - feature_list.json: 将该功能 passes 改为 true
# - CLAUDE_PROGRESS.md: 添加完成记录
```

## 文件说明

| 文件 | 作用 |
|------|------|
| `feature_list.json` | 所有功能点列表，标记完成状态 |
| `CLAUDE_PROGRESS.md` | 每次 session 的进度记录 |
| `init.sh` | 启动开发服务器脚本 |
| `agent_loop.sh` | 辅助脚本，提供菜单操作 |

## 核心原则

1. **每次只做一个功能**
2. **完成后必须测试**
3. **提交时更新进度文件**
4. **确保代码可合并**

## 添加新功能

编辑 `feature_list.json`:

```json
{
  "category": "backend|frontend|database",
  "description": "功能描述",
  "steps": ["步骤1", "步骤2"],
  "passes": false,
  "priority": 1
}
```

## 常见问题

### Q: 如何知道下一步做什么？
A: 查看 `feature_list.json` 中 `passes: false` 且 `priority` 最小的项

### Q: 代码有问题怎么办？
A: 使用 `git revert` 或 `git checkout` 恢复，参考 CLAUDE_PROGRESS.md 中的记录

### Q: 环境起不来怎么办？
A: 运行 `agent_loop.sh verify` 检查依赖
