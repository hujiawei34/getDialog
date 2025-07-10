#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于QWEN3模型的中文小说人物名称提取工具
实现LLM驱动的人名识别和别名关联功能
"""

import json
import re
import os
import logging
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import lru_cache


# 导入项目常量
from utils.constants import PROJECT_ROOT, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Character:
    """人物信息数据结构"""
    name: str

@dataclass
class DialogueEntry:
    """对话条目数据结构"""
    dialog_id: str
    name: str
    type: str  # "说" or "想"
    dialog_content: str

@dataclass
class CharacterExtractionResult:
    """人物提取结果"""
    metadata: Dict
    characters: List[Character]
    dialogues: List[DialogueEntry]

class QwenCharacterExtractor:
    """基于QWEN3模型的人物名称提取器"""
    
    def __init__(self, model_service_url: str = "http://localhost:19100"):
        """初始化提取器
        
        Args:
            model_service_url: 模型服务地址
        """
        self.model_service_url = model_service_url.rstrip('/')
        self.api_base = f"{self.model_service_url}/api/v1"
        
    def _call_model_service(self, message: str) -> Optional[str]:
        """调用模型服务
        
        Args:
            message: 要发送的消息
            
        Returns:
            模型响应文本，如果失败返回None
        """
        try:
            url = f"{self.api_base}/chat"
            payload = {
                "message": message,
                "history": []
            }
            
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                return result.get("response", "")
            else:
                logger.error(f"模型服务调用失败: {result.get('error', '未知错误')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"调用模型服务时发生网络错误: {e}")
            return None
        except Exception as e:
            logger.error(f"调用模型服务时发生错误: {e}")
            return None
    
    def _extract_characters_and_dialogues(self, text: str) -> Tuple[List[str], List[DialogueEntry]]:
        """从文本中提取人物和对话
        
        Args:
            text: 要分析的文本
            
        Returns:
            (人物列表, 对话列表)
        """
        # 构建提示词
        prompt = f"""
请仔细分析以下中文小说文本，提取其中的人物名称和所有对话内容。

要求：
1. 识别文本中出现的所有人物名称
2. 提取所有对话内容，包括：
   - 直接说话的内容（用引号包围的）
   - 心理活动/想法的内容
3. 为每个对话标注说话人
4. 区分是"说"还是"想"

请按照以下JSON格式输出：
{{
    "characters": ["人物1", "人物2", "人物3"],
    "dialogues": [
        {{
            "name": "说话人",
            "type": "说",
            "dialog_content": "说话内容"
        }},
        {{
            "name": "说话人",
            "type": "想",
            "dialog_content": "心理活动内容"
        }}
    ]
}}

文本内容：
{text}
"""
        
        # 调用模型服务
        response = self._call_model_service(prompt)
        if not response:
            return [], []
            
        # 解析响应
        try:
            # 尝试从响应中提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                characters = data.get("characters", [])
                dialogues_data = data.get("dialogues", [])
                
                # 转换为DialogueEntry对象
                dialogues = []
                for i, dialogue in enumerate(dialogues_data):
                    dialog_id = f"{i+1:010d}"  # 10位数字序号
                    dialogues.append(DialogueEntry(
                        dialog_id=dialog_id,
                        name=dialogue.get("name", "未知"),
                        type=dialogue.get("type", "说"),
                        dialog_content=dialogue.get("dialog_content", "")
                    ))
                
                return characters, dialogues
                
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON响应失败: {e}")
            logger.error(f"响应内容: {response}")
        except Exception as e:
            logger.error(f"处理响应时发生错误: {e}")
            
        return [], []
    
    def process_file(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """处理单个文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则使用默认路径
            
        Returns:
            是否成功
        """
        try:
            # 读取输入文件
            input_path = Path(input_file)
            if not input_path.exists():
                logger.error(f"输入文件不存在: {input_file}")
                return False
                
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            logger.info(f"开始处理文件: {input_file}")
            
            # 提取人物和对话
            characters, dialogues = self._extract_characters_and_dialogues(text)
            
            if not characters and not dialogues:
                logger.warning("未提取到任何人物或对话")
                return False
                
            logger.info(f"提取到 {len(characters)} 个人物，{len(dialogues)} 条对话")
            
            # 准备输出目录和文件路径
            if output_file:
                output_path = Path(output_file)
                # 如果输出路径是目录，则在该目录下生成文件名
                if output_path.is_dir() or str(output_path).endswith('/'):
                    output_path = output_path / f"characters_{input_path.stem}.json"
            else:
                output_path = Path(OUTPUT_DIR) / f"characters_{input_path.stem}.json"
                
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 构建输出数据
            result_data = {
                "metadata": {
                    "source_file": str(input_path),
                    "processed_time": datetime.now().isoformat(),
                    "character_count": len(characters),
                    "dialogue_count": len(dialogues)
                },
                "characters": characters,
                "dialogues": [asdict(dialogue) for dialogue in dialogues]
            }
            
            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"结果已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"处理文件时发生错误: {e}")
            return False
    
    def process_chapter_file(self, chapter_file: str) -> bool:
        """处理指定的章节文件
        
        Args:
            chapter_file: 章节文件路径
            
        Returns:
            是否成功
        """
        chapter_path = Path(chapter_file)
        if not chapter_path.exists():
            logger.error(f"章节文件不存在: {chapter_file}")
            return False
            
        # 构建输出文件名
        output_file = Path(OUTPUT_DIR) / f"dialogues_{chapter_path.stem}.json"
        
        return self.process_file(chapter_file, str(output_file))


def main():
    """主函数，用于测试和独立运行"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python character_extractor.py <输入文件路径> [输出文件路径]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 创建提取器
    extractor = QwenCharacterExtractor()
    
    # 处理文件
    success = extractor.process_file(input_file, output_file)
    
    if success:
        print("✅ 人物和对话提取完成")
    else:
        print("❌ 人物和对话提取失败")
        sys.exit(1)


if __name__ == "__main__":
    main()