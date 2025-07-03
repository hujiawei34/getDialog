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

### 1. 中文人名识别策略

#### 基于规则的方法

```python
# 中文姓氏列表（常见500姓）
CHINESE_SURNAMES = {
    '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈',
    '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
    # ... 更多姓氏
}

# 人名识别模式
NAME_PATTERNS = [
    r'[赵钱孙李周吴郑王冯陈...]{1}[一-龥]{1,3}',  # 姓+名（2-4字）
    r'[一-龥]{2,4}(?=说道?|道|说|曰)',           # 说话者模式
    r'(?<=，)[一-龥]{2,4}(?=微微|缓缓|静静)',      # 动作描述中的人名
    r'(?<=对)[一-龥]{2,4}(?=说|道)',             # 对话对象
]
```

#### 基于上下文的识别

```python
# 人名上下文特征
CONTEXT_PATTERNS = {
    'speaker_context': [
        r'([一-龥]{2,4})(?:说道?|道|说|曰|开口|低声|高声|冷声)',
        r'([一-龥]{2,4})(?:摇头|点头|微笑|叹息|皱眉)',
    ],
    'address_context': [
        r'(?:对|向|找)([一-龥]{2,4})(?:说|道|问)',
        r'([一-龥]{2,4})(?:师父|师兄|师姐|师弟|师妹)',
    ],
    'possession_context': [
        r'([一-龥]{2,4})的(?:父亲|母亲|儿子|女儿|妻子|丈夫)',
        r'([一-龥]{2,4})(?:家|府|院|楼|轩)',
    ]
}
```

### 2. 核心类设计

#### CharacterExtractor 类

```python
@dataclass
class Character:
    name: str                    # 主要姓名
    aliases: List[str]           # 别名列表
    titles: List[str]            # 称谓列表
    gender: str                  # 性别
    role_type: str              # 角色类型
    first_appearance: dict       # 首次出现位置
    appearances: List[dict]      # 所有出现记录
    relationships: List[dict]    # 人物关系
    attributes: dict            # 其他属性

class CharacterExtractor:
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.characters = {}
        self.name_variants = {}  # 名称变体映射
        
    def extract_from_text(self, text, chapter_info=None):
        """从文本中提取人物信息"""
        
    def _identify_names(self, text):
        """识别文本中的所有可能人名"""
        
    def _resolve_aliases(self, names):
        """解决别名和称谓问题"""
        
    def _classify_characters(self):
        """根据出现频次等信息分类人物"""
        
    def _extract_relationships(self, text):
        """提取人物关系信息"""
```

### 3. 人名识别算法

#### 步骤1：候选人名提取

```python
def extract_candidate_names(self, text):
    """
    提取候选人名
    """
    candidates = set()
    
    # 基于正则表达式的提取
    for pattern in self.config['name_patterns']:
        matches = re.findall(pattern, text)
        candidates.update(matches)
    
    # 基于上下文的提取
    for context_type, patterns in CONTEXT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                candidates.add(match)
    
    # 过滤明显不是人名的词
    filtered_candidates = []
    for candidate in candidates:
        if self._is_valid_name(candidate):
            filtered_candidates.append(candidate)
    
    return filtered_candidates

def _is_valid_name(self, name):
    """
    判断是否为有效人名
    """
    # 长度检查
    if len(name) < 2 or len(name) > 4:
        return False
    
    # 排除常见非人名词汇
    exclude_words = {'这里', '那里', '如此', '因此', '所以', '然后', '什么', '怎么'}
    if name in exclude_words:
        return False
    
    # 检查是否包含姓氏
    if name[0] in CHINESE_SURNAMES:
        return True
    
    # 其他启发式规则
    return self._heuristic_name_check(name)
```

#### 步骤2：人名聚类和别名识别

```python
def resolve_name_variants(self, candidates):
    """
    解决人名变体和别名问题
    """
    # 基于编辑距离的相似性计算
    from difflib import SequenceMatcher
    
    name_groups = []
    processed = set()
    
    for name in candidates:
        if name in processed:
            continue
            
        group = [name]
        processed.add(name)
        
        # 寻找相似的名字
        for other_name in candidates:
            if other_name not in processed:
                similarity = SequenceMatcher(None, name, other_name).ratio()
                if similarity > self.config['name_similarity_threshold']:
                    group.append(other_name)
                    processed.add(other_name)
        
        name_groups.append(group)
    
    return name_groups

def identify_formal_titles(self, text, character_name):
    """
    识别人物的正式称谓和别名
    """
    titles = []
    
    # 称谓模式
    title_patterns = [
        rf'{character_name}(?:师父|师兄|师姐|先生|夫人|公子|小姐)',
        rf'(?:老|小|大){character_name}',
        rf'{character_name[0]}(?:某|氏|公|君)',
    ]
    
    for pattern in title_patterns:
        matches = re.findall(pattern, text)
        titles.extend(matches)
    
    return list(set(titles))
```

#### 步骤3：角色重要性分析

```python
def analyze_character_importance(self, characters):
    """
    分析角色的重要性和类型
    """
    for char_name, char_info in characters.items():
        # 出现频次
        appearance_count = len(char_info.appearances)
        
        # 对话数量
        dialogue_count = sum(1 for app in char_info.appearances if app.get('type') == 'dialogue')
        
        # 章节分布
        chapters_appeared = len(set(app['chapter'] for app in char_info.appearances))
        
        # 计算重要性得分
        importance_score = (
            appearance_count * 0.4 +
            dialogue_count * 0.4 +
            chapters_appeared * 0.2
        )
        
        # 角色分类
        if importance_score > self.config['main_character_threshold']:
            char_info.role_type = 'main_character'
        elif importance_score > self.config['supporting_character_threshold']:
            char_info.role_type = 'supporting_character'
        else:
            char_info.role_type = 'minor_character'
        
        char_info.importance_score = importance_score
```

