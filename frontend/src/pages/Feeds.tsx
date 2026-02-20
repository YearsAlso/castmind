import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Plus, RefreshCw, Edit, Trash2, ExternalLink, Filter } from 'lucide-react'

const API_BASE = '/api/v1'

export default function Feeds() {
  const [showAddForm, setShowAddForm] = useState(false)
  const [newFeed, setNewFeed] = useState({
    name: '',
    url: '',
    category: '技术',
    interval: 3600,
  })
  const queryClient = useQueryClient()

  const { data: feeds, isLoading } = useQuery({
    queryKey: ['feeds'],
    queryFn: () => axios.get(`${API_BASE}/feeds`).then(res => res.data),
  })

  const addMutation = useMutation({
    mutationFn: (feedData: any) => axios.post(`${API_BASE}/feeds`, feedData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
      setShowAddForm(false)
      setNewFeed({ name: '', url: '', category: '技术', interval: 3600 })
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
            <Filter className="h-4 w-4 text-gray-400" />
            <select className="input py-1 text-sm">
              <option>全部状态</option>
              <option>活跃</option>
              <option>暂停</option>
              <option>错误</option>
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
              {feeds?.map((feed: any) => (
                <tr key={feed.id} className="hover:bg-gray-50">
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {(!feeds || feeds.length === 0) && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-2">暂无订阅源</div>
            <p className="text-gray-500 mb-4">添加您的第一个 RSS 订阅源开始使用</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn btn-primary"
            >
              添加订阅源
            </button>
          </div>
        )}
      </div>
    </div>
  )
}