import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Search, Play, Pause, Volume2, FileText, Download,
  CheckCircle, Clock, AlertCircle, Loader2, Plus,
  SkipBack, SkipForward, Gauge
} from 'lucide-react'

const API_BASE = '/api/v1'

// 音频播放器组件
interface AudioPlayerProps {
  audioUrl: string
  title: string
}

function AudioPlayer({ audioUrl, title }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [showSpeedMenu, setShowSpeedMenu] = useState(false)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const onEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', onEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', onEnded)
    }
  }, [audioUrl])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return

    const newTime = parseFloat(e.target.value)
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleSkip = (seconds: number) => {
    const audio = audioRef.current
    if (!audio) return

    audio.currentTime = Math.max(0, Math.min(audio.duration, audio.currentTime + seconds))
  }

  const changePlaybackRate = (rate: number) => {
    const audio = audioRef.current
    if (!audio) return

    audio.playbackRate = rate
    setPlaybackRate(rate)
    setShowSpeedMenu(false)
  }

  const formatTime = (time: number) => {
    if (!time || isNaN(time)) return '00:00'
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="bg-gray-900 rounded-lg p-3 text-white">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />
      
      {/* 标题 */}
      <div className="text-sm text-gray-300 mb-2 truncate">{title}</div>
      
      {/* 进度条 */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-gray-400 w-10 text-right">{formatTime(currentTime)}</span>
        <input
          type="range"
          min={0}
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-primary-500"
        />
        <span className="text-xs text-gray-400 w-10">{formatTime(duration)}</span>
      </div>
      
      {/* 控制按钮 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleSkip(-15)}
            className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
            title="后退 15 秒"
          >
            <SkipBack className="h-4 w-4" />
          </button>
          
          <button
            onClick={togglePlay}
            className="p-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
          >
            {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </button>
          
          <button
            onClick={() => handleSkip(30)}
            className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
            title="前进 30 秒"
          >
            <SkipForward className="h-4 w-4" />
          </button>
        </div>
        
        {/* 速度控制 */}
        <div className="relative">
          <button
            onClick={() => setShowSpeedMenu(!showSpeedMenu)}
            className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-gray-700 rounded-lg transition-colors"
          >
            <Gauge className="h-3 w-3" />
            {playbackRate}x
          </button>
          
          {showSpeedMenu && (
            <div className="absolute bottom-full right-0 mb-1 bg-gray-800 rounded-lg shadow-lg py-1 min-w-[80px]">
              {[0.5, 0.75, 1, 1.25, 1.5, 1.75, 2].map((rate) => (
                <button
                  key={rate}
                  onClick={() => changePlaybackRate(rate)}
                  className={`w-full px-3 py-1.5 text-xs text-left hover:bg-gray-700 transition-colors ${
                    playbackRate === rate ? 'text-primary-400' : 'text-gray-300'
                  }`}
                >
                  {rate}x
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Podcasts() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [playingPodcast, setPlayingPodcast] = useState<number | null>(null)
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
      toast.success('音频下载成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '音频下载失败')
    },
  })

  const transcribeMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/transcribe`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
      toast.success('转录任务已启动')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '转录任务启动失败')
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/analyze-transcript`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
      toast.success('分析任务已启动')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '分析任务启动失败')
    },
  })

  const fullPipelineMutation = useMutation({
    mutationFn: (id: number) => axios.post(`${API_BASE}/articles/${id}/full-pipeline`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcasts'] })
      toast.success('完整处理流程已启动')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '处理流程启动失败')
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
                  <button
                    onClick={() => setPlayingPodcast(playingPodcast === podcast.id ? null : podcast.id)}
                    className={`btn btn-sm flex items-center ${
                      playingPodcast === podcast.id 
                        ? 'btn-primary' 
                        : 'btn-secondary'
                    }`}
                  >
                    {playingPodcast === podcast.id ? (
                      <><Pause className="h-4 w-4 mr-1" />关闭</>
                    ) : (
                      <><Play className="h-4 w-4 mr-1" />播放</>
                    )}
                  </button>
                )}
                
                {/* 内置音频播放器 */}
                {playingPodcast === podcast.id && podcast.audio_url && (
                  <div className="w-full mt-3">
                    <AudioPlayer 
                      audioUrl={podcast.audio_url} 
                      title={podcast.title}
                    />
                  </div>
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
