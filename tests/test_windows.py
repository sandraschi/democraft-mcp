"""Window focus for hands-in runs - logic only, no real windows.

The ctypes layer is injected, so these tests assert orchestration: which exe is
targeted, when a launch happens, and that a missing GUI or a Windows refusal is
reported instead of raising.
"""

from pathlib import Path

import pytest

from democraft_mcp import windows

_REAL_QUARANTINE = windows.quarantine_recovery


@pytest.fixture(autouse=True)
def on_windows(monkeypatch):
    monkeypatch.setattr(windows, "IS_WINDOWS", True)
    monkeypatch.setattr(
        windows, "quarantine_recovery", lambda *a, **k: {"moved": [], "dest": None, "error": None}
    )


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


def test_quarantine_moves_stale_autosave_and_recovery(tmp_path):
    appdata = tmp_path / "AppData"
    auto = appdata / "SoundCraft" / "Autosave" / "Untitled 1"
    auto.mkdir(parents=True)
    (auto / "session.scraft").write_text("x", encoding="utf-8")
    rec = appdata / "SoundCraft" / "Recovery" / "run-1-0"
    rec.mkdir(parents=True)
    (rec / "lock").write_text("", encoding="utf-8")
    got = _REAL_QUARANTINE("SoundCraft", appdata, tmp_path / "q")
    assert got["error"] is None
    assert sorted(got["moved"]) == ["Autosave/Untitled 1", "Recovery/run-1-0"]
    assert not auto.exists() and not rec.exists()
    kept = Path(got["dest"]) / "Autosave" / "Untitled 1" / "session.scraft"
    assert kept.read_text(encoding="utf-8") == "x"


def test_quarantine_is_a_noop_without_stale_state(tmp_path):
    got = _REAL_QUARANTINE("FilmCraft", tmp_path / "AppData", tmp_path / "q")
    assert got == {"moved": [], "dest": None, "error": None}


def test_app_data_name_is_install_folder():
    cli = Path(r"C:\Program Files\SoundCraft\soundcraft-cli.exe")
    assert windows.app_data_name(cli) == "SoundCraft"


def test_open_file_in_gui_falls_back_to_launch(tmp_path, monkeypatch):
    cli = tmp_path / "gridcraft-cli.exe"
    cli.write_text("stub", encoding="utf-8")
    windows.gui_exe(cli).write_text("stub", encoding="utf-8")
    file_path = tmp_path / "report.xlsx"
    file_path.write_text("data", encoding="utf-8")

    launched = []
    monkeypatch.setattr(windows, "_launch", lambda exe, extra=None: launched.append((exe, extra)))
    monkeypatch.setattr(windows.GridCraftLiveClient, "connect", lambda self: False)

    ok = windows.open_file_in_gui(cli, file_path)
    assert ok is True
    assert len(launched) == 1
    assert launched[0][0].name == "gridcraft.exe"
    assert str(file_path.resolve()) in (launched[0][1] or [])


def test_gridcraft_live_client_methods():
    client = windows.GridCraftLiveClient(port=9999, token="test-token")
    assert client.port == 9999
    assert client.token == "test-token"
    assert client.send_command("test", {}) is None
    assert client.set_cell("A1", "100") is False
    assert client.open_workbook("test.xlsx") is False


def test_generalized_live_clients():
    wc = windows.WordCraftLiveClient(port=9998)
    assert wc.port == 9998
    assert wc.insert_text("hello") is False

    cad = windows.CADCraftLiveClient(port=9997)
    assert cad.port == 9997
    assert cad.execute_command("line", {}) is False

    pc = windows.PhotoCraftLiveClient(port=9996)
    assert pc.port == 9996
    assert pc.execute_command("brush", {}) is False

    dc = windows.DeckCraftLiveClient(port=9995)
    assert dc.port == 9995
    assert dc.execute_command("slide.new", {}) is False

    fc = windows.FigCraftLiveClient(port=9994)
    assert fc.port == 9994
    assert fc.execute_command("text.set", {}) is False

    film = windows.FilmCraftLiveClient(port=9993, token="film-tok")
    assert film.port == 9993
    assert film.token == "film-tok"
    assert film.execute_command("sequence.cut", {}) is False

    solid = windows.SolidCraftLiveClient(port=9992)
    assert solid.port == 9992
    assert solid.execute_command("parameters.change", {}) is False

    vec = windows.VectorCraftLiveClient(port=9991)
    assert vec.port == 9991
    assert vec.execute_command("addon.cleanup.fix", {}) is False

    snd = windows.SoundCraftLiveClient(port=9990)
    assert snd.port == 9990
    assert snd.execute_command("mix.solo", {}) is False


def test_open_file_in_gui_with_new_clients(tmp_path, monkeypatch):
    for name, client_cls in [
        ("filmcraft", windows.FilmCraftLiveClient),
        ("solidcraft", windows.SolidCraftLiveClient),
        ("vectorcraft", windows.VectorCraftLiveClient),
        ("soundcraft", windows.SoundCraftLiveClient),
        ("figcraft", windows.FigCraftLiveClient),
    ]:
        cli = tmp_path / f"{name}-cli.exe"
        cli.write_text("stub", encoding="utf-8")
        windows.gui_exe(cli).write_text("stub", encoding="utf-8")
        target_file = tmp_path / f"out.{name[:3]}"
        target_file.write_text("data", encoding="utf-8")

        monkeypatch.setattr(client_cls, "connect", lambda self: True)
        monkeypatch.setattr(client_cls, "execute_command", lambda self, cmd, params: True)
        monkeypatch.setattr(windows, "_find_window", lambda exe, n=name: (100, 200, f"{n.title()}"))
        monkeypatch.setattr(windows, "_foreground", lambda hwnd: True)

        ok = windows.open_file_in_gui(cli, target_file)
        assert ok is True
