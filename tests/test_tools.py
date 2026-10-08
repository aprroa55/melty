"""Development-tool tests with synthetic data; none claim to test gameplay."""
import copy
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.isaac_index import name_hash, read_index
from tools.probe_games import probe
from tools.sheets import generate, load_sheets, preflight
from tools.steam import find_games, parse_vdf


def verified_sheet(rows=None):
    return {'schemaVersion': 1, 'columns': {'id': {'type': 'string'}, 'damage': {'type': 'float', 'minimum': 0}},
            'rows': rows or [{'values': {'id': 'beam', 'damage': 12.5},
                            'checks': {'id': {'verified': True, 'evidence': 'test fixture'},
                                       'damage': {'verified': True, 'evidence': 'test fixture'}}}]}


def write_manifest(library, appid, folder, build='123'):
    apps = library / 'steamapps'
    apps.mkdir(parents=True, exist_ok=True)
    (apps / f'appmanifest_{appid}.acf').write_text(
        f'"AppState" {{ "appid" "{appid}" "installdir" "{folder}" "buildid" "{build}" }}')
    (apps / 'common' / folder).mkdir(parents=True, exist_ok=True)
    return apps / 'common' / folder


def archive_bytes(entries):
    data = b'test-only synthetic payload'
    offset = 14 + len(data)
    header = b'ARCH000' + struct.pack('<BIH', 0, offset, len(entries))
    table = b''.join(struct.pack('<IIIII', hash_ & 0xFFFFFFFF, hash_ >> 32, 14, len(data), 0)
                     for hash_ in entries)
    return header + data + table


class SteamTests(unittest.TestCase):
    def test_windows_paths_comments_and_bare_tokens(self):
        parsed = parse_vdf('// comment\n"libraryfolders" { "0" { "path" "D:\\\\Steam Library" } 1 "E:\\\\Games" }')
        self.assertEqual(parsed['libraryfolders']['0']['path'], 'D:\\Steam Library')
        self.assertEqual(parsed['libraryfolders']['1'], 'E:\\Games')

    def test_malformed_vdf_is_rejected(self):
        for text in ['"a" {', '"a"', '}', '"a" "unterminated', '"a" "x" "a" "y"']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_vdf(text)

    def test_external_library_without_folder_name_guessing(self):
        with tempfile.TemporaryDirectory() as d:
            root, second = Path(d) / 'Steam', Path(d) / 'Unusual Library'
            (root / 'steamapps').mkdir(parents=True)
            (root / 'steamapps/libraryfolders.vdf').write_text(
                '"libraryfolders" { "0" { "path" ' + json.dumps(str(second)) + ' } }')
            installed = write_manifest(second, '250900', 'Renamed Isaac Directory')
            found, errors = find_games([root])
            self.assertFalse(errors)
            self.assertEqual(found['250900'][0]['path'], str(installed))

    def test_old_library_format(self):
        with tempfile.TemporaryDirectory() as d:
            root, second = Path(d) / 'Steam', Path(d) / 'Other'
            (root / 'steamapps').mkdir(parents=True)
            (root / 'steamapps/libraryfolders.vdf').write_text(
                '"LibraryFolders" { "1" ' + json.dumps(str(second)) + ' }')
            write_manifest(second, '311690', 'EtG')
            found, errors = find_games([root])
            self.assertFalse(errors)
            self.assertEqual(len(found['311690']), 1)

    def test_wrong_manifest_app_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            library = Path(d)
            write_manifest(library, '250900', 'Isaac')
            path = library / 'steamapps/appmanifest_250900.acf'
            path.write_text(path.read_text().replace('250900', '1'))
            found, errors = find_games([library])
            self.assertFalse(found['250900'])
            self.assertTrue(errors)

    def test_manifest_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            library = Path(d)
            write_manifest(library, '250900', 'Isaac')
            path = library / 'steamapps/appmanifest_250900.acf'
            path.write_text(path.read_text().replace('Isaac', '../Escape'))
            found, errors = find_games([library])
            self.assertFalse(found['250900'])
            self.assertTrue(errors)

    def test_multiple_installs_are_reported_not_silently_selected(self):
        with tempfile.TemporaryDirectory() as d:
            roots = [Path(d) / 'one', Path(d) / 'two']
            for root in roots:
                write_manifest(root, '250900', 'Isaac')
            found, errors = find_games(roots)
            self.assertFalse(errors)
            self.assertEqual(len(found['250900']), 2)


