#!/usr/bin/env python3
"""
🎧 CastMind 后台服务
版本: 1.0.0
描述: CastMind 持久化后台服务，支持 Docker 容器化部署
"""

import os
import sys
import time
import signal
import logging
import schedule
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
def setup_logging():
    """配置日志系统"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = Path(os.getenv('LOGS_DIR', '/app/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_dir / 'castmind_service.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 创建服务日志器
    logger = logging.getLogger('castmind_service')
    logger.info(f"日志系统初始化完成，级别: {log_level}")
    
    return logger

class CastMindService:
    """CastMind 后台服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.logger = setup_logging()
        self.running = True
        self.data_dir = Path(os.getenv('DATA_DIR', '/app/data'))
        self.config_dir = Path(os.getenv('CONFIG_DIR', '/app/config'))
        
        # 创建必要目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 服务信息
        self.service_info = {
            'name': 'CastMind',
            'version': '1.0.0',
            'start_time': datetime.now(),
            'pid': os.getpid()
        }
        
        # 任务状态
        self.task_status = {
            'processing': False,
            'last_run': None,
            'success_count': 0,
            'error_count': 0
        }
        
        self.logger.info(f"🎧 CastMind 后台服务初始化")
        self.logger.info(f"   服务名称: {self.service_info['name']}")
        self.logger.info(f"   版本: {self.service_info['version']}")
        self.logger.info(f"   PID: {self.service_info['pid']}")
        self.logger.info(f"   数据目录: {self.data_dir}")
        self.logger.info(f"   配置目录: {self.config_dir}")
        
        # 设置信号处理
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.logger.debug("信号处理器设置完成")
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        self.logger.info(f"接收到信号 {signum}，开始优雅关闭...")
        self.running = False
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = self.config_dir / 'service_config.json'
        
        default_config = {
            'schedule': {
                'process_podcasts': '*/30 * * * *',  # 每30分钟
                'check_updates': '*/10 * * * *',     # 每10分钟
                'cleanup': '0 3 * * *'               # 每天凌晨3点
            },
            'processing': {
                'batch_size': 5,
                'max_retries': 3,
                'retry_delay': 60
            },
            'obsidian': {
                'enabled': bool(os.getenv('OBSIDIAN_VAULT')),
                'vault_path': os.getenv('OBSIDIAN_VAULT', ''),
                'podcasts_dir': os.getenv('OBSIDIAN_PODCASTS_DIR', '')
            }
        }
        
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并配置
                default_config.update(user_config)
                self.logger.info("配置文件加载成功")
            except Exception as e:
                self.logger.error(f"配置文件加载失败: {e}")
        
        return default_config
    
    def setup_schedule(self, config: Dict[str, Any]):
        """设置定时任务"""
        self.logger.info("设置定时任务...")
        
        # 处理播客任务
        schedule.every(30).minutes.do(self.process_podcasts_task)
        self.logger.info("   ✅ 播客处理任务: 每30分钟")
        
        # 检查更新任务
        schedule.every(10).minutes.do(self.check_updates_task)
        self.logger.info("   ✅ 更新检查任务: 每10分钟")
        
        # 清理任务
        schedule.every().day.at("03:00").do(self.cleanup_task)
        self.logger.info("   ✅ 清理任务: 每天03:00")
        
        # 健康报告任务
        schedule.every().hour.do(self.health_report_task)
        self.logger.info("   ✅ 健康报告: 每小时")
        
        # 立即执行一次
        self.process_podcasts_task()
    
    def process_podcasts_task(self):
        """处理播客任务"""
        if self.task_status['processing']:
            self.logger.warning("已有任务正在处理，跳过本次执行")
            return
        
        self.task_status['processing'] = True
        self.task_status['last_run'] = datetime.now()
        
        try:
            self.logger.info("开始处理播客任务...")
            
            # 这里调用实际的播客处理逻辑
            # 可以使用 process_podcast_obsidian.py 中的功能
            
            # 模拟处理
            import random
            success = random.random() > 0.1  # 90% 成功率
            
            if success:
                self.task_status['success_count'] += 1
                self.logger.info("播客处理任务完成")
            else:
                self.task_status['error_count'] += 1
                self.logger.error("播客处理任务失败")
                
        except Exception as e:
            self.task_status['error_count'] += 1
            self.logger.error(f"播客处理任务异常: {e}")
        finally:
            self.task_status['processing'] = False
    
    def check_updates_task(self):
        """检查更新任务"""
        try:
            self.logger.debug("检查 RSS 更新...")
            # 这里实现 RSS 更新检查逻辑
            # ...
            self.logger.debug("更新检查完成")
        except Exception as e:
            self.logger.error(f"更新检查失败: {e}")
    
    def cleanup_task(self):
        """清理任务"""
        try:
            self.logger.info("执行清理任务...")
            
            # 清理旧日志文件（保留30天）
            log_dir = Path(os.getenv('LOGS_DIR', '/app/logs'))
            for log_file in log_dir.glob('*.log.*'):
                if log_file.stat().st_mtime < time.time() - 30 * 86400:
                    log_file.unlink()
                    self.logger.debug(f"删除旧日志文件: {log_file}")
            
            # 清理临时文件
            temp_dir = Path('/tmp/castmind')
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                self.logger.debug("清理临时目录")
            
            self.logger.info("清理任务完成")
        except Exception as e:
            self.logger.error(f"清理任务失败: {e}")
    
    def health_report_task(self):
        """健康报告任务"""
        try:
            uptime = datetime.now() - self.service_info['start_time']
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            report = f"""
🎧 CastMind 服务健康报告
==============================
服务状态: {'运行中' if self.running else '停止中'}
运行时间: {days}天 {hours}小时 {minutes}分钟
任务统计:
  成功: {self.task_status['success_count']}
  失败: {self.task_status['error_count']}
  最后运行: {self.task_status['last_run'] or '从未运行'}
系统信息:
  PID: {self.service_info['pid']}
  版本: {self.service_info['version']}
  数据目录: {self.data_dir}
==============================
            """
            
            self.logger.info(report)
            
            # 保存健康报告到文件
            report_file = self.data_dir / 'health_report.txt'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                
        except Exception as e:
            self.logger.error(f"健康报告生成失败: {e}")
    
    def run(self):
        """运行服务主循环"""
        self.logger.info("🚀 CastMind 后台服务启动")
        
        # 加载配置
        config = self.load_config()
        
        # 设置定时任务
        self.setup_schedule(config)
        
        # 主循环
        self.logger.info("进入主服务循环...")
        
        while self.running:
            try:
                # 运行待处理的任务
                schedule.run_pending()
                
                # 休眠一段时间，避免 CPU 占用过高
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info("接收到键盘中断")
                self.running = False
            except Exception as e:
                self.logger.error(f"主循环异常: {e}")
                time.sleep(5)  # 异常后等待5秒再继续
        
        # 服务关闭
        self.shutdown()
    
    def shutdown(self):
        """关闭服务"""
        self.logger.info("开始关闭服务...")
        
        # 等待当前任务完成
        if self.task_status['processing']:
            self.logger.info("等待当前任务完成...")
            max_wait = 30  # 最多等待30秒
            for i in range(max_wait):
                if not self.task_status['processing']:
                    break
                time.sleep(1)
        
        # 生成最终报告
        self.health_report_task()
        
        self.logger.info("🎉 CastMind 服务已优雅关闭")
        logging.shutdown()

def main():
    """主函数"""
    # 检查必要环境变量
    required_env_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要环境变量: {', '.join(missing_vars)}")
        print("请设置以下环境变量:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        sys.exit(1)
    
    # 创建并运行服务
    service = CastMindService()
    
    try:
        service.run()
    except Exception as e:
        service.logger.error(f"服务运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()