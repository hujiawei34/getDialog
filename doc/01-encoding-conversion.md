# 文本编码转换指导文档

## 概述

本文档介绍如何使用项目中的编码转换工具将中文小说文本文件从原始编码（如GB2312）转换为UTF-8编码，以便后续的文本处理工作。

## 问题背景

中文文本文件通常使用多种编码格式，如GB2312、GBK、UTF-8等。不同编码可能导致：
- 文本显示乱码
- 程序读取文件时出现编码错误
- 跨平台兼容性问题

统一使用UTF-8编码可以解决这些问题。

## 工具介绍

### convert_encoding.py

位置：`src/py/step01_encoding/convert_encoding.py`

这是一个Python脚本，用于自动检测和转换文本文件编码。

**主要功能：**
- 自动检测源文件编码
- 将文件转换为UTF-8编码
- 创建备份文件
- 验证转换结果
- 命令行界面操作

## 使用方法

### 基本用法

```bash
# 转换单个文件（会覆盖原文件）
python3 src/py/step01_encoding/convert_encoding.py data/ziyang.txt

# 转换文件并创建备份
python3 src/py/step01_encoding/convert_encoding.py data/ziyang.txt --backup

# 转换到新文件
python3 src/py/step01_encoding/convert_encoding.py data/ziyang.txt -o data/ziyang_utf8.txt

# 指定源文件编码
python3 src/py/step01_encoding/convert_encoding.py data/ziyang.txt -e GB2312
```

### 参数说明

- `input_file`: 输入文件路径（必需）
- `-o, --output`: 输出文件路径（可选，默认覆盖原文件）
- `-e, --encoding`: 指定源文件编码（可选，默认自动检测）
- `--backup`: 创建原文件备份

## 实际操作示例

### 转换ziyang.txt文件

1. **检测文件编码**
   ```bash
   python3 -c "import chardet; f=open('data/ziyang.txt', 'rb'); result=chardet.detect(f.read()); f.close(); print(result)"
   ```
   
   输出：
   ```
   {'encoding': 'GB2312', 'confidence': 0.99, 'language': 'Chinese'}
   ```

2. **执行转换**
   ```bash
   python3 src/py/step01_encoding/convert_encoding.py data/ziyang.txt --backup
   ```
   
   输出：
   ```
   已创建备份文件: data/ziyang.txt.bak
   检测到文件编码: GB2312 (置信度: 0.99)
   转换完成: data/ziyang.txt -> data/ziyang.txt
   源编码: GB2312 -> 目标编码: UTF-8
   验证成功: 文件包含 36504 行，2010091 个字符
   编码转换完成！
   ```

3. **验证转换结果**
   
   转换前（乱码）：
   ```
   ���� ���ߣ���������
   ```
   
   转换后（正常显示）：
   ```
   紫阳 作者：风御九秋
   ```

## 注意事项

1. **备份重要性**
   - 建议始终使用 `--backup` 参数创建备份
   - 备份文件会添加 `.bak` 后缀

2. **编码检测准确性**
   - 工具会显示编码检测的置信度
   - 置信度低于0.8时会显示警告
   - 必要时可使用 `-e` 参数手动指定编码

3. **文件处理**
   - 转换过程中会统一行结束符为Unix格式（LF）
   - 会移除Windows格式的回车符（CRLF -> LF）

4. **错误处理**
   - 如果遇到无法解码的字符，会使用替换字符
   - 转换完成后会自动验证UTF-8格式的正确性

## 依赖要求

确保安装了以下Python包：
```bash
pip install chardet
```

## 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'chardet'**
   ```bash
   pip install chardet
   ```

2. **编码检测失败**
   - 尝试手动指定编码：`-e GB2312` 或 `-e GBK`
   - 检查文件是否为纯文本文件

3. **转换后仍显示乱码**
   - 确认终端支持UTF-8显示
   - 检查文本编辑器的编码设置

4. **文件权限错误**
   - 确保对目标文件有写权限
   - 使用 `chmod` 命令调整文件权限

## 后续步骤

转换完成后，可以进行：
1. 章节结构识别
2. 人物名称提取
3. 对话内容分离
4. 数据格式化输出

这些功能的实现文档将在后续章节中详细说明。