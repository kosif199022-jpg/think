"""
Telephony & Communication Lane Engine for KOSIF Think.
Dispatches voice phone calls, VoIP/SIP connections, IVR interactions, and Astra voice sessions.
"""

from typing import Dict, Any, Optional
import time
from .call_manager import CallManager
from .astra_session import AstraVoiceSession
from ...core.cancellation import CancellationToken

class TelephonyLane:
    """Unified execution lane for telephone, voice calls, and multimodal meetings."""

    def __init__(self):
        self.call_manager = CallManager()
        self.active_sessions: Dict[str, AstraVoiceSession] = {}

    async def dispatch_step(self, step: Any, cancellation_token: Optional[CancellationToken] = None) -> Dict[str, Any]:
        """Dispatches an action in the telephony lane."""
        if cancellation_token:
            cancellation_token.throw_if_cancellation_requested()

        t0 = time.perf_counter()
        intent = str(getattr(step, "intent", "dial")).lower()
        target_ref = str(getattr(getattr(step, "target", None), "ref", "") or "")
        val = getattr(step, "value", None)
        args = getattr(step, "args", {}) or {}

        # 1. Dial phone call
        if intent in ("dial", "call", "make_call"):
            num = target_ref or str(val or "123456789")
            provider = args.get("provider", "cellular")
            notes = args.get("notes") or str(val)
            res = self.call_manager.dial_phone(num, provider=provider, notes=notes)
            res["lane"] = "telephony"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 2. Hang up call
        elif intent in ("hangup", "end_call", "terminate_call"):
            call_id = target_ref or str(val or "")
            res = self.call_manager.hangup_call(call_id if call_id else None)
            res["lane"] = "telephony"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 3. Create virtual meeting room
        elif intent in ("meeting", "create_meeting", "zoom", "meet", "teams"):
            platform = "zoom" if "zoom" in intent else ("teams" if "teams" in intent else "google_meet")
            topic = target_ref or str(val or "KOSIF Intelligence Conference")
            res = self.call_manager.create_meeting_link(platform=platform, topic=topic)
            res["lane"] = "telephony"
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 4. Astra Multimodal Voice Turn
        elif intent in ("astra_session", "voice_turn", "interactive_voice"):
            session_id = args.get("session_id", "default_session")
            session = self.active_sessions.get(session_id)
            if not session:
                session = AstraVoiceSession(session_id)
                self.active_sessions[session_id] = session
                session.start_session()

            user_text = str(val or target_ref or "ما هو تحليلك للوضع الراهن؟")
            res = session.process_user_speech(transcribed_text=user_text)
            res["lane"] = "telephony"
            res["changed"] = True
            res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return res

        # 5. IVR TwiML Generation
        elif intent in ("ivr", "twiml"):
            msg = str(val or target_ref or "شكراً لاتصالكم بمركز الذكاء الاصطناعي الفائق.")
            xml = self.call_manager.generate_twiml_response(msg, gather_digits=args.get("gather", False))
            return {
                "status": "ok",
                "lane": "telephony",
                "twiml": xml,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        return {
            "status": "ok",
            "lane": "telephony",
            "action": intent,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }
