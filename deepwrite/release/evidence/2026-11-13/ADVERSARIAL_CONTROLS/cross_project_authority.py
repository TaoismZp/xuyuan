#!/usr/bin/env python3
"""Cross-project authority binding negative control; engineering fixture only."""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

p=Path('/workspace/deepwrite-release/deepwrite/tools/tests/test_writing_loop_experimental.py')
s=importlib.util.spec_from_file_location('audit_other_auth',p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)/'project';cfg=m.config(root)
    reference=cfg['execution_contract']['authorization']
    auth=root/reference['path']
    raw=json.dumps({'schema':'deepwrite/author-project-authorization/v1',
        'project_id':'ANOTHER_BOOK','mode':'AUTONOMOUS_FULL_DRAFT',
        'evidence_kind':'PUBLIC_ENGINEERING_FIXTURE_NOT_REAL_AUTHOR'}).encode()
    auth.write_bytes(raw);h=m.loop.digest(raw)
    next(row for row in cfg['sources'] if row['path']==reference['path'])['sha256']=h
    reference['sha256']=h
    try:
        obj=m.loop.WritingLoop(root,cfg,model=m.ScriptedModel(clean=True))
        result={'status':'ACCEPTED_CROSS_PROJECT_AUTHORITY_REFERENCE',
            'requested_project':cfg['project_id'],'actual_authority_artifact_project':'ANOTHER_BOOK',
            'frozen_mode':obj.state['execution_mode']}
    except Exception as error:
        result={'status':'BLOCKED','type':type(error).__name__,'reason':str(error)}
    result['evidence_kind']='ACTUAL_ENGINEERING_FIXTURE_NOT_MODEL_OR_AUTHOR_VERIFICATION'
    print(json.dumps(result,indent=2))
