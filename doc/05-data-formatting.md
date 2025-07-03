# 数据格式化输出实现文档

## 概述

数据格式化输出是项目的最终阶段，目标是将前面各个模块提取的信息整合成结构化的数据格式，生成多种类型的输出文件，并提供数据统计分析和可视化功能。

## 功能需求

### 核心功能
1. **数据整合** - 合并章节、人物、对话等信息
2. **多格式输出** - 支持JSON、CSV、Excel、SQLite等格式
3. **数据验证** - 确保输出数据的完整性和一致性
4. **统计分析** - 生成各种统计指标和摘要信息
5. **报告生成** - 创建可读性强的分析报告

### 扩展功能
1. **可视化图表** - 生成人物关系图、对话统计图等
2. **数据压缩** - 优化大文件的存储和传输
3. **增量更新** - 支持数据的增量更新和合并
4. **API接口** - 提供RESTful API访问数据
5. **Web界面** - 创建交互式的数据展示界面

## 数据模型设计

### 1. 统一数据模型

```python
@dataclass
class NovelAnalysisResult:
    metadata: NovelMetadata
    chapters: List[Chapter]
    characters: List[Character]
    dialogues: List[Dialogue]
    relationships: List[Relationship]
    statistics: AnalysisStatistics
    
@dataclass
class NovelMetadata:
    title: str
    author: str
    source_file: str
    file_size: int
    encoding: str
    total_lines: int
    total_words: int
    processing_time: datetime
    version: str
    
@dataclass
class AnalysisStatistics:
    chapter_stats: ChapterStatistics
    character_stats: CharacterStatistics
    dialogue_stats: DialogueStatistics
    content_stats: ContentStatistics
```

### 2. 核心类设计

```python
class DataFormatter:
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.formatters = {
            'json': JSONFormatter(),
            'csv': CSVFormatter(),
            'excel': ExcelFormatter(),
            'sqlite': SQLiteFormatter(),
            'html': HTMLFormatter(),
        }
    
    def format_data(self, analysis_result, output_format, output_path):
        """格式化数据并输出"""
        
    def generate_report(self, analysis_result, template='default'):
        """生成分析报告"""
        
    def create_visualizations(self, analysis_result, chart_types):
        """创建可视化图表"""
        
    def validate_data(self, analysis_result):
        """验证数据完整性"""
```

## 具体实现方案

### 1. JSON格式输出

```python
class JSONFormatter:
    def __init__(self, config=None):
        self.config = config or {'indent': 2, 'ensure_ascii': False}
    
    def format(self, analysis_result, output_path):
        """
        生成JSON格式输出
        """
        data = {
            'metadata': self._format_metadata(analysis_result.metadata),
            'structure': self._format_chapters(analysis_result.chapters),
            'characters': self._format_characters(analysis_result.characters),
            'dialogues': self._format_dialogues(analysis_result.dialogues),
            'relationships': self._format_relationships(analysis_result.relationships),
            'statistics': self._format_statistics(analysis_result.statistics)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, **self.config, cls=CustomJSONEncoder)
        
        return output_path
    
    def _format_chapters(self, chapters):
        """格式化章节数据"""
        return [
            {
                'id': i + 1,
                'volume': {
                    'title': chapter.volume_title,
                    'number': chapter.volume_number
                },
                'chapter': {
                    'title': chapter.chapter_title,
                    'number': chapter.chapter_number,
                    'start_line': chapter.start_line,
                    'end_line': chapter.end_line,
                    'word_count': chapter.word_count
                },
                'summary': {
                    'character_count': len(chapter.characters_mentioned),
                    'dialogue_count': chapter.dialogue_count,
                    'content_preview': chapter.content[:200] + '...' if len(chapter.content) > 200 else chapter.content
                }
            }
            for i, chapter in enumerate(chapters)
        ]
    
    def _format_characters(self, characters):
        """格式化人物数据"""
        return [
            {
                'id': i + 1,
                'name': char.name,
                'aliases': char.aliases,
                'gender': char.gender,
                'role_type': char.role_type,
                'importance_score': round(char.importance_score, 2),
                'statistics': {
                    'total_appearances': len(char.appearances),
                    'dialogue_count': sum(1 for app in char.appearances if app.get('type') == 'dialogue'),
                    'chapters_appeared': len(set(app['chapter'] for app in char.appearances)),
                    'first_appearance': char.first_appearance
                },
                'attributes': char.attributes,
                'relationships': [
                    {
                        'character': rel.character,
                        'type': rel.type,
                        'strength': rel.strength
                    }
                    for rel in char.relationships
                ]
            }
            for i, char in enumerate(characters)
        ]
```

