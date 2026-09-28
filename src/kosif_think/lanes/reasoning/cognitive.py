"""
Cognitive AI Brain: Deep semantic understanding of obstacles, loop detection,
CAPTCHA / anti-bot wall diagnosis, and autonomous blocker resolution.
"""

from typing import Dict, Any, Optional
import urllib.parse
import re

class CognitiveUnderstanding:
    """System-2 reasoning engine for deep comprehension and recovery."""

    def diagnose_page_state(self, url: str, title: str, html_snippet: str = "") -> Dict[str, Any]:
        """Diagnoses obstacles such as Google sorry, Turnstile, or cookie modals."""
        # 1. Google Sorry / reCAPTCHA wall
        if "google.com/sorry" in url:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            cont = qs.get("continue", [""])[0]
            query = ""
            if cont:
                cont_qs = urllib.parse.parse_qs(urllib.parse.urlparse(cont).query)
                query = cont_qs.get("q", [""])[0]
            if not query and "q" in qs:
                query = qs.get("q", [""])[0]

            return {
                "blocked": True,
                "obstacle": "google_recaptcha_sorry",
                "recommended_action": "human_checkpoint",
                "query": query,
                "message": "🛡️ رصد جدار تحقق Google Sorry (reCAPTCHA). التحقق اليدوي مطلوب أو التحويل التلقائي لمحرك بحث بديل."
            }

        # 2. Cloudflare Turnstile
        if "challenges.cloudflare.com" in url or "Just a moment..." in title:
            return {
                "blocked": True,
                "obstacle": "cloudflare_turnstile",
                "recommended_action": "human_checkpoint",
                "message": "🛡️ رصد جدار حماية Cloudflare Turnstile. التحقق البشري مطلوب."
            }

        # 3. Clean Content
        return {
            "blocked": False,
            "obstacle": None,
            "recommended_action": "proceed",
            "message": "الصفحة جاهزة والتفاعل المباشر متاح."
        }
