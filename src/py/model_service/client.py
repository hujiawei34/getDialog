"""
客户端示例代码

演示如何调用 Qwen3 模型服务的各种接口
"""

import json
import requests
import sseclient
from typing import List, Dict, Any, Optional

class QwenClient:
    """Qwen3 模型服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:19100"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        
    def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """普通聊天"""
        url = f"{self.api_base}/chat"
        
        payload = {
            "message": message,
            "history": history or []
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def chat_stream(self, message: str, history: Optional[List[Dict[str, str]]] = None):
        """流式聊天"""
        url = f"{self.api_base}/chat/stream"
        
        payload = {
            "message": message,
            "history": history or []
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=300)
            response.raise_for_status()
            
            client = sseclient.SSEClient(response)
            
            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        yield data
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            yield {"type": "error", "content": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        url = f"{self.api_base}/health"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        url = f"{self.api_base}/model/info"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def load_model(self) -> Dict[str, Any]:
        """加载模型"""
        url = f"{self.api_base}/model/load"
        
        try:
            response = requests.post(url, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def demo_normal_chat():
    """演示普通聊天"""
    print("=== 普通聊天演示 ===")
    client = QwenClient()
    
    # 检查服务状态
    health = client.health_check()
    print(f"服务状态: {health}")
    
    if health.get("status") != "healthy":
        print("服务不健康，请检查服务状态")
        return
    
    # 进行对话
    message = "你好，请简单介绍一下你自己"
    print(f"用户: {message}")
    
    response = client.chat(message)
    if response.get("success"):
        print(f"助手: {response['response']}")
    else:
        print(f"错误: {response.get('error', '未知错误')}")


def demo_stream_chat():
    """演示流式聊天"""
    print("\n=== 流式聊天演示 ===")
    client = QwenClient()
    
    message = "请解释一下什么是人工智能"
    print(f"用户: {message}")
    print("助手: ", end="", flush=True)
    
    full_response = ""
    for chunk in client.chat_stream(message):
        if chunk.get("type") == "start":
            continue
        elif chunk.get("type") == "chunk":
            content = chunk.get("content", "")
            print(content, end="", flush=True)
            full_response += content
        elif chunk.get("type") == "end":
            print()  # 换行
            break
        elif chunk.get("type") == "error":
            print(f"\n错误: {chunk.get('content', '未知错误')}")
            break


def demo_interactive_chat():
    """演示交互式聊天"""
    print("\n=== 交互式聊天演示 ===")
    client = QwenClient()
    
    history = []
    
    print("开始对话 (输入 'quit' 退出, 输入 '/stream' 开头使用流式模式)")
    
    while True:
        user_input = input("\n你: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if not user_input:
            continue
        
        if user_input.startswith('/stream'):
            # 流式模式
            message = user_input[7:].strip()
            if not message:
                continue
            
            print("助手: ", end="", flush=True)
            
            full_response = ""
            for chunk in client.chat_stream(message, history):
                if chunk.get("type") == "start":
                    continue
                elif chunk.get("type") == "chunk":
                    content = chunk.get("content", "")
                    print(content, end="", flush=True)
                    full_response += content
                elif chunk.get("type") == "end":
                    print()  # 换行
                    break
                elif chunk.get("type") == "error":
                    print(f"\n错误: {chunk.get('content', '未知错误')}")
                    break
            
            if full_response:
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": full_response})
        
        else:
            # 普通模式
            response = client.chat(user_input, history)
            
            if response.get("success"):
                assistant_response = response["response"]
                print(f"助手: {assistant_response}")
                
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": assistant_response})
            else:
                print(f"错误: {response.get('error', '未知错误')}")


if __name__ == "__main__":
    print("Qwen3 模型服务客户端演示")
    print("=" * 50)
    
    try:
        # 演示普通聊天
        demo_normal_chat()
        
        # 演示流式聊天
        demo_stream_chat()
        
        # 演示交互式聊天
        demo_interactive_chat()
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {e}")