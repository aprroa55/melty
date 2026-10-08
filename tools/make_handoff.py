"""Package source preparation only, never game files or an installable release."""
import argparse
import hashlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT_FILES = {'.gitignore', 'README.md', 'CONTINUE_ON_PC.md', 'MODLOG.md'}
ALLOWED_FOLDERS = {'tools', 'tests', 'sheets', 'docs', 'third_party'}
ALLOWED_SUFFIXES = {'.py', '.md', '.json', '.txt'}


def package(destination):
    entries = []
    for file in sorted(ROOT.rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(ROOT)
        if relative.name not in ALLOWED_ROOT_FILES and (
            relative.parts[0] not in ALLOWED_FOLDERS or file.suffix not in ALLOWED_SUFFIXES):
            continue
        if any(part in {'.git', '.local', '__pycache__', '.tools', 'artifacts'} for part in relative.parts):
            continue
        if file.is_symlink():
            raise ValueError('Refusing a source symlink: ' + str(relative))
        content = file.read_bytes()
        if re.search(rb'llc_[A-Za-z0-9_-]{20,}', content):
            raise ValueError('Possible Melty credential found; refusing to package')
        entries.append((relative, content))
    if not entries or not any(str(path) == 'CONTINUE_ON_PC.md' for path, _ in entries):
        raise ValueError('Incomplete source handoff')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for relative, content in entries:
            info = zipfile.ZipInfo('isaac-gungeon-source/' + relative.as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    return {'entries': len(entries), 'bytes': destination.stat().st_size, 'sha256': digest}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(package(args.destination))
