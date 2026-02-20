#!/usr/bin/env python3
"""
🎧 Zoo Framework + FastAPI 集成原型
演示继承模式的实现方式
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 假设的 Zoo Framework 导入
# from zoo_framework.core import Master
# from zoo_framework.workers import BaseWorker
# from zoo_framework.utils import LogUtils

# FastAPI 导入
from fastapi import FastAPI, HTTPException
import uvicorn

# 模拟 Zoo Framework 的核心类
class MockMaster:
    """模拟 Zoo Framework 的 Master 类"""
    
    def __init__(self, worker_count: int = 1):
        self.worker_count = worker_count
        self.workers = {}
        self.event_queue = []
        self.running = False
        self._lock = threading.RLock()
        
        print(f"🎪 MockMaster 初始化，Worker 数量: {worker_count}")
    
    def register_worker(self, name: str, worker):
        """注册 Worker"""
        with self._lock:
            self.workers[name] = worker
            print(f"✅ 注册 Worker: {name}")
    
    def put_event(self, event: Dict[str, Any]):
        """放入事件"""
        with self._lock:
            self.event_queue.append(event)
            print(f"📨 放入事件: {event.get('type', 'unknown')}")
    
    def run(self):
        """启动框架"""
        self.running = True
        print("🚀 MockMaster 启动")
        
        # 模拟事件循环
        def event_loop():
            while self.running:
                if self.event_queue:
                    with self._lock:
                        event = self.event_queue.pop(0)
                        print(f"🔄 处理事件: {event}")
                time.sleep(0.1)
        
        self.event_thread = threading.Thread(target=event_loop, daemon=True)
        self.event_thread.start()
    
    def shutdown(self):
        """关闭框架"""
        self.running = False
        print("🛑 MockMaster 关闭")


class MockBaseWorker:
    """模拟 Zoo Framework 的 BaseWorker"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "unnamed_worker")
        self.config = config
        self.running = False
        
    def start(self):
        """启动 Worker"""
        self.running = True
        print(f"🦁 Worker {self.name} 启动")
    
    def stop(self):
        """停止 Worker"""
        self.running = False
        print(f"🛑 Worker {self.name} 停止")


