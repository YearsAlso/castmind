import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Search, Filter, Eye, EyeOff, CheckCircle, Clock, Calendar, Hash } from 'lucide-react'

const API_BASE = '/api/v1'

export default function Articles() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [page, setPage] = useState(1)
  const pageSize = 20

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', page, statusFilter],
    queryFn: () => axios.get(`${API_BASE}/articles`, {
      params: {
        page,
        page_size: pageSize,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      }
    }).then(res => res.data),
  })

  const { data: stats } = useQuery({
    queryKey: ['article-stats'],
    queryFn: () => axios.get(`${API_BASE}/articles/stats/summary`).then(res => res.data),
  })

  const filteredArticles = articles?.filter((article: any) => {
    if (!search) return true
    const searchLower = search.toLowerCase()
    return (
      article.title?.toLowerCase().includes(searchLower) ||
      article.content?.toLowerCase().includes(searchLower) ||
      article.feed_name?.toLowerCase().includes(searchLower)
    )
  })

  const statusTabs = [
    { id: 'all', label: '全部', count: stats?.total || 0 },
    { id: 'unread', label: '未读', count: stats?.unread || 0 },
    { id: 'read', label: '已读', count: (stats?.total || 0) - (stats?.unread || 0) },
    { id: 'processed', label: '已处理', count: stats?.processed || 0 },
  ]

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">加载文章...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">文章管理</h1>
        <p className="text-gray-600">查看和管理抓取的文章内容</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {statusTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setStatusFilter(tab.id)}
            className={`card text-left transition-colors ${
              statusFilter === tab.id
                ? 'border-primary-500 bg-primary-50'
                : 'hover:bg-gray-50'
            }`}
          >
            <div className="text-2xl font-bold text-gray-900">{tab.count}</div>
            <div className="text-sm text-gray-600">{tab.label}</div>
          </button>
        ))}
      </div>

      {/* 搜索和筛选 */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索文章标题或内容..."
              className="input pl-10"
            />
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Filter className="h-4 w-4 text-gray-400 mr-2" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input py-1 text-sm"
              >
                {statusTabs.map((tab) => (
                  <option key={tab.id} value={tab.id}>
                    {tab.label} ({tab.count})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* 文章列表 */}
      <div className="space-y-4">
        {filteredArticles?.map((article: any) => (
          <div key={article.id} className="card hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {article.title}
                </h3>
                <div className="flex items-center text-sm text-gray-500 mb-2">
                  <Calendar className="h-3 w-3 mr-1" />
                  {new Date(article.published_at).toLocaleDateString()}
                  <span className="mx-2">•</span>
                  <Hash className="h-3 w-3 mr-1" />
                  {article.feed_name}
                </div>
                {article.summary && (
                  <p className="text-gray-600 line-clamp-2">{article.summary}</p>
                )}
              </div>
              <div className="flex items-center space-x-2 ml-4">
                {article.read_status ? (
                  <span className="badge badge-success flex items-center">
                    <Eye className="h-3 w-3 mr-1" />
                    已读
                  </span>
                ) : (
                  <span className="badge badge-warning flex items-center">
                    <EyeOff className="h-3 w-3 mr-1" />
                    未读
                  </span>
                )}
                {article.processed_status && (
                  <span className="badge badge-success flex items-center">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    已处理
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex justify-between items-center pt-3 border-t border-gray-100">
              <div className="flex items-center text-sm text-gray-500">
                <Clock className="h-3 w-3 mr-1" />
                抓取于 {new Date(article.created_at).toLocaleString()}
              </div>
              <div className="flex space-x-2">
                <button className="text-sm text-primary-600 hover:text-primary-800">
                  标记为已读
                </button>
                <button className="text-sm text-gray-600 hover:text-gray-800">
                  查看详情
                </button>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  原文链接
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 分页 */}
      {articles && articles.length > 0 && (
        <div className="flex justify-center items-center mt-8 space-x-4">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="btn btn-secondary px-4"
          >
            上一页
          </button>
          <span className="text-gray-600">
            第 {page} 页
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={articles.length < pageSize}
            className="btn btn-secondary px-4"
          >
            下一页
          </button>
        </div>
      )}

      {(!filteredArticles || filteredArticles.length === 0) && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-2">暂无文章</div>
          <p className="text-gray-500">
            {search ? '没有找到匹配的文章' : '添加订阅源并等待抓取文章'}
          </p>
        </div>
      )}
    </div>
  )
}