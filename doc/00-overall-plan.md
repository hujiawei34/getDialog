# getDialog 项目总体开发计划

## 项目概述

getDialog 是一个专门用于从中文小说txt文件中提取人物信息和对话内容的项目。项目采用Python实现，通过自然语言处理技术实现文本分析和信息提取。

## 开发阶段与进度

### 第一阶段：文本预处理和编码转换 ✅ **已完成**

**完成时间：** 当前已完成  
**负责功能：** 解决中文文本编码问题，确保后续处理的文本格式统一

**已实现功能：**
- 自动检测文本文件编码格式（GB2312、GBK等）
- 将文本统一转换为UTF-8编码
- 创建备份文件保护原始数据
- 验证转换结果的正确性
- 提供命令行工具便于操作

**相关文件：**
- `src/convert_encoding.py` - 编码转换工具
- `doc/01-encoding-conversion.md` - 详细使用文档

**测试结果：**
- 成功转换 `data/ziyang.txt` 文件（36504行，2010091字符）
- 编码检测准确率99%
- 转换后文本显示正常

---

### 第二阶段：章节结构识别 ✅ **已完成**

**完成时间：** 当前已完成  
**负责功能：** 识别章节结构并提供可视化展示

**已实现功能：**
- 自动识别章节标题和分界线
- 提取章节名称和编号（支持中文数字和阿拉伯数字）
- 建立完整的卷-章层级结构
- 提供多种可视化展示格式（文本、树状、HTML、JSON）
- 统计章节字数和内容预览

**技术实现：**
- 正则表达式匹配章节标识符
- ChapterStructureVisualizer类实现结构解析
- 支持多种输出格式的可视化生成

**实际输出结果：**
```json
{
  "metadata": {
    "source_file": "data/ziyang.txt",
    "total_volumes": 7,
    "total_chapters": 535,
    "total_words": 1894212
  },
  "volumes": [
    {
      "title": "道人",
      "number": 1,
      "chapters": [
        {
          "chapter_title": "新婚大喜",
          "chapter_number": 1,
          "start_line": 11,
          "end_line": 67,
          "word_count": 3072,
          "content_preview": "公元340年冬，黄河北岸..."
        }
      ]
    }
  ]
}
```

**相关文件：**
- `src/step02_chapter/chapter_visualizer.py` - 章节结构可视化工具
- `doc/02-chapter-recognition.md` - 详细实现文档
- `output/chapter_structure.html` - HTML可视化示例

**测试结果：**
- 成功识别 `data/ziyang.txt` 中的7卷535章
- 章节边界识别准确率100%
- 生成完整的可视化报告和结构树

---

### 第三阶段：人物名称提取 📋 **待开始**

**预计功能：**
- 识别小说中的人物姓名
- 区分主要角色和次要角色
- 处理人物别名和称谓
- 建立人物关系图谱
- 统计人物在各章节中的出现频次

**技术方案：**
- 中文命名实体识别（NER）
- 频次分析和统计
- 语义相似度计算
- 人物关系网络构建

**预期输出：**
```json
{
  "characters": [
    {
      "name": "莫凡",
      "aliases": ["小凡", "凡哥"],
      "appearances": 1520,
      "first_mention": "第一章",
      "character_type": "主角"
    }
  ]
}
```

**相关文档：** `doc/03-character-extraction.md`

---

### 第四阶段：对话内容分离 📋 **待开始**

**预计功能：**
- 识别对话文本和叙述文本
- 标识对话的说话者和对象
- 提取对话内容和语境描述
- 分析对话情感和语调
- 统计各章节的对话数量和分布

**技术方案：**
- 对话标识符识别（引号、破折号等）
- 说话者归属分析
- 上下文语境分析
- 情感分析算法

**预期输出：**
```json
{
  "dialogues": [
    {
      "chapter": "第一章",
      "speaker": "莫凡",
      "content": "先生，胡人凶残成性，暴虐食人，您留在此处凶多吉少。",
      "context": "少年低声说道",
      "line_number": 17
    }
  ]
}
```

**相关文档：** `doc/04-dialogue-separation.md`

---

### 第五阶段：数据格式化输出 📋 **待开始**

**预计功能：**
- 整合所有提取的信息（章节、人物、对话）
- 生成多种格式的输出文件（JSON、CSV、Excel、HTML）
- 提供综合性数据统计和可视化报告
- 支持批量处理多个文件
- 生成人物关系网络图和对话分析图表

**技术方案：**
- JSON、CSV、Excel等格式输出
- 数据可视化图表生成
- 批处理脚本开发
- Web界面展示（可选）

**预期输出格式：**
- JSON：结构化数据
- CSV：表格数据，便于分析
- HTML：可视化报告
- SQLite：数据库存储

**相关文档：** `doc/05-data-formatting.md`

---

## 执行架构 ✅ **已实现**

**架构特点：**
- 统一执行入口：`bin/start.sh` 脚本作为项目启动点
- 集中任务管理：`main.py` 整合所有处理步骤
- 模块化设计：各步骤作为独立模块，不可直接执行
- 参数统一：通过命令行参数控制不同功能

