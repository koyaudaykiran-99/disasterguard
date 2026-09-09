import re
from typing import Dict, Any, List

ADVISORY_DISCLAIMER = "Advisory decision support only. Human operator approval is required before field execution."

class AISafetyGuard:
    """Safety guardrails for DisasterGuard Emergency AI."""

    @staticmethod
    def sanitize_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strip accidental secrets, enforce advisory warnings, and sanitize outputs."""
        answer = response_data.get("answer", "")
        
        # 1. Redact API keys, tokens, or connection strings
        secret_patterns = [
            r"xpl_[a-zA-Z0-9]{30,}",
            r"sk-[a-zA-Z0-9]{20,}",
            r"postgres://[^\s]+",
            r"postgresql://[^\s]+"
        ]
        for pat in secret_patterns:
            answer = re.sub(pat, "[REDACTED_CREDENTIAL]", answer)

        # 2. Enforce human-in-the-loop warning if autonomous dispatch claimed
        forbidden_claims = [
            "i have dispatched", "i dispatched", "system has autonomously deployed",
            "autonomous rescue initiated", "rescue team dispatched automatically"
        ]
        lowered = answer.lower()
        for fc in forbidden_claims:
            if fc in lowered:
                answer += f"\n\n**SAFETY CORRECTION**: {ADVISORY_DISCLAIMER}"
                break

        response_data["answer"] = answer

        # 3. Ensure recommendations include advisory caveat if empty
        recs: List[str] = response_data.get("recommendations", [])
        if not recs:
            recs = ["Monitor live telemetry", "Awaiting operator command"]
        response_data["recommendations"] = recs

        # 4. Ensure warnings include disclaimer
        warnings: List[str] = response_data.get("warnings", [])
        if ADVISORY_DISCLAIMER not in warnings:
            warnings.append(ADVISORY_DISCLAIMER)
        response_data["warnings"] = warnings

        return response_data
