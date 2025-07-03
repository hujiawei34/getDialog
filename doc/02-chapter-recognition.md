# 章节结构识别实现文档

## 概述

章节结构识别是文本处理的第二个关键步骤，目标是从小说文本中自动识别和提取章节信息，建立完整的章节结构树。

## 功能需求

### 核心功能
1. **章节边界识别** - 准确定位每个章节的开始和结束位置
2. **章节标题提取** - 提取章节的完整标题信息
3. **层级结构构建** - 处理卷、章、节等多级结构
4. **元数据提取** - 提取章节编号、字数统计等信息

### 扩展功能
1. **异常处理** - 处理格式不规范的章节标题
2. **灵活配置** - 支持不同小说的章节格式
3. **验证机制** - 确保章节划分的完整性和准确性

## 技术实现方案

### 1. 章节标识符分析

基于对 `ziyang.txt` 的分析，常见的章节标识符包括：

```python
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千万\d]+卷\s+(.+)$',  # 卷标题：第一卷 道人
    r'^第[一二三四五六七八九十百千万\d]+章\s+(.+)$',  # 章标题：第一章 新婚大喜
    r'^第[一二三四五六七八九十百千万\d]+节\s+(.+)$',  # 节标题（如果有）
    r'^[一二三四五六七八九十百千万\d]+、(.+)$',      # 数字序号格式
    r'^\d+\.?\s*(.+)$',                              # 阿拉伯数字格式
]
```

### 2. 核心算法实现

#### ChapterParser 类设计

```python
class ChapterParser:
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.chapters = []
        self.volumes = []
    
    def parse_file(self, file_path):
        """解析整个文件的章节结构"""
        
    def _identify_chapter_lines(self, lines):
        """识别章节标题行"""
        
    def _build_chapter_structure(self, chapter_lines):
        """构建章节结构树"""
        
    def _extract_content(self, lines, start, end):
        """提取章节内容"""
        
    def _validate_structure(self):
        """验证章节结构的完整性"""
```

### 3. 数据结构设计

#### 章节信息结构

```python
@dataclass
class Chapter:
    volume_title: str          # 所属卷标题
    volume_number: int         # 卷编号
    chapter_title: str         # 章节标题
    chapter_number: int        # 章节编号
    start_line: int           # 开始行号
    end_line: int             # 结束行号
    content: str              # 章节内容
    word_count: int           # 字数统计
    metadata: dict            # 额外元数据

@dataclass
class Volume:
    title: str                # 卷标题
    number: int               # 卷编号
    chapters: List[Chapter]   # 包含的章节列表
    start_line: int           # 开始行号
    end_line: int             # 结束行号
```

## 具体实现步骤

### 步骤1：文本预处理

```python
def preprocess_text(self, file_path):
    """
    预处理文本，为章节识别做准备
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 清理空行和特殊字符
    cleaned_lines = []
    for i, line in enumerate(lines):
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append((i+1, cleaned_line))  # 保存原始行号
    
    return cleaned_lines
```

### 步骤2：章节标识符匹配

```python
def identify_chapter_lines(self, lines):
    """
    识别所有可能的章节标题行
    """
    chapter_candidates = []
    
    for line_num, line_content in lines:
        for pattern in self.config['chapter_patterns']:
            match = re.match(pattern, line_content)
            if match:
                chapter_info = {
                    'line_number': line_num,
                    'raw_text': line_content,
                    'matched_pattern': pattern,
                    'extracted_title': match.group(1) if match.groups() else line_content,
                    'type': self._determine_chapter_type(pattern)
                }
                chapter_candidates.append(chapter_info)
                break
    
    return chapter_candidates
```

### 步骤3：层级结构构建

```python
def build_hierarchy(self, chapter_candidates, all_lines):
    """
    构建章节的层级结构
    """
    volumes = []
    current_volume = None
    chapters = []
    
    for i, candidate in enumerate(chapter_candidates):
        if candidate['type'] == 'volume':
            # 处理卷级别
            if current_volume:
                current_volume['chapters'] = chapters
                volumes.append(current_volume)
            
            current_volume = {
                'title': candidate['extracted_title'],
                'line_number': candidate['line_number'],
                'chapters': []
            }
            chapters = []
            
        elif candidate['type'] == 'chapter':
            # 处理章级别
            next_line = chapter_candidates[i+1]['line_number'] if i+1 < len(chapter_candidates) else len(all_lines)
            
            chapter = {
                'title': candidate['extracted_title'],
                'start_line': candidate['line_number'],
                'end_line': next_line - 1,
                'content': self._extract_content(all_lines, candidate['line_number'], next_line - 1)
            }
            chapters.append(chapter)
    
    # 处理最后一个卷
    if current_volume:
        current_volume['chapters'] = chapters
        volumes.append(current_volume)
    
    return volumes
```

### 步骤4：内容提取和统计

```python
def extract_content(self, lines, start_line, end_line):
    """
    提取指定范围内的章节内容
    """
    content_lines = []
    word_count = 0
    
    for line_num, line_content in lines:
        if start_line < line_num <= end_line:
            content_lines.append(line_content)
            word_count += len(line_content.replace(' ', ''))
    
    return {
        'content': '\n'.join(content_lines),
        'word_count': word_count,
        'line_count': len(content_lines)
    }
```

## 配置文件设计

### chapter_config.json

