import json
from typing import Any, Dict
from urllib.error import URLError
from urllib.request import Request, urlopen

from backend.ai_engine.provider.base_provider import BaseAIProvider
from backend.core.config import settings


class LocalAIProvider(BaseAIProvider):
    """
    Local AI provider using Ollama.

    The provider communicates with an Ollama instance
    running locally on the user's machine.
    """

    def __init__(
        self,
        server_url: str | None = None,
        model: str | None = None,
    ):
        self.server_url = (
            server_url or settings.AI_SERVER_URL
        ).rstrip("/")

        self.model = model or settings.AI_MODEL

    def analyze(
        self,
        content: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Analyze file content using Ollama and return
        structured AI information.
        """

        prompt = self._build_prompt(
            content=content,
            context=context,
        )

        schema = {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                },
                "category": {
                    "type": "string",
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "risk_level": {
                    "type": "string",
                },
                "confidence": {
                    "type": "number",
                },
            },
            "required": [
                "summary",
                "category",
                "tags",
                "risk_level",
                "confidence",
            ],
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema,
        }

        request = Request(
            f"{self.server_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

        except (URLError, TimeoutError) as exc:
            return {
                "status": "runtime_unavailable",
                "error": str(exc),
                "content_analyzed": False,
            }

        response_text = result.get("response")

        if not response_text:
            return {
                "status": "invalid_response",
                "content_analyzed": False,
            }

        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError as exc:
            return {
                "status": "invalid_json",
                "error": str(exc),
                "content_analyzed": False,
            }

        return {
            "status": "success",
            "content_analyzed": True,
            "model": self.model,
            "analysis": analysis,
        }

    @staticmethod
    def _build_prompt(
        content: str,
        context: Dict[str, Any] | None = None,
    ) -> str:
        """
        Build a controlled prompt for file analysis.
        """

        context = context or {}

        return (
            "You are the AI engine of a file manager.\n"
            "Analyze the provided file information and content.\n"
            "Do not modify, delete, move, or rename files.\n"
            "Return only information about the file.\n\n"
            "Rules:\n"
            "- summary: briefly describe what the file contains.\n"
            "- category: choose the most appropriate category.\n"
            "- tags: provide useful short descriptive tags.\n"
            "- risk_level: use only Low, Medium, or High.\n"
            "- confidence: number from 0 to 1.\n\n"
            f"File context:\n"
            f"{json.dumps(context, ensure_ascii=False)}\n\n"
            f"File content:\n"
            f"{content}"
        )
