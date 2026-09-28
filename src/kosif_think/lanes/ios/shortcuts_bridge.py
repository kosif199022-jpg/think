"""
Apple Shortcuts & iOS Automation Bridge for KOSIF Think.
Enables bidirectional communication between ChatGPT/KOSIF Think and an iPhone
via Apple Shortcuts (اختصارات آبل), URL Schemes, and local network webhooks.
"""

import time
import json
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

# Common iOS URL schemes
COMMON_IOS_SCHEMES = {
    "safari": "https://www.google.com",
    "notes": "mobilenotes://",
    "camera": "camera://",
    "photos": "photos-redirect://",
    "messages": "sms://",
    "settings": "app-settings:",
    "maps": "maps://",
    "whatsapp": "whatsapp://",
    "youtube": "youtube://",
    "music": "music://",
    "mail": "message://",
    "calendar": "calshow://",
    "reminders": "x-apple-reminderkit://",
    "clock": "clock-alarm://"
}

class ShortcutsBridge:
    """Manages command queuing, device pairing, and webhooks for iOS devices."""

    def __init__(self):
        self._command_queue: List[Dict[str, Any]] = []
        self._execution_history: List[Dict[str, Any]] = []
        self._registered_devices: Dict[str, Dict[str, Any]] = {}

    def register_device(self, device_id: str, device_name: str = "iPhone", ip_address: str = "") -> Dict[str, Any]:
        """Registers an iPhone connected to the local network."""
        now = time.time()
        self._registered_devices[device_id] = {
            "device_id": device_id,
            "name": device_name,
            "ip": ip_address,
            "last_seen": now,
            "paired": True
        }
        return {"status": "ok", "device_id": device_id, "paired": True}

    def enqueue_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enqueues an action to be dispatched or fetched by the iPhone shortcut."""
        cmd_id = f"ios_{uuid.uuid4().hex[:8]}"
        cmd = {
            "cmd_id": cmd_id,
            "timestamp": time.time(),
            "action": action_type,
            "params": params,
            "status": "pending"
        }
        self._command_queue.append(cmd)
        if len(self._command_queue) > 100:
            self._command_queue.pop(0)
        return {"status": "enqueued", "cmd_id": cmd_id, "action": action_type}

    def poll_pending_actions(self, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Used by iPhone Shortcut automation to poll for actions to execute."""
        pending = [c for c in self._command_queue if c["status"] == "pending"]
        for p in pending:
            p["status"] = "dispatched"
        return pending

    def report_action_result(self, cmd_id: str, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Called by iPhone to acknowledge successful execution of an action."""
        for c in self._command_queue:
            if c["cmd_id"] == cmd_id:
                c["status"] = "completed"
                c["result"] = result_data
                self._execution_history.append(c)
                return {"status": "ok", "acknowledged": True}
        return {"status": "error", "message": "Command ID not found"}

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Resolves URL scheme or Shortcut action to open an iOS app."""
        key = app_name.lower().strip()
        scheme = COMMON_IOS_SCHEMES.get(key, f"{key}://")
        return self.enqueue_action("open_url_scheme", {"url": scheme, "app_name": app_name})

    def speak_text(self, text: str) -> Dict[str, Any]:
        """Sends text to be spoken via Siri on iPhone."""
        return self.enqueue_action("speak_text", {"text": text, "voice": "natural"})

    def notify(self, title: str, body: str) -> Dict[str, Any]:
        """Sends push notification to iPhone."""
        return self.enqueue_action("show_notification", {"title": title, "body": body})

    def run_shortcut(self, shortcut_name: str, input_value: Optional[str] = None) -> Dict[str, Any]:
        """Triggers a named Apple Shortcut on iPhone."""
        return self.enqueue_action("run_shortcut", {"shortcut_name": shortcut_name, "input": input_value})

    def set_system_setting(self, setting_name: str, value: Any) -> Dict[str, Any]:
        """Sets brightness, volume, low power mode, or focus mode."""
        return self.enqueue_action("set_setting", {"setting": setting_name, "value": value})