```json
{
    "patterns": {
        "volume": [
            "^第[一二三四五六七八九十百千万\\d]+卷\\s+(.+)$"
        ],
        "chapter": [
            "^第[一二三四五六七八九十百千万\\d]+章\\s+(.+)$"
        ],
        "section": [
            "^第[一二三四五六七八九十百千万\\d]+节\\s+(.+)$"
        ]
    },
    "numbering": {
        "chinese_numerals": true,
        "arabic_numerals": true,
        "mixed_format": true
    },
    "validation": {
        "min_chapter_length": 100,
        "max_chapter_length": 50000,
        "require_continuous_numbering": false
    }
}
```

## 输出格式设计

### JSON 输出格式

```json
{
    "metadata": {
        "source_file": "data/ziyang.txt",
        "total_volumes": 1,
        "total_chapters": 156,
        "total_words": 2010091,
        "processed_time": "2024-07-02T17:30:00Z"
    },
    "structure": [
        {
            "volume": {
                "title": "道人",
                "number": 1,
                "start_line": 8,
                "chapters": [
                    {
                        "title": "新婚大喜",
                        "number": 1,
                        "start_line": 11,
                        "end_line": 520,
                        "word_count": 3524,
                        "content_preview": "公元340年冬，黄河北岸，西阳县东郊...",
                        "characters_mentioned": ["莫凡", "老先生"],
                        "dialogue_count": 15
                    }
                ]
            }
        }
    ]
}
```

## 错误处理和边界情况

### 1. 格式异常处理

```python
def handle_format_exceptions(self, line_content):
    """
    处理格式不规范的章节标题
    """
    # 处理标题中包含特殊字符的情况
    cleaned_title = re.sub(r'[^\u4e00-\u9fff\w\s]', '', line_content)
    
    # 处理编号不连续的情况
    if self.config['validation']['require_continuous_numbering']:
        # 实现编号连续性检查
        pass
    
    return cleaned_title
```

### 2. 验证机制

```python
def validate_chapter_structure(self, chapters):
    """
    验证章节结构的合理性
    """
    issues = []
    
    for i, chapter in enumerate(chapters):
        # 检查章节长度
        if chapter['word_count'] < self.config['validation']['min_chapter_length']:
            issues.append(f"章节 {chapter['title']} 内容过短")
        
        # 检查章节边界
        if i > 0 and chapter['start_line'] <= chapters[i-1]['end_line']:
            issues.append(f"章节 {chapter['title']} 边界重叠")
    
    return issues
```

## 性能优化

### 1. 内存优化
- 分块处理大文件
- 延迟加载章节内容
- 使用生成器减少内存占用

### 2. 处理速度优化
- 编译正则表达式
- 使用多进程处理大文件
- 缓存中间结果

## 测试用例设计

### 单元测试

```python
def test_chapter_recognition():
    test_cases = [
        ("第一章 新婚大喜", True, "新婚大喜"),
        ("第二十三章　夜袭", True, "夜袭"),
        ("普通文本内容", False, None),
        ("第1章 现代格式", True, "现代格式")
    ]
    
    parser = ChapterParser()
    for text, should_match, expected_title in test_cases:
        result = parser.is_chapter_title(text)
        assert result == should_match
        if should_match:
            assert parser.extract_title(text) == expected_title
```


## 已实现功能 ✅

### 章节结构可视化工具

**实现文件：** `src/step02_chapter/chapter_visualizer.py`

**功能特点：**
- 📊 **多种格式**：支持文本、树状、HTML、JSON四种可视化格式
- 🏗️ **层级结构**：自动识别卷和章节的层级关系
- 📈 **统计信息**：显示字数、章节数等统计数据
- 🎨 **HTML可视化**：生成美观的网页版可视化界面

**使用示例：**
```bash
# 树状结构显示
python src/step02_chapter/chapter_visualizer.py data/ziyang.txt -f tree

# 生成HTML可视化文件
python src/step02_chapter/chapter_visualizer.py data/ziyang.txt -f html -o output/chapter_structure.html

# 文本格式详细显示
python src/step02_chapter/chapter_visualizer.py data/ziyang.txt -f text

# JSON格式输出
python src/step02_chapter/chapter_visualizer.py data/ziyang.txt -f json -o output/chapter_structure.json
```

**解析结果：**
- 识别出7卷，535章，共1,894,212字
- 自动解析章节标题和字数统计
- 生成完整的章节结构树
- HTML版本包含进度条和字数占比可视化

### 核心算法实现

**ChapterStructureVisualizer类：**
- 支持中文数字和阿拉伯数字的章节编号识别
- 自动构建卷-章层级结构
- 提供多种输出格式的可视化展示
- 包含字数统计和章节内容预览功能

**正则表达式模式：**
```python
patterns = {
    'volume': [
        r'^第([一二三四五六七八九十百千万\d]+)卷\s+(.+)$',
        r'^第(\d+)卷\s+(.+)$'
    ],
    'chapter': [
        r'^第([一二三四五六七八九十百千万\d]+)章\s+(.+)$', 
        r'^第(\d+)章\s+(.+)$'
    ]
}
```

## 后续扩展

1. **智能学习** - 基于已标注数据训练章节识别模型
2. **多格式支持** - 支持更多小说格式和网站格式
3. ~~**可视化工具** - 提供章节结构的可视化展示~~ ✅ **已完成**
4. **批量处理** - 支持批量处理多个小说文件
5. **API接口** - 提供REST API供其他应用调用