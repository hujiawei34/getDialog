#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目常量定义
"""

from pathlib import Path

# 项目根目录 - 从当前文件向上4级
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 重要路径
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
MODELS_DIR = PROJECT_ROOT / "models"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# 确保目录存在
OUTPUT_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)