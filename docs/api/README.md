# CastMind API 文档

欢迎来到 CastMind API 文档！这里详细介绍了 CastMind 播客智能流系统的所有 API 接口。

## API 概览

CastMind 提供了丰富的 API 接口，包括：
- 核心系统 API
- 配置管理 API
- 工作流控制 API
- AI 模型 API

## 版本信息

当前 API 版本: v1.0.0
基础URL: `http://localhost:8000/api/v1`

## 认证

所有 API 请求都需要在请求头中包含认证令牌：

```bash
Authorization: Bearer <your_api_token>
```

获取 API 令牌的方法请参考 [配置文档](../user-guide/configuration.md)。

## API 响应格式

所有 API 响应都遵循统一的 JSON 格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 错误处理

当 API 请求失败时，会返回相应的错误信息：

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

详细的错误代码列表请参考 [错误代码文档](../troubleshooting/error-codes.md)。

## 目录

- [核心API](core.md)
- [配置API](configuration.md)
- [工作流API](workflow.md)
- [AI模型API](ai-models.md)

## 速率限制

为了确保系统稳定，API 实施了速率限制：
- 每分钟最多 100 个请求
- 每小时最多 1000 个请求
- 每天最多 10000 个请求

超出限制时将返回 HTTP 429 状态码。

## SDK 和工具

CastMind 提供了多种语言的 SDK：
- [Python SDK](https://github.com/YearsAlso/castmind-python-sdk)
- [JavaScript SDK](https://github.com/YearsAlso/castmind-js-sdk)
- [CLI 工具](../user-guide/cli-reference.md)

## 支持

如有任何问题，请通过以下方式获取帮助：
- [GitHub Issues](https://github.com/YearsAlso/castmind/issues)
- [API 论坛](https://github.com/YearsAlso/castmind/discussions)
- [邮件支持](mailto:support@castmind.ai)