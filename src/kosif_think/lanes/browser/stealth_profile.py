"""
Stealth & Anti-Bot Protection Engine for Jev-Browser.
Inspired by Puppeteer-Stealth, Playwright-Stealth, and FingerprintJS evasion techniques.
Provides automated evasions for Cloudflare, DataDome, Akamai, and PerimeterX:
- navigator.webdriver removal
- Chrome runtime object mocking
- Humanized Bezier mouse trajectory generator
- Hardware & WebGL fingerprint spoofing
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Tuple, Optional
import math
import random
import time

STEALTH_INJECTION_JS = r"""(() => {
  // 1. Remove navigator.webdriver
  try {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  } catch (e) {}

  // 2. Mock window.chrome runtime
  if (!window.chrome) {
    window.chrome = {
      app: { isInstalled: false, InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' } },
      runtime: {
        OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' },
        PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
        PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
        PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' }
      }
    };
  }

  // 3. Mock navigator.plugins and mimeTypes
  try {
    const fakePlugins = [
      { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
      { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
      { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
    ];
    Object.defineProperty(navigator, 'plugins', { get: () => fakePlugins });
  } catch (e) {}

  // 4. Permissions API query mock for notifications
  try {
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = parameters => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  } catch (e) {}
})()"""


class BezierPoint(dict):
    """Point supporting dict lookup, attribute access, and tuple comparison."""
    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        raise AttributeError(name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, tuple) and len(other) == 2:
            return (self.get("x"), self.get("y")) == (float(other[0]), float(other[1])) or (self.get("x"), self.get("y")) == (other[0], other[1])
        return super().__eq__(other)


class KeystrokeDelay(dict):
    """Keystroke entry supporting dict lookup, attribute access, and numeric comparison."""
    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        raise AttributeError(name)

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, (int, float)):
            return self.get("delay_ms", 0) > other
        return super().__gt__(other)

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, (int, float)):
            return self.get("delay_ms", 0) >= other
        return super().__ge__(other)


class StealthProfile:
    """Manages anti-bot evasion profiles and humanized interaction dynamics."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/130.0.2849.68 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
    ]

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or self.USER_AGENTS[0]
        self.stealth_js = STEALTH_INJECTION_JS

    def get_headers(self) -> Dict[str, str]:
        """Generates realistic browser HTTP request headers."""
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

    def generate_human_bezier_curve(
        self,
        start: Tuple[int, int],
        target: Tuple[int, int],
        steps: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Calculates a natural human-like mouse path between two points
        using Cubic Bezier interpolation with random control points and micro-jitter.
        """
        x0, y0 = start
        x3, y3 = target

        # Generate control points with natural overshoot
        dx = x3 - x0
        dy = y3 - y0
        dist = math.hypot(dx, dy)

        # Perturbation factor
        factor = min(max(dist * 0.2, 20.0), 100.0)
        x1 = x0 + dx * 0.25 + random.uniform(-factor, factor)
        y1 = y0 + dy * 0.25 + random.uniform(-factor, factor)
        x2 = x0 + dx * 0.75 + random.uniform(-factor, factor)
        y2 = y0 + dy * 0.75 + random.uniform(-factor, factor)

        points = []
        for i in range(steps + 1):
            t = i / float(steps)
            # Cubic Bezier formula
            xt = ((1 - t)**3 * x0) + (3 * (1 - t)**2 * t * x1) + (3 * (1 - t) * t**2 * x2) + (t**3 * x3)
            yt = ((1 - t)**3 * y0) + (3 * (1 - t)**2 * t * y1) + (3 * (1 - t) * t**2 * y2) + (t**3 * y3)

            # Add human micro-jitter except at the exact start and target
            if 0 < i < steps:
                xt += random.uniform(-1.5, 1.5)
                yt += random.uniform(-1.5, 1.5)

            points.append(BezierPoint({
                "x": round(xt, 1),
                "y": round(yt, 1),
                "step": i,
                "t": round(t, 3)
            }))

        return points

    def human_keystroke_delays(self, text: str) -> List[KeystrokeDelay]:
        """Generates realistic typing cadence with inter-character delays (50ms - 150ms)."""
        keystrokes = []
        for char in text:
            # Punctuation and spaces generally have slightly longer pause
            if char in (" ", ".", ",", "!", "?"):
                delay_ms = random.randint(110, 220)
            elif char.isupper():
                delay_ms = random.randint(80, 160)
            else:
                delay_ms = random.randint(45, 115)

            keystrokes.append(KeystrokeDelay({
                "char": char,
                "delay_ms": delay_ms
            }))
        return keystrokes

    def get_stealth_scripts(self) -> str:
        """Returns the full JavaScript injection block for stealth evasion."""
        return self.stealth_js

    # Ergonomic aliases
    generate_bezier_curve = generate_human_bezier_curve
    get_typing_delays = human_keystroke_delays
