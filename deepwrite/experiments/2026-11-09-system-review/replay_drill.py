#!/usr/bin/env python3
"""Public synthetic byte rollback drill. No private manuscript or quality claim."""
import hashlib
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
from urllib.request import urlopen
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'deepwrite/qa'))
from checkpoint import snapshot, verify, restore, digest
from release_guard import evaluate

BASE = 'd64b9e0a69deed62101dfe55d9798b84a32d9def'


def git_object(spec):
    return subprocess.check_output(['git', '-C', str(REPO), 'show', BASE + ':' + spec])


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def http_bytes(directory):
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *_): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(directory)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen('http://127.0.0.1:' + str(server.server_port) + '/', timeout=5) as response:
            return response.read()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def expect_blocked(call):
    try:
        call()
    except (OSError, ValueError) as exc:
        return str(exc)
    raise AssertionError('expected BLOCKED')


def run_case(temp, kind):
    project_id = 'PUBLIC_SYNTHETIC_' + kind.upper()
    root = temp / kind
    root.mkdir()
    artifact = 'draft.md' if kind == 'writing' else 'index.html'
    initial = ('# 合成说明\n先查看到期日，再比较总价；总价相同，付款时点不同仍会影响现金缺口。\n'
               if kind == 'writing' else
               '<!doctype html><html lang="zh"><meta charset="utf-8"><title>公共演练</title><h1>预约</h1><button>查看空位</button></html>\n').encode()
    changed = ('# 合成说明\n只要更努力，所有问题都会解决。\n' if kind == 'writing' else
               '<!doctype html><html><title>试验分支</title><h1>预约</h1></html>\n').encode()
    (root / artifact).write_bytes(initial)
    protocols = {}
    specs = []
    for key, version, spec in [('deepwrite', 'v0.1', 'deepwrite/versions/v0.1.md'),
                               ('wish_delivery', 'v7.6', 'wish-delivery/versions/v7.6.md')]:
        data = git_object(spec)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        protocols[key] = {'version': version, 'commit': BASE, 'spec_sha': blob}
        local = key + '-spec.md'
        (root / local).write_bytes(data)
        specs.append(local)
    write_json(root / 'pins.json', {'project_id': project_id, 'protocols': protocols, 'channel': 'STABLE'})
    write_json(root / 'config.json', {'modules': {'discovery_gate': False}, 'channel': 'STABLE'})
    write_json(root / 'STATE.json', {'project_id': project_id, 'next_executable_action': 'READ_FROZEN_SOURCE_BEFORE_CONTINUING'})
    names = [artifact, 'pins.json', 'config.json', 'STATE.json', *specs]
    expected = {name: (root / name).read_bytes() for name in names}
    before_http = http_bytes(root) if kind == 'website' else None
    checkpoint = temp / (kind + '-checkpoint')
    snap = snapshot(root, checkpoint, project_id, artifact, 'pins.json', 'config.json', ['STATE.json', *specs])
    sha = snap['manifest_sha256']
    verification = verify(checkpoint, sha)
    # Keep a failed branch, then remove ONLY this drill's synthetic source.
    candidate = temp / (kind + '-failed-candidate')
    shutil.copytree(root, candidate)
    (candidate / artifact).write_bytes(changed)
    write_json(candidate / 'config.json', {'modules': {'discovery_gate': True}, 'channel': 'CANDIDATE_OPT_IN'})
    shutil.rmtree(root)
    destination = temp / (kind + '-restored')
    restore(checkpoint, destination, sha)
    assert all((destination / name).read_bytes() == data for name, data in expected.items())
    assert (candidate / artifact).read_bytes() == changed
    assert json.loads((destination / 'config.json').read_text())['modules']['discovery_gate'] is False
    after_http = http_bytes(destination) if kind == 'website' else None
    if kind == 'website':
        assert before_http == after_http == initial
    blocked = {}
    for name in (artifact, 'config.json'):
        p = checkpoint / 'files' / name
        data = p.read_bytes()
        p.write_bytes(data + b' TAMPER')
        out = temp / (kind + '-tampered-' + name.replace('.', '-'))
        blocked[name] = expect_blocked(lambda: restore(checkpoint, out, sha))
        assert not out.exists()
        p.write_bytes(data)
    manifest = checkpoint / 'manifest.json'
    old = manifest.read_bytes()
    manifest.write_bytes(old + b'\n')
    out = temp / (kind + '-manifest-tamper')
    blocked['manifest'] = expect_blocked(lambda: restore(checkpoint, out, sha))
    assert not out.exists()
    manifest.write_bytes(old)
    blocked['existing_destination'] = expect_blocked(lambda: restore(checkpoint, destination, sha))
    assert all((destination / name).read_bytes() == data for name, data in expected.items())
    return {'status': 'PASS_BYTES_ONLY', 'manifest_sha256': sha, 'files': len(names),
            'artifact_sha256': digest(initial), 'failed_candidate_sha256': digest(changed),
            'source_deleted_before_restore': True, 'all_files_byte_equal': True,
            'two_protocol_specs_and_pins_restored': True, 'candidate_preserved': True,
            'module_disabled_in_restored_config': True, 'tamper_and_overwrite_blocked': blocked,
            'http_response_byte_equal': before_http == after_http if kind == 'website' else None,
            'verify': verification}


