"""
Qwen3 模型服务启动脚本
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "py"))

def main():
    parser = argparse.ArgumentParser(description="启动 Qwen3 模型服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=19100, help="服务器端口 (默认: 19100)")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数 (默认: 1)")
    parser.add_argument("--reload", action="store_true", help="启用热重载 (开发模式)")
    parser.add_argument("--log-level", default="info", 
                       choices=["critical", "error", "warning", "info", "debug"],
                       help="日志级别 (默认: info)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Qwen3 模型服务")
    print("=" * 60)
    print(f"主机地址: {args.host}")
    print(f"端口号: {args.port}")
    print(f"工作进程数: {args.workers}")
    print(f"热重载: {'启用' if args.reload else '禁用'}")
    print(f"日志级别: {args.log_level}")
    print("=" * 60)
    print("服务启动中...")
    print(f"访问地址: http://{args.host}:{args.port}")
    print(f"API 文档: http://{args.host}:{args.port}/docs")
    print(f"健康检查: http://{args.host}:{args.port}/health")
    print("=" * 60)
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = str(project_root / "src" / "py")
    
    try:
        uvicorn.run(
            "model_service.server:app",
            host=args.host,
            port=args.port,
            workers=args.workers if not args.reload else 1,  # 热重载模式下只能用单进程
            reload=args.reload,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"\n服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()