### 2. CSV格式输出

```python
class CSVFormatter:
    def format(self, analysis_result, output_dir):
        """
        生成多个CSV文件
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成各种CSV文件
        files_created = []
        
        # 章节信息CSV
        chapters_file = os.path.join(output_dir, 'chapters.csv')
        self._write_chapters_csv(analysis_result.chapters, chapters_file)
        files_created.append(chapters_file)
        
        # 人物信息CSV
        characters_file = os.path.join(output_dir, 'characters.csv')
        self._write_characters_csv(analysis_result.characters, characters_file)
        files_created.append(characters_file)
        
        # 对话信息CSV
        dialogues_file = os.path.join(output_dir, 'dialogues.csv')
        self._write_dialogues_csv(analysis_result.dialogues, dialogues_file)
        files_created.append(dialogues_file)
        
        # 人物关系CSV
        relationships_file = os.path.join(output_dir, 'relationships.csv')
        self._write_relationships_csv(analysis_result.relationships, relationships_file)
        files_created.append(relationships_file)
        
        return files_created
    
    def _write_chapters_csv(self, chapters, output_path):
        """写入章节CSV"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '章节ID', '卷标题', '卷编号', '章节标题', '章节编号',
                '开始行', '结束行', '字数', '人物数量', '对话数量'
            ])
            
            # 写入数据行
            for i, chapter in enumerate(chapters):
                writer.writerow([
                    i + 1,
                    chapter.volume_title,
                    chapter.volume_number,
                    chapter.chapter_title,
                    chapter.chapter_number,
                    chapter.start_line,
                    chapter.end_line,
                    chapter.word_count,
                    len(chapter.characters_mentioned),
                    chapter.dialogue_count
                ])
    
    def _write_dialogues_csv(self, dialogues, output_path):
        """写入对话CSV"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow([
                '对话ID', '内容', '说话者', '听话者', '类型', '情感',
                '章节', '行号', '置信度', '字数'
            ])
            
            for i, dialogue in enumerate(dialogues):
                writer.writerow([
                    i + 1,
                    dialogue.content,
                    dialogue.speaker or '',
                    dialogue.listener or '',
                    dialogue.type,
                    dialogue.emotion,
                    dialogue.chapter,
                    dialogue.line_number,
                    round(dialogue.confidence, 3),
                    len(dialogue.content)
                ])
```

### 3. Excel格式输出

```python
class ExcelFormatter:
    def format(self, analysis_result, output_path):
        """
        生成Excel文件（多个工作表）
        """
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.chart import BarChart, PieChart, Reference
        
        wb = openpyxl.Workbook()
        
        # 删除默认工作表
        wb.remove(wb.active)
        
        # 创建各个工作表
        self._create_summary_sheet(wb, analysis_result)
        self._create_chapters_sheet(wb, analysis_result.chapters)
        self._create_characters_sheet(wb, analysis_result.characters)
        self._create_dialogues_sheet(wb, analysis_result.dialogues)
        self._create_statistics_sheet(wb, analysis_result.statistics)
        self._create_charts_sheet(wb, analysis_result)
        
        wb.save(output_path)
        return output_path
    
    def _create_summary_sheet(self, workbook, analysis_result):
        """创建摘要工作表"""
        ws = workbook.create_sheet("摘要")
        
        # 设置标题样式
        title_font = Font(size=16, bold=True)
        header_font = Font(size=12, bold=True)
        
        # 基本信息
        ws['A1'] = '小说分析摘要'
        ws['A1'].font = title_font
        
        ws['A3'] = '文件信息'
        ws['A3'].font = header_font
        
        info_data = [
            ['文件名', analysis_result.metadata.source_file],
            ['作者', analysis_result.metadata.author],
            ['文件大小', f"{analysis_result.metadata.file_size:,} 字节"],
            ['总行数', f"{analysis_result.metadata.total_lines:,}"],
            ['总字数', f"{analysis_result.metadata.total_words:,}"],
            ['处理时间', analysis_result.metadata.processing_time.strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        for i, (key, value) in enumerate(info_data):
            ws[f'A{4+i}'] = key
            ws[f'B{4+i}'] = value
        
        # 统计信息
        ws['A12'] = '分析统计'
        ws['A12'].font = header_font
        
        stats_data = [
            ['总章节数', len(analysis_result.chapters)],
            ['总人物数', len(analysis_result.characters)],
            ['主要人物数', len([c for c in analysis_result.characters if c.role_type == 'main_character'])],
            ['总对话数', len(analysis_result.dialogues)],
            ['平均每章对话数', round(len(analysis_result.dialogues) / len(analysis_result.chapters), 1)]
        ]
        
        for i, (key, value) in enumerate(stats_data):
            ws[f'A{13+i}'] = key
            ws[f'B{13+i}'] = value
```

