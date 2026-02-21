import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Plus, RefreshCw, Edit, Trash2, ExternalLink, Filter, Save, X } from 'lucide-react'

const API_BASE = '/api/v1'

export default function Feeds() {
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingFeed, setEditingFeed] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [newFeed, setNewFeed] = useState({
    name: '',
    url: '',
    category: '技术',
    interval: 3600,
  })
  const [editForm, setEditForm] = useState({
    name: '',
    url: '',
    category: '技术',
    interval: 3600,
    status: 'active' as 'active' | 'paused' | 'error'
  })
  
  const queryClient = useQueryClient()

  const { data: feeds, isLoading } = useQuery({
    queryKey: ['feeds'],
    queryFn: () => axios.get(`${API_BASE}/feeds`).then(res => res.data),
  })

  // 获取所有分类
  const categories = ['all', ...new Set(feeds?.map((f: any) => f.category || '未分类') || ['all'])]

  // 筛选订阅源
  const filteredFeeds = feeds?.filter((feed: any) => {
    const statusMatch = statusFilter === 'all' || feed.status === statusFilter
    const categoryMatch = categoryFilter === 'all' || feed.category === categoryFilter
    return statusMatch && categoryMatch
  })

  const addMutation = useMutation({
    mutationFn: (feedData: any) => axios.post(`${API_BASE}/feeds`, feedData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
      setShowAddForm(false)
      setNewFeed({ name: '', url: '', category: '技术', interval: 3600 })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number, data: any }) => 
      axios.put(`${API_BASE}/feeds/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
      setEditingFeed(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => axios.delete(`${API_BASE}/feeds/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
    },
  })

  const fetchMutation = useMutation({
    mutationFn: (id: string) => axios.post(`${API_BASE}/feeds/${id}/fetch`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addMutation.mutate(newFeed)
  }

  const handleEdit = (feed: any) => {
    setEditingFeed(feed.id)
    setEditForm({
      name: feed.name,
      url: feed.url,
      category: feed.category || '技术',
      interval: feed.interval || 3600,
      status: feed.status || 'active'
    })
  }

  const handleSaveEdit = (id: number) => {
    updateMutation.mutate({ id, data: editForm })
  }

  const handleCancelEdit = () => {
    setEditingFeed(null)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">加载订阅源...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">订阅源管理</h1>
          <p className="text-gray-600">管理您的 RSS/Atom 订阅源</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          添加订阅源
        </button>
      </div>

      {/* 添加表单 */}
      {showAddForm && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">添加新订阅源</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                名称
              </label>
              <input
                type="text"
                value={newFeed.name}
                onChange={(e) => setNewFeed({ ...newFeed, name: e.target.value })}
                className="input"
                placeholder="例如：技术博客"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                RSS URL
              </label>
              <input
                type="url"
                value={newFeed.url}
                onChange={(e) => setNewFeed({ ...newFeed, url: e.target.value })}
                className="input"
                placeholder="https://example.com/rss"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                支持标准 RSS/Atom 和 RSSHub URL（如 https://rsshub.app/twitter/user/elonmusk）
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  分类
                </label>
                <select
                  value={newFeed.category}
                  onChange={(e) => setNewFeed({ ...newFeed, category: e.target.value })}
                  className="input"
                >
                  <option value="技术">技术</option>
                  <option value="新闻">新闻</option>
                  <option value="娱乐">娱乐</option>
                  <option value="教育">教育</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  抓取间隔（秒）
                </label>
                <input
                  type="number"
                  value={newFeed.interval}
                  onChange={(e) => setNewFeed({ ...newFeed, interval: parseInt(e.target.value) })}
                  className="input"
                  min="300"
                  step="300"
                />
                <p className="mt-1 text-xs text-gray-500">建议：高频源 300-1800，低频源 3600-86400</p>
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={addMutation.isPending}
                className="btn btn-primary"
              >
                {addMutation.isPending ? '添加中...' : '添加订阅源'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 订阅源列表 */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900">所有订阅源</h2>
          <div className="flex items-center space-x-2">
            <select 
              className="input py-1 text-sm"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">全部状态</option>
              <option value="active">活跃</option>
              <option value="paused">暂停</option>
              <option value="error">错误</option>
            </select>
            <select 
              className="input py-1 text-sm"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="all">全部分类</option>
              {categories.filter(c => c !== 'all').map((cat: any) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  名称
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  分类
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  最后抓取
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  文章数
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFeeds?.map((feed: any) => (
                <tr key={feed.id} className="hover:bg-gray-50">
                  {editingFeed === feed.id ? (
                    // 编辑模式
                    <>
                      <td className="px-6 py-4">
                        <input
                          type="text"
                          value={editForm.name}
                          onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                          className="input input-sm w-full"
                          required
                        />
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={editForm.category}
                          onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                          className="input input-sm w-full"
                        >
                          <option value="技术">技术</option>
                          <option value="新闻">新闻</option>
                          <option value="娱乐">娱乐</option>
                          <option value="教育">教育</option>
                          <option value="其他">其他</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={editForm.status}
                          onChange={(e) => setEditForm({ ...editForm, status: e.target.value as any })}
                          className="input input-sm w-full"
                        >
                          <option value="active">活跃</option>
                          <option value="paused">暂停</option>
                          <option value="error">错误</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {feed.last_fetch ? new Date(feed.last_fetch).toLocaleString() : '从未'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {feed.article_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleSaveEdit(feed.id)}
                            disabled={updateMutation.isPending}
                            className="text-green-600 hover:text-green-900"
                            title="保存"
                          >
                            <Save className="h-4 w-4" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="text-gray-600 hover:text-gray-900"
                            title="取消"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </>
                  ) : (
                    // 查看模式
                    <>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{feed.name}</div>
                        <div className="text-sm text-gray-500 truncate max-w-xs">{feed.url}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                          {feed.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          feed.status === 'active' ? 'bg-green-100 text-green-800' :
                          feed.status === 'error' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {feed.status === 'active' ? '活跃' : feed.status === 'error' ? '错误' : '暂停'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {feed.last_fetch ? new Date(feed.last_fetch).toLocaleString() : '从未'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {feed.article_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => fetchMutation.mutate(feed.id)}
                            disabled={fetchMutation.isPending}
                            className="text-blue-600 hover:text-blue-900"
                            title="手动抓取"
                          >
                            <RefreshCw className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleEdit(feed)}
                            className="text-gray-600 hover:text-gray-900"
                            title="编辑"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <a
                            href={feed.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-600 hover:text-gray-900"
                            title="打开链接"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                          <button
                            onClick={() => {
                              if (window.confirm('确定要删除这个订阅源吗？')) {
                                deleteMutation.mutate(feed.id)
                              }
                            }}
                            disabled={deleteMutation.isPending}
                            className="text-red-600 hover:text-red-900"
                            title="删除"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {(!feeds || feeds.length === 0) && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">暂无订阅源</div>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn btn-primary"
            >
              添加第一个订阅源
            </button>
          </div>
        )}
      </div>

      {/* 使用提示 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <RefreshCw className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">使用提示</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc pl-5 space-y-1">
                <li>点击"手动抓取"按钮可以立即更新订阅源内容</li>
                <li>编辑订阅源可以修改名称、分类、状态等信息</li>
                <li>支持 RSSHub URL，可以订阅 Twitter、GitHub、B站等内容</li>
                <li>合理的抓取间隔可以避免被封禁（建议 30-60 分钟）</li>
                <li>定期检查错误状态的订阅源，及时修复或删除</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}