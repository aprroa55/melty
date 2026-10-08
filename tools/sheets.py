"""Validate every sheet cell and reference before generating any C# records."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_sheets(directory=ROOT / 'sheets'):
    return {path.stem: json.loads(path.read_text()) for path in sorted(directory.glob('*.json'))}


def preflight(sheets):
    issues, ids = [], {}
    generated_names = set()
    checked, total = 0, 0
    if not sheets:
        issues.append({'cell': 'sheets', 'kind': 'missing', 'detail': 'No sheets found'})
    for name, sheet in sheets.items():
        ids[name] = set()
        if not re.fullmatch('[a-z][a-z0-9_]*', name):
            issues.append({'cell': name, 'kind': 'schema', 'detail': 'Invalid sheet name'})
        if sheet.get('schemaVersion') != 1 or not isinstance(sheet.get('columns'), dict) or not sheet['columns']:
            issues.append({'cell': name, 'kind': 'schema', 'detail': 'Invalid sheet schema or empty columns'})
            continue
        if not isinstance(sheet.get('rows'), list) or not sheet['rows']:
            issues.append({'cell': name, 'kind': 'missing', 'detail': 'No rows found'})
            continue
        for index, row in enumerate(sheet['rows']):
            values = row.get('values', {})
            row_id = values.get('id')
            if not isinstance(row_id, str) or not re.fullmatch('[a-z][a-z0-9_]*', row_id):
                issues.append({'cell': f'{name}[{index}].id', 'kind': 'schema', 'detail': 'Invalid row ID'})
            elif row_id in ids[name]:
                issues.append({'cell': f'{name}.{row_id}', 'kind': 'duplicate', 'detail': 'Duplicate row ID'})
            else:
                ids[name].add(row_id)
                generated_name = pascal(name) + pascal(row_id)
                if generated_name in generated_names:
                    issues.append({'cell': f'{name}.{row_id}', 'kind': 'duplicate', 'detail': 'Generated C# name collision'})
                generated_names.add(generated_name)
    for name, sheet in sheets.items():
        columns = sheet.get('columns', {})
        for index, row in enumerate(sheet.get('rows', [])):
            values = row.get('values', {})
            checks = row.get('checks', {})
            row_name = values.get('id', str(index))
            for extra in sorted(set(values) - set(columns)):
                issues.append({'cell': f'{name}.{row_name}.{extra}', 'kind': 'schema', 'detail': 'Undeclared column'})
            for extra in sorted(set(checks) - set(columns)):
                issues.append({'cell': f'{name}.{row_name}.{extra}', 'kind': 'schema', 'detail': 'Undeclared checkbox'})
            for column, spec in columns.items():
                total += 1
                cell = f'{name}.{row_name}.{column}'
                if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_]*', column):
                    issues.append({'cell': cell, 'kind': 'schema', 'detail': 'Invalid column name'})
                value = values.get(column)
                if value is None or value == '':
                    issues.append({'cell': cell, 'kind': 'unfilled', 'detail': 'Value is missing'})
                    continue
                kind = spec.get('type')
                valid = ((kind == 'string' and isinstance(value, str)) or
                         (kind == 'int' and type(value) is int) or
                         (kind == 'float' and type(value) in (int, float) and math.isfinite(value)) or
                         (kind == 'bool' and type(value) is bool))
                if not valid:
                    issues.append({'cell': cell, 'kind': 'type', 'detail': f'Expected {kind}'})
                    continue
                if kind == 'int' and not (-2147483648 <= value <= 2147483647):
                    issues.append({'cell': cell, 'kind': 'range', 'detail': 'Outside C# int range'})
                if kind in ('int', 'float') and ('minimum' in spec and value < spec['minimum']):
                    issues.append({'cell': cell, 'kind': 'range', 'detail': 'Below minimum'})
                if 'choices' in spec and value not in spec['choices']:
                    issues.append({'cell': cell, 'kind': 'choice', 'detail': 'Not an allowed value'})
                if 'ref' in spec and value not in ids.get(spec['ref'], set()):
                    issues.append({'cell': cell, 'kind': 'unresolved_reference', 'detail': f'{spec["ref"]}.{value}'})
                evidence = checks.get(column, {})
                if evidence.get('verified') is not True or not isinstance(evidence.get('evidence'), str) or not evidence['evidence'].strip():
                    issues.append({'cell': cell, 'kind': 'unverified',
                                   'detail': evidence.get('evidence', 'No verification recorded')})
                else:
                    checked += 1
    return {'ready': not issues, 'cells': total, 'verified_cells': checked, 'issues': issues}


def pascal(name):
    return ''.join(part[:1].upper() + part[1:] for part in name.split('_'))


def generate(sheets, directory):
    report = preflight(sheets)
    if not report['ready']:
        raise ValueError('Preflight blocked: no C# files generated')
    files = {}
    types = {'string': 'string', 'int': 'int', 'float': 'double', 'bool': 'bool'}
    for sheet_name, sheet in sorted(sheets.items()):
        for row in sheet['rows']:
            values = row['values']
            name = pascal(sheet_name) + pascal(values['id'])
            lines = ['// Generated from JSON sheets. Change the sheets, not this file.',
                     'namespace IsaacGungeon.Definitions', '{', f'    internal static class {name}', '    {']
            for column, spec in sheet['columns'].items():
                if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_]*', column):
                    raise ValueError('Column is not a C# identifier')
                value = values[column]
                literal = json.dumps(value, ensure_ascii=True)
                if spec['type'] == 'float' and type(value) is int:
                    literal += '.0'
                lines.append(f'        public const {types[spec["type"]]} {pascal(column)} = {literal};')
            files[name + '.cs'] = '\n'.join(lines + ['    }', '}', ''])
    # Validate all names and values before touching the output directory.
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / '.generated-index.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    for name in previous:
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*\.cs', name):
            raise ValueError('Invalid generated file manifest')
    for name in files:
        if (directory / name).exists() and name not in previous:
            raise ValueError('Refusing to overwrite a file not owned by the generator: ' + name)
    for name, text in files.items():
        (directory / name).write_text(text)
    for name in set(previous) - set(files):
        (directory / name).unlink(missing_ok=True)
    manifest.write_text(json.dumps(sorted(files)) + '\n')
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheets', type=Path, default=ROOT / 'sheets')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--generate', type=Path)
    args = parser.parse_args()
    sheets = load_sheets(args.sheets)
    report = preflight(sheets)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Checked {report["cells"]} cells: {report["verified_cells"]} verified; {len(report["issues"])} issues')
    for issue in report['issues']:
        print(f'{issue["kind"]}: {issue["cell"]} — {issue["detail"]}')
    if not report['ready']:
        print('BUILD BLOCKED. Resolve every cell and reference before generating or building the mod.')
        return 2
    if args.generate:
        print(f'Generated {len(generate(sheets, args.generate))} row definitions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
