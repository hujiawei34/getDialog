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
            from utils.constants import PROJECT_ROOT
            
            logger.info(f"从ModelScope下载模型: {model_name}")
            
            model_dir = snapshot_download(
                model_name, 
                cache_dir=str(self.model_dir)
            )
            
            # 转换为相对于PROJECT_ROOT的路径
            model_path = Path(model_dir)
            try:
                relative_path = model_path.relative_to(PROJECT_ROOT)
                model_path_str = str(relative_path)
            except ValueError:
                # 如果无法转换为相对路径，使用绝对路径
                model_path_str = str(model_path)
            
            # 保存配置
            config = {
                "model_name": model_name,
                "model_path": model_path_str,
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
            
            # 如果是相对路径，基于PROJECT_ROOT解析
            from utils.constants import PROJECT_ROOT
            if not os.path.isabs(model_path):
                model_path = str(PROJECT_ROOT / model_path)
            
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

# 注意：此模块不支持直接执行，请通过main.py调用
# 如需执行模型管理操作，请使用：
# python main.py --step model --action [install|download|verify|info]