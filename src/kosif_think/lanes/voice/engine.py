"""
Voice Lane Engine for KOSIF Think.
Autonomous Lane 8: Coordinates Text-to-Speech (TTS), Speech-to-Text (STT),
SSML markup, and conversational audio synthesis.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, Optional
import time
from .tts import VoiceSynthesizer
from .stt import AudioTranscriber
from ...core.cancellation import CancellationToken

class VoiceLane:
    """Unified handler for voice and speech automation."""

    def __init__(self):
        self.tts = VoiceSynthesizer()
        self.stt = AudioTranscriber()

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the voice lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "speak")).lower()
        val = str(getattr(step, "value", "") or getattr(step, "description", ""))

        # 1. Text-to-Speech
        if intent in ("speak", "tts", "say"):
            res = self.tts.speak(val, async_mode=True)
            res["lane"] = "voice"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Generate SSML
        elif intent in ("ssml", "generate_ssml"):
            ssml_markup = self.tts.generate_ssml(val)
            return {
                "status": "ok",
                "lane": "voice",
                "mode": "ssml",
                "ssml": ssml_markup,
                "changed": True,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # 3. Speech-to-Text Transcription
        elif intent in ("transcribe", "stt", "listen"):
            res = self.stt.transcribe(val)
            res["lane"] = "voice"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 4. Default Voice Response
        return {
            "status": "ok",
            "lane": "voice",
            "message": f"Voice intent '{intent}' processed.",
            "value": val,
            "changed": True,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
