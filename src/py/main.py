#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getDialog项目主执行入口
整合各步骤的执行参数，统一管理任务流程
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_encoding(input_file, output_file=None):
    """步骤1: 编码转换"""
    try:
        from steps.step01_encoding import convert_encoding
        logger.info("=== 执行编码转换 ===")
        result = convert_encoding.convert_to_utf8(input_file, output_file)
        if result:
            logger.info("✅ 编码转换完成")
        else:
            logger.error("❌ 编码转换失败")
        return result
    except Exception as e:
        logger.error(f"❌ 编码转换失败: {e}")
        return False

def extract_chapters(input_file, output_dir=None):
    """步骤2: 章节识别"""
    try:
        from steps.step02_chapter import chapter_visualizer
        logger.info("=== 执行章节识别 ===")
        result = chapter_visualizer.process_file(input_file, output_dir)
        if result:
            logger.info("✅ 章节识别完成")
        else:
            logger.error("❌ 章节识别失败")
        return result
    except Exception as e:
        logger.error(f"❌ 章节识别失败: {e}")
        return False

def extract_chapters_to_files(input_file, output_dir=None):
    """步骤2附加: 章节文件提取"""
    try:
        from steps.step02_chapter import chapter_extractor
        logger.info("=== 执行章节文件提取 ===")
        
        # 创建提取器
        extractor = chapter_extractor.ChapterExtractor()
        
        # 处理文件
        result = extractor.extract_chapters_to_files(input_file, output_dir)
        if result:
            logger.info("✅ 章节文件提取完成")
        else:
            logger.error("❌ 章节文件提取失败")
        return result
    except Exception as e:
        logger.error(f"❌ 章节文件提取失败: {e}")
        return False

def extract_characters(input_file, output_file=None):
    """步骤3: 人物名称提取"""
    try:
        from steps.step03_character import character_extractor
        logger.info("=== 执行人物名称提取 ===")
        
        # 创建提取器
        extractor = character_extractor.QwenCharacterExtractor()
        
        # 处理文件
        result = extractor.process_file(input_file, output_file)
        if result:
            logger.info("✅ 人物名称提取完成")
        else:
            logger.error("❌ 人物名称提取失败")
        return result
    except Exception as e:
        logger.error(f"❌ 人物名称提取失败: {e}")
        return False


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(
        description="getDialog - 中文小说对话提取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 环境准备
  python main.py --step setup --action install
  
  # 编码转换
  python main.py --step encoding --input data/ziyang.txt --output data/ziyang_utf8.txt
  
  # 章节识别
  python main.py --step chapter --input data/ziyang_utf8.txt --output output/
  
  # 章节文件提取
  python main.py --step extract --input data/ziyang_utf8.txt --output data/
  
  # 人物名称提取
  python main.py --step character --input data/ziyang_utf8.txt --output output/
  
  
  # 完整流程
  python main.py --step all --input data/ziyang.txt --output output/
        """
    )
    
    parser.add_argument("--step", 
                       choices=["setup", "encoding", "chapter", "extract", "character", "all"],
                       required=True,
                       help="执行步骤")
    
    parser.add_argument("--input", "-i",
                       help="输入文件路径")
    
    parser.add_argument("--output", "-o", 
                       help="输出文件/目录路径")
    
    parser.add_argument("--action",
                       choices=["install", "download", "verify", "info"],
                       help="模型管理操作")
    
    parser.add_argument("--source",
                       choices=["huggingface", "modelscope"],
                       default="modelscope",
                       help="模型下载源")
    
    parser.add_argument("--model-dir",
                       default="./models",
                       help="模型存储目录")
    
    args = parser.parse_args()
    
    
    if args.step in ["encoding", "chapter", "extract", "character", "all"] and not args.input:
        parser.error(f"步骤 {args.step} 需要指定 --input 参数")
    
    # 执行相应步骤
    success = False
    
    
    if args.step == "encoding":
        success = convert_encoding(args.input, args.output)
    
    elif args.step == "chapter":
        success = extract_chapters(args.input, args.output)
    
    elif args.step == "extract":
        success = extract_chapters_to_files(args.input, args.output)
    
    elif args.step == "character":
        success = extract_characters(args.input, args.output)
    
    elif args.step == "all":
        # 执行完整流程
        logger.info("=== 开始完整流程 ===")
        
        # 2. 编码转换
        encoding_output = args.input.replace('.txt', '_utf8.txt') if args.input else None
        if not convert_encoding(args.input, encoding_output):
            sys.exit(1)
        
        # 3. 章节识别
        if not extract_chapters(encoding_output or args.input, args.output):
            sys.exit(1)
        
        # 4. 章节文件提取
        if not extract_chapters_to_files(encoding_output or args.input, args.output):
            sys.exit(1)
        
        # 5. 人物名称提取
        if not extract_characters(encoding_output or args.input, args.output):
            sys.exit(1)
        
        logger.info("✅ 完整流程执行完成")
        success = True
    
    if success:
        logger.info("✅ 任务执行成功")
        sys.exit(0)
    else:
        logger.error("❌ 任务执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()