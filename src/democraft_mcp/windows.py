"""Bring a Craft app's own window to the foreground for hands-in runs.

The demos drive the installed `<app>-cli.exe` headlessly; the app's GUI is a
separate `<app>.exe` next to it. For a hands-in run a human asked to watch, we
start that GUI if needed, restore and maximise its main window, and hand it the
foreground before the first CLI step, so the app is on screen while the work
happens rather than appearing afterwards.

Two honest limits:

* This raises the app, it does not route commands through it. The demo still
  runs the headless CLI (FilmCraft's own ``--bridge`` is a separate feature).
* Windows may refuse the foreground handoff to a background process. We try
  the direct call, then the Alt-key unlock, and report ``foreground: false``
  instead of pretending it worked.

No third-party dependencies; ctypes only.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"

SW_RESTORE = 9
SW_MAXIMIZE = 3
VK_MENU = 0x12
KEYEVENTF_KEYUP = 0x0002
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
CREATE_DETACHED = 0x00000008

if IS_WINDOWS:
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _user32.GetForegroundWindow.restype = wintypes.HWND
else:  # pragma: no cover - the fleet is Windows, keep imports safe elsewhere
    _user32 = None
    _kernel32 = None
    _WNDENUMPROC = None


def gui_exe(cli_path: Path) -> Path:
    """`cadcraft-cli.exe` -> `cadcraft.exe`, in the same install directory."""
    name = cli_path.name
    suffix = "-cli.exe"
    if name.lower().endswith(suffix):
        name = name[: -len(suffix)] + ".exe"
    return cli_path.with_name(name)


def pick_main_window(rows: list[tuple[int, str, int]]) -> int | None:
    """Largest titled window; untitled helpers only if nothing is titled."""
    if not rows:
        return None
    titled = [row for row in rows if row[1].strip()]
    return max(titled or rows, key=lambda row: row[2])[0]


def _pid_image(pid: int) -> str | None:
    handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buf))
        ok = _kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
        return buf.value if ok else None
    finally:
        _kernel32.CloseHandle(handle)


def _all_windows() -> list[tuple[int, int, str, int]]:
    """Visible top-level windows: (hwnd, pid, title, area)."""
    found: list[tuple[int, int, str, int]] = []

    def callback(hwnd, _lparam):
        if not _user32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        length = _user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(length + 1)
        _user32.GetWindowTextW(hwnd, title, length + 1)
        rect = wintypes.RECT()
        _user32.GetWindowRect(hwnd, ctypes.byref(rect))
        area = max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)
        found.append((int(hwnd), int(pid.value), title.value, area))
        return True

    _user32.EnumWindows(_WNDENUMPROC(callback), 0)
    return found


def _find_window(exe: Path) -> tuple[int, int, str] | None:
    """The app's main window, matched by the owning process image name."""
    rows: list[tuple[int, int, str, int]] = []
    pid_seen: dict[int, str | None] = {}
    target = exe.name.lower()
    for hwnd, pid, title, area in _all_windows():
        if pid not in pid_seen:
            pid_seen[pid] = _pid_image(pid)
        image = pid_seen[pid]
        if image and Path(image).name.lower() == target:
            rows.append((hwnd, pid, title, area))
    hwnd = pick_main_window([(h, title, area) for h, _p, title, area in rows])
    if hwnd is None:
        return None
    for row in rows:
        if row[0] == hwnd:
            return row[0], row[1], row[2]
    return None


def _launch(exe: Path) -> None:
    subprocess.Popen(  # noqa: S603 - absolute path, no shell, fixed argv
        [str(exe)],
        cwd=str(exe.parent),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_DETACHED,
    )


def _maximize(hwnd: int) -> None:
    _user32.ShowWindow(hwnd, SW_RESTORE)
    _user32.ShowWindow(hwnd, SW_MAXIMIZE)


def _foreground(hwnd: int) -> bool:
    if _user32.SetForegroundWindow(hwnd):
        return True
    # Windows blocks a background process from stealing the foreground; a
    # synthetic Alt press lifts the restriction for the next call.
    _user32.keybd_event(VK_MENU, 0, 0, 0)
    try:
        return bool(_user32.SetForegroundWindow(hwnd))
    finally:
        _user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)


