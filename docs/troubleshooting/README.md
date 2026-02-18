# 🔧 CastMind 故障排除指南

本指南帮助您诊断和解决CastMind系统中的常见问题。

## 🚨 紧急问题

### 系统完全无法启动

#### 症状
- 服务无法启动
- 端口被占用
- 依赖缺失

#### 解决步骤
1. **检查端口占用**
   ```bash
   # Linux/macOS
   sudo lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

2. **检查Python环境**
   ```bash
   # 检查Python版本
   python --version
   
   # 检查虚拟环境
   which python
   
   # 检查依赖
   python -c "import feedparser; print('feedparser OK')"
   python -c "import openai; print('openai OK')"
   ```

3. **查看错误日志**
   ```bash
   # 启动时查看详细输出
   python castmind.py start --verbose
   
   # 查看日志文件
   tail -f logs/castmind.log
   ```

### 内存泄漏或崩溃

#### 症状
- 内存使用持续增长
- 进程被OOM Killer终止
- 系统变慢或卡死

#### 解决步骤
1. **监控内存使用**
   ```bash
   # 实时监控
   top -p $(pgrep -f castmind)
   
   # 查看内存统计
   free -h
   
   # 查看进程内存
   ps aux | grep castmind
   ```

2. **调整内存限制**
   ```bash
   # Docker环境
   docker update --memory="2g" --memory-swap="4g" castmind
   
   # 系统级限制
   ulimit -v 2097152  # 2GB内存限制
   ```

3. **启用内存分析**
   ```python
   # 在代码中添加内存分析
   import tracemalloc
   
   tracemalloc.start()
   # ... 运行代码 ...
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')
   for stat in top_stats[:10]:
       print(stat)
   ```

## 🔍 常见问题分类

### 1. 安装问题

#### 问题：依赖安装失败
**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement package-name
ERROR: No matching distribution found for package-name
```

**解决**:
```bash
# 更新pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用uv（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

#### 问题：Python版本不兼容
**错误信息**:
```
SyntaxError: invalid syntax
ImportError: cannot import name '...' from '...'
```

**解决**:
```bash
# 检查Python版本
python --version  # 需要3.9+

# 使用pyenv管理版本
pyenv install 3.12.2
pyenv local 3.12.2

# 创建新的虚拟环境
python -m venv .venv
source .venv/bin/activate
```

### 2. 配置问题

#### 问题：API密钥无效
**错误信息**:
```
AuthenticationError: Incorrect API key provided
openai.error.AuthenticationError: Invalid authentication
```

**解决**:
1. **检查API密钥**
   ```bash
   # 查看环境变量
   echo $OPENAI_API_KEY
   
   # 检查配置文件
   cat config/.env | grep API_KEY
   ```

2. **验证API密钥**
   ```bash
   # 测试OpenAI API
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   
   # 测试DeepSeek API
   curl https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'
   ```

3. **重新生成密钥**
   - OpenAI: https://platform.openai.com/api-keys
   - DeepSeek: https://platform.deepseek.com/api_keys
   - Kimi: https://platform.moonshot.cn/api-keys

#### 问题：配置文件缺失
**错误信息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/.env'
ConfigError: Missing required configuration file
```

**解决**:
```bash
# 复制配置文件模板
cp config/.env.example config/.env

# 创建必要的目录
mkdir -p config data logs

# 设置正确的权限
chmod 644 config/.env
chmod 755 data logs
```

### 3. 网络问题

#### 问题：无法下载音频
**错误信息**:
```
requests.exceptions.ConnectionError: HTTPSConnectionPool
TimeoutError: [Errno 110] Connection timed out
```

**解决**:
1. **测试网络连接**
   ```bash
   # 测试基本连接
   ping -c 4 8.8.8.8
   
   # 测试DNS解析
   nslookup github.com
   
   # 测试HTTP连接
   curl -I https://github.com
   ```

2. **配置代理**
   ```bash
   # 设置环境变量
   export http_proxy=http://proxy.example.com:8080
   export https_proxy=http://proxy.example.com:8080
   
   # 或在配置文件中设置
   # config/.env
   HTTP_PROXY=http://proxy.example.com:8080
   HTTPS_PROXY=http://proxy.example.com:8080
   ```

3. **调整超时设置**
   ```python
   # 在代码中调整超时
   import requests
   
   session = requests.Session()
   session.timeout = 60  # 60秒超时
   ```

#### 问题：RSS解析失败
**错误信息**:
```
feedparser.FeedParserDict object has no attribute 'entries'
ValueError: Invalid RSS feed format
```

