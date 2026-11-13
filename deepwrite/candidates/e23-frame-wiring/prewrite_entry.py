#!/usr/bin/env python3
"""Explicitly opt-in prewrite gate for E18 runner, no implied quality PASS.

This candidate only prepares a pinned SHADOW run; no model calls by default.
When --execute is present it invokes the existing E18 writing_loop_experimental.py.
All artifacts are caller-private. This is NOT the active DeepWrite entry point.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path


def source_module(name):
    """Execute the source bytes whose identity is recorded, not a stale pyc."""
    path = Path(__file__).resolve().parent / (name + '.py')
    loaded = types.ModuleType('_e23_source_' + name)
    loaded.__file__ = str(path)
    sys.modules[loaded.__name__] = loaded
    exec(compile(path.read_bytes(), str(path), 'exec'), loaded.__dict__)
    return loaded


evaluate = source_module('perspective_gate').evaluate
reader_source = source_module('reader_source_gate')
canonical, validate_contract = reader_source.canonical, reader_source.validate_contract


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module_identity(path):
    """Bind loaded source bytes; do not mislabel uncommitted bytes as a commit."""
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[3]
    relative = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    commit = None
    try:
        head = subprocess.check_output(['git', '--no-replace-objects', '-C', str(root),
                                        'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL, text=True).strip()
        committed = subprocess.check_output(['git', '--no-replace-objects', '-C', str(root),
                                             'show', head + ':' + relative], stderr=subprocess.DEVNULL)
        if committed == raw:
            commit = head
    except (OSError, subprocess.CalledProcessError):
        pass
    return {'path': relative, 'sha256': sha(raw), 'commit': commit,
            'commit_status': 'COMMITTED_SOURCE_BYTES_MATCH' if commit else 'UNCOMMITTED_SOURCE_SHA_RECORDED'}


def verified_runner(path, expected_sha256):
    """Only execute this checkout's existing writer at an explicit byte pin."""
    root = Path(__file__).resolve().parents[3]
    canonical_runner = root / 'deepwrite/tools/writing_loop_experimental.py'
    selected = Path(path).absolute() if path is not None else canonical_runner
    if any(p.is_symlink() for p in (selected, *selected.parents)):
        raise ValueError('E18_RUNNER_SYMLINK_REJECTED')
    if selected.resolve() != canonical_runner or not selected.is_file():
        raise ValueError('ONLY_EXISTING_CANONICAL_E18_RUNNER_MAY_EXECUTE')
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or sha(selected.read_bytes()) != expected_sha256:
        raise ValueError('E18_RUNNER_EXPECTED_SHA_REQUIRED_OR_MISMATCH')
    return module_identity(selected)


