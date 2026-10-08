"""Read-only ARCH000 index inspection for development, not content extraction.

Altered Python adaptation of the index and filename hash algorithms in
Gibbed.Rebirth by Rick, commit 8454c449cc60d680d57e3edb27ea9e56009c024a.
See third_party/Gibbed.Rebirth-LICENSE.txt for the original zlib notice.
This module never decrypts, extracts, modifies, or packages game content.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    name_hash: int
    offset: int
    length: int
    checksum: int


def name_hash(path: str) -> int:
    path = path.lower().replace('\\', '/')
    if not path.isascii():
        raise ValueError('Only ASCII resource paths are supported by this development inspector')
    first, second = 5381, 0x5BB2220E
    for character in path:
        first = (first * 33 + ord(character)) & 0xFFFFFFFF
        second = ((second ^ ord(character)) * 0x1000193) & 0xFFFFFFFF
    return first | (second << 32)


def read_index(path: Path) -> tuple[int, dict[int, Entry]]:
    size = path.stat().st_size
    with path.open('rb') as stream:
        header = stream.read(14)
        if len(header) != 14 or header[:7] != b'ARCH000':
            raise ValueError('Not a supported Rebirth ARCH000 archive')
        mode, index_offset, count = struct.unpack('<BIH', header[7:])
        if mode not in (0, 1, 2, 5):
            raise ValueError(f'Unsupported archive mode: {mode}')
        if index_offset < 14 or index_offset + count * 20 > size:
            raise ValueError('Archive index is outside the file')
        stream.seek(index_offset)
        entries = {}
        for _ in range(count):
            part_a, part_b, offset, length, checksum = struct.unpack('<IIIII', stream.read(20))
            combined = part_a | (part_b << 32)
            if combined in entries:
                raise ValueError('Duplicate archive entry hash')
            if offset < 14 or offset > size or (length and offset == size):
                raise ValueError('Archive entry offset is outside the data region')
            if index_offset <= offset < index_offset + count * 20:
                raise ValueError('Archive entry points into its index')
            entries[combined] = Entry(combined, offset, length, checksum)
        return mode, entries


def archives_at(install: Path) -> list[Path]:
    # Bounded search: game root and direct resource directories only.
    found = list(install.glob('*.a'))
    for directory in install.iterdir():
        if directory.is_dir() and directory.name.lower().startswith('resources'):
            found.extend(directory.glob('*.a'))
    return sorted(set(found))