**解决**:
1. **验证RSS链接**
   ```bash
   # 测试RSS链接
   curl -I "https://example.com/podcast/rss"
   
   # 查看RSS内容
   curl -s "https://example.com/podcast/rss" | head -50
   ```

2. **使用备用解析器**
   ```python
   # 尝试不同的解析方式
   import feedparser
   
   # 方法1：直接解析
   feed = feedparser.parse(rss_url)
   
   # 方法2：下载后解析
   import requests
   response = requests.get(rss_url)
   feed = feedparser.parse(response.content)
   
   # 方法3：使用BeautifulSoup
   from bs4 import BeautifulSoup
   soup = BeautifulSoup(response.content, 'xml')
   ```

### 4. 音频处理问题

#### 问题：音频格式不支持
**错误信息**:
```
AudioProcessingError: Unsupported audio format
pydub.exceptions.CouldntDecodeError: Decoding failed
```

**解决**:
1. **安装编解码器**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg libavcodec-extra
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # 下载FFmpeg并添加到PATH
   ```

2. **转换音频格式**
   ```python
   from pydub import AudioSegment
   
   # 转换格式
   audio = AudioSegment.from_file("input.m4a", format="m4a")
   audio.export("output.mp3", format="mp3")
   ```

3. **检查文件完整性**
   ```bash
   # 检查音频文件
   file audio.mp3
   
   # 查看音频信息
   ffprobe audio.mp3
   ```

#### 问题：转录质量差
**错误信息**:
```
低转录准确率
大量识别错误
```

**解决**:
1. **优化音频质量**
   ```python
   # 预处理音频
   audio = AudioSegment.from_file("input.mp3")
   
   # 标准化音量
   audio = audio.normalize()
   
   # 降噪
   audio = audio.low_pass_filter(3000)
   
   # 提高采样率
   audio = audio.set_frame_rate(16000)
   ```

2. **调整转录参数**
   ```python
   # 使用不同的模型
   import whisper
   
   # 小模型（速度快，准确率较低）
   model = whisper.load_model("tiny")
   
   # 大模型（速度慢，准确率高）
   model = whisper.load_model("large")
   
   # 调整参数
   result = model.transcribe(
       audio_path,
       language="zh",
       temperature=0.2,
       beam_size=5
   )
   ```

### 5. AI分析问题

#### 问题：API调用超限
**错误信息**:
```
RateLimitError: You exceeded your current quota
openai.error.RateLimitError: Rate limit reached
```

**解决**:
1. **监控使用量**
   ```bash
   # 查看API使用统计
   python castmind.py stats --api-usage
   
   # 设置使用限制
   # config/ai_models.json
   {
     "cost_management": {
       "daily_budget": 1.0,
       "monthly_budget": 30.0
     }
   }
   ```

2. **实现退避策略**
   ```python
   import time
   import openai
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10)
   )
   def call_openai_with_retry(prompt):
       return openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
   ```

3. **使用备用模型**
   ```python
   def get_ai_response(prompt, primary_model="openai", fallback_models=["deepseek", "kimi"]):
       for model in [primary_model] + fallback_models:
           try:
               return call_ai_model(model, prompt)
           except Exception as e:
               print(f"Model {model} failed: {e}")
               continue
       raise Exception("All AI models failed")
   ```

#### 问题：分析结果不准确
**错误信息**:
```
分析结果与内容不符
关键信息缺失
```

**解决**:
1. **优化提示词**
   ```python
   # 改进提示词模板
   prompt_template = """
   请分析以下播客内容：
   
   {transcript}
   
   要求：
   1. 提取3-5个关键点
   2. 总结核心观点
   3. 分析商业价值
   4. 提供行动建议
   
   请用中文回答，保持专业和准确。
   """
   ```

2. **后处理结果**
   ```python
   def post_process_analysis(result):
       # 清理文本
       result = result.strip()
       
       # 提取结构化信息
       import re
       key_points = re.findall(r'\d+\.\s*(.+)', result)
       
       # 验证结果
       if len(key_points) < 2:
           return "分析结果不完整，请重试"
       
       return result
   ```

### 6. 存储问题

#### 问题：磁盘空间不足
**错误信息**:
```
OSError: [Errno 28] No space left on device
IOError: Disk full
```

**解决**:
1. **检查磁盘使用**
   ```bash
   # 查看磁盘空间
   df -h
   
   # 查看大文件
   du -sh data/*
   du -ah data/ | sort -rh | head -20
   ```

2. **清理旧数据**
   ```bash
   # 自动清理脚本
   python castmind.py cleanup --older-than 30 --dry-run
   python castmind.py cleanup --older-than 30
   
   # 手动清理
   find data/ -name "*.mp3" -mtime +30 -delete
   find data/transcripts/ -name "*.txt" -mtime +90 -delete
   ```

3. **配置存储策略**
   ```yaml
   # config/storage.yaml
   retention_policy:
     audio_files: 30  # 保留30天
     transcripts: 90  # 保留90天
     notes: 365       # 保留365天
   
   compression:
     enabled: true
     level: 6
   
   backup:
     enabled: true
     interval: daily
     keep_last: 7
   ```

#### 问题：数据库损坏
**错误信息**:
```
sqlite3.DatabaseError: database disk image is malformed
OperationalError: unable to open database file
```

**解决**:
1. **备份数据**
   ```bash
   # 立即备份
   python castmind.py backup --output emergency-backup.tar.gz
   
   # 复制数据库文件
   cp data/castmind.db data/castmind.db.backup
   ```

2. **修复数据库**
   ```bash
   # 使用sqlite工具修复
   sqlite3 data/castmind.db ".backup data/castmind.db.repaired"
   mv data/castmind.db.repaired data/castmind.db
   
   # 或使用Python修复
   python -c "
   import sqlite3
   conn = sqlite3.connect('data/castmind.db')
   conn.execute('VACUUM')
   conn.close()
   "
   ```

3. **重建数据库**
   ```bash
   # 删除损坏的数据库
   rm data/castmind.db
   
   # 重新初始化
   python castmind.py init
   
   # 从备份恢复
   python castmind.py restore --input backup.tar.gz
   ```

## 📊 诊断工具

### 系统状态检查
```bash
# 运行完整诊断
python castmind.py diagnose

# 检查特定组件
python castmind.py diagnose --component network
python castmind.py diagnose --component storage
python castmind.py diagnose --component ai

# 生成诊断报告
python castmind.py diagnose --output report.html
```

### 性能分析
```bash
# 监控实时性能
python castmind.py monitor --interval 5

# 分析性能瓶颈
python -m cProfile -o profile.prof castmind.py process --name "test"
python -m snakeviz profile.prof

# 内存分析
python -m memory_profiler castmind.py
```

### 日志分析
```bash
# 查看错误日志
grep -i error logs/castmind.log | tail -20

# 分析日志模式
python castmind.py analyze-logs --pattern "timeout"

# 生成日志报告
python castmind.py logs --report --period 24h
```

## 🛠️ 调试技巧

### 启用调试模式
```bash
# 设置调试环境变量
export CASTMIND_ENV=debug
export LOG_LEVEL=DEBUG

# 启动调试模式
python castmind.py start --debug

# 或直接运行
CASTMIND_ENV=debug LOG_LEVEL=DEBUG python castmind.py start
```

### 使用调试器
```python
# 在代码中添加断点
import pdb

def process_audio(audio_path):
    try:
        # ... 代码 ...
        pdb.set_trace()  # 在这里暂停
        # ... 更多代码 ...
    except Exception as e:
        import traceback
        traceback.print_exc()
        pdb.post_mortem()
```

### 远程调试
```bash
# 启用远程调试
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client castmind.py start

# 在VS Code中连接
# 添加launch.json配置
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    }
}
```

## 📞 获取帮助

### 自助解决
1. **查看文档**: https://github.com/YearsAlso/castmind/docs
2. **搜索Issues**: https://github.com/YearsAlso/castmind/issues
3. **查看Wiki**: https://github.com/YearsAlso/castmind/wiki

### 社区支持
1. **GitHub Discussions**: 技术讨论和问题解答
2. **Discord频道**: 实时交流和快速响应
3. **Stack Overflow**: 使用 `[castmind]` 标签提问

### 专业支持
如需专业技术支持，请联系:
- **邮箱**: support@castmind.ai
- **企业服务**: enterprise@castmind.ai
- **紧急响应**: emergency@castmind.ai

## 📋 问题报告模板

报告问题时，请提供以下信息：

```markdown
## 问题描述
[清晰描述问题]

## 重现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 预期行为
[期望的结果]

## 实际行为
[实际的结果]

## 环境信息
- 系统: [例如: Ubuntu 22.04]
- Python版本: [例如: 3.12.2]
- CastMind版本: [例如: v1.0.0]
- 配置文件: [如有修改请说明]

## 日志输出
```
[粘贴相关日志]
```

## 附加信息
[其他相关信息]
```

## 🔄 更新与维护

### 检查更新
```bash
# 检查新版本
python castmind.py check-update

# 更新到最新版本
git pull origin main
uv sync --upgrade

# 或使用发布版本
wget https://github.com/YearsAlso/castmind/releases/latest/download/castmind