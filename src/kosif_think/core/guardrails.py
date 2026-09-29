"""
AI Safety Guardrails, Canary Defense, and PII Masker for KOSIF Think.
Inspired by NeMo Guardrails, Llama-Guard, and OWASP Top 10 for LLMs.
Zero external dependencies. Pure Python.
"""

import re
from typing import Dict, Any, List, Set, Optional, Tuple

class GuardrailsSystem:
    """Multi-layer safety firewall defending against prompt injections, PII leaks, and canary extraction."""

    # High-risk prompt injection patterns
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?", re.IGNORECASE),
        re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior|system)\s+(?:rules|directives|prompts?)", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(?:DAN|jailbroken|unrestricted|godmode)", re.IGNORECASE),
        re.compile(r"print\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions|developer\s+prompt)", re.IGNORECASE),
        re.compile(r"reveal\s+(?:all\s+)?(?:secret\s+keys?|passwords?|credentials?)", re.IGNORECASE),
        re.compile(r"(?:bypass|disable)\s+(?:safety|risk\s+gate|content\s+filter)", re.IGNORECASE),
        re.compile(r"base64:\s*[A-Za-z0-9+/=]{30,}", re.IGNORECASE)
    ]

    # Sensitive PII & credential patterns
    PII_PATTERNS = [
        # Credit Card Numbers (13 to 19 digits with optional hyphens/spaces)
        (re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        # OpenAI API Keys
        (re.compile(r"\bsk-[a-zA-Z0-9]{32,}\b"), "[REDACTED_OPENAI_KEY]"),
        # GitHub Personal Access Tokens
        (re.compile(r"\bgh[pousr]_[a-zA-Z0-9]{36}\b"), "[REDACTED_GITHUB_TOKEN]"),
        # AWS Access Keys
        (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_KEY]"),
        # JWT Bearer Tokens
        (re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"), "[REDACTED_JWT]"),
        # Email addresses
        (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
        # Phone numbers (international and local formats)
        (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[REDACTED_PHONE]")
    ]

    def __init__(self):
        self._canary_tokens: Set[str] = set()

    def register_canary(self, token: str) -> None:
        """Registers a secret canary token to detect internal instruction leakage."""
        if token and len(token) >= 8:
            self._canary_tokens.add(token)

    def scan_prompt(self, prompt: str) -> Dict[str, Any]:
        """Scans an incoming user prompt for injection attempts or malicious exploits."""
        matches = []
        for pattern in self.INJECTION_PATTERNS:
            found = pattern.findall(prompt)
            if found:
                matches.append(pattern.pattern)

        is_safe = len(matches) == 0
        risk_level = "safe" if is_safe else ("high" if len(matches) > 1 else "medium")

        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "detected_patterns": matches,
            "sanitized_prompt": prompt if is_safe else "[BLOCKED: Prompt Injection Signature Detected]"
        }

    def redact_pii(self, text: str) -> Tuple[str, int]:
        """Redacts sensitive PII, API tokens, and credentials from text. Returns (cleaned_text, redaction_count)."""
        if not text:
            return "", 0

        redacted = text
        count = 0

        for pattern, replacement in self.PII_PATTERNS:
            redacted, n = pattern.subn(replacement, redacted)
            count += n

        # Check for canary tokens
        for canary in self._canary_tokens:
            if canary in redacted:
                redacted = redacted.replace(canary, "[REDACTED_CANARY_TOKEN]")
                count += 1

        return redacted, count

    def guard_output(self, output_text: str) -> Dict[str, Any]:
        """Inspects agent generated response to ensure no canaries or credentials leak."""
        canary_leak = any(canary in output_text for canary in self._canary_tokens)
        cleaned_text, pii_count = self.redact_pii(output_text)

        return {
            "canary_leak_detected": canary_leak,
            "pii_redacted_count": pii_count,
            "guarded_text": cleaned_text,
            "is_safe": not canary_leak
        }
