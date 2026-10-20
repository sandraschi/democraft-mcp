"""Craft CLI version and command-catalog probes.

The 13 Craft CLIs are separate Rust binaries that ship new builds several times
a week. Measured 2026-10-20: the launcher wrote four new builds to
``C:\\Program Files`` at 10:29-10:43 UTC while GitHub published the matching
tags at 14:34-16:48 UTC. A calendar probe is therefore always late - the only
reliable detector is the binary in front of you at call time.

Discovery dialects differ per app (measured 2026-10-20):

    cadcraft   ``commands``         -> JSON, and no ``--json`` flag
    figcraft   ``commands --json``  -> JSON (plain ``commands`` is text)
    pdfcraft   ``tools --json``     -> JSON (no ``commands`` verb at all)

So the probe walks a dialect ladder and falls back to hashing raw text. It
records a baseline per installed CLI in ``data/craft_compat.json``; once the
baseline exists, a changed version or verb set is reported as drift instead of
being silently accepted.

No third-party dependencies. CLI output is read as text and parsed, never
executed.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
TEXT_VERB_RE = re.compile(r"^([a-z][a-z0-9_.-]*[a-z0-9])\*?\s")
DIALECTS: tuple[tuple[str, ...], ...] = (
    ("commands", "--json"),
    ("tools", "--json"),
    ("commands",),
)
MAX_CATALOG_BYTES = 4_000_000
STATE_NAME = "craft_compat.json"

_CACHE: dict[str, dict] = {}


def state_path() -> Path:
    """Baseline file lives next to the package, not in the caller's cwd."""
    return Path(__file__).resolve().parents[2] / "data" / STATE_NAME


