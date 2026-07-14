#!/usr/bin/env python3
"""Best-effort desktop notification for QA pipeline runs (Claude Code
hooks -> hooks/hooks.json). Strictly opt-in: does nothing unless
QA_PIPELINE_NOTIFY=1. Never fails the hook (always exits 0)."""
import os
import platform
import subprocess
import sys

MSG = {"done": "QA pipeline: Claude finished.",
       "attention": "QA pipeline: Claude needs your input."}


def main():
    if os.environ.get("QA_PIPELINE_NOTIFY") != "1":
        return
    msg = MSG.get(sys.argv[1] if len(sys.argv) > 1 else "done", MSG["done"])
    sys.stdout.write("\a")  # terminal bell, works everywhere
    sys.stdout.flush()
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command",
                 f"(New-Object -ComObject WScript.Shell).Popup('{msg}',5,'Claude',64)"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin":
            subprocess.Popen(
                ["osascript", "-e",
                 f'display notification "{msg}" with title "Claude"'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["notify-send", "Claude", msg],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
