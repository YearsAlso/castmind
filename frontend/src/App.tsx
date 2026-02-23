import { Routes, Route, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Home, Rss, BookOpen, Settings, BarChart3, Mic, FileText } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Feeds from './pages/Feeds'
import Excerpts from './pages/Excerpts'
import Podcasts from './pages/Podcasts'
import System from './pages/System'
import Articles from './pages/Articles'

const API_BASE = '/api/v1'

function App() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => axios.get(`${API_BASE}/system/health`).then(res => res.data),
    refetchInterval: 30000,
  })

  const navItems = [
    { path: '/', label: '仪表板', icon: <Home size={20} /> },
    { path: '/feeds', label: '订阅源', icon: <Rss size={20} /> },
    { path: '/articles', label: '文章', icon: <FileText size={20} /> },
    { path: '/podcasts', label: '播客', icon: <Mic size={20} /> },
    { path: '/excerpts', label: '摘录', icon: <BookOpen size={20} /> },
    { path: '/system', label: '系统', icon: <Settings size={20} /> },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <BarChart3 className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">🎯 CastMind</span>
              </div>
              
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600"
                  >
                    {item.icon}
                    <span className="ml-2">{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            <div className="flex items-center">
              {isLoading ? (
                <div className="text-sm text-gray-500">检查服务状态...</div>
              ) : health?.status === 'healthy' ? (
                <div className="flex items-center text-sm text-green-600">
                  <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                  服务正常
                </div>
              ) : (
                <div className="flex items-center text-sm text-red-600">
                  <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                  服务异常
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/feeds" element={<Feeds />} />
          <Route path="/articles" element={<Articles />} />
          <Route path="/podcasts" element={<Podcasts />} />
          <Route path="/excerpts" element={<Excerpts />} />
          <Route path="/system" element={<System />} />
        </Routes>
      </main>

      {/* 移动端底部导航 */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <div className="flex justify-around py-3">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="flex flex-col items-center text-xs text-gray-600 hover:text-primary-600"
            >
              {item.icon}
              <span className="mt-1">{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App