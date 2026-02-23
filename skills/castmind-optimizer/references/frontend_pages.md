# 前端页面

## 页面列表

| 组件 | 路由 | 说明 |
|------|------|------|
| Dashboard.tsx | / | 仪表盘，展示统计和最近内容 |
| Feeds.tsx | /feeds | 订阅源管理 |
| Articles.tsx | /articles | 文章列表 |
| Excerpts.tsx | /excerpts | 摘录管理 |
| Podcasts.tsx | /podcasts | 播客管理 |
| System.tsx | /system | 系统设置 |

## 常用模式

### 使用 TanStack Query
```tsx
const { data, isLoading } = useQuery({
  queryKey: ['feeds'],
  queryFn: () => axios.get('/api/v1/feeds/').then(res => res.data),
})

const mutation = useMutation({
  mutationFn: (data) => axios.post('/api/v1/feeds/', data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['feeds'] })
  }
})
```

### 表单提交
```tsx
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  mutation.mutate(formData)
}
```

### 条件渲染
```tsx
{showForm && (
  <div className="card">
    <form onSubmit={handleSubmit}>...</form>
  </div>
)}
```