### 4. 关系提取算法

#### 社交关系识别

```python
def extract_relationships(self, text, characters):
    """
    提取人物间的关系
    """
    relationships = []
    
    # 关系模式
    relationship_patterns = {
        'family': [
            r'([一-龥]{2,4})(?:的)?(?:父亲|母亲|儿子|女儿|兄弟|姐妹)([一-龥]{2,4})',
            r'([一-龥]{2,4})(?:与|和)([一-龥]{2,4})(?:夫妻|夫妇)',
        ],
        'social': [
            r'([一-龥]{2,4})(?:的)?(?:师父|师傅|老师)([一-龥]{2,4})',
            r'([一-龥]{2,4})(?:的)?(?:朋友|好友|挚友)([一-龥]{2,4})',
        ],
        'antagonistic': [
            r'([一-龥]{2,4})(?:与|和)([一-龥]{2,4})(?:为敌|作对|争斗)',
            r'([一-龥]{2,4})(?:杀死|击败|战胜)(?:了)?([一-龥]{2,4})',
        ]
    }
    
    for relation_type, patterns in relationship_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                char1, char2 = match
                if char1 in characters and char2 in characters:
                    relationships.append({
                        'character1': char1,
                        'character2': char2,
                        'relationship_type': relation_type,
                        'evidence': match
                    })
    
    return relationships
```

#### 共现关系分析

```python
def analyze_co_occurrence(self, characters, chapters):
    """
    分析人物共现关系
    """
    co_occurrence_matrix = {}
    
    for chapter in chapters:
        # 获取本章出现的人物
        chapter_characters = self._get_chapter_characters(chapter['content'])
        
        # 计算两两共现
        for i, char1 in enumerate(chapter_characters):
            for char2 in chapter_characters[i+1:]:
                pair = tuple(sorted([char1, char2]))
                co_occurrence_matrix[pair] = co_occurrence_matrix.get(pair, 0) + 1
    
    # 转换为关系强度
    relationships = []
    for (char1, char2), count in co_occurrence_matrix.items():
        if count >= self.config['min_co_occurrence']:
            strength = min(count / self.config['max_co_occurrence'], 1.0)
            relationships.append({
                'character1': char1,
                'character2': char2,
                'relationship_type': 'co_occurrence',
                'strength': strength,
                'frequency': count
            })
    
    return relationships
```

### 5. 性别和属性识别

```python
def identify_gender_and_attributes(self, character_name, context_texts):
    """
    识别人物的性别和其他属性
    """
    attributes = {}
    
    # 性别识别模式
    gender_patterns = {
        'male': [
            rf'{character_name}(?:他|公子|先生|君|郎|男子|男人)',
            rf'(?:他|这个男子|这个男人)(?:就是|便是)?{character_name}',
        ],
        'female': [
            rf'{character_name}(?:她|小姐|夫人|女子|女人|姑娘)',
            rf'(?:她|这个女子|这个女人|这个姑娘)(?:就是|便是)?{character_name}',
        ]
    }
    
    male_score = 0
    female_score = 0
    
    for text in context_texts:
        for pattern in gender_patterns['male']:
            male_score += len(re.findall(pattern, text))
        for pattern in gender_patterns['female']:
            female_score += len(re.findall(pattern, text))
    
    if male_score > female_score:
        attributes['gender'] = 'male'
    elif female_score > male_score:
        attributes['gender'] = 'female'
    else:
        attributes['gender'] = 'unknown'
    
    # 职业/身份识别
    profession_patterns = {
        'scholar': rf'{character_name}(?:先生|学士|书生|文人)',
        'martial_artist': rf'{character_name}(?:武者|剑客|刀客|侠客)',
        'official': rf'{character_name}(?:大人|官员|县令|知府)',
        'merchant': rf'{character_name}(?:商人|掌柜|老板)',
    }
    
    for profession, pattern in profession_patterns.items():
        if any(re.search(pattern, text) for text in context_texts):
            attributes['profession'] = profession
            break
    
    return attributes
```

## 配置文件设计

### character_config.json

```json
{
    "extraction": {
        "min_name_length": 2,
        "max_name_length": 4,
        "name_similarity_threshold": 0.8,
        "min_appearances": 3
    },
    "classification": {
        "main_character_threshold": 50,
        "supporting_character_threshold": 10,
        "min_co_occurrence": 5,
        "max_co_occurrence": 100
    },
    "patterns": {
        "speaker_indicators": ["说道", "说", "道", "曰", "开口", "低声"],
        "action_indicators": ["微笑", "点头", "摇头", "皱眉", "叹息"],
        "relationship_keywords": {
            "family": ["父亲", "母亲", "儿子", "女儿", "兄弟", "姐妹", "夫妻"],
            "social": ["朋友", "师父", "师兄", "师姐", "同门"],
            "professional": ["同事", "上级", "下属", "伙伴"]
        }
    },
    "filters": {
        "exclude_words": ["这里", "那里", "如此", "因此", "什么", "怎么", "为什么"],
        "common_titles": ["先生", "夫人", "公子", "小姐", "大人"]
    }
}
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