#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3思考模式人物名称提取器
使用思考模式分析中文古代小说文本，提取人物名称并记录推理过程
"""

import json
import re
import sys
import torch
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from steps.step03_character.character_extractor import QwenCharacterExtractor
from utils.log_util import log_info, log_debug, log_warning, log_error


class QwenThinkExtractor(QwenCharacterExtractor):
    """
    基于Qwen3思考模式的人物名称提取器
    继承原有功能，增加思考模式推理
    """
    
    def __init__(self, model_dir: str = None):
        super().__init__(model_dir)
        self.think_mode_enabled = True
        self.thinking_logs = []
    
    def generate_response_with_thinking(self, prompt: str, max_length: int = None) -> Dict[str, str]:
        """
        使用思考模式生成回应，分离思考过程和最终答案
        
        Returns:
            Dict包含 'thinking' 和 'answer' 两部分
        """
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return {"thinking": "", "answer": ""}
        
        model_config = self.project_config.get("model", {})
        if max_length is None:
            max_length = model_config.get("max_length", 1024)  # 思考模式需要更长输出
        
        try:
            # 编码输入
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            log_info(f"prompt:{prompt}")
            # 生成回应
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs["input_ids"].shape[1] + max_length,
                    temperature=model_config.get("temperature", 0.7),
                    do_sample=model_config.get("do_sample", True),
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码输出
            full_response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            ).strip()
            log_info(f"response:{full_response}",)
            # 分离思考过程和最终答案
            thinking_part, answer_part = self.parse_thinking_response(full_response)
            
            return {
                "thinking": thinking_part,
                "answer": answer_part,
                "full_response": full_response
            }
            
        except Exception as e:
            log_error(f"思考模式生成失败: {e}")
            return {"thinking": "", "answer": "", "full_response": ""}
    
    def parse_thinking_response(self, response: str) -> tuple[str, str]:
        """
        解析模型输出，分离思考过程和最终答案
        """
        # 查找思考标记
        thinking_markers = ["思考过程：", "分析：", "让我分析", "首先", "步骤", "推理："]
        answer_markers = ["最终答案：", "结论：", "人物名称：", "提取结果：", "答案："]
        
        thinking_part = ""
        answer_part = ""
        
        # 尝试分离思考和答案部分
        for marker in answer_markers:
            if marker in response:
                parts = response.split(marker, 1)
                if len(parts) == 2:
                    thinking_part = parts[0].strip()
                    answer_part = parts[1].strip()
                    break
        
        # 如果没有找到明确分隔符，使用启发式方法
        if not answer_part:
            lines = response.split('\n')
            thinking_lines = []
            answer_lines = []
            in_answer_section = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 判断是否进入答案部分
                if any(marker in line.lower() for marker in ["人物", "名称", "角色", "登场"]):
                    in_answer_section = True
                
                if in_answer_section:
                    answer_lines.append(line)
                else:
                    thinking_lines.append(line)
            
            thinking_part = '\n'.join(thinking_lines)
            answer_part = '\n'.join(answer_lines)
        
        return thinking_part, answer_part
    
    def extract_names_with_thinking(self, text: str) -> Dict[str, any]:
        """
        使用思考模式提取人物姓名
        """
        log_info("开始使用思考模式分析文本")
        
        # 限制文本长度
        extraction_config = self.project_config.get("extraction", {})
        chunk_size = extraction_config.get("text_chunk_size", 1500)
        
        if len(text) > chunk_size:
            text = text[:chunk_size]
            log_debug(f"文本过长，截取前{chunk_size}字符进行分析")
        
        # 设计思考模式的提示词
        prompt = f"""你是一个专业的中文古代小说分析专家。请仔细分析以下文本，提取所有人物姓名。

请按以下步骤思考：

1. 首先分析文本的基本结构和写作风格
2. 识别对话、叙述和描写的不同部分
3. 查找人物出现的线索（对话标识、称谓、动作描述等）
4. 区分真实人物姓名和代词、称谓
5. 验证提取的名称是否合理

思考过程：
[请详细记录你的分析思路]

最终答案：
[列出提取的人物姓名，每行一个]

文本内容：
{text}

