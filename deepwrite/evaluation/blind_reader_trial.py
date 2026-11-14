#!/usr/bin/env python3
"""Human reading trial packaging: blinded book pairs and knowledge transfer.

Does not simulate a reader, judge creativity, or claim randomization was truly
independent. The separate operator key must never enter the reviewer packet.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


class TrialBlocked(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def private(path):
    path = Path(path).absolute()
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise TrialBlocked("TRIAL_SYMLINK_FORBIDDEN")
    root = Path(__file__).resolve().parents[2].resolve()
    if path.resolve().is_relative_to(root):
        raise TrialBlocked("TRIAL_PRIVATE_FILES_MUST_STAY_OUTSIDE_PUBLIC_CODE")
    return path.resolve()


def input_source(path, expected_sha256):
    p = private(path)
    if not p.is_file() or not re.fullmatch(r"[a-f0-9]{64}", str(expected_sha256)):
        raise TrialBlocked("TRIAL_EXACT_SOURCE_SHA_REQUIRED")
    raw = p.read_bytes()
    if digest(raw) != expected_sha256:
        raise TrialBlocked("TRIAL_SOURCE_BYTES_CHANGED")
    if len(raw) < 120 or len(raw) > 3_000_000:
        raise TrialBlocked("TRIAL_SOURCE_LENGTH_INVALID")
    raw.decode("utf-8")
    return raw


def prepare(config, packet_folder, secret_folder):
    """Frozen complete works. Requires external novel transfer question.

    Packet may be shared with external readers; secret mapping belongs in a
    distinct private folder, NEVER in packet or published source repository.
    """
    if config.get("schema") != "deepwrite/paired-reader-trial/v1":
        raise TrialBlocked("TRIAL_CONFIG_SCHEMA_REQUIRED")
    for x in ("project_id", "reader_task", "novel_transfer_question",
              "novel_transfer_expected_mechanism", "novel_transfer_counterexample"):
        if not isinstance(config.get(x), str) or len(config[x].strip()) < 15:
            raise TrialBlocked("TRIAL_READER_TASK_AND_TRANSFER_REQUIRED_" + x)
    pairs = config.get("works")
    if not isinstance(pairs, dict) or set(pairs) != {"baseline", "candidate"}:
        raise TrialBlocked("TRIAL_FROZEN_PAIR_REQUIRED")
    baseline = input_source(pairs["baseline"]["path"], pairs["baseline"]["sha256"])
    candidate = input_source(pairs["candidate"]["path"], pairs["candidate"]["sha256"])
    if baseline == candidate:
        raise TrialBlocked("TRIAL_IDENTICAL_WORKS_NOT_INFORMATIVE")
    key = config.get("operator_blinding_seed")
    if not isinstance(key, str) or len(key) < 24:
        raise TrialBlocked("TRIAL_EXTERNAL_BLINDING_SEED_REQUIRED")
    packet_folder, secret_folder = private(packet_folder), private(secret_folder)
    if (packet_folder == secret_folder or
            packet_folder.is_relative_to(secret_folder) or secret_folder.is_relative_to(packet_folder)):
        raise TrialBlocked("TRIAL_KEY_MUST_BE_OUTSIDE_REVIEW_PACKET")
    if packet_folder.exists() or secret_folder.exists():
        raise TrialBlocked("TRIAL_NO_OVERWRITE_EXISTING_PACKET_OR_KEY")
    packet_folder.parent.mkdir(parents=True, exist_ok=True)
    secret_folder.parent.mkdir(parents=True, exist_ok=True)
    first = (digest((key + "\0" + config["project_id"]).encode("utf-8"))[-1] in "02468ace")
    mapping = {"A": "baseline" if first else "candidate",
               "B": "candidate" if first else "baseline"}
    raw = {"baseline": baseline, "candidate": candidate}
    secret_folder.mkdir(mode=0o700)
    # If writing fails halfway the directory is intentionally left for audit;
    # retries require a fresh project/trial id and new destination.
    (secret_folder / "MAPPING_PRIVATE.json").write_bytes(canonical({
        "schema": "deepwrite/reader-trial-private-key/v1",
        "project_id": config["project_id"], "mapping": mapping,
        "expected_baseline_sha256": digest(baseline),
        "expected_candidate_sha256": digest(candidate),
        "seed_sha256": digest(key.encode("utf-8")),
        "is_true_independent_blind": "UNVERIFIED",
        "author_signoff": "NOT_RUN"
    }))
    packet_folder.mkdir(mode=0o700)
    for label, tag in mapping.items():
        (packet_folder / (label + ".md")).write_bytes(raw[tag])
    tasks = ("# DeepWrite 陌生读者双盲式比较问卷（标签不代表质量排序）\n\n"
             "本次材料A/B的真实来源由独立保管者持有。阅读时不要打开任何答案映射。\n\n"
             "## 阅读任务\n" + config["reader_task"] + "\n\n"
             "## 三层读者回答（必须给出明确正文证据）\n"
             "1. 新手：哪篇帮助你真实理解陌生源领域、为什么有意思？哪里读不下去？\n"
             "2. 熟手：哪篇改变了你原有判断？能否准确描述新机制而非只背结论？\n"
             "3. 高手：哪篇对关键前提、反例、源学科事实和数学有更完整的检验？\n"
             "4. 反方：指出两篇各自最严重的内容缺陷与有价值的KEEP段落。\n\n"
             "## 事先冻结的跨情境迁移试题（知识复利）\n" +
             config["novel_transfer_question"] + "\n\n"
             "请先独立解题，不读取模型示范答案。读者ID、答案及声明分开存到保密评估档案。\n\n"
             "本问卷不提供参考答案，避免评审信息泄漏。真实读者是否独立、是否看到了映射，需外部记录。\n")
    (packet_folder / "READER_TASK.md").write_text(tasks, encoding="utf-8")
    receipt = {"schema": "deepwrite/blinded-reader-packet-receipt/v1",
               "status": "PACKET_PREPARED_READER_ASSESSMENT_NOT_RUN",
               "project_id": config["project_id"],
               "sha256": {label: digest((packet_folder / (label + ".md")).read_bytes())
                          for label in ("A", "B")},
               "reader_task_sha256": digest((packet_folder / "READER_TASK.md").read_bytes()),
               "key_outside_packet": True, "human_readers": 0,
               "blindness_validated_by_independent_operator": False,
               "author_acceptance": "NOT_RUN", "quality_result": "UNVERIFIED"}
    (packet_folder / "RECEIPT.json").write_bytes(canonical(receipt))
    return receipt


def collect(packet_folder, secret_folder, reader_responses, evaluation_out):
    """Only records actual supplied responses; does not fabricate people or infer taste."""
    packet_folder, secret_folder = private(packet_folder), private(secret_folder)
    evaluation_out = private(evaluation_out)
    if evaluation_out.exists():
        raise TrialBlocked("TRIAL_EVALUATION_OUTPUT_ALREADY_EXISTS")
    receipt = json.loads((packet_folder / "RECEIPT.json").read_bytes())
    mapping = json.loads((secret_folder / "MAPPING_PRIVATE.json").read_bytes())
    if receipt["project_id"] != mapping["project_id"]:
        raise TrialBlocked("TRIAL_KEY_PACKET_PROJECT_ID_MISMATCH")
    for letter in ("A", "B"):
        if digest((packet_folder / (letter + ".md")).read_bytes()) != receipt["sha256"][letter]:
            raise TrialBlocked("TRIAL_READER_PACKET_CHANGED_AFTER_FREEZE")
    if not isinstance(reader_responses, list) or not reader_responses:
        raise TrialBlocked("TRIAL_REAL_READER_RESPONSES_REQUIRED")
    identities = set()
    votes = {"A": 0, "B": 0, "TIE": 0}
    raw = []
    for path in reader_responses:
        p = private(path)
        raw_response = p.read_bytes()
        answer = json.loads(raw_response)
        name = answer.get("reader_id")
        if (not isinstance(name, str) or not name.strip() or name in identities or
                answer.get("saw_private_mapping") is not False or
                answer.get("independent_reader_attestation") is not True):
            raise TrialBlocked("TRIAL_READER_RESPONSES_INCOMPLETE_OR_NOT_DECLARED_BLIND")
        identities.add(name)
        for axis in ("novice", "practitioner", "expert", "transfer_answer", "negative_findings"):
            if not isinstance(answer.get(axis), str) or len(answer[axis].strip()) < 15:
                raise TrialBlocked("TRIAL_READER_REASONING_REQUIRED_" + axis)
        if answer.get("preference") not in votes:
            raise TrialBlocked("TRIAL_READER_CHOICE_REQUIRED")
        votes[answer["preference"]] += 1
        raw.append({"reader_id": name, "response_sha256": digest(raw_response),
                    "preference": answer["preference"]})
    result = {"schema": "deepwrite/reader-trial-tally/v1",
              "project_id": receipt["project_id"], "recorded_responses": len(raw),
              "responses": raw, "votes": votes,
              "correspondence": mapping["mapping"],
              "reader_independence": "SELF_ATTESTED_NOT_AUTHENTICATED",
              "reader_transfer_success": "REQUIRES_EXTERNAL_JUDGING_OF_CONTENT",
              "equal_budget_and_source_control": "NOT_VERIFIED_BY_THIS_TOOL",
              "validity": "RESPONSE_FILES_RECORDED_NOT_AUTOMATIC_QUALITY_PASS",
              "author_acceptance": "NOT_RUN"}
    evaluation_out.parent.mkdir(parents=True, exist_ok=True)
    evaluation_out.write_bytes(canonical(result))
    return result
