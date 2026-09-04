"""
LLM客户端工具 
一个封装好的大模型调用工具 支持智谱 GLM 和 DeepSeek


用法：
1.先注册账号拿 API Key

2. 复制 .env.example 为.env 填上API Key

3. 在其他脚本中调用
    from utils.llm_client import LLMClient
    client = LLMClient(provider="zhipu")  # 或者provider="deepseek"
    answer = client.chat("你好")
    print(answer)

技术点：
 - 类封装
 - .env配置管理(python-dotenv)
 - request POST 请求
 - 异常处理 + 自动重试
 - 多 provider 抽象（统一接口）

注意： 永远不要把.env 提交到github!!    

"""

import os
import time
import json
import requests

# 读取.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("未安装python-dotenv,运行 pip install python-dotenv")


# 各家API 的配置 (endpoint + 默认模型名)

PROVIDER_CONFIG = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "default_model": "glm-4-flash",
        "env_key": "ZHIPU_API_KEY"
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY"
    }
}


class LLMClient:
    """统一的LLM 调用客户端"""

    def __init__(self, provider: str = "zhipu", model: str = None, temperature: float = 0.7):
        """
        初始化客户端
        param provider: 服务商 zhipu 还是deepseek
        param model: 模型名 默认用该服务商推荐的模型
        param temperature: 输出随机性 0-1 越小越稳定
        """
        if provider not in PROVIDER_CONFIG:
            raise ValueError(f"不支持的provider：{provider},可选：{list(PROVIDER_CONFIG.keys())}")

        config = PROVIDER_CONFIG[provider]
        self.base_url = config["base_url"]
        self.model = model or config["default_model"]
        self.temperature = temperature

        # 从环境变量读取API Key
        self.api_key = os.getenv(config["env_key"])
        if not self.api_key:
            print(f"未找到{config['env_key']} 环境变量,请检查 .env 文件")

    def chat(
        self,
        message,
        temperature: float = None,
        max_retries: int = 3,
        response_format: dict = None,
    ) -> str:
        """
        发送对话请求 （核心方法）
        param messages: 消息列表，如[{"role":"user", "content":"你好"}]
                                role 可以是system user assistant
        param temperature
        param max_retries:失败重试次数
        param response_format: 如{"type":"json_object"} 强制json输出
        return 模型的回复文本
        """

        # 兼容 “直接传字符串” 的写法： 自动转成user消息
        if isinstance(message, str):
            message = [{"role": "user", "content": message}]

        payload = {
            "model": self.model,
            "messages": message,   # 注意：OpenAI / 智谱 标准字段是 messages（复数）
            "temperature": temperature if temperature is not None else self.temperature,
        }

        if response_format:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 重试循环
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                elif resp.status_code == 401:
                    print("API_Key错误，请检查 .env 里的密钥")
                    return None
                elif resp.status_code == 429:
                    print(f"请求太频繁,第{attempt}次重试。。。")
                else:
                    print(f"请求失败，{resp.status_code}: {resp.text[:200]}")
            except requests.exceptions.Timeout:
                print(f"请求超时，第{attempt}次重试")
            except requests.exceptions.ConnectTimeout:
                print(f"网络连接失败，请检查网络,第{attempt}次重试...")
            except Exception as e:
                print(f"未知错误：{e}")

            # 重试前等待 指数退避 2s 4s 6s
            if attempt < max_retries:
                time.sleep(2 * attempt)

        print("重试次数用尽，调用失败")
        return None

    # -------------便捷方法-------------------
    def chat_single(self, prompt: str, system: str = None, **kwargs) -> str:
        """单条消息调用（最常用）"""
        message = []
        if system:
            message.append({"role": "system", "content": system})
        message.append({"role": "user", "content": prompt})
        return self.chat(message, **kwargs)

    def chat_json(self, prompt: str, system: str = None, **kwargs) -> dict:
        """调用模型并解析JSON 返回（用于结构化提取）"""
        message = []
        if system:
            message.append({"role": "system", "content": system})
        message.append({"role": "user", "content": prompt})

        result = self.chat(
            message=message,
            response_format={"type": "json_object"},
            **kwargs,
        )
        if result is None:
            return None

        try:
            return json.loads(result)   # json.loads 解析字符串；json.load 是读文件
        except json.JSONDecodeError:
            print(f"模型返回的不是合法JSON： {result[:100]}...")
            return None


if __name__ == "__main__":
    client = LLMClient(provider="zhipu")
    answer = client.chat_single("你好，请用一句话介绍你自己")
    print("回应：", answer)
