import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { 
  Search, Filter, Eye, EyeOff, CheckCircle, Clock, 
  Calendar, Hash, FileText, Copy, BookOpen, Star,
  FileEdit, Template, Layout
} from 'lucide-react'

const API_BASE = '/api/v1'

// 默认文档模板
const DEFAULT_TEMPLATES = [
  {
    id: 'simple',
    name: '简洁摘要',
    description: '基础的文章摘要格式',
    template: `# {{title}}

**来源**: {{feed_name}}
**发布时间**: {{published_at}}
**关键词**: {{keywords}}

## 摘要
{{summary}}

## 主要内容
{{content}}

## AI分析
- **情感倾向**: {{sentiment}}
- **关键要点**: {{key_points}}
- **行动建议**: {{action_items}}`
  },
  {
    id: 'detailed',
    name: '详细笔记',
    description: '包含完整分析和结构的笔记',
    template: `# {{title}}

## 基本信息
- **来源**: {{feed_name}}
- **URL**: {{url}}
- **发布时间**: {{published_at}}
- **阅读状态**: {{read_status ? '已读' : '未读'}}
- **处理状态**: {{processed_status ? '已处理' : '未处理'}}

## 内容摘要
{{summary}}

## 完整内容
{{content}}

## AI深度分析

### 关键词提取
{{keywords}}

### 情感分析
{{sentiment}}

### 商业洞察
{{business_insights}}

### 技术要点
{{technical_points}}

### 行动建议
{{action_items}}

## 元数据
- **创建时间**: {{created_at}}
- **更新时间**: {{updated_at}}
- **文章ID**: {{id}}
- **订阅源ID**: {{feed_id}}`
  },
  {
    id: 'podcast',
    name: '播客笔记',
    description: '专门为播客内容优化的模板',
    template: `# 🎙️ {{title}}

## 📋 播客信息
- **节目**: {{feed_name}}
- **发布时间**: {{published_at}}
- **时长**: {{duration}}
- **主持人**: {{hosts}}
- **嘉宾**: {{guests}}

## 🎯 核心观点
{{key_points}}

## 📝 详细笔记

### 主要内容
{{content}}

### 精彩片段
{{highlights}}

### 引用和名言
{{quotes}}

## 🤖 AI分析

### 情感基调
{{sentiment}}

### 话题分布
{{topics}}

### 学习收获
{{learnings}}

### 行动启发
{{inspirations}}

## 🔗 相关资源
- 播客链接: {{url}}
- 相关文章: {{related_articles}}
- 推荐工具: {{recommended_tools}}`
  }
]

