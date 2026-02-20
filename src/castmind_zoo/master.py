"""
🎧 CastMindMaster - 继承 Zoo Framework，集成 FastAPI

核心主控制器，管理整个 CastMind 系统
"""

import asyncio
import threading
import time
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Zoo Framework 导入
try:
    from zoo_framework.core import Master as ZooMaster
    from zoo_framework.workers import BaseWorker
    from zoo_framework.utils import LogUtils
    from zoo_framework.statemachine import StateMachineManager
    ZOO_AVAILABLE = True
except ImportError:
    print("⚠️  Zoo Framework 未安装，使用模拟模式")
    ZOO_AVAILABLE = False
    # 创建模拟类
    class ZooMaster:
        def __init__(self, worker_count=1):
            self.worker_count = worker_count
            self.workers = {}
            self.running = False
        
        def run(self):
            self.running = True
        
        def shutdown(self):
            self.running = False
    
    class BaseWorker:
        def __init__(self, config):
            self.config = config
            self.running = False
        
        def start(self):
            self.running = True
        
        def stop(self):
            self.running = False
    
    class LogUtils:
        @staticmethod
        def info(msg):
            print(f"[INFO] {msg}")
        
        @staticmethod
        def error(msg):
            print(f"[ERROR] {msg}")
        
        @staticmethod
        def warning(msg):
            print(f"[WARNING] {msg}")
    
    class StateMachineManager:
        @staticmethod
        def set_state(scope, key, value):
            pass
        
        @staticmethod
        def get_state(scope, key):
            return None

# FastAPI 导入
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 本地导入
from .config import CastMindConfig
from .api.dependencies import get_config, verify_api_key
from .api.routers import health, workers, tasks, podcasts, system


