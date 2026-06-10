import requests
import json
from django.conf import settings

def call_aliyun_llm(prompt, system_prompt=None, temperature=0.7, max_tokens=1024):
    """
    调用阿里云 DashScope 兼容模式的 LLM API
    :param prompt: 用户输入的提示词
    :param system_prompt: 系统提示词（可选）
    :param temperature: 温度参数 (0~1)
    :param max_tokens: 最大输出 token 数
    :return: 模型返回的文本内容，失败返回 None
    """
    # 从 settings 中获取配置（也可以在 settings.py 中定义）
    api_key = getattr(settings, "ALIYUN_API_KEY", "")
    if not api_key:
        print("ALIYUN_API_KEY is not configured")
        return None
    # 如果AI功能不能正常使用，可能是密钥额度已满，可以换用sk-5c33f5da98fa478ba85844f7e66521a9
    base_url = getattr(settings, "ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    url = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "qwen-plus",  # 可换成 qwen-turbo, qwen-max 等
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # 兼容 OpenAI 格式返回
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"阿里云 LLM API 调用失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"响应内容: {e.response.text}")
        return None
