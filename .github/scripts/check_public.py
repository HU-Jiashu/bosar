#!/usr/bin/env python3
# Copyright (c) 2026 Jiashu Hu. All rights reserved.
"""The content check of this documentation repository (generated - do not edit by hand).

Structural checks: no local home path, no drive-rooted absolute path and no e-mail address
other than the published contact - in every file that decodes as UTF-8, in the text chunks of
every PNG and, with --history, in every commit (author, committer, message, diff) and tag.

    python .github/scripts/check_public.py <dir>              # the tree, exit 1 on any hit
    python .github/scripts/check_public.py <dir> --history    # ... and the history
"""

from __future__ import annotations

import argparse
import bisect
import re
import subprocess
import sys
import unicodedata
import zlib
from pathlib import Path

_PNG = b"\x89PNG\r\n\x1a\n"
HISTORY_FORMAT = "commit %H%nAuthor: %an <%ae>%nCommitter: %cn <%ce>%n%n%B"
TAG_FORMAT = "tag %(refname)%0aTagger: %(taggername) %(taggeremail)%0a%0a%(contents)"


def normalise(text: str) -> str:
    """NFKC: full-width and compatibility forms become their plain equivalents."""
    return unicodedata.normalize("NFKC", text)


def png_text(data: bytes) -> str:
    """The text chunks (tEXt, zTXt, iTXt) of a PNG, one per line."""
    out, pos = [], len(_PNG)
    while pos + 8 <= len(data):
        size = int.from_bytes(data[pos : pos + 4], "big")
        kind, body = data[pos + 4 : pos + 8], data[pos + 8 : pos + 8 + size]
        pos += 12 + size
        try:
            if kind == b"tEXt":
                out.append(body.replace(b"\0", b" ").decode("latin-1"))
            elif kind == b"zTXt":
                name, _, rest = body.partition(b"\0")
                out.append(
                    name.decode("latin-1") + " " + zlib.decompress(rest[1:]).decode("latin-1")
                )
            elif kind == b"iTXt":
                name, _, rest = body.partition(b"\0")
                flag, rest = rest[0], rest[2:]
                lang, _, rest = rest.partition(b"\0")
                local, _, value = rest.partition(b"\0")
                value = zlib.decompress(value) if flag else value
                parts = (name, lang, local, value)
                out.append(" ".join(p.decode("utf-8", errors="replace") for p in parts))
        except (zlib.error, IndexError):
            out.append(f"unreadable {kind.decode('latin-1')} chunk")
        if kind == b"IEND":
            break
    return "\n".join(out)


def file_text(path: Path) -> str | None:
    """The text to scan of ``path``: a UTF-8 file as it is, a PNG's text chunks, else None."""
    data = path.read_bytes()
    if data.startswith(_PNG):
        return png_text(data)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def history_text(root: Path) -> str:
    """The history of the clone at ``root``: ``git log -p --all`` with the author and the
    committer of every commit, then every tag with its tagger and message."""

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-c", "safe.directory=*", *args],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout

    log = git("log", "-p", "--all", "--format=" + HISTORY_FORMAT)
    tags = git("for-each-ref", "--format=" + TAG_FORMAT, "refs/tags")
    return log + "\n" + tags


def scan_patterns(text: str, pats: list[tuple]) -> list[tuple[str, int, str]]:
    """``(label, line number, the line)`` for every match of ``pats`` - ``(label, compiled
    pattern, compiled exemptions)``: a match that lies inside a match of one of its exemptions
    is innocent. The text is NFKC-normalised and matched whole."""
    text = normalise(text)
    starts = [0] + [m.end() for m in re.finditer("\n", text)]
    lines = text.split("\n")
    found: set[tuple[int, str]] = set()
    for label, pat, exempt in pats:
        spans = [(e.start(), e.end()) for x in exempt for e in x.finditer(text)]
        for m in pat.finditer(text):
            if any(a <= m.start() and m.end() <= b for a, b in spans):
                continue
            found.add((bisect.bisect_right(starts, m.start()), label))
    return [(label, n, lines[n - 1].strip()[:120]) for n, label in sorted(found)]


def scan_tree_with(root: Path, scan, skip: tuple[str, ...] = (".git",)) -> list[tuple]:
    """``(file, label, line number, line)`` of ``scan(text)`` over every file under ``root``
    that decodes as UTF-8, and the text chunks of every PNG."""
    out = []
    for p in sorted(root.rglob("*")):
        if any(part in skip for part in p.relative_to(root).parts) or not p.is_file():
            continue
        text = file_text(p)
        if text is None:
            continue
        for label, lineno, line in scan(text):
            out.append((p.relative_to(root).as_posix(), label, lineno, line))
    return out


PATTERNS = [
    ('home path', '(?<![\\w/`])/(?:Users|home|Volumes|mnt)/', []),
    ('home path', '(?<![A-Za-z0-9_])[A-Za-z]:(?:\\\\+|/)(?i:users)(?:\\\\+|/)', []),
    ('drive path', '(?<![A-Za-z0-9_])[D-Zd-z]:[\\\\/]', []),
    ('e-mail address', '(?<![\\w.%+-])[\\w.%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,}(?![\\w-])', ['(?i)(?<![\\w.%+-])(?:oswaldmurphy66@gmail\\.com|noreply@github\\.com|git@github\\.com|[\\w.+-]+@users\\.noreply\\.github\\.com)(?![\\w-])']),
]

COMPILED = [(label, re.compile(p), [re.compile(e) for e in ex]) for label, p, ex in PATTERNS]


def scan(text: str) -> list[tuple[str, int, str]]:
    """``(label, line number, the line)`` for every structural hit of ``text``."""
    return scan_patterns(text, COMPILED)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root")
    ap.add_argument("--history", action="store_true", help="also scan the history")
    args = ap.parse_args(argv)
    root = Path(args.root)
    hits = scan_tree_with(root, scan)
    for file, label, lineno, line in hits:
        print(f"{file}:{lineno}: {label}: {line}")
    print(f"tree: {len(hits)} hit(s)")
    bad = len(hits)
    if args.history:
        found = scan(history_text(root))
        for label, lineno, line in found[:50]:
            print(f"history:{lineno}: {label}: {line}")
        print(f"history: {len(found)} hit(s)")
        bad += len(found)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