# 实际的集成实现
class CastMindMaster(MockMaster):
    """CastMind 主控制器 - 继承 Zoo Framework，集成 FastAPI"""
    
    def __init__(self, worker_count: int = 1, api_port: int = 8000):
        # 初始化父类
        super().__init__(worker_count)
        
        # FastAPI 应用
        self.api_port = api_port
        self.app = FastAPI(
            title="CastMind API",
            description="播客智能处理系统 - Zoo Framework + FastAPI 集成",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        
        # Web 服务器线程
        self._web_thread: Optional[threading.Thread] = None
        self._web_running = False
        
        # 设置 API 路由
        self._setup_api_routes()
        
        # 初始化 Worker
        self._init_workers()
        
        print(f"🎧 CastMindMaster 初始化完成，API 端口: {api_port}")
    
    def _setup_api_routes(self):
        """设置 API 路由"""
        
        @self.app.get("/")
        async def root():
            """根端点"""
            return {
                "service": "CastMind",
                "framework": "Zoo Framework + FastAPI",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/v1/health")
        async def health_check():
            """健康检查端点"""
            return {
                "status": "healthy",
                "workers": len(self.workers),
                "events_in_queue": len(self.event_queue),
                "api_server": "running" if self._web_running else "stopped",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/v1/workers")
        async def list_workers():
            """列出所有 Worker"""
            workers_info = []
            for name, worker in self.workers.items():
                workers_info.append({
                    "name": name,
                    "status": "running" if worker.running else "stopped",
                    "config": worker.config
                })
            
            return {
                "count": len(workers_info),
                "workers": workers_info
            }
        
        @self.app.post("/api/v1/tasks/process-podcast")
        async def process_podcast(podcast_id: str):
            """处理播客任务"""
            if not podcast_id:
                raise HTTPException(status_code=400, detail="需要提供 podcast_id")
            
            # 创建处理事件
            event = {
                "type": "process_podcast",
                "podcast_id": podcast_id,
                "timestamp": datetime.now().isoformat(),
                "status": "queued"
            }
            
            # 通过 Zoo Framework 事件系统分发任务
            self.put_event(event)
            
            return {
                "task_id": podcast_id,
                "status": "queued",
                "message": "播客处理任务已加入队列",
                "event": event,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/v1/events")
        async def list_events(limit: int = 10):
            """查看事件队列"""
            with self._lock:
                events = self.event_queue[:limit]
            
            return {
                "total": len(self.event_queue),
                "limit": limit,
                "events": events
            }
        
        @self.app.post("/api/v1/system/shutdown")
        async def system_shutdown():
            """系统关闭端点（需要身份验证）"""
            # 在实际应用中，这里需要身份验证
            
            # 异步关闭
            shutdown_thread = threading.Thread(target=self.shutdown)
            shutdown_thread.start()
            
            return {
                "status": "shutting_down",
                "message": "系统正在关闭...",
                "timestamp": datetime.now().isoformat()
            }
    
    def _init_workers(self):
        """初始化 Worker"""
        
        # 播客处理 Worker
        podcast_worker = MockBaseWorker({
            "name": "podcast_processor",
            "type": "processor",
            "batch_size": 5,
            "max_retries": 3
        })
        self.register_worker("podcast_processor", podcast_worker)
        
        # RSS 解析 Worker
        rss_worker = MockBaseWorker({
            "name": "rss_parser",
            "type": "parser",
            "timeout": 30,
            "cache_ttl": 3600
        })
        self.register_worker("rss_parser", rss_worker)
        
        # AI 处理 Worker
        ai_worker = MockBaseWorker({
            "name": "ai_processor",
            "type": "ai",
            "model": "deepseek-chat",
            "max_tokens": 1000
        })
        self.register_worker("ai_processor", ai_worker)
        
        print(f"✅ 初始化了 {len(self.workers)} 个 Worker")
    
    def _start_web_server(self):
        """启动 FastAPI Web 服务器"""
        
        def run_web_server():
            """运行 Web 服务器的内部函数"""
            try:
                self._web_running = True
                print(f"🌐 启动 Web 服务器，端口: {self.api_port}")
                
                uvicorn.run(
                    self.app,
                    host="0.0.0.0",
                    port=self.api_port,
                    log_level="info",
                    access_log=True
                )
            except Exception as e:
                print(f"❌ Web 服务器错误: {e}")
            finally:
                self._web_running = False
        
        # 创建并启动 Web 服务器线程
        self._web_thread = threading.Thread(
            target=run_web_server,
            daemon=True,
            name="FastAPI-Web-Server"
        )
        self._web_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        if self._web_running:
            print(f"✅ Web 服务器已启动: http://localhost:{self.api_port}")
            print(f"   📚 API 文档: http://localhost:{self.api_port}/api/docs")
        else:
            print("❌ Web 服务器启动失败")
    
    def _start_workers(self):
        """启动所有 Worker"""
        print("🚀 启动所有 Worker...")
        
        for name, worker in self.workers.items():
            worker.start()
            print(f"   ✅ 启动 Worker: {name}")
    
    def run(self):
        """启动 CastMind 服务"""
        print("=" * 60)
        print("🎧 启动 CastMind 服务")
        print("=" * 60)
        
        # 1. 启动 Zoo Framework（父类）
        super().run()
        
        # 2. 启动 Worker
        self._start_workers()
        
        # 3. 启动 Web 服务器
        self._start_web_server()
        
        # 4. 启动监控循环
        self._start_monitoring()
        
        print("✅ CastMind 服务启动完成")
        print(f"🔗 访问地址: http://localhost:{self.api_port}")
        print("=" * 60)
    
    def _start_monitoring(self):
        """启动监控循环"""
        def monitor_loop():
            """监控循环"""
            while self.running:
                time.sleep(10)
                
                # 打印状态信息
                print(f"\n📊 系统状态监控 [{datetime.now().strftime('%H:%M:%S')}]")
                print(f"   Worker 数量: {len(self.workers)}")
                print(f"   事件队列长度: {len(self.event_queue)}")
                print(f"   Web 服务器: {'运行中' if self._web_running else '已停止'}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def shutdown(self):
        """优雅关闭"""
        print("\n" + "=" * 60)
        print("🛑 开始关闭 CastMind 服务")
        print("=" * 60)
        
        # 1. 停止 Worker
        print("停止 Worker...")
        for name, worker in self.workers.items():
            worker.stop()
            print(f"   ✅ 停止 Worker: {name}")
        
        # 2. 停止 Zoo Framework（父类）
        super().shutdown()
        
        # 3. Web 服务器会自动停止（daemon 线程）
        
        print("✅ CastMind 服务已关闭")
        print("=" * 60)


# 使用示例
def main():
    """主函数"""
    
    # 创建 CastMindMaster 实例
    master = CastMindMaster(
        worker_count=3,
        api_port=8000
    )
    
    try:
        # 启动服务
        master.run()
        
        # 保持主线程运行
        print("\n📝 命令提示:")
        print("  • 按 Ctrl+C 停止服务")
        print("  • 访问 http://localhost:8000/api/docs 查看 API 文档")
        print("  • 访问 http://localhost:8000/api/v1/health 检查健康状态")
        
        # 模拟一些 API 调用
        print("\n🎯 模拟 API 调用:")
        
        # 这里可以添加实际的 HTTP 请求测试
        # 或者保持服务运行
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 接收到中断信号")
    finally:
        # 优雅关闭
        master.shutdown()


if __name__ == "__main__":
    main()