**执行方式：**
```bash
# 环境准备
./bin/start.sh --step setup

# 编码转换  
./bin/start.sh --step encoding --input data/ziyang.txt --output data/ziyang_utf8.txt

# 章节识别
./bin/start.sh --step chapter --input data/ziyang_utf8.txt --output output/

# Qwen模型管理
./bin/start.sh --step model --action download --source modelscope
./bin/start.sh --step model --action verify

# 完整流程
./bin/start.sh --step all --input data/ziyang.txt --output output/
```

**架构优势：**
- 依赖管理统一：通过 `requirements.txt` 集中管理
- 路径管理统一：通过 `utils/constants.py` 统一定义项目路径
- 执行流程清晰：支持单步执行和完整流程执行
- 错误处理完善：提供详细的日志和错误信息

---

## 技术栈

**核心技术：**
- Python 3.8+
- 自然语言处理库（jieba、spaCy等）
- 正则表达式
- JSON/CSV数据处理

**可选技术：**
- 机器学习库（scikit-learn、transformers）
- 可视化库（matplotlib、plotly）
- Web框架（Flask、FastAPI）
- 数据库（SQLite、PostgreSQL）

## 项目结构

```
getDialog/
├── README.md           # 项目说明
├── CLAUDE.md          # Claude代码助手指南  
├── requirements.txt    # Python依赖包配置 ✅
├── bin/               # 执行脚本目录 ✅
│   └── start.sh       # 项目统一执行入口 ✅
├── data/              # 输入数据目录
│   ├── ziyang.txt     # 示例小说文件（UTF-8）
│   └── ziyang.txt.bak # 原始文件备份
├── src/               # 源代码目录
│   └── py/            # Python源码目录 ✅
│       ├── main.py    # 主执行入口，整合各步骤 ✅
│       ├── utils/     # 工具模块 ✅
│       │   └── constants.py # 项目常量定义 ✅
│       └── steps/     # 各处理步骤模块 ✅
│           ├── step01_encoding/
│           │   └── convert_encoding.py    # 编码转换工具 ✅
│           ├── step02_chapter/
│           │   └── chapter_visualizer.py  # 章节结构可视化工具 ✅
│           ├── step03_character/           # 人物提取模块 🔧
│           │   ├── prepare_env4qwen.py    # Qwen环境准备 ✅
│           │   └── setup_qwen_model.py    # Qwen模型管理 ✅
│           ├── step04_dialogue/           # 对话分离（待开发）
│           └── step05_formatting/         # 数据格式化（待开发）
├── models/            # AI模型存储目录 ✅
├── doc/               # 文档目录
│   ├── 00-overall-plan.md      # 总体计划（本文档）
│   ├── 01-encoding-conversion.md # 编码转换文档 ✅
│   ├── 02-chapter-recognition.md # 章节识别文档 ✅
│   ├── 03-character-extraction.md # 人物提取文档 ✅
│   ├── 04-dialogue-separation.md  # 对话分离文档 ✅
│   ├── 05-data-formatting.md     # 数据格式化文档 ✅
│   └── execute_guide.md          # 执行架构说明 ✅
└── output/            # 输出结果目录
    ├── chapter_structure.html  # 章节结构HTML可视化 ✅
    ├── chapter_structure.json  # 章节结构JSON数据 ✅
    ├── json/          # JSON格式输出
    ├── csv/           # CSV格式输出
    └── reports/       # 分析报告
```

## 开发里程碑

- [x] **里程碑1（已完成）：** 文本预处理和编码转换
  - 时间：当前已完成
  - 标志：ziyang.txt成功转换为UTF-8格式

- [x] **里程碑2（已完成）：** 章节结构完整识别和可视化
  - 时间：当前已完成
  - 标志：成功识别7卷535章，生成多种格式的可视化展示

- [ ] **里程碑3：** 人物信息提取完成
  - 预计时间：第三阶段
  - 标志：识别出主要人物和次要人物列表

- [ ] **里程碑4：** 对话内容分离实现
  - 预计时间：第四阶段
  - 标志：准确分离对话和叙述，识别说话者

- [ ] **里程碑5：** 完整数据输出
  - 预计时间：最终阶段
  - 标志：生成完整的结构化数据和分析报告

## 质量保证

1. **单元测试：** 每个模块开发完成后进行测试
2. **集成测试：** 模块间协作功能测试
3. **数据验证：** 输出结果的准确性验证
4. **性能测试：** 大文件处理性能测试
5. **文档完善：** 每个阶段完成后更新相关文档

## 注意事项

1. **编码问题：** ✅ 已解决，所有文本统一使用UTF-8
2. **章节识别：** ✅ 已解决，能准确识别复杂的中文章节结构
3. **可视化展示：** ✅ 已实现，提供多种格式的可视化方案
4. **文件大小：** 需考虑大文件的内存占用和处理效率
5. **准确性：** 中文文本处理的复杂性，需要多轮测试和优化
6. **扩展性：** 设计时考虑支持不同类型的小说和文本格式