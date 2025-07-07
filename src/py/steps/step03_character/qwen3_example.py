import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from utils.log_util import default_logger as logger

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    logger.warning("pynvml 不可用，将使用简单的 GPU 选择策略")

def get_best_gpu():
    """选择可用内存最多的 GPU 设备"""
    if not torch.cuda.is_available():
        return None
    
    best_gpu = 0
    max_free_memory = 0
    
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            for i in range(torch.cuda.device_count()):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                total_memory = meminfo.total
                used_memory = meminfo.used
                free_memory = meminfo.free
                
                logger.info(f"GPU {i}: 总内存 {total_memory / 1024**3:.2f} GB, 已用 {used_memory / 1024**3:.2f} GB, 可用 {free_memory / 1024**3:.2f} GB")
                
                if free_memory > max_free_memory:
                    max_free_memory = free_memory
                    best_gpu = i
            
            logger.info(f"选择 GPU {best_gpu} (可用内存: {max_free_memory / 1024**3:.2f} GB)")
            return best_gpu
            
        except Exception as e:
            logger.error(f"使用 pynvml 检测 GPU 时出错: {e}")
            # 回退到简单策略
    
    # 简单策略：使用固定 GPU 3
    logger.info("使用简单的 GPU 选择策略，固定选择 GPU 3")
    return 3

class QwenChatbot:
    def __init__(self, model_name="Qwen/Qwen3-8B"):
        model_kwargs = {
            "trust_remote_code": True,
        }
        
        # 自动选择内存最多的 GPU
        best_gpu = get_best_gpu()
        if best_gpu is not None:
            model_kwargs.update(
                {
                    "torch_dtype": torch.float16,
                    "device_map": {"": best_gpu},
                }
            )
        else:
            logger.warning("未检测到 CUDA 设备，使用 CPU")
            model_kwargs.update({"torch_dtype": torch.float32})        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_name,**model_kwargs)
        self.history = []

    def generate_response(self, user_input):
        messages = self.history + [{"role": "user", "content": user_input}]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        result=self.model.generate(**inputs, max_new_tokens=32768)
        # logger.info(f"generate result:{result}")
        response_ids = result[0][len(inputs["input_ids"][0]):].tolist()
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)

        # Update history
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})

        return response

    def generate_response_stream(self, user_input):
        """流式输出响应，可以实时看到模型的思考过程"""
        messages = self.history + [{"role": "user", "content": user_input}]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # 使用流式生成
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=32768)
        
        import threading
        thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        generated_text = ""
        for new_text in streamer:
            generated_text += new_text
            print(new_text, end='', flush=True)
        
        thread.join()
        
        # Update history
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": generated_text})
        
        return generated_text

if __name__ == "__main__":
    chatbot = QwenChatbot()
    file_path = "/data/hjw/github/getDialog/data/ziyang/第1卷/第1章.txt"
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    prompt = f"""你是一个专业的中文网络小说分析专家。请仔细分析以下文本，提取所有人物姓名。
最终答案：
[列出提取的人物姓名，每行一个]

文本内容(以========分割)：
========
{text}
========
请开始分析："""
    logger.info(f"promt:{prompt}")
    logger.info("=======start=========")
    response_2 = chatbot.generate_response_stream(prompt)
    logger.info(response_2)
    logger.info("========end ==========")