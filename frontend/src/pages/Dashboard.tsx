import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Rss, BookOpen, Clock, TrendingUp, AlertCircle } from 'lucide-react'

const API_BASE = '/api/v1'

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => axios.get(`${API_BASE}/system/stats`).then(res => res.data),
  })

  const { data: trends } = useQuery({
    queryKey: ['trends'],
    queryFn: () => axios.get(`${API_BASE}/system/trends`).then(res => res.data),
  })

  const { data: feeds } = useQuery({
    queryKey: ['feeds'],
    queryFn: () => axios.get(`${API_BASE}/feeds`).then(res => res.data),
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => axios.get(`${API_BASE}/system/health`).then(res => res.data),
  })

  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: () => axios.get(`${API_BASE}/system/config`).then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  const statCards = [
    {
      title: '订阅源',
      value: stats?.feeds?.total || 0,
      icon: <Rss className="h-6 w-6 text-primary-600" />,
      change: trends?.feeds?.change ? (trends.feeds.change > 0 ? `+${trends.feeds.change}` : trends.feeds.change.toString()) : '--',
      description: '活跃订阅源',
    },
    {
      title: '文章总数',
      value: stats?.articles?.total || 0,
      icon: <BookOpen className="h-6 w-6 text-green-600" />,
      change: trends?.articles?.weekly ? `+${trends.articles.weekly}` : '--',
      description: '本周新增',
    },
    {
      title: '未读文章',
      value: stats?.articles?.unread || 0,
      icon: <AlertCircle className="h-6 w-6 text-yellow-600" />,
      change: trends?.unread_articles?.change ? (trends.unread_articles.change > 0 ? `+${trends.unread_articles.change}` : trends.unread_articles.change.toString()) : '--',
      description: '比昨天变化',
    },
    {
      title: '任务执行',
      value: stats?.tasks?.total || 0,
      icon: <Clock className="h-6 w-6 text-blue-600" />,
      change: `${trends?.tasks?.success_rate?.toFixed(1) || 0}%`,
      description: '成功率',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">仪表板</h1>
        <p className="text-gray-600">欢迎使用 CastMind 播客订阅处理平台</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-gray-50 rounded-lg">{card.icon}</div>
              <div className="flex items-center text-sm text-green-600">
                <TrendingUp className="h-4 w-4 mr-1" />
                {card.change}
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900">{card.value}</div>
            <div className="text-sm text-gray-600">{card.title}</div>
            <div className="text-xs text-gray-500 mt-1">{card.description}</div>
          </div>
        ))}
      </div>

      {/* 订阅源状态 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">订阅源状态</h2>
          <div className="space-y-4">
            {feeds?.slice(0, 5).map((feed: any) => (
              <div key={feed.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{feed.name}</div>
                  <div className="text-sm text-gray-500 truncate">{feed.url}</div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  feed.status === 'active' ? 'bg-green-100 text-green-800' :
                  feed.status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {feed.status === 'active' ? '活跃' : feed.status === 'error' ? '错误' : '暂停'}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">系统信息</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">后端版本</span>
              <span className="font-medium">{health?.version || 'v1.0.0'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">数据库</span>
              <span className="font-medium">{health?.database || 'SQLite'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">定时任务</span>
              <span className="font-medium">{health?.scheduler || '未知'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">AI 分析</span>
              <span className="font-medium">{config?.ai_service_enabled ? '可用' : '禁用'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">最后更新</span>
              <span className="font-medium">{health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : '--'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 快速操作 */}
      <div className="mt-8 card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="flex flex-wrap gap-3">
          <button className="btn btn-primary">添加订阅源</button>
          <button className="btn btn-secondary">手动抓取</button>
          <button className="btn btn-secondary">查看日志</button>
          <button className="btn btn-secondary">导出数据</button>
        </div>
      </div>
    </div>
  )
}