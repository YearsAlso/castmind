import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { 
  Server, Database, Cpu, HardDrive, 
  Play, Stop, RefreshCw, Settings,
  Shield, Terminal, BarChart, Clock
} from 'lucide-react'

const API_BASE = '/api/v1'

export default function System() {
  const [activeTab, setActiveTab] = useState('overview')
  const queryClient = useQueryClient()

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => axios.get(`${API_BASE}/system/health`).then(res => res.data),
    refetchInterval: 10000,
  })

  const { data: stats } = useQuery({
    queryKey: ['system-stats'],
    queryFn: () => axios.get(`${API_BASE}/system/stats`).then(res => res.data),
  })

  const { data: config } = useQuery({
    queryKey: ['config'],
    queryFn: () => axios.get(`${API_BASE}/system/config`).then(res => res.data),
  })

  const startScheduler = useMutation({
    mutationFn: () => axios.post(`${API_BASE}/system/scheduler/start`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health'] })
    },
  })

  const stopScheduler = useMutation({
    mutationFn: () => axios.post(`${API_BASE}/system/scheduler/stop`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health'] })
    },
  })

  const processAll = useMutation({
    mutationFn: () => axios.post(`${API_BASE}/system/process/all`),
  })

  const tabs = [
    { id: 'overview', label: '概览', icon: <BarChart size={18} /> },
    { id: 'scheduler', label: '调度器', icon: <Clock size={18} /> },
    { id: 'config', label: '配置', icon: <Settings size={18} /> },
    { id: 'logs', label: '日志', icon: <Terminal size={18} /> },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">系统管理</h1>
        <p className="text-gray-600">监控和管理系统状态</p>
      </div>

      {/* 健康状态 */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">系统状态</h2>
          <div className={`flex items-center ${
            health?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            {health?.status === 'healthy' ? '运行正常' : '服务异常'}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <Database className="h-5 w-5 text-blue-600 mr-3" />
            <div>
              <div className="text-sm text-gray-600">数据库</div>
              <div className="font-medium">{health?.database === 'connected' ? '已连接' : '断开'}</div>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <Cpu className="h-5 w-5 text-purple-600 mr-3" />
            <div>
              <div className="text-sm text-gray-600">AI 服务</div>
              <div className="font-medium">{health?.ai_service === 'available' ? '可用' : '不可用'}</div>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <Server className="h-5 w-5 text-green-600 mr-3" />
            <div>
              <div className="text-sm text-gray-600">调度器</div>
              <div className="font-medium">{health?.scheduler?.status || '未知'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 标签页 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon}
              <span className="ml-2">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* 概览标签页 */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">系统信息</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">应用名称</span>
                <span className="font-medium">{config?.app_name || 'CastMind'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">版本</span>
                <span className="font-medium">{config?.app_version || '1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">运行时间</span>
                <span className="font-medium">--</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">时区</span>
                <span className="font-medium">Asia/Shanghai</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">资源使用</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">CPU 使用率</span>
                  <span className="font-medium">{stats?.system?.cpu_percent || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${stats?.system?.cpu_percent || 0}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">内存使用率</span>
                  <span className="font-medium">{stats?.system?.memory_percent || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${stats?.system?.memory_percent || 0}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">磁盘使用率</span>
                  <span className="font-medium">{stats?.system?.disk_usage || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full" 
                    style={{ width: `${stats?.system?.disk_usage || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 调度器标签页 */}
      {activeTab === 'scheduler' && (
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">任务调度器</h3>
            <div className="flex space-x-3">
              <button
                onClick={() => startScheduler.mutate()}
                disabled={startScheduler.isPending || health?.scheduler?.status === 'running'}
                className="btn btn-primary flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                启动调度器
              </button>
              <button
                onClick={() => stopScheduler.mutate()}
                disabled={stopScheduler.isPending || health?.scheduler?.status !== 'running'}
                className="btn btn-secondary flex items-center"
              >
                <Stop className="h-4 w-4 mr-2" />
                停止调度器
              </button>
              <button
                onClick={() => processAll.mutate()}
                disabled={processAll.isPending}
                className="btn btn-secondary flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                立即处理所有
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <div className="font-medium">订阅源抓取任务</div>
                <div className="text-sm text-green-600">运行中</div>
              </div>
              <div className="text-sm text-gray-600">
                每 {config?.fetch_interval_minutes || 10} 分钟执行一次
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <div className="font-medium">数据清理任务</div>
                <div className="text-sm text-green-600">运行中</div>
              </div>
              <div className="text-sm text-gray-600">
                清理 {config?.cleanup_days || 30} 天前的数据
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <div className="font-medium">状态更新任务</div>
                <div className="text-sm text-green-600">运行中</div>
              </div>
              <div className="text-sm text-gray-600">
                每天凌晨 2:00 执行
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 配置标签页 */}
      {activeTab === 'config' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">系统配置</h3>
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">服务器配置</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    主机地址
                  </label>
                  <input
                    type="text"
                    defaultValue={config?.host || '0.0.0.0'}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    端口
                  </label>
                  <input
                    type="number"
                    defaultValue={config?.port || 8000}
                    className="input"
                  />
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3">任务配置</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    抓取间隔（分钟）
                  </label>
                  <input
                    type="number"
                    defaultValue={config?.fetch_interval_minutes || 10}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    清理周期（天）
                  </label>
                  <input
                    type="number"
                    defaultValue={config?.cleanup_days || 30}
                    className="input"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <button className="btn btn-primary">保存配置</button>
            </div>
          </div>
        </div>
      )}

      {/* 快速操作 */}
      <div className="mt-8 card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">系统工具</h3>
        <div className="flex flex-wrap gap-3">
          <button className="btn btn-secondary flex items-center">
            <Shield className="h-4 w-4 mr-2" />
            备份数据库
          </button>
          <button className="btn btn-secondary flex items-center">
            <HardDrive className="h-4 w-4 mr-2" />
            清理缓存
          </button>
          <button className="btn btn-secondary flex items-center">
            <Terminal className="h-4 w-4 mr-2" />
            查看完整日志
          </button>
          <button className="btn btn-secondary flex items-center">
            <RefreshCw className="h-4 w-4 mr-2" />
            重启服务
          </button>
        </div>
      </div>
    </div>
  )
}