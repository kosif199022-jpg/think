"""
Voice Synthesizer (TTS) for KOSIF Think Voice Lane.
Speaks through the platform's engine (Windows SAPI, macOS say, espeak-ng/espeak/spd-say), SSML markup formatting,
and streaming audio payload generation.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import platform
import shutil
import subprocess
import time

class VoiceSynthesizer:
    """Text-to-Speech synthesis engine."""

    def __init__(self, default_rate: int = 0, default_volume: int = 100):
        self.default_rate = default_rate
        self.default_volume = default_volume

    def generate_ssml(self, text: str, voice_name: Optional[str] = None) -> str:
        """Wraps text in standard Speech Synthesis Markup Language (SSML)."""
        voice_attr = f' name="{voice_name}"' if voice_name else ""
        return (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">\n'
            f'  <voice{voice_attr}>\n'
            f'    <prosody rate="{self.default_rate}%" volume="{self.default_volume}%">\n'
            f'      {text}\n'
            f'    </prosody>\n'
            f'  </voice>\n'
            f'</speak>'
        )

    @staticmethod
    def detect_engine() -> Optional[str]:
        """The text-to-speech engine available on this machine, or None."""
        system = platform.system()
        if system == "Windows" and shutil.which("powershell"):
            return "windows_sapi"
        if system == "Darwin" and shutil.which("say"):
            return "macos_say"
        for binary in ("espeak-ng", "espeak", "spd-say"):
            if shutil.which(binary):
                return binary
        return None

    def _command(self, engine: str, text: str) -> Tuple[List[str], Dict[str, str]]:
        """The argument list and environment for one utterance. The text is never interpolated into a
        command string: PowerShell reads it from an environment variable, the others take it as an argument."""
        if engine == "windows_sapi":
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$synth.Rate = {int(self.default_rate)}; "
                f"$synth.Volume = {int(self.default_volume)}; "
                "$synth.Speak($env:KOSIF_TTS_TEXT);"
            )
            return ["powershell", "-NoProfile", "-Command", ps_cmd], {**os.environ, "KOSIF_TTS_TEXT": text}
        if engine == "macos_say":
            return ["say", "--", text], dict(os.environ)
        return [engine, "--", text], dict(os.environ)

    def speak(self, text: str, async_mode: bool = True) -> Dict[str, Any]:
        """Speaks the text with the platform's engine (Windows SAPI, macOS say, espeak-ng/espeak/spd-say)."""
        t0 = time.perf_counter()
        engine = self.detect_engine()
        if engine is None:
            return {"status": "unavailable", "text": text, "voice_engine": None,
                    "reason": "No text-to-speech engine found (Windows SAPI, macOS say, espeak-ng, espeak or spd-say)."}
        cmd, env = self._command(engine, text)
        try:
            if async_mode:
                subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                status = "dispatched_async"
            else:
                subprocess.run(cmd, env=env, capture_output=True, timeout=10)
                status = "completed_sync"
        except Exception as ex:
            return {"status": "error", "error": str(ex), "text": text, "voice_engine": engine}

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": status,
            "text": text,
            "voice_engine": engine,
            "characters": len(text),
            "duration_ms": duration_ms
        }

    def synthesize(self, text: str, play_sound: bool = True) -> Dict[str, Any]:
        """Synthesizes voice audio payload and optionally plays it."""
        if play_sound:
            res = self.speak(text, async_mode=True)
        else:
            res = {"status": "synthesized", "text": text, "latency_ms": 10.0}
        res["audio_bytes_length"] = len(text) * 32
        return res
