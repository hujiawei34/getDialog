# 人物名称提取实现文档

## 概述

人物名称提取是小说分析的核心环节，目标是从文本中准确识别所有出现的人物，建立人物档案，并分析人物关系和重要程度。

## 功能需求

### 核心功能
1. **人物名称识别** - 从文本中提取所有人物姓名
2. **别名关联** - 识别同一人物的不同称谓和别名
3. **角色分类** - 区分主角、配角、群演等角色类型
4. **出场统计** - 统计人物在各章节的出现频次
5. **关系分析** - 分析人物间的互动关系

### 扩展功能
1. **称谓识别** - 识别"师父"、"夫人"等称谓
2. **人物属性** - 提取人物的性别、身份、职业等信息
3. **情感分析** - 分析人物对话的情感倾向
4. **关系图谱** - 构建人物关系网络图

## 技术实现方案

### 1. 基于Qwen3-8B模型的人名识别策略

#### LLM驱动的人名提取

```python
def extract_names_with_llm(self, text: str) -> List[str]:
    """使用Qwen3-8B模型提取人物姓名"""
    prompt = f"""请从以下中文小说文本中提取所有人物姓名。
    
要求：
1. 只提取真实的人物姓名，不要提取代词、称谓或地名
2. 每行返回一个人名，不要添加其他内容
3. 如果同一人物有多个称呼，只返回最正式的姓名

文本：
{text}

人物姓名："""
    
    # 调用模型生成
    response = self.generate_response(prompt)
    names = self.parse_name_list(response)
    return names
```

#### 基于提示工程的别名识别

```python
def identify_aliases_with_llm(self, text: str, main_names: List[str]) -> Dict[str, List[str]]:
    """使用LLM识别人物别名和称谓"""
    aliases_map = {}
    
    for name in main_names:
        prompt = f"""在以下文本中，找出"{name}"这个人物的所有别名、称谓和不同叫法。

文本：
{text}

请列出"{name}"的所有别名：
- 包括：昵称、尊称、简称、外号等
- 格式：每行一个别名
- 如果没有别名，回答"无"

"{name}"的别名："""
        
        response = self.generate_response(prompt)
        aliases = self.parse_alias_list(response, name)
        aliases_map[name] = aliases
    
    return aliases_map
```

## 输出格式设计

### JSON 输出示例

```json
{
    "metadata": {
        "source_file": "data/ziyang.txt",
        "extraction_time": "2024-07-02T18:00:00Z",
        "total_characters": 45,
        "main_characters": 8,
        "supporting_characters": 15,
        "minor_characters": 22
    },
    "characters": [
        {
            "name": "莫凡",
            "aliases": ["小凡", "凡哥", "莫师兄"],
            "gender": "male",
            "role_type": "main_character",
            "importance_score": 95.5,
            "first_appearance": {
                "chapter": "第一章 新婚大喜",
                "line": 15
            },
            "statistics": {
                "total_appearances": 156,
                "dialogue_count": 89,
                "chapters_appeared": 45,
                "average_per_chapter": 3.47
            },
            "attributes": {
                "profession": "scholar",
                "age_group": "young_adult",
                "social_status": "noble"
            },
            "relationships": [
                {
                    "character": "慧喜",
                    "type": "romantic",
                    "strength": 0.9,
                    "description": "新婚妻子"
                }
            ]
        }
    ],
    "relationships": [
        {
            "character1": "莫凡",
            "character2": "慧喜",
            "type": "romantic",
            "strength": 0.95,
            "evidence_count": 23,
            "first_interaction": "第一章 新婚大喜"
        }
    ],
    "statistics": {
        "character_network_density": 0.34,
        "most_connected_character": "莫凡",
        "average_relationships_per_character": 2.1
    }
}
```

## 性能优化策略

### 1. 内存优化
```python
# 使用生成器处理大文件
def process_chapters_generator(self, file_path):
    """逐章处理，减少内存占用"""
    for chapter in self.read_chapters(file_path):
        yield self.extract_from_chapter(chapter)

# 缓存频繁访问的数据
from functools import lru_cache

@lru_cache(maxsize=1000)
def is_common_surname(self, char):
    return char in CHINESE_SURNAMES
```

### 2. 处理速度优化
```python
# 预编译正则表达式
import re
COMPILED_PATTERNS = {
    name: re.compile(pattern) 
    for name, pattern in NAME_PATTERNS.items()
}

# 并行处理
from multiprocessing import Pool

def parallel_character_extraction(self, chapters):
    with Pool() as pool:
        results = pool.map(self.extract_from_chapter, chapters)
    return self.merge_results(results)
```

## 验证和测试

### 1. 准确性验证
```python
def validate_extraction_accuracy(self, ground_truth, extracted):
    """
    验证提取准确性
    """
    true_positives = len(ground_truth & extracted)
    false_positives = len(extracted - ground_truth)
    false_negatives = len(ground_truth - extracted)
    
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1_score = 2 * (precision * recall) / (precision + recall)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }
```

### 2. 单元测试
```python
def test_name_extraction():
    test_text = "莫凡对慧喜说道："夫人，天色已晚，我们该回去了。""
    extractor = CharacterExtractor()
    names = extractor.extract_candidate_names(test_text)
    assert "莫凡" in names
    assert "慧喜" in names
```

## 命令行工具

```bash
# 基本提取
python src/character_extractor.py data/ziyang.txt

# 详细模式
python src/character_extractor.py data/ziyang.txt --detailed

# 指定输出格式
python src/character_extractor.py data/ziyang.txt --format json --output characters.json

# 关系分析
python src/character_extractor.py data/ziyang.txt --with-relationships

# 可视化输出
python src/character_extractor.py data/ziyang.txt --visualize --output network.html
```

## 后续扩展方向

1. **机器学习增强** - 使用NER模型提高识别准确率
2. **知识图谱** - 构建完整的人物知识图谱
3. **情感分析** - 分析人物对话和行为的情感色彩
4. **人物画像** - 基于文本描述生成人物形象
5. **交互式界面** - 提供Web界面进行人物信息编辑和验证