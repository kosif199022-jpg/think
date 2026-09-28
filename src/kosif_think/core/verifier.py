"""
Observable Verifier: Revalidates that an action produced verifiable, concrete real-world changes.
A returned HTTP 200 or click event is NOT proof of completion; observable postconditions must hold.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

@dataclass
class VerificationResult:
    verified: bool
    observable_delta: Dict[str, Any] = field(default_factory=dict)
    failure_reason: Optional[str] = None


class ObservableVerifier:
    """Evaluates expected postconditions against observed reality."""

    def verify_step_postconditions(
        self,
        expected_conditions: List[Dict[str, Any]],
        observed_state: Dict[str, Any]
    ) -> VerificationResult:
        """Checks each condition in the contract against post-execution state."""
        if not expected_conditions:
            # Default fallback: check if state reported any positive delta
            has_delta = bool(observed_state.get("changed", True))
            return VerificationResult(verified=has_delta, observable_delta=observed_state)

        for cond in expected_conditions:
            cond_type = cond.get("type")

            # 1. URL change verification
            if cond_type == "url_matches":
                expected_url = cond.get("expected", "").lower()
                actual_url = str(observed_state.get("url", "")).lower()
                if expected_url not in actual_url:
                    return VerificationResult(
                        verified=False,
                        failure_reason=f"Expected URL to contain '{expected_url}', but got '{actual_url}'"
                    )

            # 2. DOM text emergence
            elif cond_type == "text_contains":
                expected_text = cond.get("text", "").lower()
                page_text = str(observed_state.get("text", "")).lower()
                if expected_text not in page_text:
                    return VerificationResult(
                        verified=False,
                        failure_reason=f"Expected text '{expected_text}' was not found in page content."
                    )

            # 3. File existence / size verification
            elif cond_type == "file_exists":
                target_path = Path(cond.get("path", ""))
                min_bytes = int(cond.get("min_bytes", 1))
                if not target_path.exists() or target_path.stat().st_size < min_bytes:
                    return VerificationResult(
                        verified=False,
                        failure_reason=f"File {target_path} does not exist or size < {min_bytes} bytes."
                    )

            # 4. Message dispatch verification
            elif cond_type == "message_dispatched":
                if not observed_state.get("dispatched"):
                    return VerificationResult(
                        verified=False,
                        failure_reason="Message delivery was not confirmed by the communication bridge."
                    )

            # 5. DOM state changed
            elif cond_type == "dom_state_changed":
                if not observed_state.get("changed", True):
                    return VerificationResult(
                        verified=False,
                        failure_reason="No observable DOM change occurred after action."
                    )

        return VerificationResult(verified=True, observable_delta=observed_state)
