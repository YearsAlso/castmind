#!/usr/bin/env python3
"""
🎧 CastMind Zoo 启动脚本

启动 Zoo Framework + FastAPI 集成的 CastMind 服务
"""

import argparse
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from castmind_zoo.master import run_castmind


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🎧 CastMind Zoo - Zoo Framework + FastAPI 集成服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 使用默认配置启动
  %(prog)s --config config.json     # 使用配置文件启动
  %(prog)s --port 8080 --debug      # 在端口 8080 启动调试模式
  %(prog)s --workers 10             # 启动 10 个 Worker
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径 (JSON 格式)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Worker 数量 (默认: 5)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API 服务端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="API 服务主机 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CastMind Zoo 0.1.0"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎧 启动 CastMind Zoo 服务")
    print("=" * 60)
    
    try:
        # 启动服务
        run_castmind(
            config_path=args.config,
            worker_count=args.workers,
            api_port=args.port,
            api_host=args.host,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()