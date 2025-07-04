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
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import lru_cache

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 导入项目常量
from utils.constants import PROJECT_ROOT, MODELS_DIR, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Character:
    """人物信息数据结构"""
    name: str
    aliases: List[str]
    gender: Optional[str] = None
    role_type: str = "unknown"  # main_character, supporting_character, minor_character
    importance_score: float = 0.0
    first_appearance: Optional[Dict] = None
    statistics: Optional[Dict] = None
    attributes: Optional[Dict] = None
    relationships: Optional[List[Dict]] = None

@dataclass
class CharacterExtractionResult:
    """人物提取结果"""
    metadata: Dict
    characters: List[Character]

class QwenCharacterExtractor:
    """基于QWEN3模型的人物名称提取器"""
    
    def __init__(self, model_dir: str = None):
        """
        初始化人物提取器
        
        Args:
            model_dir: 模型目录路径
        """
        self.model_dir = Path(model_dir) if model_dir else MODELS_DIR
        self.model = None
        self.tokenizer = None
        self.model_config = None
        
        # 加载项目配置
        self.project_config = self._load_project_config()
        
        # 设置设备
        self.device = self._setup_device()
        
        # 加载模型配置
        self._load_model_config()
        
        # 中文姓氏缓存
        self.chinese_surnames = self._load_chinese_surnames()
        
        # 人物名称缓存
        self.character_cache = {}
    
    def _load_project_config(self):
        """加载项目配置文件"""
        config_file = PROJECT_ROOT / "config.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("已加载项目配置文件")
                return config
        except Exception as e:
            logger.warning(f"无法加载项目配置文件: {e}，使用默认配置")
            return {
                "gpu": {"device_id": 0, "enable_cuda": True},
                "model": {"max_length": 512, "temperature": 0.7},
                "extraction": {"text_chunk_size": 2000}
            }
    
    def _setup_device(self):
        """根据配置设置设备"""
        gpu_config = self.project_config.get("gpu", {})
        
        if not gpu_config.get("enable_cuda", True) or not torch.cuda.is_available():
            logger.info("使用CPU运行")
            return "cpu"
        
        device_id = gpu_config.get("device_id", 0)
        if torch.cuda.device_count() <= device_id:
            logger.warning(f"指定的GPU {device_id} 不存在，使用GPU 0")
            device_id = 0
        
        device = f"cuda:{device_id}"
        logger.info(f"使用GPU设备: {device}")
        
        # 检查GPU内存
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(device_id).total_memory / (1024**3)
            gpu_memory_allocated = torch.cuda.memory_allocated(device_id) / (1024**3)
            gpu_memory_free = gpu_memory - gpu_memory_allocated
            logger.info(f"GPU {device_id} 内存: {gpu_memory_free:.1f}GB 可用 / {gpu_memory:.1f}GB 总计")
        
        return device
        
    def _load_model_config(self):
        """加载模型配置"""
        config_file = self.model_dir / "model_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.model_config = json.load(f)
                logger.info(f"已加载模型配置: {self.model_config.get('model_name', 'unknown')}")
        else:
            logger.warning("模型配置文件不存在，请先下载模型")
    
    def _load_chinese_surnames(self) -> Set[str]:
        """加载中文姓氏列表"""
        # 常见中文姓氏
        common_surnames = {
            "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
            "徐", "孙", "朱", "马", "胡", "郭", "林", "何", "高", "梁",
            "郑", "罗", "宋", "谢", "唐", "韩", "曹", "许", "邓", "萧",
            "冯", "曾", "程", "蔡", "彭", "潘", "袁", "于", "董", "余",
            "苏", "叶", "吕", "魏", "蒋", "田", "杜", "丁", "沈", "姜",
            "范", "江", "傅", "钟", "卢", "汪", "戴", "崔", "任", "陆",
            "廖", "姚", "方", "金", "邱", "夏", "谭", "韦", "贾", "邹",
            "石", "熊", "孟", "秦", "阎", "薛", "侯", "雷", "白", "龙",
            "段", "郝", "孔", "邵", "史", "毛", "常", "万", "顾", "赖",
            "武", "康", "贺", "严", "尹", "钱", "施", "牛", "洪", "龚",
            "莫", "欧", "司徒", "司马", "上官", "欧阳", "太史", "端木",
            "公孙", "轩辕", "令狐", "钟离", "宇文", "长孙", "慕容", "鲜于",
            "闾丘", "司空", "亓官", "司寇", "仉督", "子车", "颛孙", "端木"
        }
        return common_surnames
    
    def load_model(self):
        """加载QWEN模型"""
        if self.model is not None:
            return True
            
        if not self.model_config:
            logger.error("模型配置未加载")
            return False
            
        try:
            model_path = self.model_config.get("model_path")
            
            # 处理相对路径
            if not os.path.isabs(model_path):
                model_path = str(PROJECT_ROOT / model_path)
            
            logger.info(f"正在加载模型: {model_path}")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # 根据设备类型设置模型参数
            model_kwargs = {
                "trust_remote_code": True,
            }
            
            if self.device != "cpu":
                # GPU模式
                device_id = int(self.device.split(':')[1]) if ':' in self.device else 0
                model_kwargs.update({
                    "torch_dtype": torch.float16,
                    "device_map": {
                        "": device_id  # 指定具体的GPU设备
                    }
                })
            else:
                # CPU模式
                model_kwargs.update({
                    "torch_dtype": torch.float32,
                    "device_map": None
                })
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                **model_kwargs
            )
            
            # 如果是CPU模式，手动移动到设备
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info(f"模型已加载到设备: {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = None) -> str:
        """使用QWEN模型生成回应"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return ""
        
        # 从配置获取生成参数
        model_config = self.project_config.get("model", {})
        if max_length is None:
            max_length = model_config.get("max_length", 512)
        
        try:
            # 编码输入
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # 生成回应
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs["input_ids"].shape[1] + max_length,
                    temperature=model_config.get("temperature", 0.7),
                    do_sample=model_config.get("do_sample", True),
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码输出
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"生成回应失败: {e}")
            return ""
    
    def extract_names_with_llm(self, text: str) -> List[str]:
        """使用QWEN3模型提取人物姓名"""
        extraction_config = self.project_config.get("extraction", {})
        chunk_size = extraction_config.get("text_chunk_size", 2000)
        
        if len(text) > chunk_size:
            text = text[:chunk_size]  # 限制文本长度
        
        prompt = f"""请从以下中文小说文本中提取所有人物姓名。

要求：
1. 只提取真实的人物姓名，不要提取代词、称谓或地名
2. 每行返回一个人名，不要添加其他内容
3. 如果同一人物有多个称呼，只返回最正式的姓名
4. 不要返回"无"或"没有"等词语

文本：
{text}

人物姓名："""
        
        # 调用模型生成
        response = self.generate_response(prompt)
        names = self.parse_name_list(response)
        
        # 过滤和验证人名
        filtered_names = []
        for name in names:
            if self.is_valid_name(name):
                filtered_names.append(name)
        
        return filtered_names
    
    def identify_aliases_with_llm(self, text: str, main_names: List[str]) -> Dict[str, List[str]]:
        """使用LLM识别人物别名和称谓"""
        aliases_map = {}
        
        for name in main_names:
            if len(text) > 2000:
                # 如果文本太长，搜索包含该人名的上下文
                context = self.extract_context_for_name(text, name)
            else:
                context = text
            
            prompt = f"""在以下文本中，找出"{name}"这个人物的所有别名、称谓和不同叫法。

文本：
{context}

请列出"{name}"的所有别名：
- 包括：昵称、尊称、简称、外号等
- 格式：每行一个别名
- 如果没有别名，回答"无"

"{name}"的别名："""
            
            response = self.generate_response(prompt)
            aliases = self.parse_alias_list(response, name)
            aliases_map[name] = aliases
        
        return aliases_map
    
    def extract_context_for_name(self, text: str, name: str, context_size: int = None) -> str:
        """为指定人名提取上下文"""
        extraction_config = self.project_config.get("extraction", {})
        if context_size is None:
            context_size = extraction_config.get("context_window", 1000)
            
        contexts = []
        sentences = text.split('。')
        
        for i, sentence in enumerate(sentences):
            if name in sentence:
                # 提取前后各几句作为上下文
                start = max(0, i - 2)
                end = min(len(sentences), i + 3)
                context = '。'.join(sentences[start:end])
                contexts.append(context)
        
        # 合并上下文，限制长度
        full_context = '。'.join(contexts)
        if len(full_context) > context_size:
            full_context = full_context[:context_size]
        
        return full_context
    
    def parse_name_list(self, response: str) -> List[str]:
        """解析模型返回的人名列表"""
        names = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 移除序号和标点
            line = re.sub(r'^\d+[.、]?\s*', '', line)
            line = re.sub(r'^[•·-]\s*', '', line)
            line = line.strip('.,;:：，。；')
            
            if line and len(line) <= 10:  # 人名通常不超过10个字符
                names.append(line)
        
        return list(set(names))  # 去重
    
    def parse_alias_list(self, response: str, main_name: str) -> List[str]:
        """解析别名列表"""
        aliases = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line == "无" or line == "没有":
                continue
            
            # 移除序号和标点
            line = re.sub(r'^\d+[.、]?\s*', '', line)
            line = re.sub(r'^[•·-]\s*', '', line)
            line = line.strip('.,;:：，。；')
            
            if line and line != main_name and len(line) <= 10:
                aliases.append(line)
        
        return list(set(aliases))  # 去重
    
    @lru_cache(maxsize=1000)
    def is_valid_name(self, name: str) -> bool:
        """验证是否为有效的人名"""
        extraction_config = self.project_config.get("extraction", {})
        min_length = extraction_config.get("min_name_length", 2)
        max_length = extraction_config.get("max_name_length", 10)
        
        if not name or len(name) < min_length or len(name) > max_length:
            return False
        
        # 过滤明显不是人名的词汇
        invalid_words = {
            "他", "她", "它", "我", "你", "您", "大家", "众人", "所有人",
            "这个", "那个", "这里", "那里", "地方", "时候", "东西",
            "什么", "怎么", "为什么", "哪里", "怎样", "多少",
            "第一", "第二", "第三", "一个", "两个", "三个",
            "天下", "世界", "国家", "朝廷", "皇帝", "官府"
        }
        
        if name in invalid_words:
            return False
        
        # 检查是否包含中文姓氏
        if any(name.startswith(surname) for surname in self.chinese_surnames):
            return True
        
        # 检查是否为纯中文
        if all('\u4e00' <= char <= '\u9fff' for char in name):
            return True
        
        return False
    
    def extract_characters_from_text(self, text: str, source_info: Dict = None) -> CharacterExtractionResult:
        """从文本中提取人物信息"""
        logger.info("开始提取人物信息...")
        
        # 1. 提取人物名称
        names = self.extract_names_with_llm(text)
        logger.info(f"提取到 {len(names)} 个人物名称")
        
        # 2. 识别别名
        # aliases_map = self.identify_aliases_with_llm(text, names)
        # logger.info("完成别名识别")
        
        # 3. 统计人物出现频次
        character_stats = self.calculate_character_statistics(text, names)
        
        # 4. 创建人物对象
        characters = []
        for name in names:
            character = Character(
                name=name,
                role_type=self.classify_character_role(character_stats.get(name, {})),
                importance_score=character_stats.get(name, {}).get('importance_score', 0.0),
                statistics=character_stats.get(name, {}),
                first_appearance=self.find_first_appearance(text, name),
                relationships=[]
            )
            characters.append(character)
        
        
        # 6. 生成统计信息
        
        # 7. 创建结果对象
        metadata = {
            "source_file": source_info.get("file_path", "unknown") if source_info else "unknown",
            "extraction_time": datetime.now().isoformat(),
            "total_characters": len(characters),
            "main_characters": len([c for c in characters if c.role_type == "main_character"]),
            "supporting_characters": len([c for c in characters if c.role_type == "supporting_character"]),
            "minor_characters": len([c for c in characters if c.role_type == "minor_character"])
        }
        
        result = CharacterExtractionResult(
            metadata=metadata,
            characters=characters,
        )
        
        logger.info("人物信息提取完成")
        return result
    
    def calculate_character_statistics(self, text: str, names: List[str]) -> Dict:
        """计算人物出现统计"""
        stats = {}
        
        for name in names:
            # 计算所有称谓的出现次数
            all_names = [name]
            total_count = 0
            
            for n in all_names:
                total_count += text.count(n)
            
            # 计算重要性分数（基于出现频次）
            importance_score = min(100.0, total_count * 2.0)
            
            stats[name] = {
                "total_appearances": total_count,
                "importance_score": importance_score,
                "main_name": name
            }
        
        return stats
    
    def classify_character_role(self, stats: Dict) -> str:
        """根据统计信息分类角色类型"""
        importance_score = stats.get("importance_score", 0.0)
        
        if importance_score >= 50:
            return "main_character"
        elif importance_score >= 20:
            return "supporting_character"
        else:
            return "minor_character"
    
    def find_first_appearance(self, text: str, name: str) -> Optional[Dict]:
        """查找人物首次出现的位置"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if name in line:
                return {
                    "line": i + 1,
                    "context": line.strip()[:100]
                }
        return None
    
    
    def generate_statistics(self, characters: List[Character]) -> Dict:
        """生成整体统计信息"""
        if not characters:
            return {}
        
        # 计算最活跃的人物
        most_active = max(characters, key=lambda c: c.importance_score)
        
        # 计算平均关系数
        
        return {
            "most_connected_character": most_active.name,
        }
    
    def save_results(self, result: CharacterExtractionResult, output_path: str):
        """保存提取结果"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为可序列化的格式
        serializable_data = {
            "metadata": result.metadata,
            "characters": [asdict(char) for char in result.characters],
            "relationships": result.relationships,
            "statistics": result.statistics
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {output_path}")
    
    def process_file(self, input_file: str, output_file: str = None) -> bool:
        """处理单个文件"""
        try:
            # 处理相对路径
            input_path = Path(input_file)
            if not input_path.is_absolute():
                input_path = PROJECT_ROOT / input_file
            
            # 读取输入文件
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 提取人物信息
            source_info = {"file_path": input_file}
            result = self.extract_characters_from_text(text, source_info)
            
            # 保存结果
            if output_file is None:
                output_file = str(OUTPUT_DIR / f"characters_{Path(input_file).stem}.json")
            else:
                # 处理相对路径的输出文件
                output_path = Path(output_file)
                if not output_path.is_absolute():
                    if output_path.is_dir() or output_file.endswith('/'):
                        # 如果输出是目录，生成默认文件名
                        output_dir = PROJECT_ROOT / output_file
                        output_dir.mkdir(parents=True, exist_ok=True)
                        output_file = str(output_dir / f"characters_{Path(input_file).stem}.json")
                    else:
                        # 如果输出是文件，基于项目根目录解析
                        output_file = str(PROJECT_ROOT / output_file)
            
            self.save_results(result, output_file)
            
            return True
            
        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            return False
