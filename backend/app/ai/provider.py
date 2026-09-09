import abc
import json
import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("disasterguard.ai.provider")

class AIProvider(abc.ABC):
    """Abstract Base Class for LLM Providers."""
    
    @abc.abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Optional[Dict[str, Any]]:
        """Generate structured response matching DisasterGuard schema."""
        pass

class GPTAstraProvider(AIProvider):
    """Concrete provider for GPT Astra / OpenAI-compatible endpoint."""

    def __init__(self):
        self.api_key = settings.GPT_ASTRA_API_KEY
        self.candidate_urls = [
            "https://api.gptastra.com/v1/chat/completions",
            "https://api.openai.com/v1/chat/completions"
        ]

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Optional[Dict[str, Any]]:
        if not self.api_key or self.api_key.startswith("demo_"):
            return None

        # Format system prompt to explicitly enforce JSON output
        json_enforced_sys = (
            f"{system_prompt}\n\n"
            "CRITICAL REQUIREMENT: You MUST respond ONLY with valid JSON conforming to this schema:\n"
            "{\n"
            '  "answer": "string markdown answer",\n'
            '  "severity": "LOW" | "MODERATE" | "HIGH" | "CRITICAL",\n'
            '  "confidence": 0.85,\n'
            '  "confidence_type": "CALIBRATED" | "SYSTEM_HEURISTIC" | "QUALITATIVE",\n'
            '  "sources": ["source 1", "source 2"],\n'
            '  "recommendations": ["action 1", "action 2"],\n'
            '  "warnings": ["warning 1"]\n'
            "}"
        )

        for url in self.candidate_urls:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": json_enforced_sys},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            raw_content = choices[0].get("message", {}).get("content", "").strip()
                            # Clean potential markdown fences
                            if raw_content.startswith("```json"):
                                raw_content = raw_content[7:]
                            if raw_content.startswith("```"):
                                raw_content = raw_content[3:]
                            if raw_content.endswith("```"):
                                raw_content = raw_content[:-3]
                            raw_content = raw_content.strip()
                            
                            try:
                                parsed = json.loads(raw_content)
                                if isinstance(parsed, dict) and "answer" in parsed:
                                    return parsed
                            except json.JSONDecodeError:
                                # Fallback to wrapping plain text
                                return {
                                    "answer": raw_content,
                                    "severity": "MODERATE",
                                    "confidence": 0.75,
                                    "confidence_type": "QUALITATIVE",
                                    "sources": ["GPT Astra Intelligence Engine"],
                                    "recommendations": ["Review live sensor telemetry in command center"],
                                    "warnings": []
                                }
            except Exception as e:
                logger.debug(f"Remote LLM call to {url} failed: {e}")
                continue

        return None

class FallbackAIProvider(AIProvider):
    """
    Deterministic domain-expert intelligence engine.
    Always available offline, never hangs, produces grounded responses from PostgreSQL facts.
    """

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Optional[Dict[str, Any]]:
        # This fallback is invoked by the AIEmergencyAgent when remote LLM is offline.
        # Returning None instructs the agent to apply its structured domain synthesizer.
        return None

def get_ai_provider() -> AIProvider:
    """Provider factory returning primary configured LLM provider."""
    return GPTAstraProvider()
