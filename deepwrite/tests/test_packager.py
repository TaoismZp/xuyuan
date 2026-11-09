#!/usr/bin/env python3
"""Offline CLI regressions for source identity and non-destructive assembly."""
import hashlib
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

PACKAGER = Path(__file__).resolve().parents[1] / 'tools' / 'book_packager_v0.1.py'


def load_packager():
    spec = importlib.util.spec_from_file_location('book_packager', PACKAGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


class PackagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = {
            'front.md': '# 序言\n\n测试序言。\n',
            'chapters/01.md': '# 第一章\n\n第一章正文。\n',
            'chapters/02.md': '# 第二章\n\n第二章正文。\n',
            'tail.md': '# 尾声\n\n测试尾声。\n',
        }
        for name, content in self.sources.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode('utf-8'))

        def source(name):
            raw = self.sources[name].encode('utf-8')
            return {'relative_path': name, 'sha256': digest(raw), 'bytes': len(raw)}

        self.manifest = {
            'working_title': 'Synthetic book', 'expected_chapters': 2,
            'chapters': [
                {'number': 1, 'title': 'One', **source('chapters/01.md')},
                {'number': 2, 'title': 'Two', **source('chapters/02.md')},
            ],
            'front': source('front.md'), 'tail': source('tail.md'),
        }
        self.file = self.root / 'manifest.json'
        self.output = self.root / 'book.md'
        self.report = self.root / 'report.json'

    def run_packager(self, output=None, report=None, optimized=False):
        self.file.write_text(json.dumps(self.manifest, ensure_ascii=False), encoding='utf-8')
        command = [sys.executable]
        if optimized:
            command.append('-O')
        command += [str(PACKAGER), '--manifest', str(self.file), '--root', str(self.root),
                    '--output', str(output or self.output), '--report', str(report or self.report)]
        return subprocess.run(command, capture_output=True, text=True)

    def assert_rejected(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stdout + result.stderr)

    def assert_sources_unchanged(self):
        for name, content in self.sources.items():
            self.assertEqual((self.root / name).read_bytes(), content.encode('utf-8'))

    def test_assembly_order_complete_identity_and_read_only_sources(self):
        # CRLF and non-ASCII source bytes must be bound exactly, not normalized.
        self.sources['front.md'] = '# 序言\r\n\r\n测试序言。\r\n'
        raw = self.sources['front.md'].encode('utf-8')
        (self.root / 'front.md').write_bytes(raw)
        self.manifest['front'].update(sha256=digest(raw), bytes=len(raw))
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        book = self.output.read_text(encoding='utf-8')
        self.assertLess(book.index('测试序言'), book.index('第一章正文'))
        self.assertLess(book.index('第一章正文'), book.index('第二章正文'))
        self.assertLess(book.index('第二章正文'), book.index('测试尾声'))
        report = json.loads(self.report.read_text(encoding='utf-8'))
        self.assertEqual(report['sha256'], digest(self.output.read_bytes()))
        self.assertEqual(report['bytes'], self.output.stat().st_size)
        self.assertEqual(report['front_source'], self.manifest['front'])
        self.assertEqual(report['tail_source'], self.manifest['tail'])
        self.assertEqual(report['manifest_source']['sha256'], digest(self.file.read_bytes()))
        self.assertEqual(report['gates']['human_edit'], 'PENDING')
        self.assert_sources_unchanged()

    def test_tamper_rejected_without_replacing_previous_derivatives(self):
        self.assertEqual(self.run_packager().returncode, 0)
        previous = (self.output.read_bytes(), self.report.read_bytes())
        (self.root / 'chapters/02.md').write_text('tampered', encoding='utf-8')
        self.assert_rejected(self.run_packager(), 'SHA256 mismatch')
        self.assertEqual((self.output.read_bytes(), self.report.read_bytes()), previous)

    def test_order_still_enforced_under_python_optimization(self):
        self.manifest['chapters'].reverse()
        self.assert_rejected(self.run_packager(optimized=True), 'chapter order')
        self.assertFalse(self.output.exists())

    def test_count_still_enforced_under_python_optimization(self):
        self.manifest['expected_chapters'] = 3
        self.assert_rejected(self.run_packager(optimized=True), 'chapter count')
        self.assertFalse(self.output.exists())

    def test_declared_bytes_checked_before_writing(self):
        self.manifest['chapters'][1]['bytes'] += 1
        self.assert_rejected(self.run_packager(), 'byte count mismatch')
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())

    def test_omitted_bytes_supported_and_measured(self):
        for entry in [self.manifest['front'], *self.manifest['chapters'], self.manifest['tail']]:
            entry.pop('bytes')
        self.assertEqual(self.run_packager().returncode, 0)
        report = json.loads(self.report.read_text(encoding='utf-8'))
        self.assertEqual(report['chapter_source_digests'][0]['bytes'],
                         len(self.sources['chapters/01.md'].encode('utf-8')))

    def test_source_cannot_be_output_or_report(self):
        for key in ('output', 'report'):
            with self.subTest(key=key):
                self.assert_rejected(self.run_packager(**{key: self.root / 'chapters/01.md'}),
                                     'overwrite input')
                self.assert_sources_unchanged()
                self.assertFalse(self.output.exists())

    def test_manifest_cannot_be_output_or_report(self):
        for key in ('output', 'report'):
            with self.subTest(key=key):
                self.assert_rejected(self.run_packager(**{key: self.file}), 'overwrite input')
                self.assertEqual(json.loads(self.file.read_text(encoding='utf-8')), self.manifest)
                self.assertFalse(self.output.exists())

    def test_manifest_identity_must_describe_parsed_object(self):
        self.file.write_text(json.dumps({**self.manifest, 'working_title': 'different'}),
                             encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'manifest changed after parsing'):
            load_packager().assemble(self.manifest, self.root, self.output, self.report, self.file)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())

    def test_manifest_identity_uses_validated_snapshot(self):
        self.file.write_text(json.dumps(self.manifest), encoding='utf-8')
        expected = digest(self.file.read_bytes())
        packager = load_packager()
        original_load = packager.load_source

        def load_after_manifest_changed(*args, **kwargs):
            self.file.write_text(json.dumps({**self.manifest, 'working_title': 'changed later'}),
                                 encoding='utf-8')
            return original_load(*args, **kwargs)

        with patch.object(packager, 'load_source', side_effect=load_after_manifest_changed):
            with contextlib.redirect_stdout(io.StringIO()):
                packager.assemble(self.manifest, self.root, self.output, self.report, self.file)
        report = json.loads(self.report.read_text(encoding='utf-8'))
        self.assertEqual(report['title'], self.manifest['working_title'])
        self.assertEqual(report['manifest_source']['sha256'], expected)
        self.assertNotEqual(expected, digest(self.file.read_bytes()))

    def test_source_symlink_and_hardlink_aliases_cannot_be_destinations(self):
        symlink = self.root / 'alias.md'
        symlink.symlink_to(self.root / 'chapters/01.md')
        hardlink = self.root / 'hardlink.md'
        hardlink.hardlink_to(self.root / 'chapters/01.md')
        for alias in (symlink, hardlink):
            with self.subTest(alias=alias.name):
                self.assert_rejected(self.run_packager(output=alias), 'overwrite input')
                self.assert_sources_unchanged()

    def test_output_report_collision_rejected(self):
        self.assert_rejected(self.run_packager(report=self.output), 'distinct file paths')
        self.assertFalse(self.output.exists())
        # Also reject a file path that would have to become the other's directory.
        self.assert_rejected(self.run_packager(report=self.output / 'report.json'), 'distinct file paths')
        self.assertFalse(self.output.exists())

    def test_sources_cannot_escape_project_root(self):
        outside = self.root.parent / (self.root.name + '-outside.md')
        outside.write_text('outside', encoding='utf-8')
        self.addCleanup(outside.unlink)
        self.manifest['front'].update(relative_path='../' + outside.name,
                                      sha256=digest(outside.read_bytes()), bytes=outside.stat().st_size)
        self.assert_rejected(self.run_packager(), 'escapes project root')
        self.assertFalse(self.output.exists())
        alias = self.root / 'outside-link.md'
        alias.symlink_to(outside)
        self.manifest['front']['relative_path'] = alias.name
        self.assert_rejected(self.run_packager(), 'escapes project root')
        self.assertFalse(self.output.exists())

    def test_nested_report_directory_created(self):
        report = self.root / 'qa' / 'nested' / 'report.json'
        result = self.run_packager(report=report)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(report.read_text(encoding='utf-8'))['sha256'],
                         digest(self.output.read_bytes()))

    def test_invalid_report_parent_does_not_leave_book(self):
        parent = self.root / 'not-a-directory'
        parent.write_text('keep', encoding='utf-8')
        self.assert_rejected(self.run_packager(report=parent / 'report.json'), 'not a directory')
        self.assertFalse(self.output.exists())
        self.assertEqual(parent.read_text(encoding='utf-8'), 'keep')
        self.assert_sources_unchanged()


if __name__ == '__main__':
    unittest.main(verbosity=2)
