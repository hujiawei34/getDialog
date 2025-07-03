#!/usr/bin/env python3
"""
Qwen3-4B本地部署安装脚本
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装必要的依赖包"""
    
    requirements = [
        "torch>=2.0.0",
        "transformers>=4.37.0", 
        "accelerate>=0.26.0",
        "tiktoken",
        "einops",
        "transformers_stream_generator>=0.0.4",
        "scipy",
        "peft>=0.4.0",
        "huggingface_hub",
        "modelscope",  # 用于从ModelScope下载模型
    ]
    
    print("正在安装依赖包...")
    for package in requirements:
        print(f"安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("依赖安装完成！")

def check_system():
    """检查系统配置"""
    import psutil
    import torch
    
    # 检查内存
    memory_gb = psutil.virtual_memory().total / (1024**3)
    print(f"系统内存: {memory_gb:.1f}GB")
    
    if memory_gb < 8:
        print("⚠️  警告: 内存不足8GB，可能影响性能")
    
    # 检查GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
    else:
        print("未检测到GPU，将使用CPU运行（速度较慢）")

if __name__ == "__main__":
    print("=== Qwen3-4B环境准备 ===")
    check_system()
    install_dependencies()
    print("环境准备完成！")