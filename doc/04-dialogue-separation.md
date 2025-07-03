# 对话内容分离实现文档

## 概述

对话内容分离是小说分析的重要环节，目标是从混合的叙述文本中准确分离出对话内容，识别说话者，并提取对话的上下文信息。这为后续的人物分析和情节理解提供基础数据。

## 功能需求

### 核心功能
1. **对话检测** - 识别文本中的对话片段
2. **说话者识别** - 确定每段对话的说话人
3. **对话标记** - 区分直接对话、间接对话和内心独白
4. **上下文提取** - 提取对话的场景和情境信息
5. **对话分类** - 按类型、情感、功能等维度分类对话

### 扩展功能
1. **情感分析** - 分析对话的情感色彩和语调
2. **意图识别** - 识别对话的交际意图（询问、命令、请求等）
3. **话题追踪** - 跟踪对话中的话题变化
4. **对话关系** - 分析对话参与者之间的关系动态

## 中文对话格式分析

### 常见对话标记

基于 `ziyang.txt` 的分析，中文小说中的对话格式：

```python
DIALOGUE_PATTERNS = {
    'quoted_speech': [
        r'"([^"]*)"',                    # 双引号对话
        r'"([^"]*)"',                    # 中文双引号
        r''([^']*)'',                    # 中文单引号
    ],
    'speaker_tags': [
        r'([一-龥]{2,4})(?:说道?|道|说|曰|开口|低声|高声|冷声|轻声)',
        r'([一-龥]{2,4})(?:问道?|询问|追问|反问)',
        r'([一-龥]{2,4})(?:答道?|回答|应答|回应)',
        r'([一-龥]{2,4})(?:叹道?|感叹|叹息|叹气)',
    ],
    'narrative_speech': [
        r'([一-龥]{2,4})(?:心想|心道|暗想|暗道|想到)',  # 内心独白
        r'([一-龥]{2,4})(?:自语|喃喃|嘀咕)',         # 自言自语
    ],
    'action_tags': [
        r'([一-龥]{2,4})(?:微微|缓缓|轻轻|慢慢)(?:说|道)',
        r'([一-龥]{2,4})(?:摇头|点头|皱眉|微笑)(?:说|道)',
    ]
}
```

## 技术实现方案

### 1. 核心类设计

#### Dialogue 数据结构

```python
@dataclass
class Dialogue:
    content: str                 # 对话内容
    speaker: str                 # 说话者
    listener: Optional[str]      # 听话者
    type: str                   # 对话类型
    emotion: str                # 情感色彩
    context: str                # 上下文
    chapter: str                # 所属章节
    line_number: int            # 行号
    confidence: float           # 识别置信度
    metadata: dict              # 额外信息

class DialogueSeparator:
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.dialogues = []
        self.patterns = self._compile_patterns()
        
    def extract_dialogues(self, text, chapter_info=None):
        """从文本中提取所有对话"""
        
    def _identify_dialogue_segments(self, text):
        """识别对话片段"""
        
    def _identify_speakers(self, dialogue_segments):
        """识别说话者"""
        
    def _classify_dialogue_types(self, dialogues):
        """分类对话类型"""
        
    def _analyze_emotions(self, dialogues):
        """分析对话情感"""
```

### 2. 对话检测算法

#### 步骤1：对话片段识别

```python
def identify_dialogue_segments(self, text):
    """
    识别所有可能的对话片段
    """
    segments = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 检测引号包围的对话
        quoted_dialogues = self._extract_quoted_text(line, i+1)
        segments.extend(quoted_dialogues)
        
        # 检测动作描述中的隐含对话
        implicit_dialogues = self._extract_implicit_dialogue(line, i+1)
        segments.extend(implicit_dialogues)
        
        # 检测内心独白
        inner_thoughts = self._extract_inner_thoughts(line, i+1)
        segments.extend(inner_thoughts)
    
    return segments

def _extract_quoted_text(self, line, line_number):
    """
    提取引号中的对话内容
    """
    dialogues = []
    
    # 处理各种引号格式
    quote_patterns = [
        (r'"([^"]*)"', 'direct_speech'),
        (r'"([^"]*)"', 'direct_speech'),
        (r''([^']*)'', 'direct_speech'),
        (r'「([^」]*)」', 'direct_speech'),  # 日式引号
    ]
    
    for pattern, dialogue_type in quote_patterns:
        matches = re.finditer(pattern, line)
        for match in matches:
            content = match.group(1).strip()
            if content and len(content) > 1:  # 过滤过短的内容
                dialogues.append({
                    'content': content,
                    'type': dialogue_type,
                    'line_number': line_number,
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'context': line
                })
    
    return dialogues
```

