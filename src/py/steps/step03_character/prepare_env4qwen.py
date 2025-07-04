#!/usr/bin/env python3
"""
Qwen3-4B本地部署安装脚本
"""

import subprocess
import sys
import os
from utils.log_util import log_info, log_warning

def install_dependencies():
    """安装必要的依赖包"""
    from utils.constants import REQUIREMENTS_FILE
    
    log_info("正在安装依赖包...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    log_info("依赖安装完成！")

def check_system():
    """检查系统配置"""
    import psutil
    import torch
    
    # 检查内存
    memory_gb = psutil.virtual_memory().total / (1024**3)
    log_info(f"系统内存: {memory_gb:.1f}GB")
    
    if memory_gb < 8:
        log_warning("内存不足8GB，可能影响性能")
    
    # 检查GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        log_info(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
    else:
        log_info("未检测到GPU，将使用CPU运行（速度较慢）")

# 注意：此模块不支持直接执行，请通过main.py调用
# 如需执行环境准备，请使用：
# python main.py --step setup --action install