"""Bounded public demo: independent assertion, no proprietary targets."""
import json
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

GOAL = "Open Android Settings, navigate to Display settings, and leave the Display settings screen open. Do not change any settings or open other apps."

def run(*args, timeout=30):
    return subprocess.run(args, check=True, capture_output=True, timeout=timeout)

def display_visible(xml):
    nodes = ET.fromstring(xml).iter("node")
    texts = {n.get("text", "").strip().casefold() for n in nodes}
    return "display" in texts and bool(texts & {"brightness level", "adaptive brightness", "dark theme", "display size and text", "screen timeout"})

def main():
    mode = os.environ.get("DEMO_MODE", "smoke")
    out = Path("out")
    out.mkdir(exist_ok=True)
    report = {"mode": mode, "goal": GOAL, "passed": False, "agent_executed": False}
    try:
        if mode == "smoke":
            run("adb", "shell", "am", "start", "-a", "android.settings.DISPLAY_SETTINGS")
        elif mode == "agent":
            if os.environ.get("GEMINI_FREE_TIER_CONFIRMED") != "true" or not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GEMINI_MODEL"):
                raise RuntimeError("Dedicated free-tier-only project and model required")
            run("mobilerun", "setup", timeout=150)
            run("mobilerun", "ping")
            run("adb", "shell", "input", "keyevent", "KEYCODE_HOME")
            report["agent_executed"] = True
            run("mobilerun", "run", GOAL, "--provider", "GoogleGenAI", "--model", os.environ["GEMINI_MODEL"], "--steps", "12", timeout=240)
        else:
            raise ValueError("Invalid mode")
        for _ in range(5):
            run("adb", "shell", "uiautomator", "dump", "/sdcard/demo.xml")
            xml = run("adb", "shell", "cat", "/sdcard/demo.xml").stdout
            if display_visible(xml):
                report["passed"] = True
                break
            time.sleep(2)
        if not report["passed"]:
            raise RuntimeError("Independent UI assertion failed")
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        raise RuntimeError("Demo failed; consult result.json") from None
    finally:
        try:
            (out / "screen.png").write_bytes(run("adb", "exec-out", "screencap", "-p").stdout)
        except Exception:
            pass
        (out / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
