# 开发工作流

## 日常开发

```bash
# 1. 更新代码
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/xxx
# 或修复分支
git checkout -b fix/xxx

# 3. 开发并测试

# 4. 提交
git add -A && git commit -m "feat: 添加新功能"
# 或
git add -A && git commit -m "fix: 修复问题"

# 5. 推送
git push -u origin feature/xxx
```

## 提交规范

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| refactor | 重构 |
| docs | 文档 |
| style | 格式 |
| test | 测试 |
| chore | 构建/工具 |

## Lint 检查

```bash
# Backend
cd backend && ruff check .

# Frontend
cd frontend && pnpm lint
```

## 测试

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && pnpm test
```

## 运行项目

```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && pnpm dev
```
