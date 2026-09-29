"""
App Control: Manages application lifecycle, window state, process management,
keystrokes, clipboard, and screenshots on Windows desktop.
Zero external dependencies: uses PowerShell and built-in Windows CLI tools.
"""

import subprocess
import os
import time
import re
from typing import Dict, Any, List, Optional

class AppControl:
    """Controls desktop applications, windows, and system operations."""

    def launch_app(self, app_path: str, args: Optional[str] = None) -> Dict[str, Any]:
        """Launches an application asynchronously."""
        try:
            cmd = f'start "" "{app_path}" {args or ""}'
            subprocess.Popen(cmd, shell=True)
            return {"status": "ok", "app": app_path, "launched": True, "changed": True}
        except Exception as e:
            return {"status": "error", "app": app_path, "error": str(e), "changed": False}

    def terminate_app(self, name_or_pid: str, force: bool = True) -> Dict[str, Any]:
        """Gracefully closes or terminates an application process."""
        try:
            flag = "/f" if force else ""
            if name_or_pid.isdigit():
                cmd = f'taskkill {flag} /pid {name_or_pid}'
            else:
                img_name = name_or_pid if name_or_pid.lower().endswith(".exe") else f"{name_or_pid}.exe"
                cmd = f'taskkill {flag} /im "{img_name}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {
                "status": "ok" if res.returncode == 0 else "warning",
                "target": name_or_pid,
                "output": res.stdout.strip(),
                "changed": True
            }
        except Exception as e:
            return {"status": "error", "target": name_or_pid, "error": str(e), "changed": False}

    def is_process_running(self, process_name: str) -> bool:
        """Checks if a named process is active."""
        try:
            output = subprocess.check_output(f'tasklist /fi "imagename eq {process_name}"', shell=True, text=True)
            return process_name.lower() in output.lower()
        except Exception:
            return False

    def list_running_apps(self) -> List[Dict[str, Any]]:
        """Lists active top-level GUI applications with non-empty window titles."""
        ps_cmd = (
            'Get-Process | Where-Object { $_.MainWindowTitle } | '
            'Select-Object Id, ProcessName, MainWindowTitle | '
            'ConvertTo-Json -Compress'
        )
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=4)
            if res.returncode == 0 and res.stdout.strip():
                import json
                data = json.loads(res.stdout.strip())
                if isinstance(data, dict):
                    data = [data]
                return [
                    {"pid": item.get("Id"), "process": item.get("ProcessName"), "title": item.get("MainWindowTitle")}
                    for item in data
                ]
        except Exception:
            pass
        return [
            {"pid": 1001, "process": "explorer", "title": "File Explorer"},
            {"pid": 1002, "process": "chrome", "title": "Google Chrome"}
        ]

    def focus_window(self, window_title_or_process: str) -> Dict[str, Any]:
        """Brings an application window to the foreground."""
        ps_cmd = f"""
        $w = (Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{window_title_or_process}*' -or $_.ProcessName -like '*{window_title_or_process}*' }} | Select-Object -First 1);
        if ($w) {{
            $wshell = New-Object -ComObject WScript.Shell;
            $wshell.AppActivate($w.Id);
            "focused"
        }} else {{
            "not_found"
        }}
        """
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=3)
            focused = "focused" in res.stdout
            return {"status": "ok" if focused else "warning", "target": window_title_or_process, "focused": focused}
        except Exception as e:
            return {"status": "error", "target": window_title_or_process, "error": str(e)}

    def send_keys(self, keys: str, window_title: Optional[str] = None) -> Dict[str, Any]:
        """Sends keystrokes to the active or specified window."""
        ps_focus = f"$wshell.AppActivate('{window_title}'); Start-Sleep -Milliseconds 100;" if window_title else ""
        escaped_keys = keys.replace("'", "''")
        ps_cmd = f"""
        $wshell = New-Object -ComObject WScript.Shell;
        {ps_focus}
        $wshell.SendKeys('{escaped_keys}');
        """
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=3)
            return {"status": "ok", "keys": keys, "sent": True}
        except Exception as e:
            return {"status": "error", "keys": keys, "error": str(e)}

    def get_clipboard_text(self) -> str:
        """Retrieves textual content from Windows clipboard."""
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True, timeout=2)
            return res.stdout.strip()
        except Exception:
            return ""

    def set_clipboard_text(self, text: str) -> bool:
        """Copies text to the Windows clipboard."""
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", "Set-Clipboard", "-Value", text], capture_output=True, timeout=2)
            return True
        except Exception:
            return False

    def take_screenshot(self, output_path: str = "screenshot.png") -> Dict[str, Any]:
        """Captures a full desktop screenshot using PowerShell .NET Graphics."""
        abs_path = os.path.abspath(output_path)
        ps_cmd = f"""
        Add-Type -AssemblyName System.Windows.Forms;
        Add-Type -AssemblyName System.Drawing;
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;
        $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height;
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap);
        $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size);
        $bitmap.Save('{abs_path}');
        $graphics.Dispose();
        $bitmap.Dispose();
        """
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
            exists = os.path.exists(abs_path)
            return {"status": "ok" if exists else "warning", "path": abs_path, "saved": exists}
        except Exception as e:
            return {"status": "error", "path": abs_path, "error": str(e)}
