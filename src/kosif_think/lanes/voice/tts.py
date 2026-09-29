"""
Voice Synthesizer (TTS) for KOSIF Think Voice Lane.
Provides native Windows SAPI PowerShell voice triggers, SSML markup formatting,
and streaming audio payload generation.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, Optional
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

    def speak(self, text: str, async_mode: bool = True) -> Dict[str, Any]:
        """Dispatches voice speech via Windows SAPI SpeechSynthesizer."""
        t0 = time.perf_counter()
        clean_text = text.replace('"', '""').replace("'", "''")

        # PowerShell SAPI one-liner
        ps_cmd = (
            f'Add-Type -AssemblyName System.Speech; '
            f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$synth.Rate = {self.default_rate}; '
            f'$synth.Volume = {self.default_volume}; '
            f'$synth.Speak("{clean_text}");'
        )

        try:
            if async_mode:
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                status = "dispatched_async"
            else:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True,
                    timeout=10
                )
                status = "completed_sync"
        except Exception as ex:
            return {"status": "error", "error": str(ex), "text": text}

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": status,
            "text": text,
            "voice_engine": "windows_sapi",
            "characters": len(text),
            "duration_ms": duration_ms
        }
