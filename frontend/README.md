# 🎯 CastMind 前端

基于 React + TypeScript + Vite 的现代化管理界面。

## 🚀 快速开始

### 安装依赖
```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── pages/          # 页面组件
│   │   ├── Dashboard.tsx
│   │   ├── Feeds.tsx
│   │   ├── Articles.tsx
│   │   └── System.tsx
│   ├── components/     # 可复用组件
│   ├── hooks/         # 自定义 Hooks
│   ├── api/           # API 接口定义
│   ├── App.tsx        # 主应用组件
│   ├── main.tsx       # 应用入口
│   └── index.css      # 全局样式
├── public/            # 静态资源
├── index.html         # HTML 模板
├── package.json       # 依赖配置
├── vite.config.ts     # Vite 配置
├── tsconfig.json      # TypeScript 配置
├── tailwind.config.js # Tailwind CSS 配置
└── postcss.config.js  # PostCSS 配置
```

## 🎨 技术栈

- **React 18** - 用户界面库
- **TypeScript** - 类型安全
- **Vite** - 构建工具和开发服务器
- **Tailwind CSS** - 实用优先的 CSS 框架
- **React Router** - 路由管理
- **TanStack Query** - 数据获取和状态管理
- **Axios** - HTTP 客户端
- **Lucide React** - 图标库

## 🔌 API 集成

前端通过代理连接到后端 API：

```javascript
// 开发环境代理配置 (vite.config.ts)
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### 主要 API 端点
- `GET /api/v1/feeds` - 获取订阅源列表
- `GET /api/v1/articles` - 获取文章列表
- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/stats` - 系统统计

## 🎯 功能特性

### 1. 仪表板
- 系统状态概览
- 关键指标统计
- 订阅源状态监控
- 快速操作入口

### 2. 订阅源管理
- 添加/编辑/删除 RSS 订阅源
- 手动触发抓取
- 状态筛选和搜索
- 批量操作

### 3. 文章管理
- 文章列表和搜索
- 阅读状态管理
- 分页和筛选
- 内容预览

### 4. 系统管理
- 服务状态监控
- 任务调度控制
- 系统配置管理
- 日志查看

## 🛠️ 开发指南

### 添加新页面
1. 在 `src/pages/` 创建新组件
2. 在 `src/App.tsx` 中添加路由
3. 在导航栏中添加链接

### 创建可复用组件
1. 在 `src/components/` 中创建组件
2. 使用 TypeScript 定义 Props 类型
3. 添加必要的样式和逻辑

### API 调用
使用 TanStack Query 进行数据获取：

```typescript
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const { data, isLoading } = useQuery({
  queryKey: ['feeds'],
  queryFn: () => axios.get('/api/v1/feeds').then(res => res.data),
})
```

## 🎨 样式指南

### 使用 Tailwind CSS
- 使用实用类进行样式设计
- 保持一致的间距和颜色
- 响应式设计优先

### 自定义类
在 `src/index.css` 中定义自定义类：

```css
@layer components {
  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700;
  }
  .card {
    @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
  }
}
```

## 📱 响应式设计

项目支持移动端和桌面端：

- **移动端 (< 640px)**: 底部导航栏
- **平板 (640px - 1024px)**: 自适应布局
- **桌面 (> 1024px)**: 完整导航栏和侧边栏

## 🔧 环境变量

创建 `.env` 文件：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🐛 故障排除

### 常见问题

1. **API 连接失败**
   - 确保后端服务正在运行
   - 检查代理配置

2. **样式不生效**
   - 检查 Tailwind 配置
   - 确保正确导入 CSS 文件

3. **TypeScript 错误**
   - 检查类型定义
   - 更新类型声明

### 开发工具
- React Developer Tools
- TanStack Query Devtools
- Tailwind CSS IntelliSense

## 📄 许可证

MIT License