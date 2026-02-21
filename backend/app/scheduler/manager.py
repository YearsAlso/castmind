"""
调度器管理模块
使用 APScheduler 实现真正的定时任务调度
"""

import logging
from typing import Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

from app.core.config import settings
from app.scheduler.tasks import TaskScheduler

logger = logging.getLogger(__name__)


class SchedulerManager:
    """调度器管理器"""

    def __init__(self):
        # 配置作业存储和执行器
        jobstores = {
            "default": MemoryJobStore(),
        }

        executors = {
            "default": AsyncIOExecutor(),
        }

        job_defaults = {
            "coalesce": True,  # 合并多个相同的作业
            "max_instances": 1,  # 最大实例数
            "misfire_grace_time": 30,  # 错过执行的宽限时间
        }

        # 创建调度器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=settings.SCHEDULER_TIMEZONE,
        )

        # 任务调度器实例
        self.task_scheduler = TaskScheduler()

        # 调度器状态
        self.is_running = False

        # 添加事件监听器
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed, EVENT_JOB_MISSED)

        logger.info("调度器管理器初始化完成")

    def start(self):
        """启动调度器"""
        try:
            if not self.is_running:
                # 添加定时任务
                self._setup_jobs()

                # 启动调度器
                self.scheduler.start()
                self.is_running = True

                logger.info("调度器启动成功")
                return True
            else:
                logger.warning("调度器已在运行")
                return False

        except Exception as e:
            logger.error(f"调度器启动失败: {e}")
            return False

    def stop(self):
        """停止调度器"""
        try:
            if self.is_running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False

                logger.info("调度器已停止")
                return True
            else:
                logger.warning("调度器未在运行")
                return False

        except Exception as e:
            logger.error(f"调度器停止失败: {e}")
            return False

    def _setup_jobs(self):
        """设置定时任务"""
        if not settings.SCHEDULER_ENABLED:
            logger.info("调度器已禁用，跳过任务设置")
            return

        # 1. RSS 抓取任务 - 每 N 分钟执行一次
        self.scheduler.add_job(
            func=self._run_fetch_feeds,
            trigger=IntervalTrigger(minutes=settings.FETCH_INTERVAL_MINUTES),
            id="fetch_feeds",
            name="RSS订阅源抓取",
            replace_existing=True,
            max_instances=settings.SCHEDULER_MAX_INSTANCES,
        )

        # 2. 文章处理任务 - 每 N 分钟执行一次
        self.scheduler.add_job(
            func=self._run_process_articles,
            trigger=IntervalTrigger(minutes=settings.PROCESS_ARTICLES_MINUTES),
            id="process_articles",
            name="未处理文章分析",
            replace_existing=True,
            max_instances=settings.SCHEDULER_MAX_INSTANCES,
        )

        # 3. 状态更新任务 - 每小时执行一次
        self.scheduler.add_job(
            func=self._run_update_status,
            trigger=IntervalTrigger(hours=settings.UPDATE_STATUS_HOURS),
            id="update_status",
            name="订阅源状态更新",
            replace_existing=True,
            max_instances=settings.SCHEDULER_MAX_INSTANCES,
        )

        # 4. 数据清理任务 - 每天凌晨指定时间执行
        self.scheduler.add_job(
            func=self._run_cleanup,
            trigger=CronTrigger(hour=settings.CLEANUP_HOUR, minute=0),
            id="cleanup",
            name="旧数据清理",
            replace_existing=True,
            max_instances=settings.SCHEDULER_MAX_INSTANCES,
        )

        logger.info("定时任务设置完成")

    async def _run_fetch_feeds(self):
        """执行 RSS 抓取任务"""
        logger.info("开始执行 RSS 抓取任务")
        try:
            result = self.task_scheduler.fetch_all_feeds()
            logger.info(f"RSS 抓取任务完成: {result}")
            return result
        except Exception as e:
            logger.error(f"RSS 抓取任务失败: {e}")
            raise

    async def _run_process_articles(self):
        """执行文章处理任务"""
        logger.info("开始执行文章处理任务")
        try:
            result = self.task_scheduler.process_unprocessed_articles()
            logger.info(f"文章处理任务完成: {result}")
            return result
        except Exception as e:
            logger.error(f"文章处理任务失败: {e}")
            raise

    async def _run_update_status(self):
        """执行状态更新任务"""
        logger.info("开始执行状态更新任务")
        try:
            result = self.task_scheduler.update_feed_status()
            logger.info(f"状态更新任务完成: {result}")
            return result
        except Exception as e:
            logger.error(f"状态更新任务失败: {e}")
            raise

    async def _run_cleanup(self):
        """执行数据清理任务"""
        logger.info("开始执行数据清理任务")
        try:
            result = self.task_scheduler.cleanup_old_data(days=settings.CLEANUP_DAYS)
            logger.info(f"数据清理任务完成: {result}")
            return result
        except Exception as e:
            logger.error(f"数据清理任务失败: {e}")
            raise

    def _job_executed(self, event):
        """作业执行成功事件"""
        logger.info(f"任务执行成功: {event.job_id} at {event.scheduled_run_time}")

    def _job_error(self, event):
        """作业执行错误事件"""
        logger.error(
            f"任务执行失败: {event.job_id} at {event.scheduled_run_time}, exception: {event.exception}"
        )

    def _job_missed(self, event):
        """作业错过执行事件"""
        logger.warning(f"任务错过执行: {event.job_id} at {event.scheduled_run_time}")

    def get_jobs_status(self) -> Dict:
        """获取所有任务状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat()
                    if job.next_run_time
                    else None,
                    "trigger": str(job.trigger),
                    "max_instances": job.max_instances,
                    "misfire_grace_time": job.misfire_grace_time,
                }
            )

        return {
            "scheduler_running": self.is_running,
            "scheduler_enabled": settings.SCHEDULER_ENABLED,
            "total_jobs": len(jobs),
            "jobs": jobs,
        }

    def trigger_job(self, job_id: str) -> bool:
        """手动触发任务"""
        try:
            self.scheduler.run_job(job_id)
            logger.info(f"手动触发任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"手动触发任务失败 {job_id}: {e}")
            return False

    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"暂停任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败 {job_id}: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"恢复任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败 {job_id}: {e}")
            return False


# 全局调度器管理器实例
scheduler_manager = SchedulerManager()
