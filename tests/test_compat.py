"""Unit tests for the Craft CLI version and catalog probes.

Parser shapes were captured from the installed CLIs on 2026-10-20 (cadcraft,
figcraft, pdfcraft, photocraft). The check() tests patch only the subprocess
runner and the baseline path - no real CLI is executed and no real baseline
file is touched.
"""

import json
import os

import pytest

from democraft_mcp import compat


def test_parse_version_handles_the_shipped_shapes():
    assert compat.parse_version("cadcraft-cli 0.8.0") == (0, 8, 0)
    assert compat.parse_version("SoundCraft CLI 0.10.0") == (0, 10, 0)
    assert compat.parse_version("photocraft-cli 0.10.0 (8407d9ccb, 2026-10-18)") == (0, 10, 0)
    assert compat.parse_version("pdfcraft-cli 0.9.0\nDiscord: https://x/y") == (0, 9, 0)


def test_parse_version_returns_none_without_a_version():
    assert compat.parse_version("commands: unknown option --json") is None
    assert compat.parse_version("") is None


def test_list_of_alias_objects_uses_first_alias():
    verbs, kind = compat.verbs_of([{"aliases": ["info", "i"]}, {"aliases": ["convert"]}])
    assert kind == "json"
    assert verbs == ("convert", "info")


def test_list_of_id_objects():
    verbs, _ = compat.verbs_of([{"id": "node.create"}, {"id": "file.open"}])
    assert verbs == ("file.open", "node.create")


def test_null_command_falls_through_to_name():
    verbs, _ = compat.verbs_of([{"command": None, "name": "doc_open"}])
    assert verbs == ("doc_open",)


def test_command_wins_over_name():
    verbs, _ = compat.verbs_of([{"command": "combine", "name": "whatever"}])
    assert verbs == ("combine",)


def test_text_catalog_skips_indented_continuations_and_prose():
    text = "node.create*  Create layer\n    {type: rectangle|x}\nfile.open  Open\nUsage:\n"
    verbs, kind = compat.verbs_of(text)
    assert kind == "text"
    assert verbs == ("file.open", "node.create")


def test_unstructureable_text_has_no_verbs():
    verbs, kind = compat.verbs_of("commands: unknown option --json")
    assert verbs is None
    assert kind == "text"


# --- check() against a patched runner -------------------------------------

PAYLOAD_A = json.dumps([{"id": "info"}, {"id": "convert"}])
PAYLOAD_B = json.dumps([{"id": "info"}, {"id": "convert"}, {"id": "audit"}])


@pytest.fixture
def cli(tmp_path, monkeypatch):
    exe = tmp_path / "fakecli.exe"
    exe.write_text("stub", encoding="utf-8")
    monkeypatch.setattr(compat, "_CACHE", {})
    monkeypatch.setattr(compat, "state_path", lambda: tmp_path / "craft_compat.json")
    return exe


def _patch_cli(monkeypatch, version="0.9.0", payload=PAYLOAD_A):
    def fake_run(_exe, argv, _timeout):
        if argv == ("--version",):
            return 0, f"fakecli {version}"
        if argv == ("commands", "--json"):
            return 0, payload
        return 1, ""

    monkeypatch.setattr(compat, "_run", fake_run)


def _bump(exe, seconds=2):
    st = exe.stat()
    os.utime(exe, (st.st_atime, st.st_mtime + seconds))
    compat._CACHE.clear()


def test_first_check_records_baseline(cli, monkeypatch, tmp_path):
    _patch_cli(monkeypatch)
    res = compat.check(cli)
    assert res["version"] == "0.9.0"
    assert res["verbs"] == 2
    assert res["schema_kind"] == "json"
    assert res["drift"] is None
    state = json.loads((tmp_path / "craft_compat.json").read_text(encoding="utf-8"))
    assert state[str(cli)]["version"] == "0.9.0"


def test_second_check_without_change_is_quiet(cli, monkeypatch):
    _patch_cli(monkeypatch)
    compat.check(cli)
    _bump(cli)
    assert compat.check(cli)["drift"] is None


def test_version_change_is_drift(cli, monkeypatch):
    _patch_cli(monkeypatch, version="0.9.0")
    compat.check(cli)
    _patch_cli(monkeypatch, version="0.10.0")
    _bump(cli)
    drift = compat.check(cli)["drift"]
    assert drift["version_changed"] is True
    assert drift["from_version"] == "0.9.0"
    assert drift["to_version"] == "0.10.0"


def test_catalog_change_is_drift_with_added_verb(cli, monkeypatch):
    _patch_cli(monkeypatch, payload=PAYLOAD_A)
    compat.check(cli)
    _patch_cli(monkeypatch, payload=PAYLOAD_B)
    _bump(cli)
    drift = compat.check(cli)["drift"]
    assert drift["catalog_changed"] is True
    assert drift["added"] == ["audit"]
    assert drift["removed"] == []


def test_drift_persists_until_forced(cli, monkeypatch):
    _patch_cli(monkeypatch, version="0.9.0")
    compat.check(cli)
    _patch_cli(monkeypatch, version="0.11.0")
    _bump(cli)
    assert compat.check(cli)["drift"] is not None
    assert compat.check(cli)["drift"] is not None
    forced = compat.check(cli, force=True)
    assert forced["acknowledged"] is True
    assert forced["drift"] is None
    assert forced["accepted"]["to_version"] == "0.11.0"
    assert compat.check(cli)["drift"] is None


def test_missing_cli_is_reported_not_raised(tmp_path, monkeypatch):
    monkeypatch.setattr(compat, "_CACHE", {})
    monkeypatch.setattr(compat, "state_path", lambda: tmp_path / "none.json")
    res = compat.check(tmp_path / "absent.exe")
    assert res["error"] == "wrappee_missing"
    assert res["installed"] is False