### 4. SQLite数据库输出

```python
class SQLiteFormatter:
    def format(self, analysis_result, output_path):
        """
        生成SQLite数据库
        """
        import sqlite3
        
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        # 创建表结构
        self._create_tables(cursor)
        
        # 插入数据
        self._insert_metadata(cursor, analysis_result.metadata)
        self._insert_chapters(cursor, analysis_result.chapters)
        self._insert_characters(cursor, analysis_result.characters)
        self._insert_dialogues(cursor, analysis_result.dialogues)
        self._insert_relationships(cursor, analysis_result.relationships)
        
        # 创建索引
        self._create_indexes(cursor)
        
        conn.commit()
        conn.close()
        
        return output_path
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        
        # 章节表
        cursor.execute('''
            CREATE TABLE chapters (
                id INTEGER PRIMARY KEY,
                volume_title TEXT,
                volume_number INTEGER,
                chapter_title TEXT,
                chapter_number INTEGER,
                start_line INTEGER,
                end_line INTEGER,
                word_count INTEGER,
                content TEXT
            )
        ''')
        
        # 人物表
        cursor.execute('''
            CREATE TABLE characters (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                gender TEXT,
                role_type TEXT,
                importance_score REAL,
                first_appearance_chapter INTEGER,
                total_appearances INTEGER,
                dialogue_count INTEGER,
                FOREIGN KEY (first_appearance_chapter) REFERENCES chapters (id)
            )
        ''')
        
        # 对话表
        cursor.execute('''
            CREATE TABLE dialogues (
                id INTEGER PRIMARY KEY,
                content TEXT,
                speaker_id INTEGER,
                listener_id INTEGER,
                type TEXT,
                emotion TEXT,
                chapter_id INTEGER,
                line_number INTEGER,
                confidence REAL,
                FOREIGN KEY (speaker_id) REFERENCES characters (id),
                FOREIGN KEY (listener_id) REFERENCES characters (id),
                FOREIGN KEY (chapter_id) REFERENCES chapters (id)
            )
        ''')
        
        # 人物关系表
        cursor.execute('''
            CREATE TABLE relationships (
                id INTEGER PRIMARY KEY,
                character1_id INTEGER,
                character2_id INTEGER,
                relationship_type TEXT,
                strength REAL,
                evidence_count INTEGER,
                FOREIGN KEY (character1_id) REFERENCES characters (id),
                FOREIGN KEY (character2_id) REFERENCES characters (id)
            )
        ''')
    
    def _create_indexes(self, cursor):
        """创建索引提高查询性能"""
        indexes = [
            'CREATE INDEX idx_chapters_number ON chapters (volume_number, chapter_number)',
            'CREATE INDEX idx_characters_name ON characters (name)',
            'CREATE INDEX idx_characters_role ON characters (role_type)',
            'CREATE INDEX idx_dialogues_speaker ON dialogues (speaker_id)',
            'CREATE INDEX idx_dialogues_chapter ON dialogues (chapter_id)',
            'CREATE INDEX idx_relationships_chars ON relationships (character1_id, character2_id)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
```

### 5. HTML报告生成