class ArchiveTests(unittest.TestCase):
    def test_targeted_hash_lookup_is_case_insensitive(self):
        path = 'resources/gfx/items/collectibles/collectibles_118_brimstone.png'
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d) / 'graphics.a'
            archive.write_bytes(archive_bytes([name_hash(path)]))
            mode, entries = read_index(archive)
            self.assertEqual(mode, 0)
            self.assertIn(name_hash(path.upper()), entries)
            self.assertNotIn(name_hash(path.replace('118', '999')), entries)

    def test_bad_signature_truncated_index_and_unknown_modes(self):
        valid = archive_bytes([name_hash('resources/animations.b')])
        cases = [b'bad', valid[:-1], b'INVALID' + valid[7:], valid[:7] + bytes([99]) + valid[8:]]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.a'
            for payload in cases:
                with self.subTest(payload=payload[:14]):
                    path.write_bytes(payload)
                    with self.assertRaises(ValueError):
                        read_index(path)

    def test_duplicate_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'duplicate.a'
            path.write_bytes(archive_bytes([123, 123]))
            with self.assertRaises(ValueError):
                read_index(path)

    def test_entry_pointing_into_table_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.a'
            data = bytearray(archive_bytes([123]))
            offset = struct.unpack_from('<I', data, 8)[0]
            struct.pack_into('<I', data, offset + 8, offset)
            path.write_bytes(data)
            with self.assertRaises(ValueError):
                read_index(path)


class SheetTests(unittest.TestCase):
    def test_clean_sheet_generates_one_definition_per_row(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'generated'
            files = generate({'weapons': verified_sheet()}, output)
            self.assertEqual(files, ['WeaponsBeam.cs'])
            self.assertIn('public const double Damage = 12.5;', (output / files[0]).read_text())

    def test_missing_or_unverified_cells_prevent_any_output(self):
        for value, check in [(None, True), (12.5, False)]:
            sheet = verified_sheet()
            sheet['rows'][0]['values']['damage'] = value
            sheet['rows'][0]['checks']['damage']['verified'] = check
            with tempfile.TemporaryDirectory() as d:
                output = Path(d) / 'generated'
                with self.assertRaises(ValueError):
                    generate({'weapons': sheet}, output)
                self.assertFalse(output.exists())

    def test_references_must_resolve_in_target_sheet(self):
        sheet = verified_sheet()
        sheet['columns']['id']['ref'] = 'missing'
        report = preflight({'weapons': sheet})
        self.assertIn('unresolved_reference', [issue['kind'] for issue in report['issues']])

    def test_nan_wrong_types_duplicate_ids_and_empty_sheets_block(self):
        for value in [True, '12', float('nan'), -1]:
            sheet = verified_sheet()
            sheet['rows'][0]['values']['damage'] = value
            self.assertFalse(preflight({'weapons': sheet})['ready'])
        sheet = verified_sheet()
        sheet['rows'].append(copy.deepcopy(sheet['rows'][0]))
        self.assertFalse(preflight({'weapons': sheet})['ready'])
        self.assertFalse(preflight({})['ready'])

    def test_generated_name_collision_is_rejected(self):
        sheet = verified_sheet()
        sheet['rows'][0]['values']['id'] = 'a1'
        other = copy.deepcopy(sheet['rows'][0])
        other['values']['id'] = 'a_1'
        sheet['rows'].append(other)
        self.assertFalse(preflight({'weapons': sheet})['ready'])

    def test_refresh_removes_only_previously_generated_rows(self):
        sheet = verified_sheet()
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            generate({'weapons': sheet}, directory)
            (directory / 'Notes.txt').write_text('user file')
            sheet['rows'][0]['values']['id'] = 'other_beam'
            generate({'weapons': sheet}, directory)
            self.assertFalse((directory / 'WeaponsBeam.cs').exists())
            self.assertTrue((directory / 'WeaponsOtherBeam.cs').exists())
            self.assertEqual((directory / 'Notes.txt').read_text(), 'user file')

    def test_generator_preserves_preexisting_unowned_file(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            file = directory / 'WeaponsBeam.cs'
            file.write_text('user source')
            with self.assertRaises(ValueError):
                generate({'weapons': verified_sheet()}, directory)
            self.assertEqual(file.read_text(), 'user source')

    def test_real_project_has_no_structural_or_reference_errors(self):
        report = preflight(load_sheets())
        kinds = {issue['kind'] for issue in report['issues']}
        self.assertLessEqual(kinds, {'unfilled', 'unverified'})
        self.assertGreater(report['cells'], 0)


class ProbeTests(unittest.TestCase):
    def test_missing_games_stay_missing_without_fake_fallback(self):
        report = probe(steam_roots=[])
        self.assertEqual(report['status'], 'missing_game_access')
        self.assertFalse(report['gameplay_tested'])
        self.assertFalse(report['managed'])

    def test_synthetic_installs_detect_resources_without_claiming_gameplay(self):
        with tempfile.TemporaryDirectory() as d:
            library = Path(d)
            gungeon = write_manifest(library, '311690', 'Gungeon')
            isaac = write_manifest(library, '250900', 'Isaac')
            managed = gungeon / 'EtG_Data/Managed'
            managed.mkdir(parents=True)
            (managed / 'Assembly-CSharp.dll').write_bytes(b'not a real assembly; test fixture')
            resource = 'resources/gfx/items/collectibles/collectibles_118_brimstone.png'
            (isaac / 'resources').mkdir()
            (isaac / 'resources/graphics.a').write_bytes(archive_bytes([name_hash(resource)]))
            report = probe(steam_roots=[library])
            self.assertEqual(report['status'], 'install_candidates_found_not_gameplay_verified')
            self.assertIn('brimstone_icon', report['resource_candidates'])
            self.assertFalse(report['gameplay_tested'])


if __name__ == '__main__':
    unittest.main()
