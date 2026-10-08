"""Find local Steam installs and inspect only the selected resource indexes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools.isaac_index import archives_at, name_hash, read_index
from tools.steam import default_roots, find_games

ROOT = Path(__file__).resolve().parents[1]


def probe(steam_roots=None, gungeon=None, isaac=None):
    found, errors = find_games(default_roots() if steam_roots is None else steam_roots)
    report = {'status': 'missing_game_access', 'games': found, 'errors': errors,
              'managed': [], 'archives': [], 'resource_candidates': {}, 'gameplay_tested': False}
    for appid, override in [('311690', gungeon), ('250900', isaac)]:
        if override is not None:
            if override.is_dir():
                report['games'][appid] = [{'path': str(override.resolve()), 'manifest': 'explicit agent path',
                                          'build_id': 'unknown'}]
            else:
                report['errors'].append(f'Explicit game folder does not exist: {override}')
    for match in report['games']['311690']:
        root = Path(match['path'])
        for folder in root.glob('*_Data/Managed'):
            if (folder / 'Assembly-CSharp.dll').is_file():
                report['managed'].append({'path': str(folder),
                    'assembly_sha256': hashlib.sha256((folder / 'Assembly-CSharp.dll').read_bytes()).hexdigest(),
                    'unity_assemblies': [file.name for file in sorted(folder.glob('UnityEngine*.dll'))]})
    sheets = json.loads((ROOT / 'sheets/assets.json').read_text())
    wanted = {row['values']['id']: row['values']['resourcePath'] for row in sheets['rows']
              if row['values'].get('resourcePath')}
    for match in report['games']['250900']:
        install = Path(match['path'])
        for resource_id, relative in wanted.items():
            if (install / relative).is_file():
                report['resource_candidates'].setdefault(resource_id, []).append({'kind': 'loose', 'path': relative})
        for archive in archives_at(install):
            try:
                mode, entries = read_index(archive)
                report['archives'].append({'path': str(archive), 'mode': mode, 'entry_count': len(entries)})
                for resource_id, relative in wanted.items():
                    if name_hash(relative) in entries:
                        report['resource_candidates'].setdefault(resource_id, []).append(
                            {'kind': 'packed', 'archive': str(archive), 'resource_path': relative})
            except (OSError, ValueError) as error:
                report['errors'].append(f'{archive}: {error}')
    if report['managed'] and report['games']['250900']:
        report['status'] = 'install_candidates_found_not_gameplay_verified'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steam-root', action='append', type=Path)
    parser.add_argument('--gungeon', type=Path)
    parser.add_argument('--isaac', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = probe(args.steam_root, args.gungeon, args.isaac)
    output = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + '\n')
    print(output)
    return 0 if report['status'].startswith('install_candidates_found') and not report['errors'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
