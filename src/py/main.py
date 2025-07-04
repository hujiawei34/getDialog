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

def setup_environment():
    """设置项目环境"""
    try:
        from steps.step03_character import prepare_env4qwen
        logger.info("=== 环境准备 ===")
        prepare_env4qwen.check_system()
        prepare_env4qwen.install_dependencies()
        logger.info("✅ 环境准备完成")
        return True
    except Exception as e:
        logger.error(f"❌ 环境准备失败: {e}")
        return False

def convert_encoding(input_file, output_file=None):
    """步骤1: 编码转换"""
    try:
        from steps.step01_encoding import convert_encoding
        logger.info("=== 执行编码转换 ===")
        result = convert_encoding.convert_file_encoding(input_file, output_file)
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

def setup_qwen_model(action, source="modelscope", model_dir=None):
    """步骤3: Qwen模型管理"""
    try:
        from steps.step03_character import setup_qwen_model
        from utils.constants import MODELS_DIR
        
        # 如果没有指定model_dir，使用constants中定义的MODELS_DIR
        if model_dir is None:
            model_dir = str(MODELS_DIR)
        
        logger.info(f"=== 执行Qwen模型管理: {action} ===")
        
        manager = setup_qwen_model.QwenModelManager(model_dir)
        
        if action == "install":
            return setup_environment()
        elif action == "download":
            if source == "huggingface":
                return manager.download_model_from_huggingface()
            else:
                return manager.download_model_from_modelscope()
        elif action == "verify":
            return manager.verify_model()
        elif action == "info":
            info = manager.get_model_info()
            if info:
                logger.info("模型信息:")
                import json
                logger.info(json.dumps(info, indent=2, ensure_ascii=False))
                return True
            else:
                logger.error("❌ 无法获取模型信息")
                return False
        else:
            logger.error(f"❌ 不支持的操作: {action}")
            return False
    except Exception as e:
        logger.error(f"❌ Qwen模型管理失败: {e}")
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
  
  # Qwen模型管理
  python main.py --step model --action download --source modelscope
  python main.py --step model --action verify
  python main.py --step model --action info
  
  # 完整流程
  python main.py --step all --input data/ziyang.txt --output output/
        """
    )
    
    parser.add_argument("--step", 
                       choices=["setup", "encoding", "chapter", "model", "all"],
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
    
    # 验证参数
    if args.step == "setup" and not args.action:
        args.action = "install"
    
    if args.step in ["encoding", "chapter", "all"] and not args.input:
        parser.error(f"步骤 {args.step} 需要指定 --input 参数")
    
    if args.step == "model" and not args.action:
        parser.error("步骤 model 需要指定 --action 参数")
    
    # 执行相应步骤
    success = False
    
    if args.step == "setup":
        success = setup_environment()
    
    elif args.step == "encoding":
        success = convert_encoding(args.input, args.output)
    
    elif args.step == "chapter":
        success = extract_chapters(args.input, args.output)
    
    elif args.step == "model":
        # 如果用户指定了model_dir且不是默认值，则使用用户指定的值
        model_dir = None if args.model_dir == "./models" else args.model_dir
        success = setup_qwen_model(args.action, args.source, model_dir)
    
    elif args.step == "all":
        # 执行完整流程
        logger.info("=== 开始完整流程 ===")
        
        # 1. 环境准备
        if not setup_environment():
            sys.exit(1)
        
        # 2. 编码转换
        encoding_output = args.input.replace('.txt', '_utf8.txt') if args.input else None
        if not convert_encoding(args.input, encoding_output):
            sys.exit(1)
        
        # 3. 章节识别
        if not extract_chapters(encoding_output or args.input, args.output):
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