export default function Excerpts() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [showTemplates, setShowTemplates] = useState(false)
  const [activeTemplate, setActiveTemplate] = useState(DEFAULT_TEMPLATES[0])
  const [customTemplate, setCustomTemplate] = useState('')
  const [selectedExcerpts, setSelectedExcerpts] = useState<number[]>([])
  const pageSize = 20

  const queryClient = useQueryClient()

  const { data: excerpts, isLoading } = useQuery({
    queryKey: ['excerpts', page, statusFilter],
    queryFn: () => axios.get(`${API_BASE}/articles`, {
      params: {
        page,
        page_size: pageSize,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      }
    }).then(res => res.data),
  })

  const { data: stats } = useQuery({
    queryKey: ['excerpt-stats'],
    queryFn: () => axios.get(`${API_BASE}/articles/stats/summary`).then(res => res.data),
  })

  const markAsReadMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/mark-read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['excerpts'] })
      queryClient.invalidateQueries({ queryKey: ['excerpt-stats'] })
    },
  })

  const markAsUnreadMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/mark-unread`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['excerpts'] })
      queryClient.invalidateQueries({ queryKey: ['excerpt-stats'] })
    },
  })

  const filteredExcerpts = excerpts?.filter((excerpt: any) => {
    if (!search) return true
    const searchLower = search.toLowerCase()
    return (
      excerpt.title?.toLowerCase().includes(searchLower) ||
      excerpt.content?.toLowerCase().includes(searchLower) ||
      excerpt.feed_name?.toLowerCase().includes(searchLower) ||
      excerpt.summary?.toLowerCase().includes(searchLower) ||
      excerpt.keywords?.toLowerCase().includes(searchLower)
    )
  })

  const statusTabs = [
    { id: 'all', label: '全部摘录', count: stats?.total || 0 },
    { id: 'unread', label: '未读', count: stats?.unread || 0 },
    { id: 'read', label: '已读', count: (stats?.total || 0) - (stats?.unread || 0) },
    { id: 'processed', label: '已处理', count: stats?.processed || 0 },
  ]

  const handleSelectExcerpt = (id: number) => {
    setSelectedExcerpts(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    if (selectedExcerpts.length === filteredExcerpts?.length) {
      setSelectedExcerpts([])
    } else {
      setSelectedExcerpts(filteredExcerpts?.map((e: any) => e.id) || [])
    }
  }

  const handleCopyTemplate = () => {
    navigator.clipboard.writeText(customTemplate || activeTemplate.template)
    alert('模板已复制到剪贴板')
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">加载摘录...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">摘录管理</h1>
          <p className="text-gray-600">管理从订阅源提取的内容摘录和笔记</p>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="btn btn-secondary flex items-center"
          >
            <Template className="h-4 w-4 mr-2" />
            {showTemplates ? '隐藏模板' : '文档模板'}
          </button>
        </div>
      </div>

      {/* 文档模板编辑器 */}
      {showTemplates && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">文档生成模板</h2>
            <button
              onClick={handleCopyTemplate}
              className="btn btn-sm btn-secondary flex items-center"
            >
              <Copy className="h-3 w-3 mr-1" />
              复制模板
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {DEFAULT_TEMPLATES.map((template) => (
              <div
                key={template.id}
                onClick={() => {
                  setActiveTemplate(template)
                  setCustomTemplate(template.template)
                }}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  activeTemplate.id === template.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center mb-2">
                  <Layout className="h-5 w-5 text-gray-600 mr-2" />
                  <h3 className="font-medium text-gray-900">{template.name}</h3>
                </div>
                <p className="text-sm text-gray-600">{template.description}</p>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              自定义模板
            </label>
            <div className="text-xs text-gray-500 mb-2">
              可用变量: {'{{title}}'} {'{{content}}'} {'{{summary}}'} {'{{feed_name}}'} {'{{published_at}}'} {'{{keywords}}'} {'{{sentiment}}'} 等
            </div>
            <textarea
              value={customTemplate}
              onChange={(e) => setCustomTemplate(e.target.value)}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
              placeholder="输入自定义模板..."
            />
          </div>
        </div>
      )}

      {/* 搜索和筛选 */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索摘录内容、标题、关键词..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-700">筛选:</span>
            </div>
            <div className="flex space-x-1">
              {statusTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setStatusFilter(tab.id)}
                  className={`px-3 py-1 text-sm rounded-full ${
                    statusFilter === tab.id
                      ? 'bg-primary-100 text-primary-800'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {tab.label} {tab.count > 0 && `(${tab.count})`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 摘录列表 */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  标题
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  来源
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  发布时间
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredExcerpts?.map((excerpt: any) => (
                <tr key={excerpt.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="max-w-md">
                      <div className="font-medium text-gray-900 truncate">
                        {excerpt.title}
                      </div>
                      {excerpt.summary && (
                        <div className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {excerpt.summary}
                        </div>
                      )}
                      {excerpt.keywords && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {excerpt.keywords.split(',').slice(0, 3).map((keyword: string, idx: number) => (
                            <span
                              key={idx}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              <Hash className="h-3 w-3 mr-1" />
                              {keyword.trim()}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{excerpt.feed_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {excerpt.read_status ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <Eye className="h-3 w-3 mr-1" />
                          已读
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <EyeOff className="h-3 w-3 mr-1" />
                          未读
                        </span>
                      )}
                      {excerpt.processed_status && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          已处理
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {excerpt.published_at ? new Date(excerpt.published_at).toLocaleDateString() : '--'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => window.open(excerpt.url, '_blank')}
                        className="text-gray-600 hover:text-gray-900"
                        title="查看原文"
                      >
                        <BookOpen className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => excerpt.read_status ? markAsUnreadMutation.mutate(excerpt.id) : markAsReadMutation.mutate(excerpt.id)}
                        className="text-gray-600 hover:text-gray-900"
                        title={excerpt.read_status ? "标记为未读" : "标记为已读"}
                      >
                        {excerpt.read_status ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        {excerpts?.length > 0 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
            <div className="text-sm text-gray-700">
              显示第 {(page - 1) * pageSize + 1} 到 {Math.min(page * pageSize, stats?.total || 0)} 条，共 {stats?.total || 0} 条摘录
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page * pageSize >= (stats?.total || 0)}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          </div>
        )}

        {(!excerpts || excerpts.length === 0) && (
          <div className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无摘录</h3>
            <p className="text-gray-600 max-w-md mx-auto">
              还没有从订阅源中提取到内容。请确保订阅源正常工作并已抓取到内容。
            </p>
          </div>
        )}
      </div>

      {/* 使用提示 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div