#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人物和对话提取功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "py"))

from steps.step03_character.character_extractor import QwenCharacterExtractor
from utils.constants import OUTPUT_DIR

def test_character_extraction():
    """测试人物和对话提取"""
    
    # 输入文件路径
    input_file = "/data/hjw/github/useModel/getDialog/data/ziyang/第1卷/第1章.txt"
    
    # 检查输入文件是否存在
    if not Path(input_file).exists():
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    # 创建提取器
    extractor = QwenCharacterExtractor()
    
    # 处理文件
    print("开始测试人物和对话提取...")
    success = extractor.process_chapter_file(input_file)
    
    if success:
        print("✅ 测试成功！")
        # 显示输出文件位置
        output_file = Path(OUTPUT_DIR) / f"dialogues_第1章.json"
        print(f"输出文件: {output_file}")
        return True
    else:
        print("❌ 测试失败！")
        return False

if __name__ == "__main__":
    test_character_extraction()