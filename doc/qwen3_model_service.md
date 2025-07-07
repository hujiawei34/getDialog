# Qwen3 模型服务文档

## 概述

Qwen3 模型服务是一个基于 FastAPI 的 Web 服务，提供了与 Qwen3 大语言模型交互的 REST API 接口。该服务支持普通聊天和流式聊天两种模式，其中流式聊天可以实时显示模型的思考过程。

## 主要特性

- 🚀 **一次加载，多次使用**：模型只需加载一次，避免重复加载的开销
- 💬 **普通聊天模式**：传统的请求-响应模式
- 🌊 **流式聊天模式**：支持 Server-Sent Events，实时显示模型思考过程
- 🔧 **自动设备选择**：智能选择可用内存最多的 GPU 设备
- 📊 **健康检查**：提供服务状态监控接口
- 📝 **完整文档**：自带 Swagger UI 文档

## 目录结构

```
src/py/model_service/
├── __init__.py           # 模块初始化文件
├── model_manager.py      # 模型管理器，负责加载和管理 Qwen3 模型
├── api_routes.py         # API 路由定义，包含所有接口
├── server.py             # FastAPI 服务器主程序
├── client.py             # 客户端示例代码
└── start_service.py      # 启动脚本
```

## 安装依赖

确保已安装所需依赖：

```bash
pip install fastapi uvicorn[standard] sseclient-py pynvml
```

或使用项目的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 启动服务

### 基本启动

```bash
cd /data/hjw/github/getDialog
python src/py/model_service/start_service.py
```

### 自定义配置启动

```bash
# 自定义主机和端口
python src/py/model_service/start_service.py --host 0.0.0.0 --port 19100

# 启用开发模式（热重载）
python src/py/model_service/start_service.py --reload

# 设置日志级别
python src/py/model_service/start_service.py --log-level debug
```

### 启动参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | 0.0.0.0 | 服务器主机地址 |
| `--port` | 19100 | 服务器端口 |
| `--workers` | 1 | 工作进程数 |
| `--reload` | False | 启用热重载（开发模式） |
| `--log-level` | info | 日志级别 (critical/error/warning/info/debug) |

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:19100/api/v1`
- **Content-Type**: `application/json`

### 1. 普通聊天接口

**接口**: `POST /api/v1/chat`

**描述**: 发送消息并获取完整响应

**请求体**:
```json
{
  "message": "你好，请介绍一下你自己",
  "history": [
    {
      "role": "user",
      "content": "之前的用户消息"
    },
    {
      "role": "assistant", 
      "content": "之前的助手回复"
    }
  ]
}
```

**响应体**:
```json
{
  "response": "你好！我是Qwen，一个由阿里云开发的大语言模型...",
  "success": true,
  "error": null
}
```

**curl 示例**:
```bash
curl -X POST "http://localhost:19100/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "你好，请介绍一下你自己",
       "history": []
     }'
```

### 2. 流式聊天接口

**接口**: `POST /api/v1/chat/stream`

**描述**: 发送消息并实时接收响应流，可以看到模型的思考过程

**请求体**: 同普通聊天接口

**响应**: Server-Sent Events 流

**响应事件格式**:
```javascript
// 开始事件
data: {"type": "start", "content": ""}

// 文本块事件（多个）
data: {"type": "chunk", "content": "你好"}
data: {"type": "chunk", "content": "！我是"}
data: {"type": "chunk", "content": "Qwen..."}

// 结束事件
data: {"type": "end", "content": ""}

// 错误事件（如果出错）
data: {"type": "error", "content": "错误信息"}
```

**curl 示例**:
```bash
curl -X POST "http://localhost:19100/api/v1/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "请解释一下什么是人工智能",
       "history": []
     }'