```python
class HTMLFormatter:
    def __init__(self):
        self.template_dir = 'templates'
        
    def format(self, analysis_result, output_path):
        """
        生成HTML分析报告
        """
        from jinja2 import Environment, FileSystemLoader
        
        # 设置模板环境
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template('analysis_report.html')
        
        # 准备模板数据
        template_data = {
            'metadata': analysis_result.metadata,
            'chapters': analysis_result.chapters,
            'characters': analysis_result.characters[:20],  # 只显示前20个重要人物
            'dialogues': analysis_result.dialogues[:50],    # 只显示前50个对话
            'statistics': self._prepare_statistics(analysis_result.statistics),
            'charts_data': self._prepare_charts_data(analysis_result)
        }
        
        # 渲染HTML
        html_content = template.render(**template_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _prepare_charts_data(self, analysis_result):
        """准备图表数据"""
        return {
            'character_importance': [
                {'name': char.name, 'score': char.importance_score}
                for char in sorted(analysis_result.characters, 
                                 key=lambda x: x.importance_score, reverse=True)[:10]
            ],
            'dialogue_emotions': self._count_emotions(analysis_result.dialogues),
            'chapter_lengths': [
                {'chapter': f"第{ch.chapter_number}章", 'words': ch.word_count}
                for ch in analysis_result.chapters
            ]
        }
```

### 6. 数据验证模块

```python
class DataValidator:
    def validate(self, analysis_result):
        """
        验证分析结果的完整性和一致性
        """
        issues = []
        
        # 验证章节数据
        chapter_issues = self._validate_chapters(analysis_result.chapters)
        issues.extend(chapter_issues)
        
        # 验证人物数据
        character_issues = self._validate_characters(analysis_result.characters)
        issues.extend(character_issues)
        
        # 验证对话数据
        dialogue_issues = self._validate_dialogues(analysis_result.dialogues, analysis_result.characters)
        issues.extend(dialogue_issues)
        
        # 验证数据一致性
        consistency_issues = self._validate_consistency(analysis_result)
        issues.extend(consistency_issues)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'summary': self._create_validation_summary(issues)
        }
    
    def _validate_chapters(self, chapters):
        """验证章节数据"""
        issues = []
        
        for i, chapter in enumerate(chapters):
            # 检查必填字段
            if not chapter.chapter_title:
                issues.append(f"章节 {i+1} 缺少标题")
            
            # 检查行号逻辑
            if chapter.start_line >= chapter.end_line:
                issues.append(f"章节 {chapter.chapter_title} 行号逻辑错误")
            
            # 检查字数统计
            if chapter.word_count <= 0:
                issues.append(f"章节 {chapter.chapter_title} 字数统计异常")
        
        return issues
    
    def _validate_dialogues(self, dialogues, characters):
        """验证对话数据"""
        issues = []
        character_names = {char.name for char in characters}
        
        for i, dialogue in enumerate(dialogues):
            # 检查说话者是否在人物列表中
            if dialogue.speaker and dialogue.speaker not in character_names:
                issues.append(f"对话 {i+1} 的说话者 '{dialogue.speaker}' 不在人物列表中")
            
            # 检查对话内容
            if not dialogue.content or len(dialogue.content.strip()) == 0:
                issues.append(f"对话 {i+1} 内容为空")
            
            # 检查置信度
            if dialogue.confidence < 0 or dialogue.confidence > 1:
                issues.append(f"对话 {i+1} 置信度超出范围")
        
        return issues
```

### 7. 统计分析模块