#### 步骤2：说话者识别

```python
def identify_speakers(self, dialogue_segments):
    """
    为每段对话识别说话者
    """
    enhanced_dialogues = []
    
    for dialogue in dialogue_segments:
        speaker = self._find_speaker(dialogue)
        listener = self._find_listener(dialogue)
        
        enhanced_dialogue = Dialogue(
            content=dialogue['content'],
            speaker=speaker,
            listener=listener,
            type=dialogue['type'],
            context=dialogue['context'],
            line_number=dialogue['line_number'],
            confidence=self._calculate_confidence(dialogue, speaker)
        )
        
        enhanced_dialogues.append(enhanced_dialogue)
    
    return enhanced_dialogues

def _find_speaker(self, dialogue):
    """
    从上下文中识别说话者
    """
    context = dialogue['context']
    line_before = self._get_previous_line(dialogue['line_number'])
    
    # 方法1：直接标记法（最常见）
    # "老夫行将朽木，不愿背井离乡。"老先生平静摇头。
    direct_patterns = [
        r'([一-龥]{2,4})(?:说道?|道|说|曰|开口|答道|问道|叹道)',
        r'([一-龥]{2,4})(?:摇头|点头|微笑|皱眉|叹息)(?:说|道)',
    ]
    
    for pattern in direct_patterns:
        # 在对话后面查找
        after_match = re.search(pattern, context[dialogue['end_pos']:])
        if after_match:
            return after_match.group(1)
        
        # 在对话前面查找
        before_match = re.search(pattern, context[:dialogue['start_pos']])
        if before_match:
            return before_match.group(1)
    
    # 方法2：上下文推理法
    # 查找前一句中提到的人物
    if line_before:
        names = self._extract_names_from_line(line_before)
        if len(names) == 1:
            return names[0]
    
    # 方法3：对话内容分析法
    # 基于对话内容推断说话者
    speaker = self._infer_speaker_from_content(dialogue['content'])
    if speaker:
        return speaker
    
    return None  # 无法识别说话者

def _find_listener(self, dialogue):
    """
    识别对话的听众
    """
    context = dialogue['context']
    
    # 查找"对...说"模式
    listener_patterns = [
        r'(?:对|向|朝)([一-龥]{2,4})(?:说|道|问)',
        r'([一-龥]{2,4})(?:听后|闻言|听到)',
    ]
    
    for pattern in listener_patterns:
        match = re.search(pattern, context)
        if match:
            return match.group(1)
    
    return None
```

### 3. 对话类型分类

