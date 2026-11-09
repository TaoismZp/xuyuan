#!/usr/bin/env python3
"""Verified Markdown assembler; no generation or editorial acceptance.

All source bytes are checked before any output is written. Output and report
must be distinct derivatives, never aliases of a source or the input manifest.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_source(path, expected, expected_bytes=None):
    raw = Path(path).read_bytes()
    actual = sha(raw)
    if actual != expected:
        raise SystemExit(f'FAIL SHA256 mismatch for {path}: expected {expected}; got {actual}')
    if expected_bytes is not None and (
        type(expected_bytes) is not int or expected_bytes != len(raw)
    ):
        raise SystemExit(f'FAIL byte count mismatch for {path}: expected {expected_bytes}; got {len(raw)}')
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise SystemExit(f'FAIL source is not UTF-8: {path}') from error


def clean_first_h1(text):
    lines = text.splitlines(keepends=True)
    if lines and lines[0].startswith('# '):
        return ''.join(lines[1:]).lstrip('\n')
    return text


def source_path(root, entry):
    name = entry['relative_path']
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise SystemExit('FAIL source relative_path must be a nonempty relative path')
    path = (root / name).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise SystemExit(f'FAIL source escapes project root: {name}') from error
    if not path.is_file():
        raise SystemExit(f'FAIL source is not a regular file: {name}')
    return path


def same_file(first, second):
    return first == second or (
        first.exists() and second.exists() and first.samefile(second)
    )


def check_destinations(output, report, protected):
    if same_file(output, report) or output in report.parents or report in output.parents:
        raise SystemExit('FAIL output and report must be distinct file paths')
    for destination in (output, report):
        if destination.exists() and not destination.is_file():
            raise SystemExit(f'FAIL destination is not a regular file: {destination}')
        for source in protected:
            if same_file(destination, source):
                raise SystemExit(f'FAIL destination would overwrite input: {destination}')
        for parent in destination.parents:
            if parent.exists() and not parent.is_dir():
                raise SystemExit(f'FAIL destination parent is not a directory: {parent}')


def write_derivatives(output, packed, report, result):
    """Stage both files before replacing either; each replacement is atomic.

    A filesystem cannot atomically commit two paths. Consumers must verify the
    book hash in the report after interruption; the report is replaced last.
    """
    staged = []
    try:
        for destination, data in (
            (output, packed),
            (report, (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')),
        ):
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
                staged.append((Path(handle.name), destination))
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def assemble(m, root, output, report, manifest_path=None):
    root, output, report = Path(root).resolve(), Path(output).resolve(), Path(report).resolve()
    manifest_identity = None
    if manifest_path is not None:
        manifest_path = Path(manifest_path).resolve()
        manifest_raw = manifest_path.read_bytes()
        if json.loads(manifest_raw) != m:
            raise SystemExit('FAIL manifest changed after parsing')
        manifest_identity = {'path': str(manifest_path), 'sha256': sha(manifest_raw)}
    chapters = m['chapters']
    expected = m['expected_chapters']
    if type(expected) is not int or expected < 1 or len(chapters) != expected:
        raise SystemExit('FAIL chapter count must match positive expected_chapters')
    if any(type(x['number']) is not int for x in chapters) or [
        x['number'] for x in chapters
    ] != list(range(1, len(chapters) + 1)):
        raise SystemExit('FAIL chapter order must be consecutive starting at 1')
    entries = [m['front'], *chapters, m['tail']]
    paths = [source_path(root, entry) for entry in entries]
    protected = paths + ([Path(manifest_path).resolve()] if manifest_path is not None else [])
    check_destinations(output, report, protected)
    texts = [load_source(path, entry['sha256'], entry.get('bytes'))
             for entry, path in zip(entries, paths)]
    identities = [
        {'relative_path': entry['relative_path'], 'sha256': sha(text.encode('utf-8')),
         'bytes': len(text.encode('utf-8'))}
        for entry, text in zip(entries, texts)
    ]
    front, tail = texts[0], texts[-1]
    section_data = [(entry, clean_first_h1(text)) for entry, text in zip(chapters, texts[1:-1])]
    title = m.get('working_title', 'Book candidate')
    parts = m.get('parts', {})
    content = [f'# {title}\n\n',
               '> 候选汇编（未获独立编辑/作者终校签收）。编排派生稿，不修改原稿。\n\n',
               '## 目录\n\n', '- 序言\n']
    for entry, _ in section_data:
        content.append(f"- 第{entry['number']:02d}章｜{entry['title']}\n")
    content += ['- 尾声\n\n', '---\n\n', front.strip(), '\n\n---\n\n']
    for entry, body in section_data:
        if str(entry['number']) in parts:
            content.append(f"\n# {parts[str(entry['number'])]}\n\n")
        content.append(f"\n## 第{entry['number']:02d}章｜{entry['title']}\n\n")
        content.extend([body.strip(), '\n\n---\n\n'])
    content += [tail.strip(), '\n']
    packed = ''.join(content).encode('utf-8')
    result = {
        'schema': 'verified-markdown-book/v0.1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'title': title,
        'chapters': len(chapters),
        'sha256': sha(packed),
        'bytes': len(packed),
        'chapter_source_digests': [
            {'number': entry['number'], **identity}
            for entry, identity in zip(chapters, identities[1:-1])
        ],
        'front_sha256': identities[0]['sha256'],
        'tail_sha256': identities[-1]['sha256'],
        'front_source': identities[0],
        'tail_source': identities[-1],
        'gates': {'source_files': 'PASS_EXACT_DIGEST', 'book_draft': 'CANDIDATE',
                  'human_edit': 'PENDING', 'appendices': 'PENDING'},
        'note': 'Source chapter bodies copied into a new derivative; original files untouched',
    }
    if manifest_identity is not None:
        result['manifest_source'] = manifest_identity
    write_derivatives(output, packed, report, result)
    print(json.dumps({'status': 'PASS_SOURCES', 'book_path': str(output),
                      'sha256': result['sha256'], 'bytes': result['bytes'],
                      'chapters': len(chapters)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        assemble(manifest, Path(args.root), Path(args.output), Path(args.report), manifest_path)
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise SystemExit(f'FAIL {error}') from error


if __name__ == '__main__':
    main()
