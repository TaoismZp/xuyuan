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
from pathlib import Path

from perspective_gate import evaluate


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_write(path, data):
    if path.exists() and path.read_bytes() != data:
        raise ValueError('EXISTING_SOURCE_COLLISION_' + path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def prepare(config_path, frame_path, selection_path, project_root, prepared_path):
    config_path, frame_path, selection_path = [Path(p).resolve() for p in (config_path, frame_path, selection_path)]
    project_root, prepared_path = Path(project_root).resolve(), Path(prepared_path).resolve()
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
    for name, data in files.items():
        safe_write(sources / name, data)
    amended = dict(config)
    amended['sources'] = list(config['sources']) + [
        {'path':'sources/' + name, 'sha256':sha(data)} for name, data in files.items()]
    amended['wish'] = (str(config.get('wish','')) + '\n\n'
        'E23 SHADOW PERSPECTIVE GOVERNANCE: Evaluate the source-frame hypothesis from sources/e23_frame_context.md before outlining. '
        'Find contrary evidence and rewrite the chapter objective only when the selected frame makes a different reader decision. '
        'Do not call recovery of existing prior art a new discovery. Even if the sample is readable, quality stays UNVERIFIED.')
    derived = (json.dumps(amended,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    safe_write(prepared_path, derived)
    return {'status':'PASS_PREWRITE_IDENTITY_AND_PROMPT_WIRING_ONLY',
            'quality':'UNVERIFIED','full_book':'NOT_RUN',
            'selected_lens_id':ident,'source_sha256':{k:sha(v) for k,v in files.items()},
            'derived_config_sha256':sha(derived),
            'original_config_sha256':sha(raw),
            'prewrite':audit['prewrite_decision']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--selection',type=Path,required=True)
    ap.add_argument('--project-root',type=Path,required=True)
    ap.add_argument('--prepared-config',type=Path,required=True)
    ap.add_argument('--runner',type=Path)
    ap.add_argument('--execute',action='store_true')
    a=ap.parse_args()
    try:
        result=prepare(a.config,a.manifest,a.selection,a.project_root,a.prepared_config)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if a.execute:
            if not a.runner or not a.runner.is_file(): raise ValueError('E18_RUNNER_PATH_REQUIRED')
            return subprocess.run([sys.executable,str(a.runner),str(a.prepared_config),str(a.project_root)],check=False).returncode
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print('STOP_FRAME_PREFLIGHT: ' + str(exc),file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())