def concurrent_source_counterexample(temp):
    """Known limitation, not a safety guarantee: sources must be stopped first."""
    import checkpoint as implementation
    root = temp / 'concurrent-source'
    root.mkdir()
    (root / 'book.md').write_text('generation 1')
    write_json(root / 'config.json', {'generation': 1})
    write_json(root / 'pins.json', {'project_id': 'PUBLIC_CONCURRENCY_PROBE',
        'protocols': {k: {'version': v, 'commit': BASE, 'spec_sha': 'a' * 40}
                      for k, v in [('deepwrite', 'v0.1'), ('wish_delivery', 'v7.6')]}})
    real_read = implementation.read_file
    def changing_read(source, name):
        data = real_read(source, name)
        if source == root and name == 'book.md':
            (root / 'book.md').write_text('generation 2')
            write_json(root / 'config.json', {'generation': 2})
        return data
    checkpoint = temp / 'concurrent-checkpoint'
    with patch.object(implementation, 'read_file', changing_read):
        sha = snapshot(root, checkpoint, 'PUBLIC_CONCURRENCY_PROBE',
                       'book.md', 'pins.json', 'config.json')['manifest_sha256']
    destination = temp / 'concurrent-restored'
    restore(checkpoint, destination, sha)
    book = (destination / 'book.md').read_text()
    config = json.loads((destination / 'config.json').read_text())
    assert book == 'generation 1' and config['generation'] == 2
    return {'status': 'LIMITATION_REPRODUCED_NOT_TRANSACTIONAL', 'restored_book': book,
            'restored_config': config, 'requires_stopped_source_writers': True}


def main():
    fake = {'schema': 'deepwrite/release-evidence/v0.1', 'requested_channel': 'ROLLBACK',
            'immutable_baseline': True, 'baseline': {}, 'candidate': {},
            'rollback_plan': {'verified_checkpoint_sha256': 'a' * 64, 'preserve_failed_candidate': True},
            'gates': {k: 'PENDING' for k in ('engineering', 'content_quality', 'author_acceptance', 'external_validation')}}
    for side in ('baseline', 'candidate'):
        fake[side] = {'spec_git_commit': 'c' * 40, 'artifact_sha256': 'a' * 64, 'evaluation_sha256': 'a' * 64}
    assert evaluate(fake) == []  # Still intentionally a STRUCTURAL interface.
    with tempfile.TemporaryDirectory(prefix='deepwrite-public-drill-') as td:
        temp = Path(td)
        missing = expect_blocked(lambda: verify(temp / 'nonexistent', 'a' * 64))
        result = {'schema': 'deepwrite/system-review-engineering/v0.1', 'base_commit': BASE,
                  'data': 'PUBLIC_SYNTHETIC_ONLY',
                  'structural_guard_accepts_nonexistent_hash': True,
                  'byte_verifier_rejects_nonexistent_checkpoint': missing,
                  'writing': run_case(temp, 'writing'), 'website': run_case(temp, 'website'),
                  'concurrent_source_counterexample': concurrent_source_counterexample(temp),
                  'quality_improvement': 'UNVERIFIED', 'independent_human_blind': 'NOT_RUN',
                  'E1': 'NOT_IMPLEMENTED', 'E2': 'NOT_RUN',
                  'durable_private_cross_environment_restore': 'NOT_RUN',
                  'website_public_deployment_and_interaction': 'NOT_RUN'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
