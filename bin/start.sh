#!/bin/bash

# getDialog项目执行入口脚本
# 设置Python路径并调用main.py

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_HOME="$PROJECT_ROOT/src/py"

# 设置Python路径
export PYTHONPATH="$PYTHON_HOME:$PYTHONPATH"

# 切换到Python源码目录
cd "$PYTHON_HOME"

# 调用main.py，传递所有参数
python main.py "$@"