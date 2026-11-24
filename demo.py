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
    nodes = list(ET.fromstring(xml).iter("node"))
    settings = [n for n in nodes if n.get("package") == "com.android.settings"]
    # Android 34 exposes the collapsing toolbar title through content-desc.
    # The Settings package and screen-specific controls remain required.
    labels = {n.get("text", "").strip().casefold() for n in settings}
    title = any(n.get("resource-id") == "com.android.settings:id/collapsing_toolbar"
                and (n.get("content-desc", "").strip().casefold() == "display"
                     or n.get("text", "").strip().casefold() == "display")
                for n in settings)
    return title and bool(labels & {"brightness level", "adaptive brightness", "dark theme", "display size and text", "screen timeout"})

def wait_for_display(out, report):
    # Android can accept am start before the accessibility tree is ready.
    deadline = time.monotonic() + 90
    attempts = []
    while time.monotonic() < deadline:
        try:
            # Never accept a stale tree from an earlier attempt.
            run("adb", "shell", "rm", "-f", "/sdcard/demo.xml", timeout=5)
            dump = run("adb", "shell", "uiautomator", "dump", "/sdcard/demo.xml", timeout=15)
            xml = run("adb", "exec-out", "cat", "/sdcard/demo.xml", timeout=5).stdout
            (out / "hierarchy.xml").write_bytes(xml)
            matched = display_visible(xml)
            attempts.append({"matched": matched})
            if matched:
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ET.ParseError) as exc:
            attempts.append({"error": type(exc).__name__, "command": str(getattr(exc, "cmd", "")), "stderr": str(getattr(exc, "stderr", ""))[:300]})
        finally:
            report["oracle_attempts"] = attempts
        time.sleep(2)
    return False

def main():
    mode = os.environ.get("DEMO_MODE", "smoke")
    out = Path("out")
    out.mkdir(exist_ok=True)
    report = {"mode": mode, "goal": GOAL, "passed": False, "agent_executed": False}
    try:
        if mode == "smoke":
            run("adb", "shell", "am", "start", "-a", "android.settings.DISPLAY_SETTINGS")
        elif mode in ("agent", "local"):
            if mode == "agent":
                if os.environ.get("GEMINI_FREE_TIER_CONFIRMED") != "true" or not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GEMINI_MODEL"):
                    raise RuntimeError("Dedicated free-tier-only project and model required")
                provider = ["--provider", "GoogleGenAI", "--model", os.environ["GEMINI_MODEL"]]
                agent_timeout = 240
            else:
                if os.environ.get("OLLAMA_NO_CLOUD") != "1":
                    raise RuntimeError("Local-only inference required")
                provider = ["--provider", "Ollama", "--model", "qwen3.5:2b", "--base_url", "http://127.0.0.1:11434"]
                agent_timeout = 600
            run("mobilerun", "setup", timeout=150)
            run("mobilerun", "ping")
            run("adb", "shell", "input", "keyevent", "KEYCODE_HOME")
            report["agent_executed"] = True
            try:
                result = run("mobilerun", "run", GOAL, *provider, "--steps", "12", "--no-vision", timeout=agent_timeout)
                if mode == "local":
                    (out / "agent.log").write_bytes(result.stdout + result.stderr)
            except subprocess.CalledProcessError as exc:
                if mode == "local":
                    (out / "agent.log").write_bytes((exc.stdout or b"") + (exc.stderr or b""))
                raise
        else:
            raise ValueError("Invalid mode")
        report["passed"] = wait_for_display(out, report)
        if not report["passed"]:
            raise RuntimeError("Independent UI assertion failed")
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        if isinstance(exc, RuntimeError):
            report["error_message"] = str(exc)
        raise RuntimeError("Demo failed; consult result.json") from None
    finally:
        try:
            (out / "screen.png").write_bytes(run("adb", "exec-out", "screencap", "-p").stdout)
        except Exception:
            pass
        (out / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
