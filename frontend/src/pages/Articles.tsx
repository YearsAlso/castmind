import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import toast from 'react-hot-toast'
import {
  Search, Eye, EyeOff, CheckCircle,
  Hash, Copy, BookOpen,
  Trash2, RefreshCw, ChevronLeft, ChevronRight,
  ExternalLink, Calendar
} from 'lucide-react'
import { SkeletonList, ErrorState } from '../components/Skeleton'

const API_BASE = '/api/v1'

interface Article {
  id: string
  title: string
  url: string
  feed_name: string
  feed_id: string
  published_at: string
  created_at: string
  updated_at: string
  read_status: boolean
  processed_status: boolean
  summary?: string
  content?: string
  keywords?: string[]
  sentiment?: string
  key_points?: string[]
}

interface ArticlesResponse {
  data: Article[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export default function Articles() {
  const queryClient = useQueryClient()
  
  // 分页和筛选状态
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFeed, setSelectedFeed] = useState<string>('all')
  const [filterRead, setFilterRead] = useState<string>('all') // all, read, unread
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)

  // 获取文章列表
  const { data: articlesData, isLoading, error, refetch } = useQuery<ArticlesResponse>({
    queryKey: ['articles', page, pageSize, searchQuery, selectedFeed, filterRead],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      
      if (searchQuery) params.append('search', searchQuery)
      if (selectedFeed !== 'all') params.append('feed_id', selectedFeed)
      if (filterRead !== 'all') params.append('read_status', filterRead)
      
      const response = await axios.get(`${API_BASE}/articles?${params.toString()}`)
      return response.data
    },
  })

  // 获取订阅源列表（用于筛选）
  const { data: feedsData } = useQuery({
    queryKey: ['feeds'],
    queryFn: () => axios.get(`${API_BASE}/feeds`).then(res => res.data),
  })

  // 标记为已读/未读
  const toggleReadMutation = useMutation({
    mutationFn: (articleId: string) =>
      axios.patch(`${API_BASE}/articles/${articleId}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] })
      toast.success('阅读状态已更新')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '更新阅读状态失败')
    },
  })

  // 删除文章
  const deleteMutation = useMutation({
    mutationFn: (articleId: string) =>
      axios.delete(`${API_BASE}/articles/${articleId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] })
      setSelectedArticle(null)
      toast.success('文章删除成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '删除文章失败')
    },
  })

  // 复制链接
  const copyLink = (url: string) => {
    navigator.clipboard.writeText(url)
    toast.success('链接已复制到剪贴板')
  }

  // 格式化日期
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 渲染文章详情
  const renderArticleDetail = () => {
    if (!selectedArticle) return null

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-900">文章详情</h2>
            <button
              onClick={() => setSelectedArticle(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              {selectedArticle.title}
            </h1>
            
            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-6">
              <div className="flex items-center gap-1">
                <BookOpen size={16} />
                <span>{selectedArticle.feed_name}</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar size={16} />
                <span>{formatDate(selectedArticle.published_at)}</span>
              </div>
              <div className="flex items-center gap-1">
                {selectedArticle.read_status ? (
                  <CheckCircle size={16} className="text-green-600" />
                ) : (
                  <EyeOff size={16} className="text-gray-400" />
                )}
                <span>{selectedArticle.read_status ? '已读' : '未读'}</span>
              </div>
            </div>

            <div className="flex gap-2 mb-6">
              <a
                href={selectedArticle.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                <ExternalLink size={16} />
                阅读原文
              </a>
              <button
                onClick={() => copyLink(selectedArticle.url)}
                className="inline-flex items-center gap-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <Copy size={16} />
                复制链接
              </button>
              <button
                onClick={() => toggleReadMutation.mutate(selectedArticle.id)}
                className={`inline-flex items-center gap-1 px-4 py-2 rounded-md ${
                  selectedArticle.read_status 
                    ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {selectedArticle.read_status ? (
                  <><EyeOff size={16} /> 标记未读</>
                ) : (
                  <><Eye size={16} /> 标记已读</>
                )}
              </button>
              <button
                onClick={() => deleteMutation.mutate(selectedArticle.id)}
                className="inline-flex items-center gap-1 px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
              >
                <Trash2 size={16} />
                删除
              </button>
            </div>

            {selectedArticle.summary && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">摘要</h3>
                <div className="bg-gray-50 rounded-lg p-4 text-gray-700">
                  {selectedArticle.summary}
                </div>
              </div>
            )}

            {selectedArticle.keywords && selectedArticle.keywords.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">关键词</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedArticle.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      <Hash size={12} />
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedArticle.key_points && selectedArticle.key_points.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">关键要点</h3>
                <ul className="list-disc list-inside bg-gray-50 rounded-lg p-4 text-gray-700 space-y-1">
                  {selectedArticle.key_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedArticle.content && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">完整内容</h3>
                <div className="bg-gray-50 rounded-lg p-4 text-gray-700 whitespace-pre-wrap">
                  {selectedArticle.content}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">文章列表</h1>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
        >
          <RefreshCw size={16} />
          刷新
        </button>
      </div>

      {/* 筛选和搜索 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="搜索文章..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <select
            value={selectedFeed}
            onChange={(e) => setSelectedFeed(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">所有订阅源</option>
            {feedsData?.data?.map((feed: any) => (
              <option key={feed.id} value={feed.id}>
                {feed.name}
              </option>
            ))}
          </select>

          <select
            value={filterRead}
            onChange={(e) => setFilterRead(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">全部</option>
            <option value="read">已读</option>
            <option value="unread">未读</option>
          </select>
        </div>
      </div>

      {/* 文章列表 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <SkeletonList rows={8} />
        ) : error ? (
          <ErrorState
            message="加载文章列表失败，请检查网络连接"
            onRetry={() => refetch()}
          />
        ) : !articlesData?.data?.length ? (
          <div className="p-8 text-center text-gray-500">暂无文章</div>
        ) : (
          <>
            <div className="divide-y divide-gray-200">
              {articlesData.data.map((article) => (
                <div
                  key={article.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                    !article.read_status ? 'bg-blue-50/50' : ''
                  }`}
                  onClick={() => setSelectedArticle(article)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {!article.read_status && (
                          <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                        )}
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {article.title}
                        </h3>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <BookOpen size={14} />
                          {article.feed_name}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {formatDate(article.published_at)}
                        </span>
                        {article.keywords && article.keywords.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Hash size={14} />
                            {article.keywords.slice(0, 3).join(', ')}
                            {article.keywords.length > 3 && '...'}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleReadMutation.mutate(article.id)
                        }}
                        className={`p-2 rounded-md transition-colors ${
                          article.read_status
                            ? 'text-gray-400 hover:text-gray-600'
                            : 'text-blue-600 hover:text-blue-700'
                        }`}
                        title={article.read_status ? '标记未读' : '标记已读'}
                      >
                        {article.read_status ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-md transition-colors"
                        title="在新窗口打开"
                      >
                        <ExternalLink size={18} />
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 分页 */}
            {articlesData.total_pages > 1 && (
              <div className="border-t border-gray-200 px-4 py-3 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  第 {articlesData.page} 页，共 {articlesData.total_pages} 页，总计 {articlesData.total} 篇文章
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={articlesData.page === 1}
                    className="inline-flex items-center gap-1 px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    <ChevronLeft size={16} />
                    上一页
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(articlesData.total_pages, p + 1))}
                    disabled={articlesData.page === articlesData.total_pages}
                    className="inline-flex items-center gap-1 px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    下一页
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* 文章详情弹窗 */}
      {renderArticleDetail()}
    </div>
  )
}
