#!/usr/bin/env python3
"""
文本编码转换工具
将 GB2312 编码的中文小说文件转换为 UTF-8 编码
"""

import os
import chardet
import argparse


def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result


def convert_to_utf8(input_file, output_file=None, source_encoding=None):
    """
    将文件转换为 UTF-8 编码
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径，如果为None则覆盖原文件
        source_encoding: 源文件编码，如果为None则自动检测
    """
    # 检测源文件编码
    if source_encoding is None:
        encoding_info = detect_encoding(input_file)
        source_encoding = encoding_info['encoding']
        confidence = encoding_info['confidence']
        print(f"检测到文件编码: {source_encoding} (置信度: {confidence:.2f})")
        
        if confidence < 0.8:
            print("警告: 编码检测置信度较低，转换可能出现问题")
    
    # 设置输出文件路径
    if output_file is None:
        output_file = input_file
    
    try:
        # 读取源文件
        with open(input_file, 'r', encoding=source_encoding, errors='replace') as f:
            content = f.read()
        
        # 写入UTF-8文件
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            f.write(content)
        
        print(f"转换完成: {input_file} -> {output_file}")
        print(f"源编码: {source_encoding} -> 目标编码: UTF-8")
        
        # 验证转换结果
        verify_conversion(output_file)
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False
    
    return True


def verify_conversion(file_path):
    """验证转换结果"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            line_count = len(content.splitlines())
            char_count = len(content)
            print(f"验证成功: 文件包含 {line_count} 行，{char_count} 个字符")
    except UnicodeDecodeError as e:
        print(f"验证失败: UTF-8 解码错误 - {e}")
    except Exception as e:
        print(f"验证失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='将中文文本文件转换为UTF-8编码')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('-e', '--encoding', help='指定源文件编码（默认自动检测）')
    parser.add_argument('--backup', action='store_true', help='创建原文件备份')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在 - {args.input_file}")
        return
    
    # 创建备份
    if args.backup:
        backup_file = args.input_file + '.bak'
        import shutil
        shutil.copy2(args.input_file, backup_file)
        print(f"已创建备份文件: {backup_file}")
    
    # 执行转换
    success = convert_to_utf8(args.input_file, args.output, args.encoding)
    
    if success:
        print("编码转换完成！")
    else:
        print("编码转换失败！")


if __name__ == '__main__':
    main()