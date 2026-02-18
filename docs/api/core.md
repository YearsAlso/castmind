# 🔧 核心API

CastMind核心API提供系统基础功能，包括状态查询、配置管理和系统控制。

## 📋 API概览

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/health` | GET | 健康检查 | 否 |
| `/api/v1/status` | GET | 系统状态 | 是 |
| `/api/v1/config` | GET | 获取配置 | 是 |
| `/api/v1/config` | PUT | 更新配置 | 是 |
| `/api/v1/control/start` | POST | 启动系统 | 是 |
| `/api/v1/control/stop` | POST | 停止系统 | 是 |
| `/api/v1/control/restart` | POST | 重启系统 | 是 |

## 🩺 健康检查

### GET `/api/v1/health`

检查系统健康状态。

#### 请求
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

#### 响应
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-02-18T20:47:00Z",
    "version": "1.0.0",
    "uptime": "3d 5h 12m",
    "services": {
      "database": "healthy",
      "ai_services": "healthy",
      "storage": "healthy",
      "network": "healthy"
    }
  },
  "message": "系统运行正常",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

#### 状态码
- `200 OK`: 系统健康
- `503 Service Unavailable`: 系统不健康

## 📊 系统状态

### GET `/api/v1/status`

获取详细的系统状态信息。

#### 请求
```bash
curl -X GET "http://localhost:8000/api/v1/status" \
  -H "Authorization: Bearer your-api-token"
```

#### 查询参数
| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `detailed` | boolean | 是否返回详细信息 | `false` |
| `include_metrics` | boolean | 是否包含性能指标 | `false` |

#### 响应示例（简化）
```json
{
  "success": true,
  "data": {
    "system": {
      "version": "1.0.0",
      "environment": "production",
      "uptime": "3d 5h 12m",
      "start_time": "2026-02-15T15:35:00Z"
    },
    "resources": {
      "cpu_usage": 15.2,
      "memory_usage": 1248576000,
      "memory_total": 8589934592,
      "disk_usage": 5368709120,
      "disk_total": 107374182400
    },
    "processing": {
      "active_tasks": 3,
      "queued_tasks": 12,
      "completed_today": 45,
      "failed_today": 2
    },
    "subscriptions": {
      "total": 8,
      "active": 7,
      "inactive": 1
    },
    "ai_services": {
      "openai": {"status": "active", "remaining_quota": 85},
      "deepseek": {"status": "active", "remaining_quota": 92},
      "kimi": {"status": "active", "remaining_quota": 78}
    }
  },
  "message": "状态获取成功",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

#### 详细响应（`detailed=true`）
```json
{
  "success": true,
  "data": {
    "system": {...},
    "resources": {...},
    "processing": {
      "active_tasks": [
        {
          "id": "task_001",
          "type": "podcast_processing",
          "podcast": "商业思维",
          "episode": "第123期",
          "start_time": "2026-02-18T20:45:00Z",
          "progress": 65,
          "current_step": "ai_analysis"
        }
      ],
      "recent_completed": [...],
      "performance_metrics": {...}
    },
    "subscriptions": {
      "list": [
        {
          "id": "sub_001",
          "name": "商业思维",
          "url": "https://example.com/rss",
          "status": "active",
          "last_processed": "2026-02-18T19:30:00Z",
          "total_episodes": 123
        }
      ]
    }
  }
}
```

## ⚙️ 配置管理

### GET `/api/v1/config`

获取当前系统配置。

#### 请求
```bash
curl -X GET "http://localhost:8000/api/v1/config" \
  -H "Authorization: Bearer your-api-token"
```

#### 查询参数
| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `section` | string | 配置章节 | 全部 |
| `format` | string | 响应格式 (`json`/`yaml`) | `json` |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "system": {
      "environment": "production",
      "log_level": "INFO",
      "data_path": "/var/lib/castmind/data",
      "max_concurrent_tasks": 5
    },
    "ai_models": {
      "default_model": "deepseek",
      "models": {
        "deepseek": {
          "enabled": true,
          "model": "deepseek-chat",
          "max_tokens": 4096,
          "temperature": 0.7
        },
        "openai": {
          "enabled": true,
          "model": "gpt-4-turbo",
          "max_tokens": 4096,
          "temperature": 0.7
        }
      }
    },
    "workflows": {
      "default_workflow": "basic_processing",
      "workflows": {
        "basic_processing": {
          "enabled": true,
          "steps": ["rss_parsing", "audio_download", "transcription", "ai_summary", "note_generation"]
        }
      }
    },
    "storage": {
      "retention_days": 30,
      "backup_enabled": true,
      "backup_interval": "daily"
    }
  },
  "message": "配置获取成功",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

