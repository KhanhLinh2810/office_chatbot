from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class LLMBase(ABC):
    """
    Base class for all LLM providers.
    Handles common functionality and delegates provider-specific logic to subclasses.
    """

    @abstractmethod
    def generate_response(
        self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, tool_choice: str = "auto", **kwargs
    ):
        """
        Generate a response based on the given messages.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".
            **kwargs: Additional provider-specific parameters.

        Returns:
            str or dict: The generated response.
        """
        pass

        """
        Get common parameters that most providers use.

        Returns:
            Dict: Common parameters dictionary.
        """
        params = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }

        # Add provider-specific parameters from kwargs
        params.update(kwargs)

        return params