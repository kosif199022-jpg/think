"""
Risk Gate: Evaluates operational hazards and enforces human checkpoints for CAPTCHA,
OTP, payment confirmation, and destructive operations.
"""

from enum import Enum
import re
from typing import Dict, Any, Optional
from .planner import Step

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CheckpointRequired(Exception):
    """Raised when an action halts at a mandatory human checkpoint."""
    def __init__(self, checkpoint_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.checkpoint_type = checkpoint_type
        self.message = message
        self.details = details or {}


CRITICAL_PATTERNS = re.compile(
    r"\b(transfer|pay|purchase|checkout|buy|credit card|cvv|otp|2fa|authenticator|pin code)\b|دفع|شراء|تحويل|بطاقة|سحب|كود التحقق",
    re.IGNORECASE
)

DESTRUCTIVE_PATTERNS = re.compile(
    r"\b(delete|drop database|format|rmdir|rm -rf|truncate|remove permanent)\b|حذف نهائي|فورمات|مسح",
    re.IGNORECASE
)

CAPTCHA_PATTERNS = re.compile(
    r"\b(captcha|recaptcha|turnstile|hcaptcha|sorry/index|are you human|robot)\b|كابتشا|تحقق من أنك لست روبوت",
    re.IGNORECASE
)


class RiskGate:
    """Enforces safety gates and human verification checkpoints."""

    def evaluate_step(self, step: Step, page_state: Optional[Dict[str, Any]] = None) -> RiskLevel:
        """Determines the risk classification for a given step and context."""
        text_corpus = f"{step.intent} {step.description} {step.value or ''} {step.target.name or ''}"

        if CRITICAL_PATTERNS.search(text_corpus):
            return RiskLevel.CRITICAL
        if DESTRUCTIVE_PATTERNS.search(text_corpus):
            return RiskLevel.HIGH
        if step.lane == "whatsapp":
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def check_checkpoint_preconditions(
        self,
        step: Step,
        page_url: str = "",
        page_title: str = "",
        approved: bool = False
    ):
        """
        Validates whether execution must pause for a human checkpoint.
        Raises CheckpointRequired if user approval or manual interaction is required.
        """
        # 1. Anti-Bot / CAPTCHA Checkpoint
        if "google.com/sorry" in page_url or CAPTCHA_PATTERNS.search(page_title):
            if not approved:
                raise CheckpointRequired(
                    checkpoint_type="captcha_anti_bot",
                    message="🛡️ تم رصد جدار تحقق بشري (CAPTCHA / Google Sorry). يرجى إكمال التحقق في المتصفح ثم المتابعة.",
                    details={"url": page_url, "title": page_title}
                )

        # 2. Critical Action Checkpoint
        risk = self.evaluate_step(step)
        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL) and not approved:
            raise CheckpointRequired(
                checkpoint_type="critical_action_approval",
                message=f"⚠️ يتطلب هذا الإجراء ({step.intent}: {step.description}) موافقة صريحة من المستخدم لأنه ذو خطورة عالية.",
                details={"step_id": step.step_id, "intent": step.intent, "risk": risk.value}
            )
