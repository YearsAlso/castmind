import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { 
  Search, Play, Volume2, FileText, Download,
  CheckCircle, Clock, AlertCircle, Loader2, Plus, Rss
} from 'lucide-react'

const API_BASE = '/api/v1'

export default function Podcasts() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [page, setPage] = useState(1)
  const pageSize = 20

  const queryClient = useQueryClient()

  const { data: podcastsData, isLoading } = useQuery({
    queryKey: ['podcasts', page, statusFilter],
    queryFn: () => axios.get(`${API_BASE}/articles/podcasts/`).then(res => res.data),
  })

  const downloadMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/download-audio`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
    },
  })

  const transcribeMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/transcribe`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/analyze-transcript`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
    },
  })

  const fullPipelineMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/full-pipeline`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
    },
  })

  const podcasts = podcastsData?.podcasts || []
  
  const filteredPodcasts = podcasts.filter((podcast: any) => {
    if (!search) return true
    const searchLower = search.toLowerCase()
    return (
      podcast.title?.toLowerCase().includes(searchLower) ||
      podcast.summary?.toLowerCase().includes(searchLower)
    )
  })

  const statusOptions = [
    { id: 'all', label: '全部', count: podcastsData?.total || 0 },
    { id: 'pending', label: '待处理', count: podcasts.filter((p: any) => p.transcription_status === 'pending').length },
    { id: 'transcribing', label: '转录中', count: podcasts.filter((p: any) => p.transcription_status === 'running').length },
    { id: 'transcribed', label: '已转录', count: podcasts.filter((p: any) => p.transcription_status === 'completed').length },
    { id: 'analyzed', label: '已分析', count: podcasts.filter((p: any) => p.analysis_status === 'completed').length },
  ]

  const getStatusBadge = (podcast: any) => {
    const transcription = podcast.transcription_status
    const analysis = podcast.analysis_status

    if (transcription === 'running' || analysis === 'running') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          处理中
        </span>
      )
    }

    if (analysis === 'completed') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="h-3 w-3 mr-1" />
          已完成
        </span>
      )
    }

    if (transcription === 'completed') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          <Volume2 className="h-3 w-3 mr-1" />
          已转录
        </span>
      )
    }

    if (transcription === 'failed') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertCircle className="h-3 w-3 mr-1" />
          失败
        </span>
      )
    }

    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        <Clock className="h-3 w-3 mr-1" />
        待处理
      </span>
    )
  }

  const formatDuration = (seconds: number) => {
    if (!seconds) return '--'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">加载播客...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">播客管理</h1>
          <p className="text-gray-600">管理播客内容：下载、转录、AI分析</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/feeds')}
            className="btn btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            添加播客源
          </button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索播客标题..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-700">状态:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input py-1 text-sm"
            >
              {statusOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label} ({option.count})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 播客列表 */}
      <div className="space-y-4">
        {filteredPodcasts.map((podcast: any) => (
          <div key={podcast.id} className="card">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
              {/* 播客信息 */}
              <div className="flex-1">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Volume2 className="h-8 w-8 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{podcast.title}</h3>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                      {podcast.audio_duration && (
                        <span>{formatDuration(podcast.audio_duration)}</span>
                      )}
                      {podcast.audio_size && (
                        <span>{(podcast.audio_size / 1024 / 1024).toFixed(2)} MB</span>
                      )}
                    </div>
                    {podcast.summary && (
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {podcast.summary}
                      </p>
                    )}
                  </div>
                </div>

                {/* 状态标签 */}
                <div className="flex items-center gap-2 mt-3">
                  {getStatusBadge(podcast)}
                  {podcast.podcast_summary && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <FileText className="h-3 w-3 mr-1" />
                      已分析
                    </span>
                  )}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex flex-wrap gap-2">
                {podcast.audio_url && (
                  <a
                    href={podcast.audio_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-secondary flex items-center"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    播放
                  </a>
                )}
                
                {!podcast.audio_local_path && (
                  <button
                    onClick={() => downloadMutation.mutate(podcast.id)}
                    disabled={downloadMutation.isPending}
                    className="btn btn-sm btn-secondary flex items-center"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    {downloadMutation.isPending ? '下载中' : '下载'}
                  </button>
                )}
                
                {podcast.audio_local_path && podcast.transcription_status !== 'completed' && (
                  <button
                    onClick={() => transcribeMutation.mutate(podcast.id)}
                    disabled={transcribeMutation.isPending}
                    className="btn btn-sm btn-secondary flex items-center"
                  >
                    <Volume2 className="h-4 w-4 mr-1" />
                    {transcribeMutation.isPending ? '转录中' : '转录'}
                  </button>
                )}
                
                {podcast.transcription_status === 'completed' && podcast.analysis_status !== 'completed' && (
                  <button
                    onClick={() => analyzeMutation.mutate(podcast.id)}
                    disabled={analyzeMutation.isPending}
                    className="btn btn-sm btn-primary flex items-center"
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    {analyzeMutation.isPending ? '分析中' : 'AI分析'}
                  </button>
                )}
                
                {!podcast.transcript && podcast.audio_url && (
                  <button
                    onClick={() => fullPipelineMutation.mutate(podcast.id)}
                    disabled={fullPipelineMutation.isPending}
                    className="btn btn-sm btn-primary flex items-center"
                  >
                    <Loader2 className={`h-4 w-4 mr-1 ${fullPipelineMutation.isPending ? 'animate-spin' : ''}`} />
                    {fullPipelineMutation.isPending ? '处理中' : '一键处理'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 空状态 */}
      {filteredPodcasts.length === 0 && (
        <div className="card">
          <div className="text-center py-12">
            <Volume2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无播客</h3>
            <p className="text-gray-600 max-w-md mx-auto mb-4">
              添加播客订阅源后，抓取的播客内容将显示在这里。
            </p>
            <button
              onClick={() => navigate('/feeds')}
              className="btn btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              添加播客订阅源
            </button>
          </div>
        </div>
      )}

      {/* 分页 */}
      {podcastsData?.total > pageSize && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            显示第 {(page - 1) * pageSize + 1} 到 {Math.min(page * pageSize, podcastsData.total)} 条，共 {podcastsData.total} 条
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              上一页
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page * pageSize >= podcastsData.total}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
