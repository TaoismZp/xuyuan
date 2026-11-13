#!/usr/bin/env python3
"""Protected-main controller. Never imports or executes pull-request code.

Owner command: /deepwrite authorize ENGINEERING_PATCH <full-head-sha>
Append 'governance' to explicitly authorize changes to this control plane.
This is owner release authority, NOT an independent approving review. Run this
file from protected main. A head copy must not be its own release judge.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request
from release_verify import verify_transition

RUNTIME_CHECK = "activation-and-runtime-regressions"
REQUIRED_CHECK = "owner-release-authorization"
ACTIONS_APP_ID = 15368
COMMAND = re.compile(r"/deepwrite (?P<action>authorize (?P<scope>ENGINEERING_PATCH|QUALITY_BEHAVIOR_CHANGE)|revoke) (?P<head>[0-9a-f]{40})(?P<governance> governance)?$")
CONTROL_FILES = {
    ".github/workflows/deepwrite-activation.yml",
    ".github/workflows/deepwrite-owner-release.yml",
    "deepwrite/release/github_authorization.py",
    "deepwrite/release/release_verify.py",
}


class GitHub:
    def __init__(self, repository, token):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("INVALID_REPOSITORY")
        self.repository, self.token = repository, token

    def request(self, path, method="GET", data=None):
        url="https://api.github.com"+path
        raw=None if data is None else json.dumps(data).encode()
        req=urllib.request.Request(url,data=raw,method=method,headers={
            "Authorization":"Bearer "+self.token,"Accept":"application/vnd.github+json",
            "X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as response:
            payload=response.read(8*1024*1024+1)
        if len(payload)>8*1024*1024: raise ValueError("API_RESPONSE_TOO_LARGE")
        return json.loads(payload) if payload else {}

    def get(self, path): return self.request("/repos/"+self.repository+path)

    def pages(self,path):
        result=[]
        for page in range(1,32):
            rows=self.get(path+("&" if "?" in path else "?")+f"per_page=100&page={page}")
            if not isinstance(rows,list): raise ValueError("UNEXPECTED_PAGINATION_RESPONSE")
            result.extend(rows)
            if len(rows)<100: return result
        raise ValueError("PAGINATION_LIMIT_FAIL_CLOSED")


def owner_authorization(repository, pull, comments, changed_paths):
    owner=repository["owner"]
    head=pull["head"]["sha"]
    if owner.get("type")!="User":
        return {"status":"BLOCKED","reason":"ORG_AUTHORITY_NOT_CONFIGURED"}
    events=[]
    for comment in comments:
        user=comment.get("user",{})
        if user.get("type")!="User" or user.get("login","").casefold()!=owner["login"].casefold(): continue
        first=comment.get("body","").strip().splitlines()
        match=COMMAND.fullmatch(first[0]) if first else None
        if match and match["head"]==head:
            events.append((comment.get("updated_at") or comment.get("created_at") or "",comment["id"],match,comment))
    if not events: return {"status":"BLOCKED","reason":"NO_OWNER_EXACT_HEAD_AUTHORIZATION"}
    _,_,match,comment=max(events,key=lambda x:(x[0],x[1]))
    if match["action"]=="revoke": return {"status":"BLOCKED","reason":"OWNER_REVOKED","comment_id":comment["id"]}
    governance=bool(match["governance"])
    control_change=bool(set(changed_paths)&CONTROL_FILES)
    if control_change and not governance:
        return {"status":"BLOCKED","reason":"EXPLICIT_GOVERNANCE_AUTHORIZATION_REQUIRED"}
    return {"status":"OWNER_EXACT_HEAD_AUTHORIZED","scope":match["scope"],"head_sha":head,
            "owner":owner["login"],"comment_id":comment["id"],"governance":governance,
            "independent_review":False}


def runtime_ci(checks,head):
    rows=[c for c in checks if c.get("name")==RUNTIME_CHECK and c.get("head_sha")==head and
          c.get("app",{}).get("id")==ACTIONS_APP_ID]
    if not rows: return {"status":"BLOCKED","reason":"NO_ACTUAL_RUNTIME_CI_FOR_EXACT_HEAD"}
    latest=max(rows,key=lambda c:c["id"])
    if latest.get("status")!="completed" or latest.get("conclusion")!="success":
        return {"status":"BLOCKED","reason":"RUNTIME_CI_NOT_SUCCESS","check_id":latest["id"]}
    return {"status":"ACTUAL_RUNTIME_CI_SUCCESS","check_id":latest["id"]}


def protected_configuration(repository,rulesets):
    """Actual API settings, not desired settings copied from a manifest."""
    reasons=[]
    if repository.get("allow_auto_merge") is not True: reasons.append("REPOSITORY_AUTO_MERGE_DISABLED")
    if repository.get("allow_merge_commit") is not True: reasons.append("MERGE_COMMITS_REQUIRED_FOR_IMPLEMENTATION_ANCESTRY")
    selected=[]
    for rs in rulesets:
        if rs.get("enforcement")!="active" or rs.get("target")!="branch": continue
        names=rs.get("conditions",{}).get("ref_name",{})
        def applies(pattern):
            return (pattern=="~DEFAULT_BRANCH" and repository.get("default_branch")=="main") or pattern=="~ALL" or fnmatch.fnmatchcase("refs/heads/main",pattern)
        if any(applies(x) for x in names.get("include",[])) and not any(applies(x) for x in names.get("exclude",[])):
            selected.append(rs)
    if not selected: reasons.append("NO_ACTIVE_MAIN_RULESET")
    contexts=set();types=set();strict=False;pr_rule=False
    for rs in selected:
        if rs.get("bypass_actors"): reasons.append("MAIN_BYPASS_ACTORS_NOT_ALLOWED")
        for rule in rs.get("rules",[]):
            types.add(rule["type"]);parameters=rule.get("parameters",{})
            if rule["type"]=="pull_request":
                pr_rule=True
                if parameters.get("required_approving_review_count",0)!=0:
                    reasons.append("SINGLE_OWNER_REVIEW_RULE_STILL_BLOCKS")
            if rule["type"]=="required_status_checks":
                strict|=parameters.get("strict_required_status_checks_policy") is True
                contexts.update((x.get("context"),x.get("integration_id")) for x in parameters.get("required_status_checks",[]))
    if not pr_rule: reasons.append("PULL_REQUEST_RULE_REQUIRED")
    if not strict: reasons.append("STRICT_BASE_CI_REQUIRED")
    if not {"deletion","non_fast_forward"}<=types: reasons.append("MAIN_DELETION_AND_FORCE_PUSH_PROTECTION_REQUIRED")
    for context in (RUNTIME_CHECK,REQUIRED_CHECK):
        if (context,ACTIONS_APP_ID) not in contexts: reasons.append("MISSING_ACTIONS_BOUND_REQUIRED_CHECK:"+context)
    return {"status":"BLOCKED" if reasons else "ACTUAL_REPOSITORY_PROTECTION_READY","reasons":reasons}


def evaluate(repository,pull,comments,files,checks):
    if pull.get("state")!="open" or pull.get("draft") or pull.get("base",{}).get("ref")!="main":
        return {"status":"BLOCKED","reason":"NOT_READY_MAIN_PR"}
    if pull.get("head",{}).get("repo",{}).get("full_name")!=repository["full_name"]:
        return {"status":"BLOCKED","reason":"FORK_RELEASE_REQUIRES_SEPARATE_REVIEW"}
    paths={f["filename"] for f in files}|{f["previous_filename"] for f in files if "previous_filename" in f}
    ci=runtime_ci(checks,pull["head"]["sha"])
    if ci["status"]!="ACTUAL_RUNTIME_CI_SUCCESS": return ci
    if not any(p.startswith("deepwrite/") or p in CONTROL_FILES for p in paths):
        return {"status":"NOT_A_DEEPWRITE_RELEASE","ci":ci,"paths":sorted(paths)}
    authority=owner_authorization(repository,pull,comments,paths)
    if authority["status"]!="OWNER_EXACT_HEAD_AUTHORIZED": return authority
    if authority["scope"]!="ENGINEERING_PATCH":
        return {"status":"BLOCKED","reason":"QUALITY_PROMOTION_REQUIRES_SEPARATE_HUMAN_EVIDENCE_REVIEW",
                "authorization":authority}
    return {"status":"READY_FOR_TRANSITION_CHECK","authorization":authority,"ci":ci,"paths":sorted(paths)}


def checkout_pair(repository,pr_number,base_sha,head_sha,destination):
    """Checkout bytes only; no candidate programs, hooks or package installers."""
    repo=Path(destination)/"objects"
    subprocess.run(["git","clone","--quiet","--no-checkout","--filter=blob:none",
                    "https://github.com/"+repository+".git",str(repo)],check=True)
    subprocess.run(["git","-C",str(repo),"fetch","--quiet","origin",f"refs/pull/{pr_number}/head"],check=True)
    subprocess.run(["git","-C",str(repo),"cat-file","-e",head_sha+"^{commit}"],check=True)
    result=[]
    for name,sha in (("base",base_sha),("head",head_sha)):
        target=Path(destination)/name
        subprocess.run(["git","-C",str(repo),"-c","core.hooksPath=/dev/null","worktree","add","--quiet","--detach",str(target),sha],check=True)
        result.append(target)
    return result


def publish_check(api,sha,result):
    good=result["status"] in ("AUTHORIZED_ENGINEERING_RELEASE","NOT_A_DEEPWRITE_RELEASE")
    return api.request("/repos/"+api.repository+"/check-runs","POST",{
        "name":REQUIRED_CHECK,"head_sha":sha,"status":"completed",
        "conclusion":"success" if good else "failure",
        "output":{"title":result["status"],"summary":json.dumps(result,ensure_ascii=False,indent=2)}})


def enable_auto_merge(api,pull):
    # Squash/rebase would discard the implementation_commit ancestry frozen in
    # the active-engine record. Formal activation must retain the original Git
    # implementation object as an ancestor of main.
    query="mutation($id:ID!){enablePullRequestAutoMerge(input:{pullRequestId:$id,mergeMethod:MERGE}){pullRequest{number autoMergeRequest{enabledAt}}}}"
    response=api.request("/graphql","POST",{"query":query,"variables":{"id":pull["node_id"]}})
    if response.get("errors"): raise ValueError("GITHUB_AUTO_MERGE_REJECTED:"+json.dumps(response["errors"]))
    return response


def trusted_controller_source(api,base_sha,source_dir=None):
    """A candidate copy cannot publish authoritative checks for itself."""
    directory=Path(source_dir) if source_dir else Path(__file__).resolve().parent
    for filename in ("github_authorization.py","release_verify.py"):
        raw=(directory/filename).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        actual=api.get("/contents/deepwrite/release/"+filename+"?ref="+base_sha)
        if actual.get("type")!="file" or actual.get("sha")!=blob:
            raise ValueError("RUNNING_CONTROLLER_NOT_IDENTICAL_TO_PROTECTED_BASE:"+filename)


def control(api,number,publish=False,auto_merge=False):
    repository=api.get("");pull=api.get(f"/pulls/{number}")
    if publish or auto_merge:
        trusted_controller_source(api,pull["base"]["sha"])
    files=api.pages(f"/pulls/{number}/files")
    comments=api.pages(f"/issues/{number}/comments")
    checks=api.get(f"/commits/{pull['head']['sha']}/check-runs?per_page=100")["check_runs"]
    if len(checks)>=100: raise ValueError("CHECKS_PAGINATION_UNSUPPORTED_FAIL_CLOSED")
    result=evaluate(repository,pull,comments,files,checks)
    if result["status"]=="READY_FOR_TRANSITION_CHECK":
        with tempfile.TemporaryDirectory(prefix="deepwrite-release-data-") as tmp:
            base,head=checkout_pair(api.repository,number,pull["base"]["sha"],pull["head"]["sha"],tmp)
            transition=verify_transition(base,head,result["paths"])
        result["transition"]=transition
        if transition.get("change_scope") not in (None,result["authorization"]["scope"]):
            transition={"status":"BLOCKED","reasons":["OWNER_SCOPE_DOES_NOT_AUTHORIZE_MANIFEST_SCOPE"]}
            result["transition"]=transition
        result["status"]=("AUTHORIZED_ENGINEERING_RELEASE" if transition["status"] in
            ("NO_ACTIVATION_CHANGE","ACTIVATION_BYTES_READY_NEEDS_LIVE_GITHUB_AUTHORITY") else "BLOCKED")
    current=api.get(f"/pulls/{number}")
    if current["head"]["sha"]!=pull["head"]["sha"] or current["base"]["sha"]!=pull["base"]["sha"]:
        raise ValueError("PR_CHANGED_DURING_VERIFICATION")
    if result["status"]=="AUTHORIZED_ENGINEERING_RELEASE":
        rulesets=[api.get("/rulesets/"+str(r["id"])) for r in api.get("/rulesets?includes_parents=true")
                  if r.get("enforcement")=="active" and r.get("target")=="branch"]
        config=protected_configuration(repository,rulesets)
        result["repository_protection"]=config
        if config["status"]!="ACTUAL_REPOSITORY_PROTECTION_READY":
            result["status"]="BLOCKED";result["reason"]="REPOSITORY_PROTECTION_NOT_READY"
    # This check is tied to this exact head. A later push has no owner-authorized
    # combined check and cannot inherit the old success under required checks.
    if publish: result["published_check_id"]=publish_check(api,pull["head"]["sha"],result)["id"]
    if auto_merge and result["status"]=="AUTHORIZED_ENGINEERING_RELEASE":
        if repository.get("allow_merge_commit") is not True:
            raise ValueError("FORMAL_ACTIVATION_REQUIRES_MERGE_COMMITS_NOT_SQUASH_OR_REBASE")
        result["auto_merge"]=enable_auto_merge(api,current)
    result["head_sha"]=pull["head"]["sha"]
    result["authority_basis"]="REAL_GITHUB_OWNER_COMMAND_NOT_INDEPENDENT_REVIEW"
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument("--repository",default=os.environ.get("GITHUB_REPOSITORY"))
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument("--pull-request",type=int);source.add_argument("--event",type=Path)
    p.add_argument("--publish-check",action="store_true")
    p.add_argument("--auto-merge",action="store_true");a=p.parse_args()
    token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token: raise SystemExit("BLOCKED_NO_GITHUB_TOKEN")
    try:
        api=GitHub(a.repository,token)
        if a.pull_request: numbers=[a.pull_request]
        else:
            event=json.loads(a.event.read_text())
            if event.get("issue",{}).get("pull_request"): numbers=[event["issue"]["number"]]
            elif event.get("workflow_run"):
                run=event["workflow_run"]
                if run.get("event")!="pull_request": numbers=[]
                else:
                    numbers=[p["number"] for p in run.get("pull_requests",[])]
                    if not numbers:
                        numbers=[p["number"] for p in api.pages("/commits/"+run["head_sha"]+"/pulls")
                                 if p.get("state")=="open"]
            else:
                value=event.get("inputs",{}).get("pull_request","")
                if not str(value).isdigit(): raise ValueError("DISPATCH_REQUIRES_PR_NUMBER")
                numbers=[int(value)]
        results=[control(api,number,a.publish_check,a.auto_merge) for number in sorted(set(numbers))]
        result={"status":"COMPLETE" if all(r["status"] in ("AUTHORIZED_ENGINEERING_RELEASE","NOT_A_DEEPWRITE_RELEASE") for r in results) else "BLOCKED",
                "results":results,"required_source_code_policy":"PROTECTED_MAIN_ONLY",
                "mode":"PUBLICATION" if a.publish_check or a.auto_merge else "READ_ONLY_DRY_RUN"}
    except Exception as error:
        result={"status":"BLOCKED","reason":type(error).__name__+":"+str(error)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="COMPLETE" else 2

if __name__=="__main__": raise SystemExit(main())
