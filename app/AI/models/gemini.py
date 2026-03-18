import os
import threading

from typing import Dict, List, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError("The 'google-genai' library is required. Please install it using 'pip install google-genai'.")

from app.AI.models.llm_base import LLMBase
from app.core.settings import settings

class GeminiLLM(LLMBase):
    #  co the thu dung connection pool voi ket noi nay de cai thien hieu nang
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GeminiLLM, cls).__new__(cls)
        return cls._instance

    def __init__(self, model = "gemini-2.5-flash", temperature=0.7, max_tokens=1024, top_p=0.9):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.model = "gemini-2.5-flash"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._initialized = True

    def _parse_response(self, response, tools):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.

        Returns:
            str or dict: The processed response.
        """
        if response.candidates and hasattr(response.candidates, "content"):
            content = response.candidates[0].content
        else:
            return ""
        
        if tools:
            processed_response = {
                "content": None,
                "tool_calls": [],
            }

            # Extract content from the first candidate
            if hasattr(content, "parts") and content.parts:
                for part in content.parts:
                    if hasattr(part, "text") and part.text:
                        processed_response["content"] = part.text
                        break
                    
            # Extract function calls
            if hasattr(content, "parts") and content.parts:
                for part in content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fn = part.function_call
                        processed_response["tool_calls"].append(
                            {
                                "name": fn.name,
                                "arguments": dict(fn.args) if fn.args else {},
                            }
                        )

            return processed_response
        else:
            if hasattr(content, "parts") and content.parts:
                for part in content.parts:
                    if hasattr(part, "text") and part.text:
                        return part.text
            return ""

    def _reformat_messages(self, messages: List[Dict[str, str]]):
        """
        Reformat messages for Gemini.

        Args:
            messages: The list of messages provided in the request.

        Returns:
            tuple: (system_instruction, contents_list)
        """
        system_instruction = None
        contents = []

        for message in messages:
            if message["role"] == "system":
                system_instruction = message["content"]
            else:
                content = types.Content(
                    parts=[types.Part(text=message["content"])],
                    role=message["role"],
                )
                contents.append(content)

        return system_instruction, contents

    def _reformat_tools(self, tools: Optional[List[Dict]]):
        """
        Reformat tools for Gemini.

        Args:
            tools: The list of tools provided in the request.

        Returns:
            list: The list of tools in the required format.
        """

        def remove_additional_properties(data):
            """Recursively removes 'additionalProperties' from nested dictionaries."""
            if isinstance(data, dict):
                filtered_dict = {
                    key: remove_additional_properties(value)
                    for key, value in data.items()
                    if not (key == "additionalProperties")
                }
                return filtered_dict
            else:
                return data

        if tools:
            function_declarations = []
            for tool in tools:
                func = tool["function"].copy()
                cleaned_func = remove_additional_properties(func)

                function_declaration = types.FunctionDeclaration(
                    name=cleaned_func["name"],
                    description=cleaned_func.get("description", ""),
                    parameters=cleaned_func.get("parameters", {}),
                )
                function_declarations.append(function_declaration)

            tool_obj = types.Tool(function_declarations=function_declarations)
            return [tool_obj]
        else:
            return None

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ):
        """
        Generate a response based on the given messages using Gemini.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format for the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """

        # Extract system instruction and reformat messages
        system_instruction, contents = self._reformat_messages(messages)

        # Prepare generation config
        config_params = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        # Add system instruction to config if present
        if system_instruction:
            config_params["system_instruction"] = system_instruction

        if response_format is not None and response_format["type"] == "json_object":
            config_params["response_mime_type"] = "application/json"
            if "schema" in response_format:
                config_params["response_schema"] = response_format["schema"]

        if tools:
            formatted_tools = self._reformat_tools(tools)
            config_params["tools"] = formatted_tools

            if tool_choice:
                if tool_choice == "auto":
                    mode = types.FunctionCallingConfigMode.AUTO
                elif tool_choice == "any":
                    mode = types.FunctionCallingConfigMode.ANY
                else:
                    mode = types.FunctionCallingConfigMode.NONE

                tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=mode,
                        allowed_function_names=(
                            [tool["function"]["name"] for tool in tools] if tool_choice == "any" else None
                        ),
                    )
                )
                config_params["tool_config"] = tool_config

        generation_config = types.GenerateContentConfig(**config_params)
        response = self.client.models.generate_content(
            model=self.model, contents=contents, config=generation_config
        )

        return self._parse_response(response, tools)