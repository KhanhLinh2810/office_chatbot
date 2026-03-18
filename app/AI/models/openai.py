import json
import logging
import os
import re
from typing import Dict, List, Optional
from openai import OpenAI
from json_repair import repair_json

from app.AI.models.llm_base import LLMBase
from app.core.settings import settings


def extract_json(text):
    """
    Extracts JSON content from a string, removing enclosing triple backticks and optional 'json' tag if present.
    If no code block is found, returns the text as-is.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text  # assume it's raw JSON
    return json_str

class OpenAILLM(LLMBase):
    # "gpt-4.1-nano-2025-04-14" 
    def __init__(self, model="Qwen/Qwen2.5-7B-Instruct", temperature=0.2, max_tokens=1024, top_p=0.3, top_k=5, enable_vision=False, vision_details="auto", http_client=None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.enable_vision = enable_vision
        self.vision_details = vision_details
        self.http_client_proxies = http_client
        
        # Khởi tạo client
        api_key = settings.OPENAI_API_KEY
        base_url = settings.OPENAI_BASE_URL
        self.client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        self._initialized = True

    def _parse_response(self, response, tools):
        if not response or not response.choices:
            return {"content": None, "tool_calls": []} if tools else None

        message = response.choices[0].message
        processed_response = {
            "content": getattr(message, "content", None),
            "tool_calls": [],
        }
        # print(processed_response["content"])

        if not tools:
            return processed_response["content"]

        # 1. Kiểm tra Native Tool Calls (OpenAI Standard)
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                try:
                    # Giả định extract_json xử lý chuỗi JSON
                    args = json.loads(tool_call.function.arguments)
                    processed_response["tool_calls"].append({
                        "name": tool_call.function.name,
                        "arguments": args,
                    })
                except Exception as e:
                    logging.error(f"Error parsing native tool call: {e}")

        # 2. Kiểm tra Text-based Tool Calls (Fallback cho Qwen/Llama)
        # Nếu tool_calls vẫn rỗng nhưng content có dữ liệu
        elif processed_response["content"]:
            try:
                # Tìm nội dung nằm giữa <tool_call> và </tool_call>
                pattern = r"<tool_call>(.*?)</tool_call>"
                match = re.search(pattern, processed_response["content"], re.DOTALL)
                # print(match)
                
                if match:
                    raw_json = match.group(1).strip()
                    # print(raw_json)
                    tool_data = json.loads(repair_json(raw_json))
                    # print(tool_data)
                    
                    # Qwen thường trả về format: {"name": "...", "arguments": {...}}
                    processed_response["tool_calls"].append({
                        "name": tool_data.get("name"),
                        "arguments": tool_data.get("arguments"),
                    })
            except Exception as e:
                logging.error(f"Error parsing text-based tool call: {e}")

        return processed_response

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs,
    ):
        """
        Tạo phản hồi từ OpenAI hoặc OpenRouter.
        """
        # 1. Thiết lập tham số mặc định
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            **kwargs
        }

        # 2. Xử lý logic OpenRouter (nếu có API Key trong env)
        if os.getenv("OPENROUTER_API_KEY"):
            # Nếu class có thuộc tính bổ sung cho OpenRouter
            if hasattr(self, "site_url") and hasattr(self, "app_name"):
                params["extra_headers"] = {
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name,
                }
        
        # 3. Định dạng kết quả và Tools
        if response_format:
            params["response_format"] = response_format
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        # 4. Gọi API
        try:
            response = self.client.chat.completions.create(**params)
            parsed_response = self._parse_response(response, tools)
            
            # 5. Callback xử lý sau response (nếu có)
            # if hasattr(self, "config") and getattr(self.config, "response_callback", None):
            #     try:
            #         self.response_callback(self, response, params)
            #     except Exception as e:
            #         logging.error(f"Error in response callback: {e}")
                    
            return parsed_response

        except Exception as e:
            logging.error(f"OpenAI API Error: {e}")
            raise e