def safe_write(path, data):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('PRIVATE_OUTPUT_SYMLINK_REJECTED')
    if path.exists() and path.read_bytes() != data:
        raise ValueError('EXISTING_SOURCE_COLLISION_' + path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def prepare(config_path, frame_path, selection_path, project_root, prepared_path):
    config_path, frame_path, selection_path = [Path(p).resolve() for p in (config_path, frame_path, selection_path)]
    project_root, prepared_path = Path(project_root).absolute(), Path(prepared_path).absolute()
    for output in (project_root, prepared_path):
        if any(p.is_symlink() for p in (output, *output.parents)):
            raise ValueError('PRIVATE_OUTPUT_SYMLINK_REJECTED')
    project_root, prepared_path = project_root.resolve(), prepared_path.resolve()
    code_root = Path(__file__).resolve().parents[3]
    if project_root.is_relative_to(code_root) or prepared_path.is_relative_to(code_root):
        raise ValueError('PRIVATE_PREWRITE_OUTPUT_MUST_BE_OUTSIDE_PUBLIC_CODE_REPOSITORY')
    if prepared_path.is_relative_to(project_root):
        raise ValueError('DERIVED_CONFIG_MUST_BE_OUTSIDE_PRIVATE_PROJECT')
    raw = config_path.read_bytes()
    config = json.loads(raw)
    if config.get('channel') != 'SHADOW' or config.get('run_mode','fresh') != 'fresh':
        raise ValueError('REQUIRES_EXPLICIT_SHADOW_FRESH_RUN')
    if not config.get('sources') or not isinstance(config['sources'], list):
        raise ValueError('FROZEN_SOURCES_REQUIRED')
    manifest_bytes, selection_bytes = frame_path.read_bytes(), selection_path.read_bytes()
    manifest, selection = json.loads(manifest_bytes), json.loads(selection_bytes)
    audit = evaluate(manifest, frame_path.parent)
    if audit['structural'] != 'PASS':
        raise ValueError('FRAME_SOURCE_OR_PRIOR_CHECK_FAILED')
    if selection.get('schema') != 'deepwrite/perspective-selection/v0.1':
        raise ValueError('SELECTION_SCHEMA_INVALID')
    if selection.get('manifest_sha256') != sha(manifest_bytes):
        raise ValueError('FRAME_MANIFEST_SHA_MISMATCH')
    ident = selection.get('selected_lens_id')
    matches = [x for x in audit['lenses'] if x['id'] == ident]
    if len(matches) != 1 or matches[0]['status'] != 'HOLD_HUMAN_SEMANTIC_AND_ADVERSARIAL_REVIEW':
        raise ValueError('SELECTED_FRAME_IS_NOT_UNPROVEN_RIVAL')
    if selection.get('classification') not in ('REFRAME', 'HYPOTHESIS_NEW'):
        raise ValueError('REPAIRED_OLD_CONCEPT_MUST_NOT_DRIVE_REWRITE')
    for field in ('why_this_frame', 'strongest_counterargument', 'unique_reader_decision'):
        if not isinstance(selection.get(field), str) or len(selection[field].strip()) < 45:
            raise ValueError('SELECTION_MISSING_' + field)
    if selection.get('author_acceptance') != 'NOT_CLAIMED':
        raise ValueError('NO_HUMAN_AUTH_FROM_FREE_TEXT')
    if selection.get('semantic_novelty') != 'UNVERIFIED':
        raise ValueError('SEMANTIC_NOVELTY_MUST_REMAIN_UNVERIFIED')
    lens = next(x for x in manifest['lenses'] if x['id'] == ident)
    # The selected frame must genuinely enter the downstream runner's source list AND task statement.
    context = ('# Source-frame selection | EXPERIMENTAL, NOT PROVEN\n\n'
               'Selected lens: ' + ident + '\n\n'
               'Original assumption: ' + lens['source_assumption'] + '\n'
               'Counter-interpretation: ' + lens['counterinterpretation'] + '\n'
               'Target domain break: ' + lens['target_break'] + '\n'
               'Decision before: ' + lens['decision_before'] + '\n'
               'Decision after: ' + lens['decision_after'] + '\n'
               'Source falsifier: ' + lens['source_falsifier'] + '\n'
               'Target falsifier: ' + lens['target_falsifier'] + '\n'
               'Old prior-art result: ' + ', '.join(matches[0]['prior_status']) + '\n\n'
               'Counterargument: ' + selection['strongest_counterargument'] + '\n'
               'Reader decision: ' + selection['unique_reader_decision'] + '\n'
               'Quality and novelty are UNVERIFIED. No automatic publication or stable promotion.\n')
    sources = project_root / 'sources'
    files = {'e23_frame_manifest.json': manifest_bytes,
             'e23_frame_selection.json': selection_bytes,
             'e23_frame_context.md': context.encode('utf-8')}
    reader_contract = config.get('reader_prior_knowledge_contract')
    reader_receipt = None
    if reader_contract is not None:
        reader_receipt = validate_contract(reader_contract, config.get('chapters', []))
        files['e23_reader_prior_contract.json'] = canonical(reader_contract)
    for name, data in files.items():
        safe_write(sources / name, data)
    amended = dict(config)
    amended['sources'] = list(config['sources']) + [
        {'path':'sources/' + name, 'sha256':sha(data)} for name, data in files.items()]
    amended['wish'] = (str(config.get('wish','')) + '\n\n'
        'E23 SHADOW PERSPECTIVE GOVERNANCE: Evaluate the source-frame hypothesis from sources/e23_frame_context.md before outlining. '
        'Find contrary evidence and rewrite the chapter objective only when the selected frame makes a different reader decision. '
        'Do not call recovery of existing prior art a new discovery. Even if the sample is readable, quality stays UNVERIFIED.')
    if reader_receipt:
        amended['wish'] += ('\nREADER/SOURCE CONTRACT: sources/e23_reader_prior_contract.json is frozen. '
            'Establish the source-domain scene, actual actions and rules, importance, causal mechanism, '
            'counterexamples, conditions and failed analogy before target-domain transfer. '
            'The downstream runner must call its located reader/source reviewer and STOP or rewrite on major findings. '
            'This prewrite receipt is only identity wiring; it is not a semantic or human-reader PASS. '
            'Do not impose three audience headings or six-factor chapter templates.')
    # A later runner can verify these identities and prior output bytes. This
    # declaration alone cannot independently authenticate a prior invocation.
    receipt = {'schema':'deepwrite/e23-preprocess-receipt/v1',
        'claimed_execution':'ACTUALLY_PREPARED_BY_E23_ENTRY',
        'identity_scope':'DECLARED_PREPROCESS_SOURCE_AND_OUTPUT_BYTES_ONLY',
        'invocation_authenticated':False,
        'input_config_sha256':sha(raw),
        'frame_manifest_sha256':sha(manifest_bytes),
        'selection_sha256':sha(selection_bytes),
        'context_sha256':sha(files['e23_frame_context.md']),
        'module_files':[module_identity(Path(__file__).with_name(name)) for name in
                        ('prewrite_entry.py','perspective_gate.py','reader_source_gate.py')]}
    amended['e23_preprocess_receipt'] = receipt
    derived = (json.dumps(amended,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    safe_write(prepared_path, derived)
    return {'status':'PASS_PREWRITE_IDENTITY_AND_PROMPT_WIRING_ONLY',
            'quality':'UNVERIFIED','full_book':'NOT_RUN',
            'selected_lens_id':ident,'source_sha256':{k:sha(v) for k,v in files.items()},
            'derived_config_sha256':sha(derived),
            'original_config_sha256':sha(raw),
            'reader_contract':reader_receipt,
            'preprocess_receipt':receipt,
            'prewrite':audit['prewrite_decision']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--selection',type=Path,required=True)
    ap.add_argument('--project-root',type=Path,required=True)
    ap.add_argument('--prepared-config',type=Path,required=True)
    ap.add_argument('--runner',type=Path)
    ap.add_argument('--runner-sha256')
    ap.add_argument('--execute',action='store_true')
    a=ap.parse_args()
    try:
        result=prepare(a.config,a.manifest,a.selection,a.project_root,a.prepared_config)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if a.execute:
            runner_identity = verified_runner(a.runner, a.runner_sha256)
            print(json.dumps({'status':'E18_RUNNER_SOURCE_PIN_VERIFIED_NOT_QUALITY_OR_ACTIVATION',
                              'runner':runner_identity},ensure_ascii=False,indent=2),flush=True)
            result = subprocess.run([sys.executable,'-B',str(Path(__file__).resolve().parents[3] / runner_identity['path']),
                                     str(a.prepared_config),str(a.project_root)],check=False)
            print(json.dumps({'status':'E18_RUNNER_PROCESS_EXIT_RECORDED','returncode':result.returncode,
                              'formal_activation':'NOT_CLAIMED','quality':'UNVERIFIED'},ensure_ascii=False))
            return result.returncode
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print('STOP_FRAME_PREFLIGHT: ' + str(exc),file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