```python
def classify_dialogue_types(self, dialogues):
    """
    对对话进行类型分类
    """
    for dialogue in dialogues:
        # 基于标记词分类
        dialogue.type = self._classify_by_markers(dialogue)
        
        # 基于内容分析
        if dialogue.type == 'unknown':
            dialogue.type = self._classify_by_content(dialogue)
    
    return dialogues

def _classify_by_markers(self, dialogue):
    """
    基于标记词分类对话类型
    """
    context = dialogue.context.lower()
    
    type_markers = {
        'question': ['问道', '询问', '疑问', '？', '?'],
        'answer': ['答道', '回答', '应答', '回应'],
        'exclamation': ['叹道', '感叹', '！', '!'],
        'whisper': ['低声', '轻声', '小声', '悄声'],
        'shout': ['高声', '大声', '喊道', '叫道'],
        'inner_thought': ['心想', '心道', '暗想', '暗道'],
        'self_talk': ['自语', '喃喃', '嘀咕'],
        'command': ['命令', '吩咐', '令道'],
    }
    
    for dialogue_type, markers in type_markers.items():
        if any(marker in context for marker in markers):
            return dialogue_type
    
    return 'statement'  # 默认为陈述

def _classify_by_content(self, dialogue):
    """
    基于对话内容分类
    """
    content = dialogue.content
    
    # 疑问句检测
    if '？' in content or '?' in content or any(word in content for word in ['什么', '怎么', '为什么', '哪里', '谁']):
        return 'question'
    
    # 感叹句检测
    if '！' in content or '!' in content or any(word in content for word in ['啊', '呀', '哦', '唉']):
        return 'exclamation'
    
    # 命令句检测
    if any(word in content for word in ['去', '来', '快', '立即', '马上']):
        return 'command'
    
    return 'statement'
```

### 4. 情感分析

```python
def analyze_dialogue_emotions(self, dialogues):
    """
    分析对话的情感色彩
    """
    # 情感词典
    emotion_lexicon = {
        'positive': ['高兴', '开心', '喜悦', '满意', '感激', '欣慰'],
        'negative': ['愤怒', '生气', '伤心', '难过', '失望', '痛苦'],
        'neutral': ['平静', '冷漠', '淡然', '普通'],
        'surprise': ['惊讶', '震惊', '意外', '吃惊'],
        'fear': ['害怕', '恐惧', '担心', '忧虑', '紧张'],
        'contempt': ['鄙视', '轻蔑', '嘲笑', '讽刺'],
    }
    
    for dialogue in dialogues:
        emotion_scores = {}
        
        # 基于情感词典打分
        for emotion, words in emotion_lexicon.items():
            score = sum(1 for word in words if word in dialogue.content)
            if score > 0:
                emotion_scores[emotion] = score
        
        # 基于语境标记
        context_emotions = self._analyze_context_emotion(dialogue.context)
        for emotion, score in context_emotions.items():
            emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score
        
        # 确定主要情感
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            dialogue.emotion = dominant_emotion
            dialogue.metadata['emotion_scores'] = emotion_scores
        else:
            dialogue.emotion = 'neutral'
    
    return dialogues

def _analyze_context_emotion(self, context):
    """
    分析上下文中的情感标记
    """
    emotion_markers = {
        'positive': ['微笑', '笑道', '高兴', '欣然', '满意'],
        'negative': ['皱眉', '怒道', '冷声', '不悦', '愤然'],
        'sad': ['叹息', '叹道', '黯然', '悲伤', '垂泪'],
        'surprise': ['惊讶', '吃惊', '瞪大', '愣住'],
        'fear': ['颤抖', '害怕', '恐惧', '胆怯'],
    }
    
    scores = {}
    for emotion, markers in emotion_markers.items():
        score = sum(1 for marker in markers if marker in context)
        if score > 0:
            scores[emotion] = score
    
    return scores
```

### 5. 高级功能实现

#### 对话连贯性分析

```python
def analyze_dialogue_coherence(self, dialogues):
    """
    分析对话的连贯性和回应关系
    """
    dialogue_chains = []
    current_chain = []
    
    for i, dialogue in enumerate(dialogues):
        if i == 0:
            current_chain = [dialogue]
            continue
        
        prev_dialogue = dialogues[i-1]
        
        # 检查是否为连续对话
        if self._is_continuous_dialogue(prev_dialogue, dialogue):
            current_chain.append(dialogue)
        else:
            if len(current_chain) > 1:
                dialogue_chains.append(current_chain)
            current_chain = [dialogue]
    
    # 添加最后一个对话链
    if len(current_chain) > 1:
        dialogue_chains.append(current_chain)
    
    return dialogue_chains

def _is_continuous_dialogue(self, prev_dialogue, curr_dialogue):
    """
    判断两段对话是否连续
    """
    # 行号相近
    line_distance = curr_dialogue.line_number - prev_dialogue.line_number
    if line_distance > 5:
        return False
    
    # 说话者交替
    if prev_dialogue.speaker and curr_dialogue.speaker:
        if prev_dialogue.speaker != curr_dialogue.speaker:
            return True
    
    # 问答关系
    if prev_dialogue.type == 'question' and curr_dialogue.type == 'answer':
        return True
    
    return False
```