### PUT `/api/v1/config`

更新系统配置。

#### 请求
```bash
curl -X PUT "http://localhost:8000/api/v1/config" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "system": {
      "log_level": "DEBUG",
      "max_concurrent_tasks": 10
    }
  }'
```

#### 请求体
部分更新，只包含需要修改的配置项。

#### 响应
```json
{
  "success": true,
  "data": {
    "updated_sections": ["system"],
    "requires_restart": false,
    "validation_errors": []
  },
  "message": "配置更新成功",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "CONFIG_VALIDATION_ERROR",
    "message": "配置验证失败",
    "details": {
      "system.max_concurrent_tasks": "必须为正整数"
    }
  },
  "timestamp": "2026-02-18T20:47:00Z"
}
```

## 🎮 系统控制

### POST `/api/v1/control/start`

启动系统或特定服务。

#### 请求
```bash
curl -X POST "http://localhost:8000/api/v1/control/start" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "scheduler"
  }'
```

#### 请求体
```json
{
  "service": "string",  // 可选：特定服务名称，如 "scheduler", "processor", "all"
  "force": "boolean"    // 可选：是否强制启动，默认 false
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "service": "scheduler",
    "status": "started",
    "pid": 12345,
    "start_time": "2026-02-18T20:47:00Z"
  },
  "message": "服务启动成功",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

### POST `/api/v1/control/stop`

停止系统或特定服务。

#### 请求
```bash
curl -X POST "http://localhost:8000/api/v1/control/stop" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "scheduler",
    "graceful": true
  }'
```

#### 请求体
```json
{
  "service": "string",   // 可选：特定服务名称
  "graceful": "boolean", // 可选：是否优雅停止，默认 true
  "timeout": "number"    // 可选：超时时间（秒），默认 30
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "service": "scheduler",
    "status": "stopped",
    "graceful": true,
    "stop_time": "2026-02-18T20:47:05Z"
  },
  "message": "服务停止成功",
  "timestamp": "2026-02-18T20:47:05Z"
}
```

### POST `/api/v1/control/restart`

重启系统或特定服务。

#### 请求
```bash
curl -X POST "http://localhost:8000/api/v1/control/restart" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "all",
    "reason": "配置更新"
  }'
```

#### 请求体
```json
{
  "service": "string",  // 可选：特定服务名称
  "reason": "string",   // 可选：重启原因
  "delay": "number"     // 可选：延迟时间（秒），默认 0
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "service": "all",
    "status": "restarting",
    "reason": "配置更新",
    "estimated_downtime": 5,
    "scheduled_time": "2026-02-18T20:47:10Z"
  },
  "message": "系统重启已调度",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

## 📈 性能指标

### GET `/api/v1/metrics`

获取系统性能指标。

#### 请求
```bash
curl -X GET "http://localhost:8000/api/v1/metrics" \
  -H "Authorization: Bearer your-api-token" \
  -H "Accept: application/json"
```

#### 查询参数
| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `period` | string | 时间周期 (`1h`, `24h`, `7d`, `30d`) | `1h` |
| `type` | string | 指标类型 (`system`, `processing`, `ai`) | `system` |
| `format` | string | 响应格式 (`json`, `prometheus`) | `json` |

