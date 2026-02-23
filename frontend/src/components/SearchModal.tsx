import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Search, X, FileText, Mic, Rss, Loader2, ArrowRight } from 'lucide-react'

const API_BASE = '/api/v1'

interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
}

type SearchResult = {
  type: 'article' | 'podcast' | 'feed'
  id: number
  title: string
  description?: string
  url?: string
}

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  // 获取订阅源数据
  const { data: feeds } = useQuery({
    queryKey: ['feeds'],
    queryFn: () => axios.get(`${API_BASE}/feeds/`).then(res => res.data),
    enabled: isOpen,
  })

  // 获取文章数据
  const { data: articles } = useQuery({
    queryKey: ['articles'],
    queryFn: () => axios.get(`${API_BASE}/articles/`).then(res => res.data),
    enabled: isOpen,
  })

  // 获取播客数据
  const { data: podcasts } = useQuery({
    queryKey: ['podcasts'],
    queryFn: () => axios.get(`${API_BASE}/articles/podcasts`).then(res => res.data),
    enabled: isOpen,
  })

  // 搜索结果
  const results: SearchResult[] = []

  if (query.trim()) {
    const lowerQuery = query.toLowerCase()

    // 搜索订阅源
    feeds?.forEach((feed: any) => {
      if (feed.name?.toLowerCase().includes(lowerQuery) || feed.url?.toLowerCase().includes(lowerQuery)) {
        results.push({
          type: 'feed',
          id: feed.id,
          title: feed.name,
          description: feed.url,
          url: feed.url,
        })
      }
    })

    // 搜索文章
    articles?.forEach((article: any) => {
      if (article.title?.toLowerCase().includes(lowerQuery) || article.content?.toLowerCase().includes(lowerQuery)) {
        results.push({
          type: 'article',
          id: article.id,
          title: article.title,
          description: article.content?.substring(0, 100),
        })
      }
    })

    // 搜索播客
    podcasts?.forEach((podcast: any) => {
      if (podcast.title?.toLowerCase().includes(lowerQuery)) {
        results.push({
          type: 'podcast',
          id: podcast.id,
          title: podcast.title,
          description: podcast.description,
        })
      }
    })
  }

  // 重置选中状态
  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  // 自动聚焦输入框
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // 处理键盘导航
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(prev => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      e.preventDefault()
      handleSelect(results[selectedIndex])
    } else if (e.key === 'Escape') {
      onClose()
    }
  }, [results, selectedIndex, onClose])

  // 选择结果
  const handleSelect = (result: SearchResult) => {
    switch (result.type) {
      case 'feed':
        navigate('/feeds')
        break
      case 'article':
        navigate('/articles')
        break
      case 'podcast':
        navigate('/podcasts')
        break
    }
    onClose()
    setQuery('')
  }

  // 获取类型图标和颜色
  const getTypeInfo = (type: string) => {
    switch (type) {
      case 'feed':
        return { icon: Rss, color: 'text-orange-600', bg: 'bg-orange-100' }
      case 'podcast':
        return { icon: Mic, color: 'text-purple-600', bg: 'bg-purple-100' }
      case 'article':
      default:
        return { icon: FileText, color: 'text-blue-600', bg: 'bg-blue-100' }
    }
  }

  // 获取类型名称
  const getTypeName = (type: string) => {
    switch (type) {
      case 'feed':
        return '订阅源'
      case 'podcast':
        return '播客'
      case 'article':
        return '文章'
      default:
        return type
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh]">
      {/* 遮罩层 */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={() => {
          onClose()
          setQuery('')
        }}
      />

      {/* 搜索弹窗 */}
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
        {/* 搜索输入 */}
        <div className="flex items-center px-4 py-3 border-b border-gray-200">
          <Search className="h-5 w-5 text-gray-400 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 text-lg outline-none placeholder-gray-400"
            placeholder="搜索文章、播客、订阅源..."
          />
          <button
            onClick={() => {
              onClose()
              setQuery('')
            }}
            className="ml-2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* 搜索结果 */}
        <div className="max-h-[60vh] overflow-y-auto">
          {query.trim() === '' ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <p className="text-sm">输入关键词搜索内容</p>
              <p className="text-xs mt-2 text-gray-400">
                按 <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">↑</kbd>{' '}
                <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">↓</kbd>{' '}
                切换，<kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">Enter</kbd> 跳转
              </p>
            </div>
          ) : results.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <p>未找到相关结果</p>
            </div>
          ) : (
            <div className="py-2">
              {results.map((result, index) => {
                const typeInfo = getTypeInfo(result.type)
                const Icon = typeInfo.icon
                return (
                  <button
                    key={`${result.type}-${result.id}`}
                    onClick={() => handleSelect(result)}
                    className={`w-full flex items-center px-4 py-3 text-left transition-colors ${
                      index === selectedIndex ? 'bg-primary-50' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className={`flex-shrink-0 p-2 rounded-lg ${typeInfo.bg}`}>
                      <Icon className={`h-4 w-4 ${typeInfo.color}`} />
                    </div>
                    <div className="ml-3 flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {result.title}
                      </p>
                      {result.description && (
                        <p className="text-xs text-gray-500 truncate">
                          {result.description}
                        </p>
                      )}
                    </div>
                    <div className="ml-2 flex-shrink-0 flex items-center text-gray-400">
                      <span className="text-xs mr-2">{getTypeName(result.type)}</span>
                      <ArrowRight className="h-4 w-4" />
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* 底部提示 */}
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>
              <kbd className="px-1.5 py-0.5 bg-gray-200 rounded">↑</kbd>
              <kbd className="px-1.5 py-0.5 bg-gray-200 rounded ml-1">↓</kbd>
              <span className="ml-2">导航</span>
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-gray-200 rounded">Enter</kbd>
              <span className="ml-2">跳转</span>
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-gray-200 rounded">Esc</kbd>
              <span className="ml-2">关闭</span>
            </span>
          </div>
          <div className="flex items-center text-gray-400">
            <kbd className="px-1.5 py-0.5 bg-gray-200 rounded mr-1">⌘</kbd>
            <kbd className="px-1.5 py-0.5 bg-gray-200 rounded">K</kbd>
          </div>
        </div>
      </div>
    </div>
  )
}
