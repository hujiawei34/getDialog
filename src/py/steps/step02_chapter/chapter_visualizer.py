#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Chapter:
    volume_title: str
    volume_number: int
    chapter_title: str
    chapter_number: int
    start_line: int
    end_line: int
    word_count: int
    content_preview: str


@dataclass
class Volume:
    title: str
    number: int
    chapters: List[Chapter]
    start_line: int
    end_line: int
    total_words: int


class ChapterStructureVisualizer:
    def __init__(self, config_path: Optional[str] = None):
        self.chapters = []
        self.volumes = []
        self.patterns = {
            'volume': [
                r'^第([一二三四五六七八九十百千万\d]+)卷\s+(.+)$',
                r'^第(\d+)卷\s+(.+)$'
            ],
            'chapter': [
                r'^第([一二三四五六七八九十百千万\d]+)章\s+(.+)$', 
                r'^第(\d+)章\s+(.+)$'
            ]
        }
        
    def parse_file(self, file_path: str) -> Dict:
        """解析文件并生成章节结构"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 预处理文本
        cleaned_lines = []
        for i, line in enumerate(lines):
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append((i + 1, cleaned_line))
        
        # 识别章节标题
        structure_items = self._identify_structure(cleaned_lines)
        
        # 构建层级结构
        volumes = self._build_hierarchy(structure_items, cleaned_lines)
        
        return {
            'metadata': {
                'source_file': file_path,
                'total_volumes': len(volumes),
                'total_chapters': sum(len(vol.chapters) for vol in volumes),
                'total_words': sum(vol.total_words for vol in volumes)
            },
            'volumes': [asdict(vol) for vol in volumes]
        }
    
    def _identify_structure(self, lines: List[Tuple[int, str]]) -> List[Dict]:
        """识别卷和章节标题"""
        structure_items = []
        
        for line_num, line_content in lines:
            # 检查卷标题
            for pattern in self.patterns['volume']:
                match = re.match(pattern, line_content)
                if match:
                    number_str, title = match.groups()
                    structure_items.append({
                        'type': 'volume',
                        'line_number': line_num,
                        'number_str': number_str,
                        'title': title,
                        'raw_text': line_content
                    })
                    break
            else:
                # 检查章节标题
                for pattern in self.patterns['chapter']:
                    match = re.match(pattern, line_content)
                    if match:
                        number_str, title = match.groups()
                        structure_items.append({
                            'type': 'chapter',
                            'line_number': line_num,
                            'number_str': number_str,
                            'title': title,
                            'raw_text': line_content
                        })
                        break
        
        return structure_items
    
    def _build_hierarchy(self, structure_items: List[Dict], all_lines: List[Tuple[int, str]]) -> List[Volume]:
        """构建层级结构"""
        volumes = []
        current_volume = None
        chapters = []
        
        for i, item in enumerate(structure_items):
            if item['type'] == 'volume':
                # 保存之前的卷
                if current_volume:
                    current_volume.chapters = chapters
                    current_volume.end_line = chapters[-1].end_line if chapters else current_volume.start_line
                    current_volume.total_words = sum(ch.word_count for ch in chapters)
                    volumes.append(current_volume)
                
                # 创建新卷
                current_volume = Volume(
                    title=item['title'],
                    number=self._parse_number(item['number_str']),
                    chapters=[],
                    start_line=item['line_number'],
                    end_line=0,
                    total_words=0
                )
                chapters = []
                
            elif item['type'] == 'chapter':
                # 确定章节结束位置
                next_item_line = structure_items[i + 1]['line_number'] if i + 1 < len(structure_items) else len(all_lines)
                
                # 提取章节内容
                content_info = self._extract_chapter_content(all_lines, item['line_number'], next_item_line - 1)
                
                chapter = Chapter(
                    volume_title=current_volume.title if current_volume else "未知卷",
                    volume_number=current_volume.number if current_volume else 0,
                    chapter_title=item['title'],
                    chapter_number=self._parse_number(item['number_str']),
                    start_line=item['line_number'],
                    end_line=next_item_line - 1,
                    word_count=content_info['word_count'],
                    content_preview=content_info['preview']
                )
                chapters.append(chapter)
        
        # 处理最后一个卷
        if current_volume:
            current_volume.chapters = chapters
            current_volume.end_line = chapters[-1].end_line if chapters else current_volume.start_line
            current_volume.total_words = sum(ch.word_count for ch in chapters)
            volumes.append(current_volume)
        
        return volumes
    
    def _extract_chapter_content(self, lines: List[Tuple[int, str]], start_line: int, end_line: int) -> Dict:
        """提取章节内容"""
        content_lines = []
        word_count = 0
        
        for line_num, line_content in lines:
            if start_line < line_num <= end_line:
                content_lines.append(line_content)
                word_count += len(line_content.replace(' ', '').replace('\t', ''))
        
        content_text = '\n'.join(content_lines)
        preview = content_text[:100] + '...' if len(content_text) > 100 else content_text
        
        return {
            'word_count': word_count,
            'preview': preview,
            'line_count': len(content_lines)
        }
    
    def _parse_number(self, number_str: str) -> int:
        """解析中文数字或阿拉伯数字"""
        # 基础中文数字映射
        chinese_digits = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '零': 0
        }
        
        # 如果是阿拉伯数字
        if number_str.isdigit():
            return int(number_str)
        
        # 处理中文数字
        if not number_str:
            return 1
        
        # 处理简单的一位数字
        if len(number_str) == 1 and number_str in chinese_digits:
            return chinese_digits[number_str]
        
        result = 0
        
        # 处理百位数
        if '百' in number_str:
            if number_str == '百':
                return 100
            
            # 分割百位和其余部分
            parts = number_str.split('百')
            if len(parts) == 2:
                # 获取百位数字
                hundred_part = parts[0] if parts[0] else '一'  # 如果没有前缀，默认是"一"
                hundreds = chinese_digits.get(hundred_part, 1) * 100
                
                # 处理百位后的部分
                remainder = parts[1]
                if remainder:
                    if remainder == '零':
                        # 一百零X的情况，比如一百零一
                        pass
                    elif '零' in remainder:
                        # 处理"一百零一"这样的情况
                        if remainder.startswith('零'):
                            remainder = remainder[1:]  # 去掉"零"
                            result = hundreds + chinese_digits.get(remainder, 0)
                        else:
                            result = hundreds
                    elif '十' in remainder:
                        # 处理"一百一十"、"一百二十三"这样的情况
                        if remainder == '十':
                            result = hundreds + 10
                        elif remainder.startswith('十'):
                            # 一百十一、一百十二...一百十九
                            tens_remainder = remainder[1:]
                            result = hundreds + 10 + chinese_digits.get(tens_remainder, 0)
                        elif remainder.endswith('十'):
                            # 一百二十、一百三十...一百九十
                            tens_prefix = remainder[:-1]
                            result = hundreds + chinese_digits.get(tens_prefix, 1) * 10
                        else:
                            # 一百二十一、一百二十二...一百九十九
                            tens_parts = remainder.split('十')
                            if len(tens_parts) == 2:
                                tens = chinese_digits.get(tens_parts[0], 0) * 10
                                ones = chinese_digits.get(tens_parts[1], 0)
                                result = hundreds + tens + ones
                            else:
                                result = hundreds
                    else:
                        # 一百一、一百二...一百九
                        result = hundreds + chinese_digits.get(remainder, 0)
                else:
                    # 只有百位，如"三百"
                    result = hundreds
                
                return result
        
        # 处理包含"十"的数字（非百位数）
        if '十' in number_str:
            if number_str == '十':
                return 10
            elif number_str.startswith('十'):
                # 十一、十二...十九
                remainder = number_str[1:]
                return 10 + chinese_digits.get(remainder, 0)
            elif number_str.endswith('十'):
                # 二十、三十...九十
                prefix = number_str[:-1]
                return chinese_digits.get(prefix, 1) * 10
            else:
                # 二十一、二十二...九十九
                parts = number_str.split('十')
                if len(parts) == 2:
                    tens = chinese_digits.get(parts[0], 0) * 10
                    ones = chinese_digits.get(parts[1], 0)
                    return tens + ones
        
        # 如果无法解析，返回1作为默认值
        return 1
    
    def generate_text_visualization(self, structure_data: Dict) -> str:
        """生成文本格式的可视化"""
        output = []
        output.append("=" * 80)
        output.append(f"📚 小说章节结构可视化")
        output.append("=" * 80)
        output.append("")
        
        metadata = structure_data['metadata']
        output.append(f"📖 源文件: {metadata['source_file']}")
        output.append(f"📊 统计信息:")
        output.append(f"   • 总卷数: {metadata['total_volumes']}")
        output.append(f"   • 总章数: {metadata['total_chapters']}")
        output.append(f"   • 总字数: {metadata['total_words']:,}")
        output.append("")
        
        for vol_data in structure_data['volumes']:
            output.append(f"📂 第{vol_data['number']}卷: {vol_data['title']}")
            output.append(f"   └─ 行号: {vol_data['start_line']}-{vol_data['end_line']}")
            output.append(f"   └─ 章节数: {len(vol_data['chapters'])}")
            output.append(f"   └─ 字数: {vol_data['total_words']:,}")
            output.append("")
            
            for chapter in vol_data['chapters']:
                output.append(f"   📄 第{chapter['chapter_number']}章: {chapter['chapter_title']}")
                output.append(f"      ├─ 行号: {chapter['start_line']}-{chapter['end_line']}")
                output.append(f"      ├─ 字数: {chapter['word_count']:,}")
                output.append(f"      └─ 预览: {chapter['content_preview']}")
                output.append("")
        
        output.append("=" * 80)
        return '\n'.join(output)
    
    def generate_tree_visualization(self, structure_data: Dict) -> str:
        """生成树状结构可视化"""
        output = []
        output.append("小说章节结构树")
        output.append("└─ " + Path(structure_data['metadata']['source_file']).name)
        
        volumes = structure_data['volumes']
        for i, vol_data in enumerate(volumes):
            is_last_vol = i == len(volumes) - 1
            vol_prefix = "   └─ " if is_last_vol else "   ├─ "
            output.append(f"{vol_prefix}第{vol_data['number']}卷: {vol_data['title']} ({vol_data['total_words']:,}字)")
            
            chapters = vol_data['chapters']
            for j, chapter in enumerate(chapters):
                is_last_chapter = j == len(chapters) - 1
                if is_last_vol:
                    chapter_prefix = "      └─ " if is_last_chapter else "      ├─ "
                else:
                    chapter_prefix = "   │  └─ " if is_last_chapter else "   │  ├─ "
                
                output.append(f"{chapter_prefix}第{chapter['chapter_number']}章: {chapter['chapter_title']} ({chapter['word_count']:,}字)")
        
        return '\n'.join(output)
    
    def generate_html_visualization(self, structure_data: Dict) -> str:
        """生成HTML格式的可视化"""
        metadata = structure_data['metadata']
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小说章节结构可视化</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat {{ text-align: center; background: #ecf0f1; padding: 15px; border-radius: 8px; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        .volume {{ margin: 20px 0; border: 2px solid #3498db; border-radius: 10px; overflow: hidden; }}
        .volume-header {{ background: #3498db; color: white; padding: 15px; }}
        .volume-title {{ font-size: 18px; font-weight: bold; }}
        .volume-info {{ font-size: 14px; opacity: 0.9; margin-top: 5px; }}
        .chapter {{ border-bottom: 1px solid #ecf0f1; padding: 15px; background: white; }}
        .chapter:last-child {{ border-bottom: none; }}
        .chapter-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 8px; }}
        .chapter-info {{ color: #7f8c8d; font-size: 12px; }}
        .chapter-preview {{ color: #34495e; margin-top: 8px; font-style: italic; }}
        .progress-bar {{ background: #ecf0f1; height: 6px; border-radius: 3px; margin: 5px 0; }}
        .progress-fill {{ background: #27ae60; height: 100%; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 小说章节结构可视化</h1>
            <p>源文件: {metadata['source_file']}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{metadata['total_volumes']}</div>
                <div class="stat-label">总卷数</div>
            </div>
            <div class="stat">
                <div class="stat-number">{metadata['total_chapters']}</div>
                <div class="stat-label">总章数</div>
            </div>
            <div class="stat">
                <div class="stat-number">{metadata['total_words']:,}</div>
                <div class="stat-label">总字数</div>
            </div>
        </div>
"""
        
        total_words = metadata['total_words']
        for vol_data in structure_data['volumes']:
            vol_percentage = (vol_data['total_words'] / total_words * 100) if total_words > 0 else 0
            
            html += f"""
        <div class="volume">
            <div class="volume-header">
                <div class="volume-title">第{vol_data['number']}卷: {vol_data['title']}</div>
                <div class="volume-info">
                    章节数: {len(vol_data['chapters'])} | 字数: {vol_data['total_words']:,} | 占比: {vol_percentage:.1f}%
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {vol_percentage}%"></div>
                </div>
            </div>
"""
            
            for chapter in vol_data['chapters']:
                chapter_percentage = (chapter['word_count'] / vol_data['total_words'] * 100) if vol_data['total_words'] > 0 else 0
                
                html += f"""
            <div class="chapter">
                <div class="chapter-title">第{chapter['chapter_number']}章: {chapter['chapter_title']}</div>
                <div class="chapter-info">
                    行号: {chapter['start_line']}-{chapter['end_line']} | 字数: {chapter['word_count']:,} | 占本卷: {chapter_percentage:.1f}%
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {chapter_percentage}%"></div>
                </div>
                <div class="chapter-preview">{chapter['content_preview']}</div>
            </div>
"""
            
            html += "        </div>\n"
        
        html += """
    </div>
</body>
</html>
"""
        return html


def main():
    parser = argparse.ArgumentParser(description='小说章节结构可视化工具')
    parser.add_argument('input_file', help='输入的小说文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-f', '--format', choices=['text', 'tree', 'html', 'json'], 
                       default='text', help='输出格式 (默认: text)')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 创建可视化器
    visualizer = ChapterStructureVisualizer()
    
    if args.verbose:
        print(f"正在解析文件: {args.input_file}")
    
    # 解析文件
    try:
        structure_data = visualizer.parse_file(args.input_file)
    except Exception as e:
        print(f"错误: 无法解析文件 {args.input_file}: {e}")
        return 1
    
    # 生成可视化
    if args.format == 'text':
        output_content = visualizer.generate_text_visualization(structure_data)
    elif args.format == 'tree':
        output_content = visualizer.generate_tree_visualization(structure_data)
    elif args.format == 'html':
        output_content = visualizer.generate_html_visualization(structure_data)
    elif args.format == 'json':
        output_content = json.dumps(structure_data, ensure_ascii=False, indent=2)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"可视化结果已保存到: {args.output}")
    else:
        print(output_content)
    
    return 0


if __name__ == '__main__':
    exit(main())