请开始分析："""
        
        # 调用思考模式生成
        response_dict = self.generate_response_with_thinking(prompt, max_length=1024)
        
        # 记录思考过程
        thinking = response_dict.get("thinking", "")
        answer = response_dict.get("answer", "")
        full_response = response_dict.get("full_response", "")
        
        log_info("=== Qwen3 思考过程 ===")
        log_info(thinking if thinking else "未检测到独立的思考过程部分")
        log_info("=== 思考过程结束 ===")
        
        log_info("=== Qwen3 最终答案 ===")
        log_info(answer if answer else "未检测到独立的答案部分")
        log_info("=== 最终答案结束 ===")
        
        # 如果分离失败，记录完整回应
        if not thinking and not answer:
            log_warning("无法分离思考过程和答案，记录完整回应：")
            log_info(f"完整回应：\n{full_response}")
        
        # 解析人物名称
        names = self.parse_name_list(answer if answer else full_response)
        
        # 记录思考日志
        thinking_log = {
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "thinking_process": thinking,
            "final_answer": answer,
            "full_response": full_response,
            "extracted_names": names,
            "name_count": len(names)
        }
        self.thinking_logs.append(thinking_log)
        
        # 过滤和验证人名
        filtered_names = []
        log_info("开始验证提取的人物名称：")
        for name in names:
            is_valid = self.is_valid_name(name)
            log_debug(f"验证 '{name}': {'✓' if is_valid else '✗'}")
            if is_valid:
                filtered_names.append(name)
        
        log_info(f"最终确认的人物名称({len(filtered_names)}个): {filtered_names}")
        
        return {
            "names": filtered_names,
            "thinking_process": thinking,
            "raw_answer": answer,
            "full_response": full_response,
            "analysis_log": thinking_log
        }
    
    def analyze_character_relationships_with_thinking(self, text: str, names: List[str]) -> Dict[str, any]:
        """
        使用思考模式分析人物关系
        """
        if not names:
            return {"relationships": [], "thinking_process": ""}
        
        log_info("开始分析人物关系")
        
        # 构建关系分析提示词
        names_str = "、".join(names)
        prompt = f"""请分析以下文本中人物之间的关系。

已识别的人物：{names_str}

请按以下步骤思考：
1. 分析文本中人物之间的互动情况
2. 识别亲属关系、社会关系、情感关系
3. 注意称谓和对话中体现的关系线索
4. 总结主要的人物关系网络

思考过程：
[详细分析人物关系的推理过程]

最终答案：
[格式：人物A - 关系类型 - 人物B，每行一个关系]

文本内容：
{text[:1000]}

请开始分析："""
        
        response_dict = self.generate_response_with_thinking(prompt)
        thinking = response_dict.get("thinking", "")
        answer = response_dict.get("answer", "")
        
        log_info("=== 人物关系分析思考过程 ===")
        log_info(thinking)
        log_info("=== 人物关系分析结果 ===")
        log_info(answer)
        
        return {
            "relationships": self.parse_relationships(answer),
            "thinking_process": thinking,
            "raw_answer": answer
        }
    
    def parse_relationships(self, response: str) -> List[Dict]:
        """解析关系分析结果"""
        relationships = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # 尝试解析关系格式：A - 关系 - B
            if ' - ' in line:
                parts = line.split(' - ')
                if len(parts) >= 3:
                    relationships.append({
                        "person1": parts[0].strip(),
                        "relationship": parts[1].strip(),
                        "person2": parts[2].strip()
                    })
        
        return relationships
    
    def process_chapter_file(self, file_path: str) -> Dict[str, any]:
        """
        处理指定的章节文件
        """
        file_path = Path(file_path)
        if not file_path.exists():
            log_error(f"文件不存在: {file_path}")
            return {}
        
        log_info(f"开始处理章节文件: {file_path}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            log_info(f"文件读取成功，内容长度: {len(content)} 字符")
            
            # 提取人物名称
            name_result = self.extract_names_with_thinking(content)
            names = name_result["names"]
            
            # 分析人物关系
            relationship_result = self.analyze_character_relationships_with_thinking(content, names)
            
            # 生成分析报告
            report = {
                "file_info": {
                    "path": str(file_path),
                    "size": len(content),
                    "analysis_time": datetime.now().isoformat()
                },
                "character_extraction": name_result,
                "relationship_analysis": relationship_result,
                "summary": {
                    "total_characters": len(names),
                    "main_characters": [name for name in names if len(name) <= 3],  # 简单判断主要人物
                    "character_list": names
                }
            }
            
            log_info("=== 章节分析完成 ===")
            log_info(f"提取人物数量: {len(names)}")
            log_info(f"人物列表: {names}")
            
            return report
            
        except Exception as e:
            log_error(f"处理文件失败: {e}")
            return {}
    
    def save_analysis_report(self, report: Dict, output_path: str = None):
        """保存分析报告"""
        if not report:
            log_warning("没有分析报告可保存")
            return
        
        if output_path is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"qwen_think_analysis_{timestamp}.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            log_info(f"分析报告已保存: {output_path}")
            
        except Exception as e:
            log_error(f"保存报告失败: {e}")


def main():
    """
    主函数：处理指定的章节文件
    """
    log_info("启动Qwen3思考模式人物提取器")
    
    # 目标文件路径
    target_file = "/data/hjw/github/getDialog/data/ziyang/第1卷/第1章.txt"
    
    try:
        # 创建提取器实例
        extractor = QwenThinkExtractor()
        
        # 处理文件
        report = extractor.process_chapter_file(target_file)
        
        if report:
            # 保存分析报告
            extractor.save_analysis_report(report)
            
            log_info("=== 处理完成 ===")
            log_info("详细分析过程已记录在日志中")
        else:
            log_error("文件处理失败")
            
    except Exception as e:
        log_error(f"程序执行失败: {e}")


if __name__ == "__main__":
    main()