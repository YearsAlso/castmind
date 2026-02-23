# 数据库模型

## Feed (订阅源)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 名称 |
| url | String | RSS URL |
| category | String | 分类 |
| interval | Integer | 抓取间隔(秒) |
| status | String | 状态(active/paused/error) |
| feed_type | String | 类型(rss/podcast/atom) |
| author | String | 主持人/作者 |
| image_url | String | 封面图 |
| description | String | 描述 |
| last_fetch | DateTime | 上次抓取时间 |
| article_count | Integer | 文章数量 |

## Article (文章)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| feed_id | Integer | 关联订阅源 |
| title | String | 标题 |
| url | String | 原文链接 |
| author | String | 作者/嘉宾 |
| content | Text | 内容 |
| summary | Text | 摘要 |
| published_at | DateTime | 发布时间 |
| is_podcast | Boolean | 是否播客 |
| audio_url | String | 音频URL |
| audio_type | String | 音频类型 |
| audio_duration | Integer | 时长(秒) |
| audio_size | Integer | 文件大小 |
| audio_local_path | String | 本地音频路径 |
| podcast_description | String | 播客描述 |
| transcript | Text | 转录文本 |
| podcast_summary | String | AI摘要 |
| chapters | Text | 章节(JSON) |
| transcription_status | String | 转录状态 |
| analysis_status | String | 分析状态 |
| processed_status | Boolean | 已处理 |
| keywords | String | 关键词 |
| sentiment | String | 情感 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## Task (任务)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| feed_id | Integer | 关联订阅源 |
| article_id | Integer | 关联文章 |
| task_type | String | 任务类型 |
| task_name | String | 任务名称 |
| status | String | 状态 |
| progress | Integer | 进度% |
| error_message | Text | 错误信息 |
| result_data | Text | 结果(JSON) |
