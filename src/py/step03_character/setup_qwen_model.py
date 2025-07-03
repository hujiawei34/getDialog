#!/usr/bin/env python3
"""
Qwen3-4B模型下载和部署脚本
单独的模型管理工具，负责模型的下载、验证和配置
"""

import subprocess
import sys
import os
import json
import torch
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenModelManager:
    """Qwen模型管理器"""
    
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.config_file = self.model_dir / "model_config.json"
        
    def install_dependencies(self):
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
            "modelscope",
        ]
        
        logger.info("正在安装依赖包...")
        for package in requirements:
            logger.info(f"安装 {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                logger.error(f"安装 {package} 失败: {e}")
                return False
        
        logger.info("依赖安装完成！")
        return True
    
    def check_system_requirements(self):
        """检查系统配置"""
        try:
            import psutil
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
        
        # 检查内存
        memory_gb = psutil.virtual_memory().total / (1024**3)
        logger.info(f"系统内存: {memory_gb:.1f}GB")
        
        requirements = {
            "memory_ok": memory_gb >= 8,
            "gpu_available": torch.cuda.is_available(),
            "gpu_memory": 0
        }
        
        if memory_gb < 8:
            logger.warning("⚠️  警告: 内存不足8GB，可能影响性能")
        
        # 检查GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            requirements["gpu_memory"] = gpu_memory
            logger.info(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            logger.info("未检测到GPU，将使用CPU运行（速度较慢）")
        
        return requirements
    
    def download_model_from_huggingface(self, model_name: str = "Qwen/Qwen2.5-3B-Instruct"):
        """从HuggingFace下载模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            logger.info(f"从HuggingFace下载模型: {model_name}")
            
            # 下载tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=str(self.model_dir)
            )
            
            # 下载模型
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=str(self.model_dir)
            )
            
            # 保存配置
            config = {
                "model_name": model_name,
                "model_path": str(self.model_dir),
                "source": "huggingface",
                "download_success": True
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("模型下载完成！")
            return True
            
        except Exception as e:
            logger.error(f"HuggingFace下载失败: {e}")
            return False
    
    def download_model_from_modelscope(self, model_name: str = "qwen/Qwen2.5-3B-Instruct"):
        """从ModelScope下载模型"""
        try:
            from modelscope import snapshot_download
            
            logger.info(f"从ModelScope下载模型: {model_name}")
            
            model_dir = snapshot_download(
                model_name, 
                cache_dir=str(self.model_dir)
            )
            
            # 保存配置
            config = {
                "model_name": model_name,
                "model_path": model_dir,
                "source": "modelscope",
                "download_success": True
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("模型下载完成！")
            return True
            
        except Exception as e:
            logger.error(f"ModelScope下载失败: {e}")
            return False
    
    def verify_model(self):
        """验证模型是否可用"""
        if not self.config_file.exists():
            logger.error("模型配置文件不存在")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model_path = config.get("model_path")
            if not os.path.exists(model_path):
                logger.error(f"模型路径不存在: {model_path}")
                return False
            
            # 尝试加载模型
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_path, 
                trust_remote_code=True
            )
            
            logger.info("模型验证成功！")
            return True
            
        except Exception as e:
            logger.error(f"模型验证失败: {e}")
            return False
    
    def get_model_info(self):
        """获取模型信息"""
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取模型配置失败: {e}")
            return None

def main():
    """命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qwen模型管理工具")
    parser.add_argument("--action", choices=["install", "download", "verify", "info"], 
                       required=True, help="执行的操作")
    parser.add_argument("--source", choices=["huggingface", "modelscope"], 
                       default="modelscope", help="模型下载源")
    parser.add_argument("--model-dir", default="./models", help="模型存储目录")
    
    args = parser.parse_args()
    
    manager = QwenModelManager(args.model_dir)
    
    if args.action == "install":
        # 检查系统要求
        requirements = manager.check_system_requirements()
        print(f"系统要求检查: {requirements}")
        
        # 安装依赖
        success = manager.install_dependencies()
        if success:
            print("✅ 依赖安装成功")
        else:
            print("❌ 依赖安装失败")
            
    elif args.action == "download":
        if args.source == "huggingface":
            success = manager.download_model_from_huggingface()
        else:
            success = manager.download_model_from_modelscope()
        
        if success:
            print("✅ 模型下载成功")
        else:
            print("❌ 模型下载失败")
            
    elif args.action == "verify":
        if manager.verify_model():
            print("✅ 模型验证成功")
        else:
            print("❌ 模型验证失败")
            
    elif args.action == "info":
        info = manager.get_model_info()
        if info:
            print("模型信息:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print("❌ 无法获取模型信息")

if __name__ == "__main__":
    main()