#### 话题识别

```python
def identify_dialogue_topics(self, dialogue_chains):
    """
    识别对话中的话题
    """
    from collections import Counter
    import jieba
    
    for chain in dialogue_chains:
        # 提取所有对话内容
        combined_text = ' '.join(d.content for d in chain)
        
        # 分词并提取关键词
        words = jieba.cut(combined_text)
        word_freq = Counter(word for word in words if len(word) > 1)
        
        # 识别主要话题
        top_keywords = word_freq.most_common(5)
        topics = [word for word, freq in top_keywords if freq > 1]
        
        # 为对话链中的每个对话添加话题信息
        for dialogue in chain:
            dialogue.metadata['topics'] = topics
            dialogue.metadata['keyword_frequency'] = dict(word_freq)
    
    return dialogue_chains
```

## 配置文件设计

### dialogue_config.json

```json
{
    "patterns": {
        "quote_marks": [""", """, "'", "'", "「", "」"],
        "speaker_indicators": [
            "说道", "说", "道", "曰", "开口", "问道", "答道", "叹道",
            "低声", "高声", "轻声", "冷声", "笑道", "怒道"
        ],
        "action_indicators": [
            "摇头", "点头", "微笑", "皱眉", "叹息", "瞪眼", "愣住"
        ]
    },
    "classification": {
        "min_dialogue_length": 2,
        "max_context_distance": 50,
        "speaker_confidence_threshold": 0.7,
        "emotion_score_threshold": 0.5
    },
    "emotions": {
        "positive_words": ["高兴", "开心", "喜悦", "满意", "感激"],
        "negative_words": ["愤怒", "生气", "伤心", "难过", "失望"],
        "neutral_words": ["平静", "冷漠", "淡然", "普通"],
        "context_emotions": {
            "微笑": "positive",
            "皱眉": "negative",
            "叹息": "sad",
            "瞪眼": "angry"
        }
    },
    "filters": {
        "exclude_patterns": ["^\\s*$", "^[。，！？]+$"],
        "min_speaker_name_length": 2,
        "max_speaker_name_length": 4
    }
}
```

## 输出格式设计

### JSON 输出示例

```json
{
    "metadata": {
        "source_file": "data/ziyang.txt",
        "processing_time": "2024-07-02T19:00:00Z",
        "total_dialogues": 1247,
        "dialogue_types": {
            "direct_speech": 1089,
            "inner_thought": 87,
            "self_talk": 71
        },
        "speakers_identified": 856,
        "unknown_speakers": 391
    },
    "dialogues": [
        {
            "id": 1,
            "content": "先生，胡人凶残成性，暴虐食人，您留在此处凶多吉少。",
            "speaker": "莫凡",
            "listener": "老先生",
            "type": "statement",
            "emotion": "concern",
            "chapter": "第一章 新婚大喜",
            "line_number": 17,
            "context": "先生，胡人凶残成性，暴虐食人，您留在此处凶多吉少。"少年低声说道。",
            "confidence": 0.95,
            "metadata": {
                "emotion_scores": {"concern": 0.8, "fear": 0.3},
                "topics": ["胡人", "危险", "劝说"],
                "intent": "persuade",
                "formality": "formal"
            }
        }
    ],
    "dialogue_chains": [
        {
            "id": 1,
            "participants": ["莫凡", "老先生"],
            "start_line": 15,
            "end_line": 25,
            "topic": "南迁劝说",
            "dialogues": [1, 2, 3, 4, 5],
            "summary": "莫凡劝说老先生南迁避难的对话"
        }
    ],
    "statistics": {
        "most_talkative_character": "莫凡",
        "dialogue_density_per_chapter": 0.23,
        "average_dialogue_length": 15.6,
        "emotion_distribution": {
            "neutral": 0.45,
            "positive": 0.23,
            "negative": 0.18,
            "concern": 0.14
        },
        "dialogue_type_distribution": {
            "statement": 0.67,
            "question": 0.18,
            "exclamation": 0.09,
            "command": 0.06
        }
    }
}
```

