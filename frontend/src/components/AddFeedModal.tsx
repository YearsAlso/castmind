import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { X, Loader2, Link, Sparkles } from 'lucide-react'

const API_BASE = '/api/v1'

interface AddFeedModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function AddFeedModal({ isOpen, onClose, onSuccess }: AddFeedModalProps) {
  const [url, setUrl] = useState('')
  const [name, setName] = useState('')
  const [category, setCategory] = useState('技术')
  const [isLoading, setIsLoading] = useState(false)
  const [isFetchingInfo, setIsFetchingInfo] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [interval, setInterval] = useState(3600)
  const urlInputRef = useRef<HTMLInputElement>(null)

  // 自动获取 feed 信息
  useEffect(() => {
    if (!url) {
      setName('')
      return
    }

    // 检查 URL 是否有效
    try {
      new URL(url)
    } catch {
      return
    }

    const fetchFeedInfo = async () => {
      setIsFetchingInfo(true)
      try {
        const response = await axios.post(`${API_BASE}/feeds/parse?url=${encodeURIComponent(url)}`)
        if (response.data.feed_info?.title) {
          setName(response.data.feed_info.title)
          toast.success('已自动获取订阅源信息')
        }
      } catch (error: any) {
        // 自动获取失败不影响用户手动填写
        console.error('获取订阅源信息失败:', error)
      } finally {
        setIsFetchingInfo(false)
      }
    }

    // 防抖处理
    const timer = setTimeout(fetchFeedInfo, 800)
    return () => clearTimeout(timer)
  }, [url])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!url || !name) {
      toast.error('请填写完整的订阅源信息')
      return
    }

    setIsLoading(true)
    try {
      await axios.post(`${API_BASE}/feeds/`, {
        name,
        url,
        category,
        interval,
      })
      toast.success('订阅源添加成功')
      // 重置表单
      setUrl('')
      setName('')
      setCategory('技术')
      setInterval(3600)
      setShowAdvanced(false)
      onSuccess?.()
      onClose()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '添加订阅源失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    setUrl('')
    setName('')
    setCategory('技术')
    setInterval(3600)
    setShowAdvanced(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 遮罩层 */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={handleClose}
      />

      {/* Modal 内容 */}
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">添加订阅源</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* RSS URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              RSS URL <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Link className="h-4 w-4 text-gray-400" />
              </div>
              <input
                ref={urlInputRef}
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="input pl-10"
                placeholder="https://example.com/rss"
                required
              />
              {isFetchingInfo && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <Loader2 className="h-4 w-4 text-primary-600 animate-spin" />
                </div>
              )}
            </div>
            <p className="mt-1 text-xs text-gray-500">
              支持标准 RSS/Atom 和 RSSHub URL
            </p>
          </div>

          {/* 名称 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              名称 <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="自动获取或手动填写"
                required
              />
              {isFetchingInfo && name && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <Sparkles className="h-4 w-4 text-green-500" />
                </div>
              )}
            </div>
          </div>

          {/* 简易/高级切换 */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            {showAdvanced ? '收起高级选项' : '显示高级选项'}
          </button>

          {/* 高级选项 */}
          {showAdvanced && (
            <div className="space-y-4 pt-2 border-t border-gray-100">
              {/* 分类 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  分类
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="input"
                >
                  <option value="技术">技术</option>
                  <option value="新闻">新闻</option>
                  <option value="娱乐">娱乐</option>
                  <option value="教育">教育</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              {/* 抓取间隔 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  抓取间隔（秒）
                </label>
                <select
                  value={interval}
                  onChange={(e) => setInterval(parseInt(e.target.value))}
                  className="input"
                >
                  <option value="300">5 分钟</option>
                  <option value="600">10 分钟</option>
                  <option value="1800">30 分钟</option>
                  <option value="3600">1 小时</option>
                  <option value="7200">2 小时</option>
                  <option value="86400">1 天</option>
                </select>
              </div>
            </div>
          )}

          {/* 按钮 */}
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="btn btn-secondary"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isLoading || !url || !name}
              className="btn btn-primary"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  添加中...
                </>
              ) : (
                '添加订阅源'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
