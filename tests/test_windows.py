"""Window focus for hands-in runs - logic only, no real windows.

The ctypes layer is injected, so these tests assert orchestration: which exe is
targeted, when a launch happens, and that a missing GUI or a Windows refusal is
reported instead of raising.
"""

from pathlib import Path

import pytest

from democraft_mcp import windows


@pytest.fixture(autouse=True)
def on_windows(monkeypatch):
    monkeypatch.setattr(windows, "IS_WINDOWS", True)


def _cli(tmp_path: Path) -> Path:
    cli = tmp_path / "filmcraft-cli.exe"
    cli.write_text("stub", encoding="utf-8")
    windows.gui_exe(cli).write_text("stub", encoding="utf-8")
    return cli


def test_gui_exe_drops_the_cli_suffix():
    got = windows.gui_exe(Path(r"C:\Program Files\FilmCraft\filmcraft-cli.exe"))
    assert got.name == "filmcraft.exe"
    assert got.parent.name == "FilmCraft"


def test_pick_main_window_prefers_titled_then_largest():
    rows = [(1, "", 500), (2, "FilmCraft", 100), (3, "Tip", 900)]
    assert windows.pick_main_window(rows) == 3
    assert windows.pick_main_window([(1, "", 500), (2, "", 700)]) == 2
    assert windows.pick_main_window([]) is None


def test_missing_gui_is_reported_and_not_launched(tmp_path, monkeypatch):
    cli = tmp_path / "filmcraft-cli.exe"
    cli.write_text("stub", encoding="utf-8")
    launched = []
    monkeypatch.setattr(windows, "_launch", lambda exe: launched.append(exe))

    res = windows.ensure_foreground(cli, timeout_s=0)

    assert res["ok"] is False
    assert res["reason"] == "gui_missing"
    assert launched == []


def test_existing_window_is_maximised_and_raised(tmp_path, monkeypatch):
    cli = _cli(tmp_path)
    calls = []
    monkeypatch.setattr(windows, "_find_window", lambda exe: (10, 20, "FilmCraft"))
    monkeypatch.setattr(windows, "_launch", lambda exe: calls.append("launch"))
    monkeypatch.setattr(windows, "_maximize", lambda hwnd: calls.append(("max", hwnd)))
    monkeypatch.setattr(windows, "_foreground", lambda hwnd: calls.append(("fg", hwnd)) or True)
    monkeypatch.setattr(windows, "_is_zoomed", lambda hwnd: True)
    monkeypatch.setattr(windows, "_is_foreground", lambda hwnd: True)

    res = windows.ensure_foreground(cli, timeout_s=0)

    assert res["ok"] is True
    assert res["launched"] is False
    assert res["maximized"] is True
    assert res["foreground"] is True
    assert res["window"] == "FilmCraft"
    assert ("max", 10) in calls and ("fg", 10) in calls
    assert "launch" not in calls


def test_untitled_startup_window_is_not_the_target(tmp_path, monkeypatch):
    cli = _cli(tmp_path)
    seq = [(1, 2, ""), (3, 4, "FilmCraft")]
    state = {"i": 0}

    def find(exe):
        i = min(state["i"], len(seq) - 1)
        state["i"] += 1
        return seq[i]

    monkeypatch.setattr(windows, "_find_window", find)
    monkeypatch.setattr(windows, "_launch", lambda exe: None)
    monkeypatch.setattr(windows, "_maximize", lambda hwnd: None)
    monkeypatch.setattr(windows, "_foreground", lambda hwnd: True)
    monkeypatch.setattr(windows, "_is_zoomed", lambda hwnd: True)
    monkeypatch.setattr(windows, "_is_foreground", lambda hwnd: True)

    res = windows.ensure_foreground(cli, timeout_s=1, poll_s=0.001)

    assert res["ok"] is True
    assert res["window"] == "FilmCraft"


def test_launches_when_no_window_then_reports(tmp_path, monkeypatch):
    cli = _cli(tmp_path)
    state = {"calls": 0}
    launched = []

    def find(exe):
        state["calls"] += 1
        return (11, 21, "FilmCraft") if state["calls"] > 1 else None

    monkeypatch.setattr(windows, "_find_window", find)
    monkeypatch.setattr(windows, "_launch", lambda exe: launched.append(exe))
    monkeypatch.setattr(windows, "_maximize", lambda hwnd: None)
    monkeypatch.setattr(windows, "_foreground", lambda hwnd: True)
    monkeypatch.setattr(windows, "_is_zoomed", lambda hwnd: True)
    monkeypatch.setattr(windows, "_is_foreground", lambda hwnd: True)

    res = windows.ensure_foreground(cli, timeout_s=1, poll_s=0.001)

    assert res["ok"] is True
    assert res["launched"] is True
    assert len(launched) == 1
    assert launched[0].name == "filmcraft.exe"


def test_no_window_is_reported_after_the_wait(tmp_path, monkeypatch):
    cli = _cli(tmp_path)
    monkeypatch.setattr(windows, "_find_window", lambda exe: None)
    monkeypatch.setattr(windows, "_launch", lambda exe: None)

    res = windows.ensure_foreground(cli, timeout_s=0)

    assert res["ok"] is False
    assert res["reason"] == "no_window"
    assert res["launched"] is True


def test_window_failure_never_raises(tmp_path, monkeypatch):
    cli = _cli(tmp_path)

    def boom(exe):
        raise OSError("EnumWindows exploded")

    monkeypatch.setattr(windows, "_find_window", boom)

    res = windows.ensure_foreground(cli, timeout_s=0)

    assert res["ok"] is False
    assert res["reason"] == "error"
    assert "EnumWindows exploded" in res["error"]