## 性能优化

### 1. 正则表达式优化

```python
import re
from functools import lru_cache

class OptimizedPatternMatcher:
    def __init__(self):
        # 预编译所有正则表达式
        self.compiled_patterns = {
            'quotes': re.compile(r'[""''「」]([^""''「」]*)[""''「」]'),
            'speakers': re.compile(r'([一-龥]{2,4})(?:说道?|道|说|曰|开口)'),
            'emotions': re.compile(r'(?:微笑|皱眉|叹息|瞪眼|愣住)'),
        }
    
    @lru_cache(maxsize=1000)
    def find_quotes(self, text):
        return self.compiled_patterns['quotes'].findall(text)
```

### 2. 并行处理

```python
from multiprocessing import Pool
import multiprocessing as mp

def parallel_dialogue_extraction(self, chapters):
    """
    并行处理多个章节的对话提取
    """
    with Pool(processes=mp.cpu_count()) as pool:
        results = pool.map(self.extract_chapter_dialogues, chapters)
    
    # 合并结果
    all_dialogues = []
    for chapter_dialogues in results:
        all_dialogues.extend(chapter_dialogues)
    
    return all_dialogues
```

## 验证和测试

### 1. 准确性测试

```python
def test_dialogue_extraction_accuracy():
    """
    测试对话提取的准确性
    """
    test_cases = [
        {
            'input': '"先生，您好吗？"莫凡问道。',
            'expected': {
                'content': '先生，您好吗？',
                'speaker': '莫凡',
                'type': 'question'
            }
        },
        {
            'input': '老先生摇头："我不愿离开。"',
            'expected': {
                'content': '我不愿离开。',
                'speaker': '老先生',
                'type': 'statement'
            }
        }
    ]
    
    separator = DialogueSeparator()
    for case in test_cases:
        result = separator.extract_dialogues(case['input'])
        assert len(result) == 1
        dialogue = result[0]
        assert dialogue.content == case['expected']['content']
        assert dialogue.speaker == case['expected']['speaker']
        assert dialogue.type == case['expected']['type']
```

### 2. 性能测试

```python
def test_performance():
    """
    测试大文件处理性能
    """
    import time
    
    separator = DialogueSeparator()
    
    # 测试大文件
    start_time = time.time()
    dialogues = separator.extract_dialogues_from_file('data/ziyang.txt')
    end_time = time.time()
    
    processing_time = end_time - start_time
    dialogues_per_second = len(dialogues) / processing_time
    
    print(f"处理时间: {processing_time:.2f}秒")
    print(f"提取对话数: {len(dialogues)}")
    print(f"处理速度: {dialogues_per_second:.2f}对话/秒")
```

## 命令行工具

```bash
# 基本对话提取
python src/dialogue_separator.py data/ziyang.txt

# 详细分析模式
python src/dialogue_separator.py data/ziyang.txt --detailed --with-emotions

# 指定输出格式
python src/dialogue_separator.py data/ziyang.txt --format json --output dialogues.json

# 只提取特定角色的对话
python src/dialogue_separator.py data/ziyang.txt --speaker "莫凡" --output mofan_dialogues.json

# 对话链分析
python src/dialogue_separator.py data/ziyang.txt --chains --output dialogue_chains.json

# 情感分析
python src/dialogue_separator.py data/ziyang.txt --emotions --visualize
```

## 后续扩展

1. **深度学习模型** - 使用BERT等模型提高识别准确率
2. **多轮对话理解** - 实现更复杂的对话理解和生成
3. **语音转换** - 支持对话的语音合成
4. **交互式标注** - 提供人工标注界面提高数据质量
5. **跨语言支持** - 扩展到其他语言的对话提取