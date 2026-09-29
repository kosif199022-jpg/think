"""
Cloud Browser Session Manager for Jev-Browser.
Coordinates isolated virtual cloud browsing contexts, multi-tab lifecycles,
persistent session cookies, storage state, and audit logs.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Optional
import uuid
import time
from .stealth_profile import StealthProfile

class CloudTab:
    """Represents an individual tab inside a cloud browser session."""

    def __init__(self, tab_id: str, url: str = "about:blank", title: str = "New Tab"):
        self.tab_id = tab_id
        self.url = url
        self.title = title
        self.dom_hash: str = ""
        self.elements_count: int = 0
        self.created_at: float = time.time()
        self.updated_at: float = time.time()
        self.navigation_history: List[str] = [url]

    def navigate(self, url: str, title: Optional[str] = None):
        self.url = url
        if title:
            self.title = title
        self.navigation_history.append(url)
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tab_id": self.tab_id,
            "url": self.url,
            "title": self.title,
            "dom_hash": self.dom_hash,
            "elements_count": self.elements_count,
            "updated_at": self.updated_at,
            "history_length": len(self.navigation_history)
        }


class CloudBrowserSession:
    """Manages an isolated cloud browser container instance."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        stealth: Optional[StealthProfile] = None
    ):
        self.session_id = session_id or f"cbs_{uuid.uuid4().hex[:8]}"
        self.viewport = {"width": viewport_width, "height": viewport_height}
        self.stealth = stealth or StealthProfile()
        self.created_at = time.time()
        self.last_active_at = time.time()
        self.status = "ready"  # ready, busy, closed
        self.tabs: Dict[str, CloudTab] = {}
        self.active_tab_id: Optional[str] = None
        self.cookies: Dict[str, str] = {}
        self.local_storage: Dict[str, str] = {}
        self.action_history: List[Dict[str, Any]] = []

        # Open initial default tab
        initial_tab = self.open_tab("https://www.google.com", "Google Search")
        self.active_tab_id = initial_tab.tab_id

    def open_tab(self, url: str = "about:blank", title: str = "New Tab") -> CloudTab:
        """Opens a new tab within the cloud session."""
        self.last_active_at = time.time()
        tab_id = f"tab_{len(self.tabs) + 1}_{uuid.uuid4().hex[:4]}"
        tab = CloudTab(tab_id=tab_id, url=url, title=title)
        self.tabs[tab_id] = tab
        self.active_tab_id = tab_id
        return tab

    new_tab = open_tab

    def switch_tab(self, tab_id: str) -> bool:
        """Switches active focus to target tab."""
        self.last_active_at = time.time()
        if tab_id in self.tabs:
            self.active_tab_id = tab_id
            return True
        return False

    def close_tab(self, tab_id: str) -> bool:
        """Closes a tab and updates active tab pointer."""
        self.last_active_at = time.time()
        if tab_id in self.tabs:
            del self.tabs[tab_id]
            if self.active_tab_id == tab_id:
                self.active_tab_id = next(iter(self.tabs)) if self.tabs else None
            return True
        return False

    def get_active_tab(self) -> Optional[CloudTab]:
        return self.tabs.get(self.active_tab_id) if self.active_tab_id else None

    def record_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Audits Jev action execution."""
        self.last_active_at = time.time()
        entry = {
            "timestamp": time.time(),
            "action": action_type,
            "tab_id": self.active_tab_id,
            "details": details
        }
        self.action_history.append(entry)
        if len(self.action_history) > 100:
            self.action_history.pop(0)

    def set_cookie(self, name: str, value: str):
        self.cookies[name] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self.status,
            "viewport": self.viewport,
            "user_agent": self.stealth.user_agent,
            "created_at": self.created_at,
            "last_active_at": self.last_active_at,
            "active_tab_id": self.active_tab_id,
            "tab_count": len(self.tabs),
            "tabs": [t.to_dict() for t in self.tabs.values()],
            "actions_executed": len(self.action_history)
        }


class CloudSessionManager:
    """Singleton pool managing multi-tenant cloud browser sessions."""

    def __init__(self):
        self.sessions: Dict[str, CloudBrowserSession] = {}

    def create_session(
        self,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> CloudBrowserSession:
        """Allocates and initializes a new cloud session."""
        stealth = StealthProfile(user_agent=user_agent)
        session = CloudBrowserSession(
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            stealth=stealth
        )
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[CloudBrowserSession]:
        return self.sessions.get(session_id)

    def get_or_create_default(self) -> CloudBrowserSession:
        """Returns the primary active session or creates one if empty."""
        if not self.sessions:
            return self.create_session()
        return next(iter(self.sessions.values()))

    def close_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id].status = "closed"
            del self.sessions[session_id]
            return True
        return False

    def terminate_session(self, session_id: str) -> bool:
        return self.close_session(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.sessions.values()]
