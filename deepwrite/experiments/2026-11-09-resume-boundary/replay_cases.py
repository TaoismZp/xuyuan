#!/usr/bin/env python3
"""Public synthetic F1/F2 resume-boundary cases; no private source or quality claim.

Prints one receipt. All projects/checkpoints are temporary; requirements are
frozen separately before snapshot. Byte recovery and resume checks stay separate.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'deepwrite' / 'qa'))
from checkpoint import snapshot, restore
from resume_check import check

BASE = '6c6d67c91c9b84d1beb1f59754cfbac4733d8d93'
CANDIDATE = '6aca4e26c309dce6da85be592ab34f57bfe83a1b'
OTHER_COMMIT = '11adac438ba0d31271a0481a4978c54e28c733a3'
PROJECT = 'PUBLIC_RESUME_BOUNDARY'
PASS = 'PASS_DECLARED_RESUME_CHECKS_ONLY'
FILES = ['book.md', 'pins.json', 'config.json', 'SOURCE_LEDGER.json', 'STATE.json']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def put_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    path.write_bytes(data)
    return digest(data)


def protocols():
    result = {}
    for name, version, spec in [('deepwrite', 'v0.1', 'deepwrite/versions/v0.1.md'),
                                 ('wish_delivery', 'v7.6', 'wish-delivery/versions/v7.6.md')]:
        blob = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', BASE + ':' + spec], text=True).strip()
        result[name] = {'version': version, 'commit': BASE, 'spec_sha': blob}
    return result


def requirement(protocol_pins, channel, candidates):
    return {'project_id': PROJECT, 'required_files': FILES, 'protocols': protocol_pins,
            'channel': channel, 'module_policy': {'discovery_gate': 'CANDIDATE', 'spellcheck': 'STABLE'},
            'enabled_candidate_commits': candidates}


def one_case(temp, label, req_path, req_sha, protocol_pins, *, omit=False, channel='STABLE',
             enabled=False, candidate_commit=None, config_commit=None, expected=PASS):
    source = temp / (label + '-source')
    source.mkdir()
    pins = {'project_id': PROJECT, 'protocols': protocol_pins, 'channel': channel,
            'modules': [] if candidate_commit is None else [{'id': 'discovery_gate', 'commit': candidate_commit}]}
    config = {'channel': channel, 'modules': {'discovery_gate': enabled, 'spellcheck': True},
              'module_commits': {} if config_commit is None else {'discovery_gate': config_commit}}
    put_json(source / 'pins.json', pins)
    put_json(source / 'config.json', config)
    (source / 'book.md').write_text('# Public synthetic note\nRead the frozen evidence before continuing.\n', encoding='utf8')
    put_json(source / 'SOURCE_LEDGER.json', {'source': 'PUBLIC_SYNTHETIC_ONLY', 'claim': 'fixture, not outside research'})
    put_json(source / 'STATE.json', {'next_executable_action': 'READ_FROZEN_SOURCE', 'project_id': PROJECT})
    source_hashes = {name: digest((source / name).read_bytes()) for name in FILES}
    extra = [] if omit else ['SOURCE_LEDGER.json', 'STATE.json']
    checkpoint = temp / (label + '-checkpoint')
    saved = snapshot(source, checkpoint, PROJECT, 'book.md', 'pins.json', 'config.json', extra)
    restored = temp / (label + '-restored')
    shutil.rmtree(source)  # Only this script's own synthetic files.
    recovery = restore(checkpoint, restored, saved['manifest_sha256'])
    assert saved['status'] == recovery['status'] == 'PASS_BYTES_ONLY'
    assert saved['project_resume_gate'] == recovery['project_resume_gate'] == 'NOT_RUN'
    assert recovery['complete_project_recovery'] == 'UNVERIFIED'
    included = ['book.md', 'pins.json', 'config.json', *extra]
    assert all(digest((restored / name).read_bytes()) == source_hashes[name] for name in included)
    missing = [name for name in FILES if not (restored / name).exists()]
    before = {str(p.relative_to(checkpoint)): digest(p.read_bytes()) for p in checkpoint.rglob('*') if p.is_file()}
    result = check(checkpoint, saved['manifest_sha256'], req_path, req_sha)
    after = {str(p.relative_to(checkpoint)): digest(p.read_bytes()) for p in checkpoint.rglob('*') if p.is_file()}
    assert before == after  # Resume check is read-only; it never repairs the candidate.
    assert result['status'] == expected, (label, result)
    assert digest(req_path.read_bytes()) == req_sha  # Cases never adjust their own standard.
    return {'case': label, 'frozen_requirements_sha256': req_sha,
            'checkpoint_manifest_sha256': saved['manifest_sha256'],
            'byte_snapshot': saved['status'], 'byte_restore': recovery['status'],
            'byte_operation_project_resume_gate': recovery['project_resume_gate'],
            'all_included_files_byte_equal': True, 'source_deleted_before_restore': True,
            'resume_check_did_not_modify_checkpoint': True,
            'missing_required_files_after_restore': missing,
            'input': {'pins_channel': channel, 'pins_modules': pins['modules'],
                      'config_modules': config['modules'], 'config_module_commits': config['module_commits']},
            'source_sha256': source_hashes, 'expected_resume_status': expected,
            'actual_resume_check': result}


def main():
    protocol_pins = protocols()
    stable = requirement(protocol_pins, 'STABLE', {})
    opt_in = requirement(protocol_pins, 'CANDIDATE_OPT_IN', {'discovery_gate': CANDIDATE})
    with tempfile.TemporaryDirectory(prefix='deepwrite-public-resume-cases-') as directory:
        temp = Path(directory)
        # Both documents are frozen BEFORE any case starts; never infer them from
        # an incomplete checkpoint or silently adjust them to pass a failing case.
        stable_path = temp / 'stable-required-files.json'
        stable_sha = put_json(stable_path, stable)
        opt_path = temp / 'opt-in-required-files.json'
        opt_sha = put_json(opt_path, opt_in)
        cases = [
            one_case(temp, 'F1_omitted_required_source_and_state', stable_path, stable_sha,
                     protocol_pins, omit=True, expected='BLOCKED'),
            one_case(temp, 'F2_stable_with_candidate_enabled', stable_path, stable_sha,
                     protocol_pins, enabled=True, expected='BLOCKED'),
            one_case(temp, 'normal_stable_control', stable_path, stable_sha, protocol_pins),
            one_case(temp, 'normal_opt_in_control', opt_path, opt_sha, protocol_pins,
                     channel='CANDIDATE_OPT_IN', enabled=True, candidate_commit=CANDIDATE, config_commit=CANDIDATE),
            one_case(temp, 'candidate_commit_conflict', opt_path, opt_sha, protocol_pins,
                     channel='CANDIDATE_OPT_IN', enabled=True, candidate_commit=CANDIDATE,
                     config_commit=OTHER_COMMIT, expected='BLOCKED')]
        assert len({row['frozen_requirements_sha256'] for row in cases[:3]}) == 1
        receipt = {'schema': 'deepwrite/resume-boundary-cases/v0.1', 'base_commit': BASE,
                   'data': 'PUBLIC_SYNTHETIC_ONLY', 'requirements_frozen_before_snapshots': True,
                   'first_three_share_identical_requirements': True,
                   'frozen_requirements': {'stable': stable, 'opt_in': opt_in}, 'cases': cases,
                   'resume_checker_source_sha256': digest((REPO / 'deepwrite/qa/resume_check.py').read_bytes()),
                   'limits': ['Checks only the externally declared inventory and identities; not their truth or completeness.',
                              'Byte restoration is not project trust, author authorization, transaction consistency or durable storage.',
                              'Module choices and approvals here are synthetic fixtures, not real project authorizations.'],
                   'quality_improvement': 'UNVERIFIED', 'independent_human_blind': 'NOT_RUN',
                   'E1': 'NOT_IMPLEMENTED', 'E2': 'NOT_RUN'}
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
