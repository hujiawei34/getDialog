#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from typing import List
from pathlib import Path

from .chapter_visualizer import ChapterStructureVisualizer, Volume
from utils.log_util import log_info, log_error, log_warning
from utils.constants import PROJECT_ROOT


class ChapterExtractor:
    """章节内容提取器，将小说按卷和章节分离为单独的文本文件"""
    
    def __init__(self):
        self.visualizer = ChapterStructureVisualizer()
    
    def extract_chapters_to_files(self, input_file: str, output_base_dir: str = None) -> bool:
        """
        将小说按章节提取为单独的文本文件
        
        Args:
            input_file: 输入的小说文件路径
            output_base_dir: 输出基础目录，默认为 data/
            
        Returns:
            bool: 提取是否成功
        """
        try:
            # 设置输出基础目录
            if output_base_dir is None:
                output_base_dir = PROJECT_ROOT / "data"
            
            output_base_dir = Path(output_base_dir)
            
            # 获取小说名称（去掉扩展名）
            novel_name = Path(input_file).stem
            if novel_name.endswith('_utf8'):
                novel_name = novel_name[:-5]  # 去掉 _utf8 后缀
            
            # 创建小说专用目录
            novel_dir = output_base_dir / novel_name
            novel_dir.mkdir(parents=True, exist_ok=True)
            
            log_info(f"开始提取章节文件到: {novel_dir}")
            
            # 解析小说结构
            structure_data = self.visualizer.parse_file(input_file)
            volumes_data = structure_data['volumes']
            
            # 读取原始文件内容
            with open(input_file, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            # 提取每个卷和章节
            total_chapters = 0
            for vol_data in volumes_data:
                volume_dir = novel_dir / f"第{vol_data['number']}卷"
                volume_dir.mkdir(exist_ok=True)
                
                log_info(f"处理第{vol_data['number']}卷: {vol_data['title']}")
                
                # 提取卷的内容（如果有卷标题行）
                if vol_data['chapters']:
                    # 创建卷信息文件
                    volume_info_file = volume_dir / "卷信息.txt"
                    with open(volume_info_file, 'w', encoding='utf-8') as f:
                        f.write(f"第{vol_data['number']}卷: {vol_data['title']}\n")
                        f.write(f"章节数: {len(vol_data['chapters'])}\n")
                        f.write(f"总字数: {vol_data['total_words']:,}\n")
                        f.write(f"起始行: {vol_data['start_line']}\n")
                        f.write(f"结束行: {vol_data['end_line']}\n")
                
                # 提取每个章节
                for chapter_data in vol_data['chapters']:
                    chapter_filename = f"第{chapter_data['chapter_number']}章.txt"
                    chapter_file = volume_dir / chapter_filename
                    
                    # 提取章节内容
                    chapter_content = self._extract_full_chapter_content(
                        original_lines, chapter_data['start_line'], chapter_data['end_line']
                    )
                    
                    # 写入章节文件
                    with open(chapter_file, 'w', encoding='utf-8') as f:
                        # 写入章节标题
                        f.write(f"第{chapter_data['chapter_number']}章: {chapter_data['chapter_title']}\n")
                        f.write("=" * 50 + "\n\n")
                        
                        # 写入章节内容
                        f.write(chapter_content)
                    
                    total_chapters += 1
                    log_info(f"  提取第{chapter_data['chapter_number']}章: {chapter_data['chapter_title']} -> {chapter_file}")
            
            log_info(f"章节提取完成！共提取 {len(volumes_data)} 卷，{total_chapters} 章")
            log_info(f"文件保存在: {novel_dir}")
            
            return True
            
        except Exception as e:
            log_error(f"章节提取失败: {e}")
            return False
    
    def _extract_full_chapter_content(self, lines: List[str], start_line: int, end_line: int) -> str:
        """
        提取完整的章节内容
        
        Args:
            lines: 原始文件的所有行
            start_line: 起始行号（1-based）
            end_line: 结束行号（1-based）
            
        Returns:
            str: 章节内容
        """
        content_lines = []
        
        # 转换为 0-based 索引，并跳过标题行
        for i in range(start_line, min(end_line + 1, len(lines))):
            line = lines[i].strip()
            if line:  # 只保留非空行
                content_lines.append(line)
        
        # 第一行通常是章节标题，我们跳过它
        if content_lines and content_lines[0].startswith('第') and ('章' in content_lines[0]):
            content_lines = content_lines[1:]
        
        return '\n'.join(content_lines)
    
    def create_chapter_index(self, output_base_dir: str, novel_name: str) -> bool:
        """
        创建章节索引文件
        
        Args:
            output_base_dir: 输出基础目录
            novel_name: 小说名称
            
        Returns:
            bool: 创建是否成功
        """
        try:
            novel_dir = Path(output_base_dir) / novel_name
            index_file = novel_dir / "章节索引.txt"
            
            if not novel_dir.exists():
                log_warning(f"小说目录不存在: {novel_dir}")
                return False
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(f"《{novel_name}》章节索引\n")
                f.write("=" * 50 + "\n\n")
                
                # 遍历卷目录
                volume_dirs = sorted([d for d in novel_dir.iterdir() if d.is_dir() and d.name.startswith('第') and d.name.endswith('卷')])
                
                for volume_dir in volume_dirs:
                    f.write(f"{volume_dir.name}:\n")
                    
                    # 遍历章节文件
                    chapter_files = sorted([f for f in volume_dir.iterdir() if f.is_file() and f.name.endswith('.txt') and f.name.startswith('第')])
                    
                    for chapter_file in chapter_files:
                        chapter_name = chapter_file.stem  # 去掉 .txt 扩展名
                        f.write(f"  {chapter_name}\n")
                    
                    f.write("\n")
            
            log_info(f"章节索引创建完成: {index_file}")
            return True
            
        except Exception as e:
            log_error(f"创建章节索引失败: {e}")
            return False


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='小说章节提取工具')
    parser.add_argument('input_file', help='输入的小说文件路径')
    parser.add_argument('-o', '--output', help='输出基础目录路径（默认：data/）')
    parser.add_argument('--create-index', action='store_true', help='创建章节索引文件')
    
    args = parser.parse_args()
    
    # 创建提取器
    extractor = ChapterExtractor()
    
    # 执行提取
    success = extractor.extract_chapters_to_files(args.input_file, args.output)
    
    if success and args.create_index:
        # 创建索引文件
        novel_name = Path(args.input_file).stem
        if novel_name.endswith('_utf8'):
            novel_name = novel_name[:-5]
        
        output_dir = args.output or str(PROJECT_ROOT / "data")
        extractor.create_chapter_index(output_dir, novel_name)
    
    if success:
        log_info("章节提取任务完成！")
    else:
        log_error("章节提取任务失败！")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())