#### 响应示例（JSON）
```json
{
  "success": true,
  "data": {
    "system": {
      "cpu_usage": [15.2, 14.8, 16.1, 13.9],
      "memory_usage": [1248576000, 1250015232, 1249110016, 1248704512],
      "disk_io": {
        "read_bytes": [1024000, 1048576, 1015808],
        "write_bytes": [512000, 524288, 507904]
      },
      "network_io": {
        "bytes_sent": [2048000, 2097152, 2031616],
        "bytes_received": [4096000, 4194304, 4073232]
      }
    },
    "processing": {
      "tasks_completed": [45, 42, 48, 51],
      "tasks_failed": [2, 1, 3, 2],
      "avg_processing_time": [125.3, 128.7, 121.9, 123.5],
      "queue_length": [12, 10, 14, 11]
    },
    "ai_services": {
      "requests": [120, 115, 125, 118],
      "avg_response_time": [1.23, 1.31, 1.19, 1.27],
      "cost_today": 0.85,
      "tokens_used": 125000
    },
    "timestamps": [
      "2026-02-18T19:47:00Z",
      "2026-02-18T19:52:00Z",
      "2026-02-18T19:57:00Z",
      "2026-02-18T20:02:00Z"
    ]
  },
  "message": "指标获取成功",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

#### 响应示例（Prometheus格式）
```prometheus
# HELP castmind_cpu_usage CPU使用率百分比
# TYPE castmind_cpu_usage gauge
castmind_cpu_usage 15.2

# HELP castmind_memory_usage_bytes 内存使用量（字节）
# TYPE castmind_memory_usage_bytes gauge
castmind_memory_usage_bytes 1248576000

# HELP castmind_tasks_completed_total 完成的任务总数
# TYPE castmind_tasks_completed_total counter
castmind_tasks_completed_total 45

# HELP castmind_ai_requests_total AI请求总数
# TYPE castmind_ai_requests_total counter
castmind_ai_requests_total 120
```

## 🗑️ 清理操作

### POST `/api/v1/cleanup`

清理系统临时文件和旧数据。

#### 请求
```bash
curl -X POST "http://localhost:8000/api/v1/cleanup" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "temp_files",
    "older_than_days": 7
  }'
```

#### 请求体
```json
{
  "type": "string",           // 清理类型：temp_files, old_data, logs, all
  "older_than_days": "number", // 可选：清理多少天前的数据
  "dry_run": "boolean"        // 可选：试运行，默认 false
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "type": "temp_files",
    "dry_run": false,
    "files_deleted": 45,
    "space_freed": 1073741824,
    "details": {
      "temp_audio": 25,
      "cache_files": 15,
      "log_files": 5
    }
  },
  "message": "清理完成，释放了1.0GB空间",
  "timestamp": "2026-02-18T20:47:00Z"
}
```

## 🔐 认证与授权

所有需要认证的API端点都需要在请求头中包含Bearer令牌：

```bash
Authorization: Bearer your-api-token
```

### 令牌管理
- 默认令牌在 `config/.env` 中设置：`API_TOKEN=your-secret-token`
- 生产环境建议使用JWT令牌
- 支持多令牌和令牌轮换

## ⚠️ 错误处理

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {},
    "request_id": "req_1234567890"
  },
  "timestamp": "2026-02-18T20:47:00Z"
}
```

### 常见错误码
| 错误码 | HTTP状态 | 描述 |
|--------|----------|------|
| `UNAUTHORIZED` | 401 | 未认证或令牌无效 |
| `FORBIDDEN` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 422 | 请求参数验证失败 |
| `RATE_LIMITED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务暂时不可用 |

## 📝 使用示例

### Python客户端
```python
import requests

class CastMindClient:
    def __init__(self, base_url="http://localhost:8000", api_token=None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
