from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAIProvider(ABC):
    """
    Base interface for AI providers.

    Providers must implement the analyze method.
    The rest of the AI engine should not depend on
    a specific AI runtime or model.
    """

    @abstractmethod
    def analyze(
        self,
        content: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Analyze text content and return structured AI results.
        """
        raise NotImplementedError