```python
class StatisticsGenerator:
    def generate_statistics(self, analysis_result):
        """
        生成全面的统计分析
        """
        stats = AnalysisStatistics()
        
        # 章节统计
        stats.chapter_stats = self._analyze_chapters(analysis_result.chapters)
        
        # 人物统计
        stats.character_stats = self._analyze_characters(analysis_result.characters)
        
        # 对话统计
        stats.dialogue_stats = self._analyze_dialogues(analysis_result.dialogues)
        
        # 内容统计
        stats.content_stats = self._analyze_content(analysis_result)
        
        return stats
    
    def _analyze_chapters(self, chapters):
        """分析章节统计"""
        word_counts = [ch.word_count for ch in chapters]
        
        return {
            'total_chapters': len(chapters),
            'total_words': sum(word_counts),
            'average_words_per_chapter': statistics.mean(word_counts),
            'median_words_per_chapter': statistics.median(word_counts),
            'longest_chapter': max(chapters, key=lambda x: x.word_count).chapter_title,
            'shortest_chapter': min(chapters, key=lambda x: x.word_count).chapter_title,
            'word_count_distribution': {
                'min': min(word_counts),
                'max': max(word_counts),
                'std_dev': statistics.stdev(word_counts) if len(word_counts) > 1 else 0
            }
        }
    
    def _analyze_characters(self, characters):
        """分析人物统计"""
        return {
            'total_characters': len(characters),
            'main_characters': len([c for c in characters if c.role_type == 'main_character']),
            'supporting_characters': len([c for c in characters if c.role_type == 'supporting_character']),
            'minor_characters': len([c for c in characters if c.role_type == 'minor_character']),
            'gender_distribution': self._count_by_attribute(characters, 'gender'),
            'most_important_character': max(characters, key=lambda x: x.importance_score).name,
            'average_importance_score': statistics.mean([c.importance_score for c in characters])
        }
    
    def _analyze_dialogues(self, dialogues):
        """分析对话统计"""
        return {
            'total_dialogues': len(dialogues),
            'type_distribution': self._count_by_attribute(dialogues, 'type'),
            'emotion_distribution': self._count_by_attribute(dialogues, 'emotion'),
            'average_dialogue_length': statistics.mean([len(d.content) for d in dialogues]),
            'speakers_distribution': self._count_speakers(dialogues),
            'confidence_stats': {
                'average': statistics.mean([d.confidence for d in dialogues if d.confidence]),
                'high_confidence': len([d for d in dialogues if d.confidence and d.confidence > 0.8])
            }
        }
```

## 可视化模块

### 1. 图表生成

```python
class VisualizationGenerator:
    def __init__(self):
        import matplotlib.pyplot as plt
        import seaborn as sns
        import networkx as nx
        
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
        plt.rcParams['axes.unicode_minus'] = False
        
    def create_character_network(self, characters, relationships, output_path):
        """创建人物关系网络图"""
        import networkx as nx
        import matplotlib.pyplot as plt
        
        G = nx.Graph()
        
        # 添加节点
        for char in characters:
            G.add_node(char.name, 
                      importance=char.importance_score,
                      role_type=char.role_type)
        
        # 添加边
        for rel in relationships:
            if rel.strength > 0.3:  # 只显示强关系
                G.add_edge(rel.character1, rel.character2, 
                          weight=rel.strength,
                          relationship_type=rel.type)
        
        # 绘制网络图
        plt.figure(figsize=(15, 12))
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 根据重要性设置节点大小
        node_sizes = [G.nodes[node]['importance'] * 100 for node in G.nodes()]
        
        # 根据角色类型设置颜色
        color_map = {'main_character': 'red', 'supporting_character': 'blue', 'minor_character': 'gray'}
        node_colors = [color_map.get(G.nodes[node]['role_type'], 'gray') for node in G.nodes()]
        
        nx.draw(G, pos, 
                node_size=node_sizes,
                node_color=node_colors,
                with_labels=True,
                font_size=8,
                font_family='SimHei',
                edge_color='gray',
                alpha=0.7)
        
        plt.title('人物关系网络图', fontsize=16)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_dialogue_emotion_chart(self, dialogues, output_path):
        """创建对话情感分布图"""
        import matplotlib.pyplot as plt
        
        emotion_counts = {}
        for dialogue in dialogues:
            emotion = dialogue.emotion or 'unknown'
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        emotions = list(emotion_counts.keys())
        counts = list(emotion_counts.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(emotions, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        
        plt.title('对话情感分布', fontsize=14)
        plt.xlabel('情感类型', fontsize=12)
        plt.ylabel('对话数量', fontsize=12)
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
```

### 2. Web界面生成

```python
class WebInterfaceGenerator:
    def generate_web_interface(self, analysis_result, output_dir):
        """
        生成交互式Web界面
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'static'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'data'), exist_ok=True)
        
        # 生成数据文件
        self._generate_json_data(analysis_result, os.path.join(output_dir, 'data'))
        
        # 生成HTML文件
        self._generate_html_files(analysis_result, output_dir)
        
        # 复制静态资源
        self._copy_static_files(output_dir)
        
        return output_dir
    
    def _generate_html_files(self, analysis_result, output_dir):
        """生成HTML文件"""
        
        # 主页面
        index_html = self._create_index_page(analysis_result)
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # 人物页面
        characters_html = self._create_characters_page(analysis_result.characters)
        with open(os.path.join(output_dir, 'characters.html'), 'w', encoding='utf-8') as f:
            f.write(characters_html)
        
        # 对话页面
        dialogues_html = self._create_dialogues_page(analysis_result.dialogues)
        with open(os.path.join(output_dir, 'dialogues.html'), 'w', encoding='utf-8') as f:
            f.write(dialogues_html)
```