def parse_version(text: str) -> tuple[int, int, int] | None:
    """First semver in the output.

    The CLIs print at least three shapes, some with trailing prose:

        cadcraft-cli 0.8.0
        SoundCraft CLI 0.10.0
        photocraft-cli 0.10.0 (8407d9ccb, 2026-10-18)
        pdfcraft-cli 0.9.0 + three lines of Discord/web/source links

    Raw string comparison false-fires on the build hash; only the tuple counts.
    """
    m = VERSION_RE.search(text or "")
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _item_name(item: object) -> str | None:
    if not isinstance(item, dict):
        return None
    for key in ("id", "command", "verb", "name"):
        val = item.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    aliases = item.get("aliases")
    if isinstance(aliases, list) and aliases:
        first = aliases[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
        if isinstance(first, dict):
            for key in ("name", "id"):
                val = first.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
    return None


def verbs_of(payload: object) -> tuple[tuple[str, ...] | None, str]:
    """Extract a canonical verb set.

    Returns ``(verbs, kind)`` where kind is ``json``, ``text`` or ``raw``.
    ``raw`` means nothing structured was found and the caller should hash the
    text itself; drift is then still detectable, just less descriptive.
    """
    if isinstance(payload, str):
        return _verbs_from_text(payload)
    if isinstance(payload, list):
        names = {_item_name(i) for i in payload}
        found = tuple(sorted(n for n in names if n))
        return (found or None), "json"
    if isinstance(payload, dict):
        for key in ("commands", "tools", "items"):
            val = payload.get(key)
            if isinstance(val, list):
                names = {_item_name(i) for i in val}
                found = tuple(sorted(n for n in names if n))
                if found:
                    return found, "json"
        aliases = payload.get("aliases")
        if isinstance(aliases, list):
            found = tuple(sorted(a for a in aliases if isinstance(a, str) and a))
            if found:
                return found, "json"
        keys = tuple(sorted(k for k in payload if isinstance(k, str) and k))
        return (keys or None), "json"
    return None, "raw"


def _verbs_from_text(text: str) -> tuple[tuple[str, ...] | None, str]:
    found: set[str] = set()
    for line in (text or "").splitlines():
        if not line or line[0].isspace():
            continue
        m = TEXT_VERB_RE.match(line)
        if m:
            found.add(m.group(1))
    return (tuple(sorted(found)), "text") if found else (None, "text")


def _hash(verbs: tuple[str, ...] | None, text: str) -> str:
    if verbs:
        body = "\n".join(verbs)
    else:
        body = " ".join((text or "").split())
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def _run(exe: Path, argv: tuple[str, ...], timeout: int) -> tuple[int, str] | None:
    try:
        proc = subprocess.run(  # noqa: S603 - fixed argv, absolute path, no shell
            [str(exe), *argv],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = (proc.stdout or "")[:MAX_CATALOG_BYTES]
    return proc.returncode, out


def _stat_key(cli_path: Path) -> tuple[float, int]:
    st = cli_path.stat()
    return st.st_mtime, st.st_size


def _load_state() -> dict:
    path = state_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state: dict) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def recorded(cli_path: Path) -> dict | None:
    """Baseline already on disk, without touching the binary."""
    return _load_state().get(str(cli_path))


def probe_version(cli_path: Path) -> dict:
    """Version plus file facts for one CLI. One subprocess per new build."""
    key = str(cli_path)
    if not cli_path.is_file():
        return {"installed": False, "version": None, "modified": None, "semver": None}
    try:
        mtime, size = _stat_key(cli_path)
    except OSError:
        return {"installed": False, "version": None, "modified": None, "semver": None}
    hit = _CACHE.get(key)
    if hit and hit.get("mtime") == mtime and hit.get("size") == size:
        return hit
    ran = _run(cli_path, ("--version",), 15)
    text = ran[1] if ran else ""
    semver = parse_version(text)
    row = {
        "installed": True,
        "version": ".".join(str(p) for p in semver) if semver else None,
        "semver": list(semver) if semver else None,
        "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime)),
        "size": size,
        "mtime": mtime,
    }
    _CACHE[key] = row
    return row


def _discover(cli_path: Path) -> dict:
    """Walk the dialect ladder until one catalog answers."""
    for argv in DIALECTS:
        ran = _run(cli_path, argv, 30)
        if not ran:
            continue
        code, out = ran
        if code != 0 or not out.strip():
            continue
        try:
            loaded: object = json.loads(out)
        except json.JSONDecodeError:
            loaded = out
        if loaded in ([], {}, None):
            # Some builds answer the dialect but publish nothing (designcraft
            # returns [] to `commands --json`). Try the next dialect instead of
            # recording an empty catalog as if it were the whole API.
            continue
        verbs, kind = verbs_of(loaded)
        if not verbs:
            # Structured output we cannot name verbs in (pdfcraft's `tools`
            # entries carry command=null). Raw hash still detects drift.
            kind = "raw"
        return {
            "source": " ".join(argv),
            "verbs": list(verbs) if verbs else [],
            "count": len(verbs) if verbs else 0,
            "schema_hash": _hash(verbs, out),
            "schema_kind": kind,
        }
    return {
        "source": None,
        "verbs": [],
        "count": 0,
        "schema_hash": None,
        "schema_kind": "unavailable",
    }


def check(cli_path: Path, force: bool = False) -> dict:
    """Compare the installed CLI against its recorded baseline.

    ``force`` accepts the current build as the new baseline. Without it, drift
    keeps being reported on every call until someone acknowledges it - which
    is the point: a silently upgraded engine must not look like a green run.
    """
    version = probe_version(cli_path)
    if not version.get("installed"):
        return {
            "installed": False,
            "version": None,
            "modified": None,
            "schema_hash": None,
            "schema_kind": "unavailable",
            "verbs": 0,
            "drift": None,
            "error": "wrappee_missing",
        }

    cache_key = str(cli_path)
    stamp = (version.get("mtime"), version.get("size"))
    cached = _CACHE.get(f"{cache_key}#cat")
    if cached and cached.get("stamp") == stamp and not force:
        catalog = dict(cached)
    else:
        catalog = _discover(cli_path)
        catalog["stamp"] = stamp
        _CACHE[f"{cache_key}#cat"] = catalog

    state = _load_state()
    base = state.get(cache_key)
    drift = None
    if base:
        added = sorted(set(catalog["verbs"]) - set(base.get("verbs", [])))
        removed = sorted(set(base.get("verbs", [])) - set(catalog["verbs"]))
        version_changed = base.get("version") != version.get("version")
        hash_changed = base.get("schema_hash") != catalog["schema_hash"]
        if version_changed or hash_changed:
            drift = {
                "from_version": base.get("version"),
                "to_version": version.get("version"),
                "version_changed": version_changed,
                "catalog_changed": hash_changed,
                "schema_kind": catalog["schema_kind"],
                "added": added,
                "removed": removed,
            }

    accepted = None
    if drift is not None and force:
        accepted = drift
        drift = None

    if drift is None:
        prev = base or {}
        unchanged = (
            prev.get("version") == version.get("version")
            and prev.get("schema_hash") == catalog["schema_hash"]
            and prev.get("size") == version.get("size")
        )
        if not unchanged:
            state[cache_key] = {
                "version": version.get("version"),
                "modified": version.get("modified"),
                "size": version.get("size"),
                "schema_hash": catalog["schema_hash"],
                "schema_kind": catalog["schema_kind"],
                "verbs": catalog["verbs"],
                "source": catalog.get("source"),
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            _save_state(state)

    return {
        "installed": True,
        "version": version.get("version"),
        "modified": version.get("modified"),
        "schema_hash": catalog["schema_hash"],
        "schema_kind": catalog["schema_kind"],
        "verbs": catalog["count"],
        "source": catalog.get("source"),
        "drift": drift,
        "accepted": accepted,
        "acknowledged": bool(drift is None or force),
    }