class CastMindMaster(ZooMaster):
    """CastMind 主控制器 - 继承 Zoo Framework，集成 FastAPI"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        worker_count: int = 5,
        api_port: int = 8000,
        api_host: str = "0.0.0.0",
        debug: bool = False
    ):
        """
        初始化 CastMindMaster
        
        Args:
            config_path: 配置文件路径
            worker_count: Worker 数量
            api_port: API 服务端口
            api_host: API 服务主机
            debug: 调试模式
        """
        # 初始化父类 (Zoo Framework)
        super().__init__(worker_count)
        
        # 配置
        self.config = CastMindConfig(config_path)
        self.api_port = api_port
        self.api_host = api_host
        self.debug = debug
        
        # FastAPI 应用
        self.app = self._create_fastapi_app()
        
        # 运行状态
        self._web_thread: Optional[threading.Thread] = None
        self._web_running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._monitor_thread: Optional[threading.Thread] = None
        
        # 数据目录
        self.data_dir = Path(self.config.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self._init_components()
        
        LogUtils.info(f"🎧 CastMindMaster 初始化完成")
        LogUtils.info(f"   API: http://{api_host}:{api_port}")
        LogUtils.info(f"   Worker 数量: {worker_count}")
        LogUtils.info(f"   数据目录: {self.data_dir}")
    
    def _create_fastapi_app(self) -> FastAPI:
        """创建 FastAPI 应用"""
        
        app = FastAPI(
            title="CastMind API",
            description="播客智能处理系统 - Zoo Framework + FastAPI 集成",
            version=self.config.version,
            docs_url="/api/docs" if self.debug else None,
            redoc_url="/api/redoc" if self.debug else None,
            openapi_url="/api/openapi.json" if self.debug else None,
        )
        
        # CORS 中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 全局异常处理
        @app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            LogUtils.error(f"API 异常: {exc}")
            return {
                "error": "Internal Server Error",
                "message": str(exc) if self.debug else "请查看服务器日志",
                "timestamp": datetime.now().isoformat()
            }
        
        # 包含路由器
        app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
        app.include_router(workers.router, prefix="/api/v1", tags=["Worker 管理"])
        app.include_router(tasks.router, prefix="/api/v1", tags=["任务管理"])
        app.include_router(podcasts.router, prefix="/api/v1", tags=["播客管理"])
        app.include_router(system.router, prefix="/api/v1", tags=["系统管理"])
        
        # 根端点
        @app.get("/")
        async def root():
            return {
                "service": "CastMind",
                "framework": "Zoo Framework + FastAPI",
                "version": self.config.version,
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "docs": f"http://{self.api_host}:{self.api_port}/api/docs" if self.debug else None
            }
        
        # 依赖注入配置
        app.dependency_overrides[get_config] = lambda: self.config
        
        return app
    
    def _init_components(self):
        """初始化系统组件"""
        
        # 初始化状态机
        self._init_state_machine()
        
        # 初始化 Worker
        self._init_workers()
        
        # 初始化数据库连接
        self._init_database()
        
        # 初始化任务队列
        self._init_task_queue()
    
    def _init_state_machine(self):
        """初始化状态机"""
        LogUtils.info("初始化状态机...")
        
        # 系统状态
        StateMachineManager().set_state("system", "status", "initializing")
        StateMachineManager().set_state("system", "start_time", datetime.now().isoformat())
        StateMachineManager().set_state("system", "version", self.config.version)
        
        # 性能指标
        StateMachineManager().set_state("metrics", "worker_count", 0)
        StateMachineManager().set_state("metrics", "task_queue_size", 0)
        StateMachineManager().set_state("metrics", "processed_tasks", 0)
        StateMachineManager().set_state("metrics", "failed_tasks", 0)
        
        LogUtils.info("✅ 状态机初始化完成")
    
    def _init_workers(self):
        """初始化 Worker"""
        LogUtils.info("初始化 Worker...")
        
        # 这里会注册具体的 Worker
        # 例如: RSS 解析 Worker、AI 处理 Worker、文件生成 Worker 等
        
        # 临时注册一个测试 Worker
        if ZOO_AVAILABLE:
            from .workers.test_worker import TestWorker
            test_worker = TestWorker({"name": "test_worker"})
            self.register_worker("test_worker", test_worker)
        
        worker_count = len(self.workers) if hasattr(self, 'workers') else 0
        StateMachineManager().set_state("metrics", "worker_count", worker_count)
        
        LogUtils.info(f"✅ 初始化了 {worker_count} 个 Worker")
    
    def _init_database(self):
        """初始化数据库连接"""
        LogUtils.info("初始化数据库...")
        
        # 这里会初始化 SQLite/PostgreSQL 连接
        # 暂时使用模拟
        
        LogUtils.info("✅ 数据库初始化完成")
    
    def _init_task_queue(self):
        """初始化任务队列"""
        LogUtils.info("初始化任务队列...")
        
        # 这里会初始化 Redis/Celery 任务队列
        # 暂时使用内存队列
        
        self.task_queue = []
        self.task_lock = threading.RLock()
        
        LogUtils.info("✅ 任务队列初始化完成")
    
    def _start_web_server(self):
        """启动 FastAPI Web 服务器"""
        
        def run_web_server():
            """运行 Web 服务器的内部函数"""
            try:
                self._web_running = True
                LogUtils.info(f"🌐 启动 Web 服务器: {self.api_host}:{self.api_port}")
                
                uvicorn.run(
                    self.app,
                    host=self.api_host,
                    port=self.api_port,
                    log_level="debug" if self.debug else "info",
                    access_log=True,
                    reload=self.debug,  # 调试模式下启用热重载
                )
            except Exception as e:
                LogUtils.error(f"❌ Web 服务器错误: {e}")
                import traceback
                traceback.print_exc()
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
        for i in range(10):
            if self._web_running:
                break
            time.sleep(0.5)
        
        if self._web_running:
            LogUtils.info(f"✅ Web 服务器已启动")
            LogUtils.info(f"   🔗 http://{self.api_host}:{self.api_port}")
            if self.debug:
                LogUtils.info(f"   📚 API 文档: http://{self.api_host}:{self.api_port}/api/docs")
        else:
            LogUtils.error("❌ Web 服务器启动失败")
    
    def _start_scheduler(self):
        """启动定时任务调度器"""
        LogUtils.info("启动定时任务调度器...")
        
        def scheduler_loop():
            """调度器循环"""
            while self.running:
                try:
                    # 检查定时任务
                    self._check_scheduled_tasks()
                    
                    # 处理任务队列
                    self._process_task_queue()
                    
                    time.sleep(1)  # 每秒检查一次
                    
                except Exception as e:
                    LogUtils.error(f"调度器错误: {e}")
                    time.sleep(5)
        
        self._scheduler_thread = threading.Thread(
            target=scheduler_loop,
            daemon=True,
            name="Task-Scheduler"
        )
        self._scheduler_thread.start()
        
        LogUtils.info("✅ 定时任务调度器已启动")
    
    def _start_monitor(self):
        """启动系统监控"""
        LogUtils.info("启动系统监控...")
        
        def monitor_loop():
            """监控循环"""
            monitor_interval = 30  # 30秒报告一次
            
            while self.running:
                try:
                    # 更新状态
                    self._update_system_status()
                    
                    # 记录性能指标
                    self._record_metrics()
                    
                    # 检查资源使用
                    self._check_resources()
                    
                    time.sleep(monitor_interval)
                    
                except Exception as e:
                    LogUtils.error(f"监控错误: {e}")
                    time.sleep(10)
        
        self._monitor_thread = threading.Thread(
            target=monitor_loop,
            daemon=True,
            name="System-Monitor"
        )
        self._monitor_thread.start()
        
        LogUtils.info("✅ 系统监控已启动")
    
    def _check_scheduled_tasks(self):
        """检查定时任务"""
        # 这里实现定时任务逻辑
        # 例如: 定期检查 RSS 更新、清理旧文件等
        pass
    
    def _process_task_queue(self):
        """处理任务队列"""
        with self.task_lock:
            if self.task_queue:
                # 处理队列中的任务
                task = self.task_queue.pop(0)
                LogUtils.info(f"处理任务: {task.get('type', 'unknown')}")
                
                # 更新状态
                processed = StateMachineManager().get_state("metrics", "processed_tasks") or 0
                StateMachineManager().set_state("metrics", "processed_tasks", processed + 1)
    
    def _update_system_status(self):
        """更新系统状态"""
        # 更新 Worker 数量
        worker_count = len(self.workers) if hasattr(self, 'workers') else 0
        StateMachineManager().set_state("metrics", "worker_count", worker_count)
        
        # 更新任务队列大小
        with self.task_lock:
            queue_size = len(self.task_queue)
        StateMachineManager().set_state("metrics", "task_queue_size", queue_size)
        
        # 更新运行时间
        start_time = StateMachineManager().get_state("system", "start_time")
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            uptime = datetime.now() - start_dt
            StateMachineManager().set_state("system", "uptime", str(uptime))
    
    def _record_metrics(self):
        """记录性能指标"""
        # 这里可以记录 CPU、内存、磁盘使用情况
        pass
    
    def _check_resources(self):
        """检查资源使用"""
        # 检查磁盘空间、内存使用等
        pass
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            LogUtils.info(f"接收到信号 {signum}，开始优雅关闭...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """启动 CastMind 服务"""
        LogUtils.info("=" * 60)
        LogUtils.info("🎧 启动 CastMind 服务")
        LogUtils.info("=" * 60)
        
        # 设置信号处理器
        self._setup_signal_handlers()
        
        # 1. 启动 Zoo Framework（父类）
        super().run()
        StateMachineManager().set_state("system", "status", "running")
        
        # 2. 启动 Worker
        self._start_workers()
        
        # 3. 启动 Web 服务器
        self._start_web_server()
        
        # 4. 启动定时任务调度器
        self._start_scheduler()
        
        # 5. 启动系统监控
        self._start_monitor()
        
        LogUtils.info("✅ CastMind 服务启动完成")
        LogUtils.info(f"🔗 访问地址: http://{self.api_host}:{self.api_port}")
        LogUtils.info("📝 按 Ctrl+C 停止服务")
        LogUtils.info("=" * 60)
        
        # 保持主线程运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            LogUtils.info("\n🛑 接收到键盘中断")
        finally:
            self.shutdown()
    
    def _start_workers(self):
        """启动所有 Worker"""
        LogUtils.info("启动 Worker...")
        
        if hasattr(self, 'workers'):
            for name, worker in self.workers.items():
                if hasattr(worker, 'start'):
                    worker.start()
                    LogUtils.info(f"   ✅ 启动 Worker: {name}")
    
    def shutdown(self):
        """优雅关闭 CastMind 服务"""
        if not self.running:
            return
        
        LogUtils.info("\n" + "=" * 60)
        LogUtils.info("🛑 开始关闭 CastMind 服务")
        LogUtils.info("=" * 60)
        
        # 1. 更新状态
        StateMachineManager().set_state("system", "status", "shutting_down")
        
        # 2. 停止 Worker
        LogUtils.info("停止 Worker...")
        if hasattr(self, 'workers'):
            for name, worker in self.workers.items():
                if hasattr(worker, 'stop'):
                    worker.stop()
                    LogUtils.info(f"   ✅ 停止 Worker: {name}")
        
        # 3. 停止 Zoo Framework（父类）
        super().shutdown()
        
        # 4. 清理资源
        self._cleanup()
        
        # 5. 更新最终状态
        StateMachineManager().set_state("system", "status", "stopped")
        StateMachineManager().set_state("system", "stop_time", datetime.now().isoformat())
        
        LogUtils.info("✅ CastMind 服务已关闭")
        LogUtils.info("=" * 60)
    
    def _cleanup(self):
        """清理资源"""
        LogUtils.info("清理资源...")
        
        # 清理任务队列
        with self.task_lock:
            self.task_queue.clear()
        
        # 关闭数据库连接
        # 如果有数据库连接，在这里关闭
        
        LogUtils.info("✅ 资源清理完成")
    
    def add_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        添加任务到队列
        
        Args:
            task_type: 任务类型
            task_data: 任务数据
            
        Returns:
            任务ID
        """
        import uuid
        
        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "type": task_type,
            "data": task_data,
            "created_at": datetime.now().isoformat(),
            "status": "queued"
        }
        
        with self.task_lock:
            self.task_queue.append(task)
        
        LogUtils.info(f"📨 添加任务: {task_type} (ID: {task_id})")
        
        # 更新状态
        queue_size = len(self.task_queue)
        StateMachineManager().set_state("metrics", "task_queue_size", queue_size)
        
        return task_id
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "status": StateMachineManager().get_state("system", "status"),
            "version": StateMachineManager().get_state("system", "version"),
            "start_time": StateMachineManager().get_state("system", "start_time"),
            "uptime": StateMachineManager().get_state("system", "uptime"),
            "metrics": {
                "worker_count": StateMachineManager().get_state("metrics", "worker_count"),
                "task_queue_size": StateMachineManager().get_state("metrics", "task_queue_size"),
                "processed_tasks": StateMachineManager().get_state("metrics", "processed_tasks"),
                "failed_tasks": StateMachineManager().get_state("metrics", "failed_tasks"),
            },
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "running": self._web_running,
            },
            "config": {
                "debug": self.debug,
                "data_dir": str(self.data_dir),
            }
        }


# 快捷启动函数
def run_castmind(
    config_path: Optional[str] = None,
    worker_count: int = 5,
    api_port: int = 8000,
    api_host: str = "0.0.0.0",
    debug: bool = False
):
    """
    快捷启动 CastMind 服务
    
    Args:
        config_path: 配置文件路径
        worker_count: Worker 数量
        api_port: API 服务端口
        api_host: API 服务主机
        debug: 调试模式
    """
    master = CastMindMaster(
        config_path=config_path,
        worker_count=worker_count,
        api_port=api_port,
        api_host=api_host,
        debug=debug
    )
    
    master.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="启动 CastMind 服务")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--workers", type=int, default=5, help="Worker 数量")
    parser.add_argument("--port", type=int, default=8000, help="API 端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API 主机")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    run_castmind(
        config_path=args.config,
        worker_count=args.workers,
        api_port=args.port,
        api_host=args.host,
        debug=args.debug
    )