## 配置文件设计

### data_formatting_config.json

```json
{
    "output_formats": {
        "json": {
            "enabled": true,
            "indent": 2,
            "ensure_ascii": false,
            "include_content": true,
            "max_content_length": 1000
        },
        "csv": {
            "enabled": true,
            "encoding": "utf-8",
            "separator": ",",
            "include_headers": true
        },
        "excel": {
            "enabled": true,
            "include_charts": true,
            "max_rows_per_sheet": 50000
        },
        "sqlite": {
            "enabled": true,
            "create_indexes": true,
            "vacuum": true
        },
        "html": {
            "enabled": true,
            "include_charts": true,
            "template": "default"
        }
    },
    "visualization": {
        "network_graph": {
            "min_relationship_strength": 0.3,
            "node_size_factor": 100,
            "layout": "spring"
        },
        "charts": {
            "dpi": 300,
            "format": "png",
            "color_scheme": "default"
        }
    },
    "validation": {
        "strict_mode": false,
        "auto_fix": true,
        "report_warnings": true
    },
    "optimization": {
        "compress_output": false,
        "parallel_processing": true,
        "memory_limit_mb": 1024
    }
}
```

## 命令行工具

```bash
# 基本格式化输出
python src/data_formatter.py results.pkl --format json --output novel_analysis.json

# 多格式输出
python src/data_formatter.py results.pkl --formats json,csv,excel --output-dir output/

# 生成完整报告
python src/data_formatter.py results.pkl --report --with-charts --output report.html

# 生成数据库
python src/data_formatter.py results.pkl --format sqlite --output novel_data.db

# 创建Web界面
python src/data_formatter.py results.pkl --web-interface --output-dir web/

# 自定义配置
python src/data_formatter.py results.pkl --config custom_config.json --output-dir custom_output/

# 验证数据
python src/data_formatter.py results.pkl --validate-only --report validation_report.txt

# 生成可视化图表
python src/data_formatter.py results.pkl --charts-only --output-dir charts/
```

## 性能优化

### 1. 大数据处理优化

```python
class OptimizedDataFormatter:
    def __init__(self, memory_limit_mb=1024):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        
    def format_large_dataset(self, analysis_result, output_config):
        """
        优化大数据集的处理
        """
        # 分块处理
        if self._estimate_memory_usage(analysis_result) > self.memory_limit:
            return self._chunked_processing(analysis_result, output_config)
        else:
            return self._standard_processing(analysis_result, output_config)
    
    def _chunked_processing(self, analysis_result, output_config):
        """分块处理大数据"""
        chunk_size = self._calculate_chunk_size(analysis_result)
        
        for chunk in self._chunk_data(analysis_result, chunk_size):
            self._process_chunk(chunk, output_config)
```

### 2. 并行处理

```python
from multiprocessing import Pool
import multiprocessing as mp

def parallel_format_generation(self, analysis_result, formats):
    """
    并行生成多种格式
    """
    with Pool(processes=min(len(formats), mp.cpu_count())) as pool:
        tasks = [
            (analysis_result, format_type, self._get_output_path(format_type))
            for format_type in formats
        ]
        
        results = pool.starmap(self._format_single_type, tasks)
    
    return results
```

## 后续扩展

1. **云端部署** - 支持云端数据处理和存储
2. **实时更新** - 支持数据的实时更新和同步
3. **多语言支持** - 扩展到其他语言的文本分析
4. **机器学习集成** - 集成更多AI分析功能
5. **协作功能** - 支持多用户协作和数据共享

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Create overall project plan document", "status": "completed", "priority": "high"}, {"id": "2", "content": "Create chapter structure recognition document", "status": "completed", "priority": "high"}, {"id": "3", "content": "Create character name extraction document", "status": "completed", "priority": "high"}, {"id": "4", "content": "Create dialogue content separation document", "status": "completed", "priority": "high"}, {"id": "5", "content": "Create data formatting output document", "status": "completed", "priority": "high"}]