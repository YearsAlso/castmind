# 代码规范

## Backend (Python)

### Ruff 检查
```bash
cd backend && ruff check .
```

### 遵循 PEP 8
- 4 空格缩进
- 最大行长 88 字符

### 类型注解
```python
def function(param: str) -> str:
    return param
```

### 导入顺序
1. 标准库
2. 第三方库
3. 本地模块

---

## Frontend (TypeScript/React)

### ESLint
```bash
cd frontend && pnpm lint
```

### 组件规范
```tsx
interface Props {
  title: string
}

const Component: React.FC<Props> = ({ title }) => {
  return <div>{title}</div>
}
```

### 命名
- 组件: PascalCase
- 变量/函数: camelCase
- 常量: UPPER_SNAKE_CASE