```

### 3. 健康检查接口

**接口**: `GET /api/v1/health`

**描述**: 检查服务和模型的健康状态

**响应体**:
```json
{
  "status": "healthy",
  "message": "模型正常"
}
```

### 4. 模型信息接口

**接口**: `GET /api/v1/model/info`

**描述**: 获取模型的基本信息

**响应体**:
```json
{
  "model_name": "Qwen/Qwen3-8B",
  "device": "cuda:1",
  "is_loaded": true,
  "model_size": 19100000000
}
```

### 5. 模型加载接口

**接口**: `POST /api/v1/model/load`

**描述**: 手动加载模型（通常服务启动时会自动加载）

**响应体**:
```json
{
  "status": "loaded",
  "message": "模型加载完成"
}
```

## 客户端使用示例

### Python 客户端

项目提供了完整的 Python 客户端示例 (`client.py`)：

```python
from model_service.client import QwenClient

# 创建客户端
client = QwenClient(base_url="http://localhost:19100")

# 普通聊天
response = client.chat("你好")
print(response)

# 流式聊天
for chunk in client.chat_stream("请解释一下人工智能"):
    if chunk.get("type") == "chunk":
        print(chunk["content"], end="", flush=True)
```

### JavaScript 客户端

```javascript
// 普通聊天
async function chat(message) {
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            history: []
        })
    });
    
    const data = await response.json();
    return data.response;
}

// 流式聊天
function chatStream(message) {
    const eventSource = new EventSource('/api/v1/chat/stream');
    
    fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            history: []
        })
    });
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'chunk') {
            console.log(data.content);
        }
    };
}
```

## 运行客户端示例

```bash
# 运行交互式客户端
python src/py/model_service/client.py
```

客户端支持以下功能：
- 普通聊天演示
- 流式聊天演示  
- 交互式聊天（输入 `/stream` 开头使用流式模式）
- 输入 `quit` 退出

## 服务监控

### 访问 Swagger UI 文档

服务启动后，可以通过以下地址访问自动生成的 API 文档：

- **Swagger UI**: `http://localhost:19100/docs`
- **ReDoc**: `http://localhost:19100/redoc`

### 健康检查

```bash
# 简单健康检查
curl http://localhost:19100/health

# 详细健康检查（包含模型状态）
curl http://localhost:19100/api/v1/health
```

### 查看模型信息

```bash
curl http://localhost:19100/api/v1/model/info
```

## GPU 设备选择

服务会自动选择最佳的 GPU 设备：

1. **优先策略**: 使用 `pynvml` 检测所有 GPU 的实际可用内存，选择可用内存最多的设备
2. **回退策略**: 如果 `pynvml` 不可用，固定使用 GPU 3
3. **CPU 回退**: 如果没有可用的 CUDA 设备，使用 CPU

## 性能优化建议

1. **内存管理**: 服务启动后模型会持续占用 GPU 内存，确保有足够的显存
2. **并发处理**: 默认使用单进程，如需高并发可增加 `--workers` 参数
3. **网络配置**: 生产环境建议配置反向代理（如 Nginx）
4. **监控告警**: 建议对 `/api/v1/health` 接口设置监控告警

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查 GPU 内存是否足够
   - 确认模型文件是否完整下载
   - 查看日志中的详细错误信息

2. **服务无法启动**
   - 检查端口是否被占用
   - 确认依赖包是否正确安装
   - 查看 Python 路径配置

3. **流式响应中断**
   - 检查网络连接稳定性
   - 确认客户端支持 Server-Sent Events
   - 查看服务器日志中的错误信息

### 日志查看

服务启动时会显示详细的日志信息，包括：
- GPU 设备选择过程
- 模型加载进度
- API 请求处理情况
- 错误信息和堆栈跟踪

## 扩展开发

### 添加新的 API 接口

1. 在 `api_routes.py` 中添加新的路由函数
2. 在 `model_manager.py` 中添加相应的模型处理逻辑
3. 更新客户端代码以支持新接口

### 集成到其他项目

可以将 `model_service` 模块作为独立的服务集成到其他项目中：

```python
from model_service.client import QwenClient

# 在你的项目中使用
client = QwenClient(base_url="http://your-qwen-service:19100")
response = client.chat("你的问题")
```

## 版本信息

- **当前版本**: 1.0.0
- **支持的模型**: Qwen/Qwen3-8B
- **Python 版本要求**: >= 3.8
- **主要依赖**: FastAPI, PyTorch, Transformers, ModelScope