def _is_zoomed(hwnd: int) -> bool:
    return bool(_user32.IsZoomed(hwnd))


def _is_foreground(hwnd: int) -> bool:
    return int(_user32.GetForegroundWindow()) == int(hwnd)


def _wait_for_window(
    exe: Path, deadline: float, poll_s: float, want_title: bool
) -> tuple[int, int, str] | None:
    """Poll until a window exists (and, when launching, until it is titled).

    A GUI creates a transient untitled window before its main window; acting on
    that one maximises the splash and leaves the real window normal-sized.
    """
    found = _find_window(exe)
    while time.time() < deadline:
        if found is not None and (found[2].strip() or not want_title):
            return found
        time.sleep(poll_s)
        found = _find_window(exe)
    return found


RECOVERY_SUBDIRS = ("Autosave", "Recovery")


def app_data_name(cli_path: Path) -> str:
    """Install folder name doubles as the app's AppData folder (`SoundCraft`)."""
    return cli_path.parent.name


def quarantine_recovery(
    app_name: str, appdata: Path | None = None, dest_root: Path | None = None
) -> dict:
    """Move stale autosave/recovery entries aside before the GUI starts.

    egui apps show an in-window "Recover Unsaved Work" prompt when a previous
    run left an autosave. It cannot be seen by EnumWindows and Escape does not
    dismiss it, so it would sit over the demo. Only call this when the GUI is
    not running. Entries are moved, never deleted, so nothing is lost.
    """
    report: dict = {"moved": [], "dest": None, "error": None}
    try:
        base = appdata or Path(os.environ.get("APPDATA", ""))
        root = base / app_name
        entries = []
        for sub in RECOVERY_SUBDIRS:
            d = root / sub
            if d.is_dir():
                entries.extend(p for p in d.iterdir())
        if not entries:
            return report
        qroot = dest_root or (
            Path(os.environ.get("LOCALAPPDATA", str(base)))
            / "democraft-mcp"
            / "recovery_quarantine"
        )
        dest = qroot / app_name / time.strftime("%Y%m%d-%H%M%S")
        dest.mkdir(parents=True, exist_ok=True)
        report["dest"] = str(dest)
        for p in entries:
            target = dest / p.parent.name / p.name
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(p), str(target))
                report["moved"].append(f"{p.parent.name}/{p.name}")
            except OSError as exc:
                report.setdefault("failed", []).append(f"{p.name}: {exc}")
    except Exception as exc:  # noqa: BLE001 - never block a demo on housekeeping
        report["error"] = f"{type(exc).__name__}: {exc}"
    return report


def ensure_foreground(cli_path: Path, timeout_s: float = 20.0, poll_s: float = 0.25) -> dict:
    """Start/raise/maximise the app window. Never raises; always reports."""
    started = time.time()
    exe = gui_exe(cli_path)
    if not IS_WINDOWS:
        return {"ok": False, "reason": "not_windows", "exe": str(exe)}
    if not exe.is_file():
        return {"ok": False, "reason": "gui_missing", "exe": str(exe)}

    launched = False
    recovery = None
    try:
        found = _find_window(exe)
        if found is None:
            recovery = quarantine_recovery(app_data_name(cli_path))
            _launch(exe)
            launched = True
        deadline = started + max(0.0, timeout_s)
        # Always wait for the titled main window; an untitled one is a splash.
        found = _wait_for_window(exe, deadline, poll_s, want_title=True)
    except Exception as exc:  # noqa: BLE001 - the demo must not die because a window did
        return {
            "ok": False,
            "reason": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "exe": str(exe),
            "launched": launched,
            "ms": int((time.time() - started) * 1000),
        }

    if found is None:
        return {
            "ok": False,
            "reason": "no_window",
            "exe": str(exe),
            "launched": launched,
            "ms": int((time.time() - started) * 1000),
        }

    hwnd, pid, title = found
    _maximize(hwnd)
    has_foreground = _foreground(hwnd)
    time.sleep(0.15)
    return {
        "ok": True,
        "reason": None,
        "exe": str(exe),
        "pid": pid,
        "window": title,
        "launched": launched,
        "recovery_quarantine": recovery,
        "maximized": _is_zoomed(hwnd),
        "foreground": has_foreground and _is_foreground(hwnd),
        "ms": int((time.time() - started) * 1000),
    }
