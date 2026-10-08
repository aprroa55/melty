"""Read-only Steam discovery for the agent working on the player's PC."""
from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path


def parse_vdf(text: str) -> dict:
    """Parse Valve KeyValues, preserving Windows paths and rejecting broken input."""
    tokens = []
    position = 0
    text = text.lstrip('\ufeff')
    while position < len(text):
        if text[position].isspace():
            position += 1
        elif text.startswith('//', position):
            end = text.find('\n', position)
            position = len(text) if end < 0 else end + 1
        elif text[position] in '{}':
            tokens.append((text[position], text[position]))
            position += 1
        elif text[position] == '"':
            position += 1
            value = []
            while position < len(text) and text[position] != '"':
                character = text[position]
                if character == '\\' and position + 1 < len(text) and text[position + 1] in '\\"':
                    position += 1
                    character = text[position]
                value.append(character)
                position += 1
            if position >= len(text):
                raise ValueError('Unterminated VDF string')
            tokens.append(('value', ''.join(value)))
            position += 1
        else:
            start = position
            while position < len(text) and not text[position].isspace() and text[position] not in '{}"':
                position += 1
            tokens.append(('value', text[start:position]))
    index = 0

    def mapping(nested=False):
        nonlocal index
        result = {}
        while index < len(tokens):
            kind, key = tokens[index]
            index += 1
            if kind == '}':
                if not nested:
                    raise ValueError('Unexpected VDF closing brace')
                return result
            if kind != 'value' or index >= len(tokens):
                raise ValueError('VDF key has no value')
            kind, value = tokens[index]
            index += 1
            if kind == '{':
                value = mapping(True)
            elif kind != 'value':
                raise ValueError('VDF key has invalid value')
            if key in result:
                raise ValueError('Duplicate VDF key: ' + key)
            result[key] = value
        if nested:
            raise ValueError('Unclosed VDF object')
        return result

    return mapping()


def get_ci(mapping: dict, name: str, default=None):
    return next((value for key, value in mapping.items() if key.lower() == name.lower()), default)


def local_path(value: str) -> Path:
    if os.name != 'nt' and 'microsoft' in platform.release().lower():
        match = re.match(r'^([A-Za-z]):[\\/](.*)', value)
        if match:
            return Path('/mnt') / match[1].lower() / match[2].replace('\\', '/')
    return Path(value)


def default_roots() -> list[Path]:
    candidates = []
    if os.name == 'nt':
        import winreg
        for hive, key, field in [
            (winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam', 'SteamPath'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Valve\Steam', 'InstallPath'),
        ]:
            try:
                with winreg.OpenKey(hive, key) as handle:
                    candidates.append(Path(winreg.QueryValueEx(handle, field)[0]))
            except OSError:
                pass
        candidates.extend([Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Steam',
                           Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Steam'])
    elif 'microsoft' in platform.release().lower():
        try:
            result = subprocess.run(['reg.exe', 'query', r'HKCU\Software\Valve\Steam', '/v', 'SteamPath'],
                                    capture_output=True, text=True, timeout=10, check=False)
            match = re.search(r'SteamPath\s+REG_SZ\s+(.+)', result.stdout)
            if match:
                candidates.append(local_path(match[1].strip()))
        except (OSError, subprocess.TimeoutExpired):
            pass
        candidates.extend([Path('/mnt/c/Program Files (x86)/Steam'), Path('/mnt/c/Program Files/Steam')])
    home = Path.home()
    candidates.extend([home / '.steam/steam', home / '.local/share/Steam',
                       home / '.var/app/com.valvesoftware.Steam/.local/share/Steam',
                       home / 'Library/Application Support/Steam'])
    return list(dict.fromkeys(path.resolve() for path in candidates if (path / 'steamapps').is_dir()))


def libraries(roots: list[Path]) -> tuple[list[Path], list[str]]:
    result, errors = [], []
    for root in roots:
        result.append(root.resolve())
        path = root / 'steamapps/libraryfolders.vdf'
        if not path.exists():
            continue
        try:
            content = get_ci(parse_vdf(path.read_text(encoding='utf-8-sig')), 'libraryfolders', {})
            if not isinstance(content, dict):
                raise ValueError('libraryfolders must be an object')
            for key, row in content.items():
                if not key.isdigit():
                    continue
                value = get_ci(row, 'path') if isinstance(row, dict) else row
                if value:
                    result.append(local_path(value).resolve())
        except (OSError, ValueError) as error:
            errors.append(f'{path}: {error}')
    return list(dict.fromkeys(result)), errors


def find_games(roots: list[Path], app_ids=('311690', '250900')) -> tuple[dict, list[str]]:
    libs, errors = libraries(roots)
    found = {appid: [] for appid in app_ids}
    for library in libs:
        for appid in app_ids:
            manifest = library / 'steamapps' / f'appmanifest_{appid}.acf'
            if not manifest.exists():
                continue
            try:
                state = get_ci(parse_vdf(manifest.read_text(encoding='utf-8-sig')), 'AppState', {})
                if not isinstance(state, dict) or get_ci(state, 'appid') != appid:
                    raise ValueError('Manifest app ID does not match filename')
                name = get_ci(state, 'installdir')
                if not isinstance(name, str) or not name or name in ('.', '..') or '/' in name or '\\' in name:
                    raise ValueError('Invalid installdir')
                common = (library / 'steamapps/common').resolve()
                install = (common / name).resolve()
                if not install.is_relative_to(common):
                    raise ValueError('Install symlink leaves the Steam common folder')
                if install.is_dir():
                    found[appid].append({'path': str(install), 'manifest': str(manifest),
                                         'build_id': get_ci(state, 'buildid', 'unknown')})
                else:
                    errors.append(f'{manifest}: advertised install folder is missing')
            except (OSError, ValueError) as error:
                errors.append(f'{manifest}: {error}')
    return found, errors
